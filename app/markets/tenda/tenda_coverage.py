from __future__ import annotations

from typing import Any

from app.markets.tenda.tenda_session import TENDA_API_BASE_URL, TendaSession


def execute_coverage_request(
    tenda_session: TendaSession,
    postal_code: str,
) -> dict[str, Any]:
    """
    Executa coverage/shipping no endpoint próprio do Tenda.
    """
    tenda_session.ensure_ready()

    response = tenda_session.session.get(
        f"{TENDA_API_BASE_URL}/api/public/store/shipping-options/{postal_code}",
        params={"orderId": tenda_session.cart_id},
        headers=tenda_session.get_authenticated_headers(),
        timeout=tenda_session.timeout,
    )
    response.raise_for_status()

    return response.json()


def persist_delivery_zipcode(
    tenda_session: TendaSession,
    postal_code: str,
) -> None:
    """
    Persiste o CEP/modo delivery no carrinho Tenda.
    """
    tenda_session.ensure_ready()

    response = tenda_session.session.patch(
        f"{TENDA_API_BASE_URL}/api/shopping-cart/{tenda_session.cart_id}",
        json={
            "type": "delivery",
            "zipcode": postal_code,
        },
        headers={
            **tenda_session.get_authenticated_headers(),
            "content-type": "application/json",
        },
        timeout=tenda_session.timeout,
    )
    response.raise_for_status()