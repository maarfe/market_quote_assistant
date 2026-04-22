from __future__ import annotations

from typing import Any, Callable
from urllib.parse import urlencode

import requests


def prime_search_session(
    session: requests.Session,
    base_url: str,
    headers: dict[str, str],
    timeout: int = 20,
) -> None:
    """
    Inicializa a sessão HTTP antes da busca para ajudar a estabelecer
    cookies e contexto do ambiente VTEX.
    """
    response = session.get(
        base_url,
        headers=headers,
        timeout=timeout,
    )
    response.raise_for_status()


def execute_vtex_search_request(
    session: requests.Session,
    base_url: str,
    graphql_url: str,
    term: str,
    build_search_params: Callable[[str], dict[str, str]],
    build_headers: Callable[[str | None], dict[str, str]],
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa uma busca VTEX GraphQL reutilizando a mesma sessão HTTP.
    """
    prime_search_session(
        session=session,
        base_url=base_url,
        headers=build_headers(None),
        timeout=timeout,
    )

    params = build_search_params(term)
    url = f"{graphql_url}?{urlencode(params)}"

    response = session.get(
        url,
        headers=build_headers(term),
        timeout=timeout,
    )
    response.raise_for_status()

    response_json = response.json()
    if not isinstance(response_json, dict):
        return {}

    return response_json


def build_vtex_search_headers(
    base_url: str,
    referer: str | None = None,
) -> dict[str, str]:
    """
    Retorna os headers mínimos usados nas buscas VTEX.
    """
    return {
        "accept": "*/*",
        "content-type": "application/json",
        "referer": referer or f"{base_url}/",
        "origin": base_url,
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }