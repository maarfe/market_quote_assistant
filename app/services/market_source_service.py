"""Services for loading market source configuration from external sources."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.shared import InvalidMarketSourceConfigError


@dataclass(slots=True)
class MarketSource:
    """
    Represents a configured market data source.

    Attributes:
        market_name: Logical name of the market.
        file_path: Path to the source JSON file.
    """

    market_name: str
    file_path: str


class MarketSourceService:
    """
    Load market source configuration from JSON files.
    """

    def load_from_file(self, file_path: str | Path) -> list[MarketSource]:
        """
        Load market sources from a JSON file.

        Args:
            file_path: Path to the market sources JSON file.

        Returns:
            A list of configured market sources.

        Raises:
            FileNotFoundError: If the file does not exist.
            InvalidMarketSourceConfigError: If the JSON structure is invalid.
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise InvalidMarketSourceConfigError(
                f"Expected a list of market sources in '{path}', "
                f"but received '{type(payload).__name__}'."
            )

        return [self._map_market_source(raw_source) for raw_source in payload]

    def _map_market_source(self, raw_source: dict[str, Any]) -> MarketSource:
        """
        Convert a raw source payload into a MarketSource object.

        Args:
            raw_source: Raw source configuration payload.

        Returns:
            A MarketSource instance.

        Raises:
            InvalidMarketSourceConfigError: If required fields are missing or invalid.
        """
        required_fields = {"market_name", "file_path"}

        missing_fields = required_fields - raw_source.keys()
        if missing_fields:
            missing_fields_str = ", ".join(sorted(missing_fields))
            raise InvalidMarketSourceConfigError(
                f"Market source is missing required field(s): {missing_fields_str}."
            )

        market_name = str(raw_source["market_name"]).strip()
        file_path = str(raw_source["file_path"]).strip()

        if not market_name:
            raise InvalidMarketSourceConfigError(
                "Market source field 'market_name' cannot be empty."
            )

        if not file_path:
            raise InvalidMarketSourceConfigError(
                "Market source field 'file_path' cannot be empty."
            )

        return MarketSource(
            market_name=market_name,
            file_path=file_path,
        )