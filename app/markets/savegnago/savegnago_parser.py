from __future__ import annotations

from typing import Any

from app.core.entities.coverage import CoverageResult
from app.core.entities.product_offer import ProductOffer
from app.core.parsers.vtex_coverage_parser import parse_vtex_coverage_response
from app.core.parsers.vtex_product_parser import parse_vtex_products_response

SAVEGNAGO_BASE_URL = "https://www.savegnago.com.br"
SAVEGNAGO_MARKET_NAME = "Savegnago"


def parse_coverage_response(response_json: dict[str, Any]) -> CoverageResult:
    """
    Interpreta a resposta do endpoint de simulation do Savegnago.
    """
    return parse_vtex_coverage_response(response_json)


def parse_products_response(response_json: dict[str, Any]) -> list[ProductOffer]:
    """
    Interpreta a resposta do GraphQL productSearchV3 do Savegnago.
    """
    return parse_vtex_products_response(
        response_json=response_json,
        market_name=SAVEGNAGO_MARKET_NAME,
        base_url=SAVEGNAGO_BASE_URL,
    )