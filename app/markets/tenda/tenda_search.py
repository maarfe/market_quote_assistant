from __future__ import annotations

from typing import Any

from app.markets.tenda.tenda_session import TENDA_API_BASE_URL, TendaSession


def execute_search_request(
    tenda_session: TendaSession,
    term: str,
    page: int = 1,
) -> dict[str, Any]:
    """
    Executa busca real de produtos na API própria do Tenda.
    """
    tenda_session.ensure_ready()

    response = tenda_session.session.get(
        f"{TENDA_API_BASE_URL}/api/public/store/search",
        params={
            "query": term,
            "page": page,
            "order": "relevance",
            "save": "true",
            "cartId": tenda_session.cart_id,
        },
        headers=tenda_session.get_authenticated_headers(),
        timeout=tenda_session.timeout,
    )
    response.raise_for_status()

    data = response.json()
    return data if isinstance(data, dict) else {}