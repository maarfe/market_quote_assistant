"""Services for loading delivery address configuration from external sources."""

import json
from pathlib import Path
from typing import Any

from app.domain.delivery_address import DeliveryAddress
from app.shared import InvalidShoppingListError


class DeliveryAddressService:
    """
    Load delivery address configuration from JSON files.
    """

    def load_from_file(self, file_path: str | Path) -> DeliveryAddress:
        """
        Load a delivery address from a JSON file.

        Args:
            file_path: Path to the delivery address JSON file.

        Returns:
            A validated delivery address object.

        Raises:
            FileNotFoundError: If the file does not exist.
            InvalidShoppingListError: If the JSON structure is invalid.
        """
        path = Path(file_path)

        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        if not isinstance(payload, dict):
            raise InvalidShoppingListError(
                f"Expected a dictionary for delivery address in '{path}', "
                f"but received '{type(payload).__name__}'."
            )

        return self._map_address(payload)

    def _map_address(self, raw_address: dict[str, Any]) -> DeliveryAddress:
        """
        Convert a raw address payload into a DeliveryAddress object.

        Args:
            raw_address: Raw address payload.

        Returns:
            A validated delivery address object.

        Raises:
            InvalidShoppingListError: If required fields are missing or invalid.
        """
        required_fields = {
            "label",
            "recipient_name",
            "street",
            "number",
            "neighborhood",
            "city",
            "state",
            "postal_code",
            "country",
        }

        missing_fields = required_fields - raw_address.keys()
        if missing_fields:
            missing_fields_str = ", ".join(sorted(missing_fields))
            raise InvalidShoppingListError(
                f"Delivery address is missing required field(s): {missing_fields_str}."
            )

        label = str(raw_address["label"]).strip()
        recipient_name = str(raw_address["recipient_name"]).strip()
        street = str(raw_address["street"]).strip()
        number = str(raw_address["number"]).strip()
        complement = str(raw_address.get("complement", "")).strip()
        neighborhood = str(raw_address["neighborhood"]).strip()
        city = str(raw_address["city"]).strip()
        state = str(raw_address["state"]).strip()
        postal_code = str(raw_address["postal_code"]).strip()
        country = str(raw_address["country"]).strip()

        field_map = {
            "label": label,
            "recipient_name": recipient_name,
            "street": street,
            "number": number,
            "neighborhood": neighborhood,
            "city": city,
            "state": state,
            "postal_code": postal_code,
            "country": country,
        }

        for field_name, field_value in field_map.items():
            if not field_value:
                raise InvalidShoppingListError(
                    f"Delivery address field '{field_name}' cannot be empty."
                )

        return DeliveryAddress(
            label=label,
            recipient_name=recipient_name,
            street=street,
            number=number,
            complement=complement,
            neighborhood=neighborhood,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
        )