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

        preferred_brand: Optional preferred brand specified by the user.
        preferred_size_value: Optional preferred size value.
        preferred_size_unit: Optional preferred size unit.
    """

    item_id: str
    display_name: str
    normalized_name: str
    requested_quantity: float = 1.0
    requested_unit: str = "unit"

    # NOVOS CAMPOS
    preferred_brand: str | None = None
    preferred_size_value: float | None = None
    preferred_size_unit: str | None = None

    def describe(self) -> str:
        description = (
            f"{self.display_name} "
            f"({self.requested_quantity:g} {self.requested_unit})"
        )

        if self.preferred_brand:
            description += f" [brand={self.preferred_brand}]"

        if self.preferred_size_value and self.preferred_size_unit:
            description += f" [size={self.preferred_size_value:g}{self.preferred_size_unit}]"

        return description