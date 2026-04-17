"""Collector implementation that reads product offers from local JSON files."""

from typing import Any

from app.collectors.base_collector import BaseCollector
from app.collectors.market_data_loader import MarketDataLoader
from app.domain import ProductOffer


class JsonMarketCollector(BaseCollector):
    """
    Collect product offers from a local JSON file.

    This collector is designed for MVP and testing scenarios where market data
    is mocked and fully controlled.
    """

    def __init__(self, market_name: str, file_path: str) -> None:
        """
        Initialize the collector with a market identity and source file path.

        Args:
            market_name: Logical market name associated with the file.
            file_path: Path to the JSON file containing offer data.
        """
        self._market_name = market_name
        self._loader = MarketDataLoader(file_path=file_path)

    def collect_offers(self) -> list[ProductOffer]:
        """
        Collect and map raw JSON data into product offer domain objects.

        Returns:
            A list of product offers created from the input file.
        """
        raw_offers = self._loader.load()
        return [self._map_offer(raw_offer) for raw_offer in raw_offers]

    def _map_offer(self, raw_offer: dict[str, Any]) -> ProductOffer:
        """
        Convert a raw dictionary into a ProductOffer object.

        Args:
            raw_offer: Raw market offer payload.

        Returns:
            A ProductOffer instance built from the payload.
        """
        return ProductOffer(
            market_name=self._market_name,
            original_name=str(raw_offer["original_name"]),
            normalized_name=str(raw_offer.get("normalized_name", "")).strip(),
            price=float(raw_offer["price"]),
            currency=str(raw_offer.get("currency", "BRL")),
            available=bool(raw_offer.get("available", True)),
            url=raw_offer.get("url"),
            size_value=self._parse_optional_float(raw_offer.get("size_value")),
            size_unit=raw_offer.get("size_unit"),
            brand=raw_offer.get("brand"),
            raw_payload=raw_offer,
        )

    @staticmethod
    def _parse_optional_float(value: Any) -> float | None:
        """
        Safely parse optional numeric values.

        Args:
            value: Raw value to be converted.

        Returns:
            A float when conversion is possible, otherwise None.
        """
        if value is None:
            return None

        return float(value)