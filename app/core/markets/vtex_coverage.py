from __future__ import annotations

from typing import Any

import requests


def build_coverage_payload(
    postal_code: str,
    sku_id: str,
    seller: str = "1",
) -> dict[str, Any]:
    """
    Monta o payload padrão do endpoint VTEX de simulation usado
    para coverage/regionalização.
    """
    return {
        "items": [
            {
                "id": sku_id,
                "quantity": 1,
                "seller": seller,
            }
        ],
        "postalCode": postal_code,
        "country": "BRA",
    }


def prime_coverage_session(
    session: requests.Session,
    base_url: str,
    timeout: int = 20,
) -> None:
    """
    Inicializa a sessão HTTP antes da chamada de simulation para ajudar
    a estabelecer cookies e contexto do ambiente VTEX.
    """
    response = session.get(
        base_url,
        headers=_build_headers(base_url=base_url),
        timeout=timeout,
    )
    response.raise_for_status()


def execute_vtex_coverage_request(
    session: requests.Session,
    base_url: str,
    coverage_url: str,
    postal_code: str,
    sku_id: str,
    seller: str = "1",
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a request VTEX de simulation usada para coverage/regionalização.
    """
    prime_coverage_session(
        session=session,
        base_url=base_url,
        timeout=timeout,
    )

    response = session.post(
        coverage_url,
        json=build_coverage_payload(
            postal_code=postal_code,
            sku_id=sku_id,
            seller=seller,
        ),
        headers=_build_headers(base_url=base_url),
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


def _build_headers(base_url: str) -> dict[str, str]:
    """
    Headers mínimos para o fluxo de simulation VTEX.
    """
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": base_url,
        "Referer": f"{base_url}/",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }