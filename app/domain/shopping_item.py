"""Domain model that represents a requested shopping item."""

from dataclasses import dataclass


@dataclass(slots=True)
class ShoppingItem:
    """
    Represents an item requested by the user in a shopping list.

    Attributes:
        item_id: Unique identifier for the shopping item.
        display_name: Original human-readable name of the item.
        normalized_name: Normalized name used for comparisons.
        requested_quantity: Desired quantity of the item.
        requested_unit: Unit associated with the requested quantity.
    """

    item_id: str
    display_name: str
    normalized_name: str
    requested_quantity: float = 1.0
    requested_unit: str = "unit"

    def describe(self) -> str:
        """
        Return a human-readable description of the shopping item.

        Returns:
            A string describing the requested item.
        """
        return (
            f"{self.display_name} "
            f"({self.requested_quantity:g} {self.requested_unit})"
        )