from __future__ import annotations

from typing import Any

import requests

COVABRA_BASE_URL = "https://www.covabra.com.br"
COVABRA_REGIONALIZATION_SKU_ID = 6
COVABRA_REGIONALIZATION_SELLER = "1"
COVABRA_COVERAGE_URL = (
    f"{COVABRA_BASE_URL}/api/checkout/pub/orderForms/simulation"
)


def build_coverage_payload(postal_code: str) -> dict[str, Any]:
    return {
        "items": [
            {
                "id": str(COVABRA_REGIONALIZATION_SKU_ID),
                "quantity": 1,
                "seller": COVABRA_REGIONALIZATION_SELLER,
            }
        ],
        "postalCode": postal_code,
        "country": "BRA",
    }


def prime_coverage_session(
    session: requests.Session,
    timeout: int = 20,
) -> None:
    response = session.get(
        COVABRA_BASE_URL,
        headers=_build_headers(),
        timeout=timeout,
    )
    response.raise_for_status()


def execute_coverage_request(
    session: requests.Session,
    postal_code: str,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a request de simulation usada no fluxo de CEP/regionalização do Covabra.
    """
    prime_coverage_session(session=session, timeout=timeout)

    response = session.post(
        COVABRA_COVERAGE_URL,
        json=build_coverage_payload(postal_code=postal_code),
        headers=_build_headers(),
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def _build_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": COVABRA_BASE_URL,
        "Referer": f"{COVABRA_BASE_URL}/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }