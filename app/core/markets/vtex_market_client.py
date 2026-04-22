from __future__ import annotations

import re
from abc import abstractmethod

import requests

from app.core.entities.address import Address
from app.core.entities.coverage import CoverageResult, CoverageStatus
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shopping_item import ShoppingItem
from app.core.entities.shipping_info import ShippingInfo
from app.core.markets.market_client import MarketClient
from app.core.parsers.vtex_shipping_parser import parse_vtex_shipping_response


class VtexMarketClient(MarketClient):
    """
    Cliente base para mercados VTEX.

    Centraliza o fluxo comum de:
    - coverage/regionalização via simulation
    - extração de shipping pelo mesmo response
    - busca de produtos após coverage válido
    - construção de search terms
    - deduplicação de ofertas
    """

    def __init__(self) -> None:
        self.session = requests.Session()
        self.is_regionalized = False
        self._last_shipping_info: ShippingInfo | None = None

    def check_coverage(self, address: Address) -> CoverageResult:
        postal_code = self._normalize_postal_code(address.postal_code)

        if not postal_code:
            self._last_shipping_info = ShippingInfo(
                price=None,
                delivery_estimate=None,
                raw_text=None,
            )
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )

        try:
            response_json = self._execute_coverage_request(postal_code=postal_code)

            result = self._parse_coverage_response(response_json)
            self._last_shipping_info = parse_vtex_shipping_response(response_json)
            self.is_regionalized = result.status == CoverageStatus.COVERED

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
                response_json = self._execute_search_request(term=term)
                offers = self._parse_products_response(response_json)
                all_offers.extend(offers)

            return self._deduplicate_offers(all_offers)

        except requests.Timeout:
            return []
        except requests.RequestException:
            return []
        except Exception:
            return []

    def get_shipping_info(self, address: Address) -> ShippingInfo:
        """
        Retorna as informações de frete e prazo já obtidas pela sessão atual.

        Se ainda não houver contexto carregado, executa o coverage para popular
        os dados de entrega a partir do endpoint de simulation.
        """
        if self._last_shipping_info is not None:
            return self._last_shipping_info

        self.check_coverage(address)

        return self._last_shipping_info or ShippingInfo(
            price=None,
            delivery_estimate=None,
            raw_text=None,
        )

    @abstractmethod
    def _execute_coverage_request(self, postal_code: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _parse_coverage_response(self, response_json: dict) -> CoverageResult:
        raise NotImplementedError

    @abstractmethod
    def _execute_search_request(self, term: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def _parse_products_response(self, response_json: dict) -> list[ProductOffer]:
        raise NotImplementedError

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

        preferred_type = getattr(item, "preferred_type", None)

        if isinstance(preferred_type, str) and preferred_type.strip():
            terms.append(f"{base} {preferred_type.strip()}")

        elif isinstance(preferred_type, list):
            for value in preferred_type:
                if isinstance(value, str) and value.strip():
                    terms.append(f"{base} {value.strip()}")

        return VtexMarketClient._unique_terms(terms)

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
        return CoverageResult(
            status=CoverageStatus.UNKNOWN,
            has_delivery=False,
        )