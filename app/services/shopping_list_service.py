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
            InvalidShoppingListError: If the JSON structure is invalid.
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
            InvalidShoppingListError: If required fields are missing or invalid.
        """
        required_fields = {"item_id", "display_name"}

        missing_fields = required_fields - raw_item.keys()
        if missing_fields:
            missing_fields_str = ", ".join(sorted(missing_fields))
            raise InvalidShoppingListError(
                f"Shopping item is missing required field(s): {missing_fields_str}."
            )

        item_id = str(raw_item["item_id"]).strip()
        display_name = str(raw_item["display_name"]).strip()
        normalized_name = str(raw_item.get("normalized_name", "")).strip()
        requested_quantity = float(raw_item.get("requested_quantity", 1))
        requested_unit = str(raw_item.get("requested_unit", "unit")).strip()

        if not item_id:
            raise InvalidShoppingListError(
                "Shopping item field 'item_id' cannot be empty."
            )

        if not display_name:
            raise InvalidShoppingListError(
                "Shopping item field 'display_name' cannot be empty."
            )

        if requested_quantity <= 0:
            raise InvalidShoppingListError(
                "Shopping item field 'requested_quantity' must be greater than zero."
            )

        if not requested_unit:
            raise InvalidShoppingListError(
                "Shopping item field 'requested_unit' cannot be empty."
            )

        preferred_brand = raw_item.get("preferred_brand")
        if preferred_brand is not None:
            preferred_brand = str(preferred_brand).strip() or None

        preferred_size_value = raw_item.get("preferred_size_value")
        if preferred_size_value is not None:
            preferred_size_value = float(preferred_size_value)

        preferred_size_unit = raw_item.get("preferred_size_unit")
        if preferred_size_unit is not None:
            preferred_size_unit = str(preferred_size_unit).strip() or None

        return ShoppingItem(
            item_id=item_id,
            display_name=display_name,
            normalized_name=normalized_name,
            requested_quantity=requested_quantity,
            requested_unit=requested_unit,
            preferred_brand=preferred_brand,
            preferred_size_value=preferred_size_value,
            preferred_size_unit=preferred_size_unit,
        )