from __future__ import annotations

from typing import Any

import requests

from app.core.markets.vtex_coverage import execute_vtex_coverage_request

SAVEGNAGO_BASE_URL = "https://www.savegnago.com.br"
SAVEGNAGO_REGIONALIZATION_SKU_ID = "989898989"
SAVEGNAGO_REGIONALIZATION_SELLER = "1"
SAVEGNAGO_COVERAGE_URL = (
    f"{SAVEGNAGO_BASE_URL}/api/checkout/pub/orderForms/simulation?RnbBehavior=0"
)


def execute_coverage_request(
    session: requests.Session,
    postal_code: str,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a request de simulation responsável por validar cobertura/regionalização.
    """
    return execute_vtex_coverage_request(
        session=session,
        base_url=SAVEGNAGO_BASE_URL,
        coverage_url=SAVEGNAGO_COVERAGE_URL,
        postal_code=postal_code,
        sku_id=SAVEGNAGO_REGIONALIZATION_SKU_ID,
        seller=SAVEGNAGO_REGIONALIZATION_SELLER,
        timeout=timeout,
    )