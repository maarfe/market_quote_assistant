from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlencode

import requests

SAVEGNAGO_BASE_URL = "https://www.savegnago.com.br"
SAVEGNAGO_GRAPHQL_URL = f"{SAVEGNAGO_BASE_URL}/_v/segment/graphql/v1"

SAVEGNAGO_PERSISTED_QUERY_HASH = (
    "31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de"
)


def prime_search_session(
    session: requests.Session,
    timeout: int = 20,
) -> None:
    """
    Inicializa a sessão HTTP antes da busca para ajudar a estabelecer
    cookies do ambiente VTEX.
    """
    response = session.get(
        SAVEGNAGO_BASE_URL,
        headers=_build_headers(),
        timeout=timeout,
    )
    response.raise_for_status()


def build_search_params(term: str) -> dict[str, str]:
    """
    Monta os query params da request real do productSearchV3.
    """
    variables = {
        "query": term,
        "fullText": term,
        "selectedFacets": [{"key": "ft", "value": term}],
        "from": 0,
        "to": 23,
        "hideUnavailableItems": True,
        "orderBy": "OrderByScoreDESC",
        "skusFilter": "FIRST_AVAILABLE",
        "simulationBehavior": "default",
    }

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": SAVEGNAGO_PERSISTED_QUERY_HASH,
        }
    }

    return {
        "operationName": "productSearchV3",
        "variables": json.dumps(variables, ensure_ascii=False, separators=(",", ":")),
        "extensions": json.dumps(extensions, ensure_ascii=False, separators=(",", ":")),
    }


def execute_search_request(
    session: requests.Session,
    term: str,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a busca real de produtos no Savegnago via VTEX GraphQL.

    Regras:
    - usa a mesma session recebida
    - faz prime da sessão antes da busca
    - usa persisted query hash observado no tráfego real
    """
    prime_search_session(session=session, timeout=timeout)

    params = build_search_params(term=term)
    url = f"{SAVEGNAGO_GRAPHQL_URL}?{urlencode(params)}"

    response = session.get(
        url,
        headers=_build_headers(),
        timeout=timeout,
    )
    response.raise_for_status()

    response_json = response.json()
    if not isinstance(response_json, dict):
        return {}

    return response_json


def _build_headers() -> dict[str, str]:
    """
    Headers mínimos usados na busca.
    """
    return {
        "accept": "*/*",
        "content-type": "application/json",
        "referer": SAVEGNAGO_BASE_URL,
        "origin": SAVEGNAGO_BASE_URL,
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }