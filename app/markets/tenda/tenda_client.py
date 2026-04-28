from __future__ import annotations

import re

import requests

from app.core.entities.address import Address
from app.core.entities.coverage import CoverageResult, CoverageStatus
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shopping_item import ShoppingItem
from app.core.entities.shipping_info import ShippingInfo
from app.core.markets.market_client import MarketClient
from app.markets.tenda.tenda_coverage import (
    execute_coverage_request,
    persist_delivery_zipcode,
)
from app.markets.tenda.tenda_parser import (
    parse_coverage_response,
    parse_products_response,
    parse_shipping_response,
)
from app.markets.tenda.tenda_search import execute_search_request
from app.markets.tenda.tenda_session import TendaSession


class TendaClient(MarketClient):
    """
    Cliente real do Tenda Atacado.

    Usa API própria REST:
    - OAuth público para Bearer token
    - shopping-cart para cartId/orderId
    - shipping-options para coverage/frete/prazo
    - store/search para busca de produtos
    """

    def __init__(self) -> None:
        self.tenda_session = TendaSession()
        self.is_regionalized = False
        self._last_shipping_info: ShippingInfo | None = None

    def get_market_name(self) -> str:
        return "Tenda"

    def check_coverage(self, address: Address) -> CoverageResult:
        postal_code = self._normalize_postal_code(address.postal_code)

        if not postal_code:
            return self._build_unknown_coverage_result()

        try:
            response_json = execute_coverage_request(
                tenda_session=self.tenda_session,
                postal_code=postal_code,
            )

            result = parse_coverage_response(response_json)
            self._last_shipping_info = parse_shipping_response(response_json)
            self.is_regionalized = result.status == CoverageStatus.COVERED

            if self.is_regionalized:
                persist_delivery_zipcode(
                    tenda_session=self.tenda_session,
                    postal_code=postal_code,
                )

            return result

        except requests.Timeout:
            return self._build_unknown_coverage_result()
        except requests.RequestException:
            return self._build_unknown_coverage_result()
        except Exception:
            return self._build_unknown_coverage_result()

    def search_products(self, item: ShoppingItem, address: Address) -> list[ProductOffer]:
        if not self.is_regionalized:
            coverage_result = self.check_coverage(address)
            if coverage_result.status != CoverageStatus.COVERED:
                return []

        search_terms = self._build_search_terms(item)
        if not search_terms:
            return []

        all_offers: list[ProductOffer] = []

        try:
            for term in search_terms:
                response_json = execute_search_request(
                    tenda_session=self.tenda_session,
                    term=term,
                )
                all_offers.extend(parse_products_response(response_json))

            return self._deduplicate_offers(all_offers)

        except requests.Timeout:
            return []
        except requests.RequestException:
            return []
        except Exception:
            return []

    def get_shipping_info(self, address: Address) -> ShippingInfo:
        if self._last_shipping_info is not None:
            return self._last_shipping_info

        self.check_coverage(address)

        return self._last_shipping_info or ShippingInfo(
            price=None,
            delivery_estimate=None,
            raw_text=None,
        )

    @staticmethod
    def _normalize_postal_code(postal_code: str | None) -> str:
        if not postal_code:
            return ""
        return re.sub(r"\D", "", postal_code)

    @staticmethod
    def _build_search_terms(item: ShoppingItem) -> list[str]:
        base = ""

        for attr_name in ("search_term", "name", "description", "raw_text"):
            value = getattr(item, attr_name, None)
            if isinstance(value, str) and value.strip():
                base = value.strip()
                break

        if not base:
            return []

        terms: list[str] = [base]

        preferred_brand = getattr(item, "preferred_brand", None)
        if isinstance(preferred_brand, str) and preferred_brand.strip():
            terms.append(f"{base} {preferred_brand.strip()}")
        elif isinstance(preferred_brand, list):
            for value in preferred_brand:
                if isinstance(value, str) and value.strip():
                    terms.append(f"{base} {value.strip()}")

        preferred_type = getattr(item, "preferred_type", None)
        if isinstance(preferred_type, str) and preferred_type.strip():
            terms.append(f"{base} {preferred_type.strip()}")
        elif isinstance(preferred_type, list):
            for value in preferred_type:
                if isinstance(value, str) and value.strip():
                    terms.append(f"{base} {value.strip()}")

        return TendaClient._unique_terms(terms)

    @staticmethod
    def _unique_terms(terms: list[str]) -> list[str]:
        unique: list[str] = []
        seen: set[str] = set()

        for term in terms:
            normalized = " ".join(term.split()).strip().lower()
            if not normalized or normalized in seen:
                continue

            seen.add(normalized)
            unique.append(term.strip())

        return unique

    @staticmethod
    def _deduplicate_offers(offers: list[ProductOffer]) -> list[ProductOffer]:
        unique: list[ProductOffer] = []
        seen: set[tuple[str, str]] = set()

        for offer in offers:
            key = (
                offer.product_url.strip().lower(),
                offer.product_name.strip().lower(),
            )

            if key in seen:
                continue

            seen.add(key)
            unique.append(offer)

        return unique

    def _build_unknown_coverage_result(self) -> CoverageResult:
        self._last_shipping_info = ShippingInfo(
            price=None,
            delivery_estimate=None,
            raw_text=None,
        )
        self.is_regionalized = False

        return CoverageResult(
            status=CoverageStatus.UNKNOWN,
            has_delivery=False,
        )