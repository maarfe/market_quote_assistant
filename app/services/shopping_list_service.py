"""Services for loading shopping lists from external sources."""

import json
from pathlib import Path
from typing import Any

from app.domain import ShoppingItem
from app.shared import InvalidShoppingListError


class ShoppingListService:
    """
    Load shopping lists from JSON files and convert them into domain objects.
    """

    def load_from_file(self, file_path: str | Path) -> list[ShoppingItem]:
        """
        Load a shopping list from a JSON file.

        Args:
            file_path: Path to the shopping list JSON file.

        Returns:
            A list of shopping items.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the JSON structure is invalid.
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, list):
            raise InvalidShoppingListError(
                f"Expected a list of shopping items in '{path}', "
                f"but received '{type(payload).__name__}'."
            )

        return [self._map_item(raw_item) for raw_item in payload]

    def _map_item(self, raw_item: dict[str, Any]) -> ShoppingItem:
        """
        Convert a raw shopping item payload into a ShoppingItem object.

        Args:
            raw_item: Raw shopping item payload.

        Returns:
            A ShoppingItem instance.

        Raises:
            ValueError: If required fields are missing.
        """
        required_fields = {"item_id", "display_name"}

        missing_fields = required_fields - raw_item.keys()
        if missing_fields:
            missing_fields_str = ", ".join(sorted(missing_fields))
            raise InvalidShoppingListError(
                f"Shopping item is missing required field(s): {missing_fields_str}."
            )

        return ShoppingItem(
            item_id=str(raw_item["item_id"]),
            display_name=str(raw_item["display_name"]),
            normalized_name=str(raw_item.get("normalized_name", "")),
            requested_quantity=float(raw_item.get("requested_quantity", 1)),
            requested_unit=str(raw_item.get("requested_unit", "unit")),
        )