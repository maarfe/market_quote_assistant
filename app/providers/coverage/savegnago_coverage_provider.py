"""Real coverage provider implementation for Savegnago."""

from __future__ import annotations

import re
from typing import Any

import requests

from app.domain.delivery_address import DeliveryAddress
from app.domain.market_coverage import MarketCoverage
from app.providers.coverage.base_coverage_provider import BaseCoverageProvider


class SavegnagoCoverageProvider(BaseCoverageProvider):
    """
    Determine delivery coverage for Savegnago using the VTEX simulation endpoint.

    This provider uses a request-first strategy and attempts to determine whether
    Savegnago supports delivery for the provided postal code. The integration is
    based on a simulation request against the store checkout endpoint.

    The provider returns a single MarketCoverage result representing Savegnago.
    """

    STORE_NAME = "Savegnago"
    PROVIDER_NAME = "savegnago"

    BASE_URL = "https://www.savegnago.com.br"
    HOMEPAGE_URL = f"{BASE_URL}/"
    SIMULATION_URL = (
        f"{BASE_URL}/api/checkout/pub/orderForms/simulation?RnbBehavior=0"
    )

    SENTINEL_SKU_ID = 989898989
    DEFAULT_TIMEOUT_SECONDS = 15

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        """
        Initialize the Savegnago coverage provider.

        Args:
            session: Optional HTTP session for dependency injection and tests.
            timeout_seconds: Request timeout in seconds.
        """
        self._session = session or requests.Session()
        self._timeout_seconds = timeout_seconds

    def check_coverage(self, address: DeliveryAddress) -> list[MarketCoverage]:
        """
        Determine Savegnago delivery coverage for the provided address.

        Args:
            address: Delivery address used as coverage input.

        Returns:
            A single-item list containing the coverage result for Savegnago.
        """
        postal_code = self._normalize_postal_code(address.postal_code)

        try:
            self._prime_session()

            response = self._session.post(
                self.SIMULATION_URL,
                json=self._build_payload(postal_code),
                headers=self._build_headers(),
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()

            response_data = response.json()
            coverage = self._map_response_to_coverage(response_data)

            return [coverage]

        except (requests.RequestException, ValueError, TypeError, KeyError):
            return [self._build_unknown_coverage()]

    def _prime_session(self) -> None:
        """
        Prime the HTTP session with the Savegnago homepage.

        This step helps establish any cookies required by the VTEX environment
        before the simulation request is made.
        """
        response = self._session.get(
            self.HOMEPAGE_URL,
            headers=self._build_headers(),
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()

    def _build_headers(self) -> dict[str, str]:
        """
        Build the HTTP headers required for the simulation request.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "accept": "application/vnd.vtex.ds.v10+json",
            "content-type": "application/json",
            "origin": self.BASE_URL,
            "referer": self.HOMEPAGE_URL,
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
        }

    def _build_payload(self, postal_code: str) -> dict[str, Any]:
        """
        Build the simulation payload used by the Savegnago endpoint.

        Args:
            postal_code: Postal code containing only digits.

        Returns:
            A JSON-serializable payload dictionary.
        """
        return {
            "items": [
                {
                    "id": self.SENTINEL_SKU_ID,
                    "quantity": 1,
                    "seller": "1",
                }
            ],
            "postalCode": postal_code,
            "country": "BRA",
        }

    def _normalize_postal_code(self, postal_code: str) -> str:
        """
        Normalize the postal code to digits only.

        Args:
            postal_code: Raw postal code value.

        Returns:
            The normalized postal code containing only digits.
        """
        return re.sub(r"\D", "", postal_code)

    def _map_response_to_coverage(
        self,
        response_data: dict[str, Any],
    ) -> MarketCoverage:
        """
        Map the simulation response into a MarketCoverage domain object.

        Args:
            response_data: Parsed JSON response from the simulation endpoint.

        Returns:
            A MarketCoverage object for Savegnago.
        """
        slas = self._extract_slas(response_data)
        availability = self._extract_availability(response_data)

        supports_delivery = any(
            self._extract_delivery_channel(sla) == "delivery"
            for sla in slas
        )
        supports_pickup = any(
            self._extract_delivery_channel(sla) in {"pickup-in-point", "pickup"}
            for sla in slas
        )

        if supports_delivery:
            return MarketCoverage(
                provider=self.PROVIDER_NAME,
                market_name=self.STORE_NAME,
                is_covered=True,
                supports_delivery=True,
                supports_pickup=supports_pickup,
                coverage_status="covered",
            )

        if availability == "withoutStock" or not slas:
            return MarketCoverage(
                provider=self.PROVIDER_NAME,
                market_name=self.STORE_NAME,
                is_covered=False,
                supports_delivery=False,
                supports_pickup=supports_pickup,
                coverage_status="not_covered",
            )

        return self._build_unknown_coverage()

    def _extract_slas(self, response_data: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract SLA data from the Savegnago simulation response.

        Args:
            response_data: Parsed JSON response.

        Returns:
            A list of SLA dictionaries.
        """
        logistics_info = response_data.get("logisticsInfo", [])

        if not isinstance(logistics_info, list) or not logistics_info:
            return []

        first_logistics_info = logistics_info[0]
        if not isinstance(first_logistics_info, dict):
            return []

        slas = first_logistics_info.get("slas", [])
        if not isinstance(slas, list):
            return []

        return [sla for sla in slas if isinstance(sla, dict)]

    def _extract_availability(self, response_data: dict[str, Any]) -> str | None:
        """
        Extract product availability hints from the response.

        Args:
            response_data: Parsed JSON response.

        Returns:
            A best-effort availability string, or None.
        """
        top_level_availability = response_data.get("availability")
        if isinstance(top_level_availability, str):
            return top_level_availability

        logistics_info = response_data.get("logisticsInfo", [])
        if isinstance(logistics_info, list) and logistics_info:
            first_logistics_info = logistics_info[0]
            if isinstance(first_logistics_info, dict):
                logistics_availability = first_logistics_info.get("availability")
                if isinstance(logistics_availability, str):
                    return logistics_availability

        items = response_data.get("items", [])
        if isinstance(items, list) and items:
            first_item = items[0]
            if isinstance(first_item, dict):
                item_availability = first_item.get("availability")
                if isinstance(item_availability, str):
                    return item_availability

        return None

    def _extract_delivery_channel(self, sla: dict[str, Any]) -> str | None:
        """
        Extract the delivery channel from an SLA object.

        Args:
            sla: SLA dictionary.

        Returns:
            The delivery channel value, or None.
        """
        delivery_channel = sla.get("deliveryChannel")
        if isinstance(delivery_channel, str):
            return delivery_channel

        channel = sla.get("channel")
        if isinstance(channel, str):
            return channel

        return None

    def _build_unknown_coverage(self) -> MarketCoverage:
        """
        Build an unknown coverage result for Savegnago.

        Returns:
            A MarketCoverage object classified as unknown.
        """
        return MarketCoverage(
            provider=self.PROVIDER_NAME,
            market_name=self.STORE_NAME,
            is_covered=False,
            supports_delivery=False,
            supports_pickup=False,
            coverage_status="unknown",
        )