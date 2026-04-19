"""Collector implementation for Savegnago product offers using VTEX GraphQL search."""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlencode

import requests

from app.collectors.base_collector import BaseCollector
from app.domain import ProductOffer


class SavegnagoOfferCollector(BaseCollector):
    """
    Collect product offers from Savegnago using VTEX GraphQL productSearchV3.

    This collector uses a request-first strategy and queries products via
    VTEX persisted GraphQL queries.
    """

    BASE_URL = "https://www.savegnago.com.br"
    GRAPHQL_URL = BASE_URL + "/_v/segment/graphql/v1"

    DEFAULT_TIMEOUT_SECONDS = 15
    MARKET_NAME = "Savegnago"

    # Persisted query hash (observado no mapper)
    PERSISTED_QUERY_HASH = (
        "31d3fa494df1fc41efef6d16dd96a96e6911b8aed7a037868699a1f3f4d365de"
    )

    def __init__(
        self,
        search_terms: list[str],
        session: requests.Session | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._search_terms = search_terms
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def collect_offers(self) -> list[ProductOffer]:
        """
        Collect product offers from Savegnago.

        Returns:
            A list of ProductOffer objects.
        """
        offers: list[ProductOffer] = []

        self._prime_session()

        for term in self._search_terms:
            response_data = self._fetch_search_results(term)
            products = self._extract_products(response_data)

            for product in products:
                mapped = self._map_product(product)
                if mapped:
                    offers.append(mapped)

        return offers

    def _prime_session(self) -> None:
        """Prime session to establish cookies."""
        self._session.get(
            self.BASE_URL,
            headers=self._build_headers(),
            timeout=self._timeout_seconds,
        )

    def _fetch_search_results(self, term: str) -> dict[str, Any]:
        """
        Fetch product search results using VTEX GraphQL endpoint.

        Args:
            term: Search term.

        Returns:
            Parsed JSON response.
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
                "sha256Hash": self.PERSISTED_QUERY_HASH,
            }
        }

        params = {
            "operationName": "productSearchV3",
            "variables": json.dumps(variables),
            "extensions": json.dumps(extensions),
        }

        url = f"{self.GRAPHQL_URL}?{urlencode(params)}"

        response = self._session.get(
            url,
            headers=self._build_headers(),
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

        response_data = response.json()
        if not isinstance(response_data, dict):
            return {}

        return response_data

    def _build_headers(self) -> dict[str, str]:
        """Build HTTP headers."""
        return {
            "accept": "*/*",
            "content-type": "application/json",
            "referer": self.BASE_URL,
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
        }

    def _extract_products(self, response_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract product list from GraphQL response.

        Args:
            response_data: Raw JSON response.

        Returns:
            List of product dictionaries.
        """
        data = response_data.get("data")
        if not isinstance(data, dict):
            return []

        product_search = data.get("productSearch")
        if not isinstance(product_search, dict):
            return []

        products = product_search.get("products")
        if not isinstance(products, list):
            return []

        return [product for product in products if isinstance(product, dict)]

    def _map_product(self, product: dict[str, Any]) -> ProductOffer | None:
        """Map VTEX product into ProductOffer."""
        try:
            product_name = product["productName"]
            brand = product.get("brand")
            link = product.get("link")

            items = product.get("items", [])
            if not items:
                return None

            first_item = items[0]
            sellers = first_item.get("sellers", [])
            if not sellers:
                return None

            seller = sellers[0]
            offer = seller.get("commertialOffer", {})

            price = float(offer["Price"])
            available_quantity = offer.get("AvailableQuantity", 0)

            size_value, size_unit = self._extract_size(first_item)

            return ProductOffer(
                market_name=self.MARKET_NAME,
                original_name=product_name,
                normalized_name="",
                price=price,
                currency="BRL",
                available=available_quantity > 0,
                url=self._build_product_url(link),
                size_value=size_value,
                size_unit=size_unit,
                brand=brand,
                raw_payload=product,
            )

        except (KeyError, TypeError, ValueError):
            return None

    def _build_product_url(self, link: str | None) -> str | None:
        if not link:
            return None
        return f"{self.BASE_URL}{link}"

    def _extract_size(self, item: dict[str, Any]) -> tuple[float | None, str | None]:
        name = item.get("nameComplete", "")
        if not name:
            return None, None

        match = re.search(r"(\d+(?:[.,]\d+)?)\s*(kg|g|l|ml)", name.lower())
        if not match:
            return None, None

        value = float(match.group(1).replace(",", "."))
        unit = match.group(2)

        return value, unit