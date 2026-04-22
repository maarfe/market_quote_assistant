from __future__ import annotations

import base64
import json
from typing import Any

import requests

from app.core.markets.vtex_search import (
    build_vtex_search_headers,
    execute_vtex_search_request,
)

COVABRA_BASE_URL = "https://www.covabra.com.br"
COVABRA_GRAPHQL_URL = f"{COVABRA_BASE_URL}/_v/segment/graphql/v1"

COVABRA_BINDING_ID = "7ce9b3b0-6a3c-46fb-98ae-854829b7eb01"
COVABRA_PERSISTED_QUERY_HASH = (
    "31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de"
)


def build_search_params(term: str) -> dict[str, str]:
    """
    Monta os query params da request real do productSearchV3 do Covabra.

    Observação:
    - o tráfego observado usa variables={}
    - os parâmetros reais da busca ficam em extensions.variables, em base64
    """
    search_variables = {
        "hideUnavailableItems": True,
        "skusFilter": "FIRST_AVAILABLE",
        "simulationBehavior": "default",
        "installmentCriteria": "MAX_WITHOUT_INTEREST",
        "productOriginVtex": False,
        "map": "ft",
        "query": f"{term}/p",
        "orderBy": "OrderByScoreDESC",
        "from": 0,
        "to": 23,
        "selectedFacets": [{"key": "ft", "value": term}],
        "fullText": term,
        "facetsBehavior": "Static",
        "categoryTreeBehavior": "default",
        "withFacets": False,
    }

    encoded_variables = base64.b64encode(
        json.dumps(
            search_variables,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
    ).decode("utf-8")

    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": COVABRA_PERSISTED_QUERY_HASH,
            "sender": "vtex.store-resources@0.x",
            "provider": "vtex.search-graphql@0.x",
        },
        "variables": encoded_variables,
    }

    return {
        "workspace": "master",
        "maxAge": "short",
        "appsEtag": "remove",
        "domain": "store",
        "locale": "pt-BR",
        "__bindingId": COVABRA_BINDING_ID,
        "operationName": "productSearchV3",
        "variables": "{}",
        "extensions": json.dumps(extensions, ensure_ascii=False, separators=(",", ":")),
    }


def execute_search_request(
    session: requests.Session,
    term: str,
    timeout: int = 20,
) -> dict[str, Any]:
    """
    Executa a busca real de produtos no Covabra via VTEX GraphQL.
    """
    return execute_vtex_search_request(
        session=session,
        base_url=COVABRA_BASE_URL,
        graphql_url=COVABRA_GRAPHQL_URL,
        term=term,
        build_search_params=build_search_params,
        build_headers=_build_headers,
        timeout=timeout,
    )


def _build_headers(search_term: str | None = None) -> dict[str, str]:
    referer = f"{COVABRA_BASE_URL}/"
    if search_term:
        referer = f"{COVABRA_BASE_URL}/{search_term}?map=ft&p={search_term}"

    return build_vtex_search_headers(
        base_url=COVABRA_BASE_URL,
        referer=referer,
    )