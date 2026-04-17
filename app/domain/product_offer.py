"""Domain model that represents a product offer from a market."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProductOffer:
    """
    Represents a market offer for a product.

    Attributes:
        market_name: Name of the market or source that provides the offer.
        original_name: Original product name as received from the source.
        normalized_name: Normalized product name used for comparisons.
        price: Product price in the source currency.
        currency: Currency code associated with the price.
        available: Indicates whether the product is available for purchase.
        url: Optional source URL for the product page.
        size_value: Optional numeric representation of the package size.
        size_unit: Optional unit associated with the package size.
        brand: Optional product brand.
        raw_payload: Original source payload for debugging or traceability.
    """

    market_name: str
    original_name: str
    normalized_name: str
    price: float
    currency: str = "BRL"
    available: bool = True
    url: str | None = None
    size_value: float | None = None
    size_unit: str | None = None
    brand: str | None = None
    raw_payload: dict[str, Any] = field(default_factory=dict)

    def is_measurable(self) -> bool:
        """
        Indicate whether the offer has enough size information for unit-based comparisons.

        Returns:
            True when both size value and size unit are present, otherwise False.
        """
        return self.size_value is not None and self.size_unit is not None

    def describe(self) -> str:
        """
        Return a human-readable description of the product offer.

        Returns:
            A string describing the offer.
        """
        return f"{self.market_name}: {self.original_name} - {self.currency} {self.price:.2f}"