"""Domain model that represents the result of matching a shopping item with a product offer."""

from dataclasses import dataclass

from app.domain.product_offer import ProductOffer
from app.domain.shopping_item import ShoppingItem
from app.domain.types import MatchType
from app.shared import MoneyHelper


@dataclass(slots=True)
class MatchedOffer:
    """
    Represents a compatibility evaluation between a shopping item and a product offer.

    Attributes:
        shopping_item: The requested shopping item.
        product_offer: The evaluated market offer.
        match_type: Compatibility classification between item and offer.
        confidence_score: Confidence score for the match, expected between 0.0 and 1.0.
        notes: Optional explanation about the matching decision.
    """

    shopping_item: ShoppingItem
    product_offer: ProductOffer
    match_type: MatchType
    confidence_score: float
    notes: str | None = None

    def is_valid_candidate(self) -> bool:
        """
        Indicate whether the matched offer can be considered in recommendation scenarios.

        Returns:
            True for exact or adjustable matches, otherwise False.
        """
        return self.match_type in {MatchType.EXACT, MatchType.ADJUSTABLE}

    def get_unit_price(self) -> float:
        """
        Return the unit price associated with the selected product offer.

        Returns:
            The offer unit price.
        """
        return self.product_offer.price

    def get_requested_quantity(self) -> float:
        """
        Return the requested quantity associated with the shopping item.

        Returns:
            The requested quantity.
        """
        return self.shopping_item.requested_quantity

    def calculate_total_price(self) -> float:
        """
        Calculate the total price required to satisfy the requested quantity.

        Returns:
            The estimated total price for the selected offer.
        """
        return MoneyHelper.round_currency(
            self.get_unit_price() * self.get_requested_quantity()
        )
    
    def describe(self) -> str:
        """
        Return a human-readable description of the matched offer.

        Returns:
            A string describing the match result.
        """
        return (
            f"{self.shopping_item.display_name} -> "
            f"{self.product_offer.original_name} "
            f"[{self.match_type.value}, confidence={self.confidence_score:.2f}]"
        )