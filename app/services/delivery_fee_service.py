"""Services for loading delivery fee configuration from external sources."""

import json
from pathlib import Path
from typing import Any


class DeliveryFeeService:
    """
    Load delivery fee mappings from JSON files.
    """

    def load_from_file(self, file_path: str | Path) -> dict[str, float]:
        """
        Load delivery fees from a JSON file.

        Args:
            file_path: Path to the delivery fee JSON file.

        Returns:
            A dictionary mapping market names to delivery fee values.

        Raises:
            ValueError: If the JSON structure is invalid.
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise ValueError(
                f"Expected a dictionary of delivery fees in '{path}', "
                f"but received '{type(payload).__name__}'."
            )

        return self._normalize_delivery_fees(payload)

    def _normalize_delivery_fees(
        self,
        payload: dict[str, Any],
    ) -> dict[str, float]:
        """
        Normalize raw delivery fee payload values.

        Args:
            payload: Raw JSON payload.

        Returns:
            A normalized dictionary of delivery fee values.
        """
        normalized_fees: dict[str, float] = {}

        for market_name, fee_value in payload.items():
            normalized_fees[str(market_name)] = float(fee_value)

        return normalized_fees