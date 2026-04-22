from __future__ import annotations

from typing import Any

import requests

from app.core.markets.vtex_coverage import execute_vtex_coverage_request

COVABRA_BASE_URL = "https://www.covabra.com.br"
COVABRA_REGIONALIZATION_SKU_ID = "6"
COVABRA_REGIONALIZATION_SELLER = "1"
COVABRA_COVERAGE_URL = (
    f"{COVABRA_BASE_URL}/api/checkout/pub/orderForms/simulation"
)


def execute_coverage_request(
    session: requests.Session,
    postal_code: str,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a request de simulation usada no fluxo de CEP/regionalização do Covabra.
    """
    return execute_vtex_coverage_request(
        session=session,
        base_url=COVABRA_BASE_URL,
        coverage_url=COVABRA_COVERAGE_URL,
        postal_code=postal_code,
        sku_id=COVABRA_REGIONALIZATION_SKU_ID,
        seller=COVABRA_REGIONALIZATION_SELLER,
        timeout=timeout,
    )