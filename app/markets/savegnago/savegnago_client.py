from __future__ import annotations

from app.core.entities.coverage import CoverageResult
from app.core.entities.product_offer import ProductOffer
from app.core.markets.vtex_market_client import VtexMarketClient
from app.markets.savegnago.savegnago_coverage import execute_coverage_request
from app.markets.savegnago.savegnago_parser import (
    parse_coverage_response,
    parse_products_response,
)
from app.markets.savegnago.savegnago_search import execute_search_request


class SavegnagoClient(VtexMarketClient):
    """
    Cliente real do Savegnago baseado em:
    - simulation para coverage/regionalização
    - productSearchV3 para busca de produtos
    """

    def get_market_name(self) -> str:
        return "Savegnago"

    def _execute_coverage_request(self, postal_code: str) -> dict:
        return execute_coverage_request(
            session=self.session,
            postal_code=postal_code,
        )

    def _parse_coverage_response(self, response_json: dict) -> CoverageResult:
        return parse_coverage_response(response_json)

    def _execute_search_request(self, term: str) -> dict:
        return execute_search_request(
            session=self.session,
            term=term,
        )

    def _parse_products_response(self, response_json: dict) -> list[ProductOffer]:
        return parse_products_response(response_json)