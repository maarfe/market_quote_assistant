from __future__ import annotations

import json
from typing import Any

import requests

from app.core.markets.vtex_search import (
    build_vtex_search_headers,
    execute_vtex_search_request,
)

SAVEGNAGO_BASE_URL = "https://www.savegnago.com.br"
SAVEGNAGO_GRAPHQL_URL = f"{SAVEGNAGO_BASE_URL}/_v/segment/graphql/v1"

SAVEGNAGO_PERSISTED_QUERY_HASH = (
    "31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de"
)


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
    """
    return execute_vtex_search_request(
        session=session,
        base_url=SAVEGNAGO_BASE_URL,
        graphql_url=SAVEGNAGO_GRAPHQL_URL,
        term=term,
        build_search_params=build_search_params,
        build_headers=_build_headers,
        timeout=timeout,
    )


def _build_headers(search_term: str | None = None) -> dict[str, str]:
    return build_vtex_search_headers(
        base_url=SAVEGNAGO_BASE_URL,
        referer=f"{SAVEGNAGO_BASE_URL}/",
    )