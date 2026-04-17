"""Domain model that represents the result of matching a shopping item with a product offer."""

from dataclasses import dataclass

from app.domain.product_offer import ProductOffer
from app.domain.shopping_item import ShoppingItem
from app.domain.types import MatchType


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