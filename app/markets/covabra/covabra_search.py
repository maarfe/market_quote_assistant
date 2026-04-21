from __future__ import annotations

import base64
import json
from typing import Any
from urllib.parse import urlencode

import requests

COVABRA_BASE_URL = "https://www.covabra.com.br"
COVABRA_GRAPHQL_URL = f"{COVABRA_BASE_URL}/_v/segment/graphql/v1"

COVABRA_BINDING_ID = "7ce9b3b0-6a3c-46fb-98ae-854829b7eb01"
COVABRA_PERSISTED_QUERY_HASH = (
    "31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de"
)


def prime_search_session(
    session: requests.Session,
    timeout: int = 20,
) -> None:
    """
    Inicializa a sessão HTTP antes da busca para ajudar a estabelecer
    cookies de contexto VTEX.
    """
    response = session.get(
        COVABRA_BASE_URL,
        headers=_build_headers(),
        timeout=timeout,
    )
    response.raise_for_status()


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
    prime_search_session(session=session, timeout=timeout)

    params = build_search_params(term=term)
    url = f"{COVABRA_GRAPHQL_URL}?{urlencode(params)}"

    response = session.get(
        url,
        headers=_build_headers(search_term=term),
        timeout=timeout,
    )
    response.raise_for_status()

    response_json = response.json()
    if not isinstance(response_json, dict):
        return {}

    return response_json


def _build_headers(search_term: str | None = None) -> dict[str, str]:
    referer = f"{COVABRA_BASE_URL}/"
    if search_term:
        referer = f"{COVABRA_BASE_URL}/{search_term}?map=ft&p={search_term}"

    return {
        "accept": "*/*",
        "content-type": "application/json",
        "referer": referer,
        "origin": COVABRA_BASE_URL,
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/137.0.0.0 Safari/537.36"
        ),
    }