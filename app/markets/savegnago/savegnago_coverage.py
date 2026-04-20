from __future__ import annotations

from typing import Any

import requests

SAVEGNAGO_BASE_URL = "https://www.savegnago.com.br"
SAVEGNAGO_REGIONALIZATION_SKU_ID = 989898989
SAVEGNAGO_REGIONALIZATION_SELLER = "1"
SAVEGNAGO_COVERAGE_URL = (
    f"{SAVEGNAGO_BASE_URL}/api/checkout/pub/orderForms/simulation?RnbBehavior=0"
)


def build_coverage_payload(postal_code: str) -> dict[str, Any]:
    return {
        "items": [
            {
                "id": SAVEGNAGO_REGIONALIZATION_SKU_ID,
                "quantity": 1,
                "seller": SAVEGNAGO_REGIONALIZATION_SELLER,
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
        SAVEGNAGO_BASE_URL,
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
    Executa a request de simulation responsável por validar cobertura/regionalização.
    """
    prime_coverage_session(session=session, timeout=timeout)

    response = session.post(
        SAVEGNAGO_COVERAGE_URL,
        json=build_coverage_payload(postal_code=postal_code),
        timeout=timeout,
        headers=_build_headers(),
    )

    response.raise_for_status()
    return response.json()


def _build_headers() -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": SAVEGNAGO_BASE_URL,
        "Referer": f"{SAVEGNAGO_BASE_URL}/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }