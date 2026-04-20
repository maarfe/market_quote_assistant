from __future__ import annotations

import re

import requests

from app.core.entities.address import Address
from app.core.entities.coverage import CoverageResult, CoverageStatus
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shopping_item import ShoppingItem
from app.core.markets.market_client import MarketClient
from app.markets.savegnago.savegnago_coverage import execute_coverage_request
from app.markets.savegnago.savegnago_parser import (
    parse_coverage_response,
    parse_products_response,
)
from app.markets.savegnago.savegnago_search import execute_search_request


class SavegnagoClient(MarketClient):
    """
    Cliente real do Savegnago baseado em:
    - simulation para coverage/regionalização
    - productSearchV3 para busca de produtos

    Regras importantes:
    - reutiliza a mesma requests.Session()
    - search só roda após coverage bem-sucedido
    """

    def __init__(self) -> None:
        self.session = requests.Session()
        self.is_regionalized = False

    def get_market_name(self) -> str:
        return "Savegnago"

    def check_coverage(self, address: Address) -> CoverageResult:
        postal_code = self._normalize_postal_code(address.postal_code)

        if not postal_code:
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )

        try:
            response_json = execute_coverage_request(
                session=self.session,
                postal_code=postal_code,
            )

            result = parse_coverage_response(response_json)

            self.is_regionalized = result.status == CoverageStatus.COVERED

            return result

        except requests.Timeout:
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )
        except requests.RequestException:
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )
        except Exception:
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )

    def search_products(self, item: ShoppingItem, address: Address) -> list[ProductOffer]:
        """
        Busca produtos no Savegnago.

        Regra obrigatória:
        - só executa a busca após coverage bem-sucedido
        """
        if not self.is_regionalized:
            coverage_result = self.check_coverage(address)
            if coverage_result.status != CoverageStatus.COVERED:
                return []

        search_term = self._extract_search_term(item)
        if not search_term:
            return []

        try:
            response_json = execute_search_request(
                session=self.session,
                term=search_term,
            )
            return parse_products_response(response_json)

        except requests.Timeout:
            return []
        except requests.RequestException:
            return []
        except Exception:
            return []

    @staticmethod
    def _normalize_postal_code(postal_code: str | None) -> str:
        if not postal_code:
            return ""
        return re.sub(r"\D", "", postal_code)

    @staticmethod
    def _extract_search_term(item: ShoppingItem) -> str:
        """
        Extrai o termo de busca do item da lista.

        Ajuste aqui se o seu ShoppingItem usar outro atributo.
        """
        for attr_name in ("search_term", "name", "description", "raw_text"):
            value = getattr(item, attr_name, None)
            if isinstance(value, str) and value.strip():
                return value.strip()

        return ""