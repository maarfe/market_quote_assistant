"""Utilities for loading mock market data from local JSON files."""

import json
from pathlib import Path
from typing import Any


class MarketDataLoader:
    """
    Load market data from JSON files stored locally.

    This class is intentionally limited to file loading responsibilities and
    does not perform domain mapping.
    """

    def __init__(self, file_path: str | Path) -> None:
        """
        Initialize the loader with a target file path.

        Args:
            file_path: Path to the JSON file that should be loaded.
        """
        self._file_path = Path(file_path)

    def load(self) -> list[dict[str, Any]]:
        """
        Load and return the raw JSON content.

        Returns:
            A list of dictionaries representing raw market offers.

        Raises:
            FileNotFoundError: If the target JSON file does not exist.
            ValueError: If the loaded JSON content is not a list.
        """
        with self._file_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise ValueError(
                f"Expected a list of offers in '{self._file_path}', "
                f"but received '{type(payload).__name__}'."
            )

        return payload