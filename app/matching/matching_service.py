"""Services responsible for matching shopping items against product offers."""

from app.domain import MatchType, MatchedOffer, ProductOffer, ShoppingItem
from app.matching.match_result import MatchEvaluation
from app.matching.match_rules import MatchRules


class MatchingService:
    """
    Evaluate compatibility between shopping items and product offers.

    This service uses deterministic matching rules and produces domain-level
    match results that can be used later by the comparison engine.
    """

    def __init__(self) -> None:
        """Initialize the matching service dependencies."""
        self._rules = MatchRules()

    def match_offer(
        self,
        shopping_item: ShoppingItem,
        product_offer: ProductOffer,
    ) -> MatchedOffer:
        """
        Match a single product offer against a shopping item.

        Args:
            shopping_item: Normalized shopping item to be evaluated.
            product_offer: Normalized product offer to be evaluated.

        Returns:
            A domain-level matched offer result.
        """
        evaluation = self._evaluate_match(
            shopping_item=shopping_item,
            product_offer=product_offer,
        )

        return MatchedOffer(
            shopping_item=shopping_item,
            product_offer=product_offer,
            match_type=evaluation.match_type,
            confidence_score=evaluation.confidence_score,
            notes=evaluation.notes,
        )

    def match_offers(
        self,
        shopping_item: ShoppingItem,
        product_offers: list[ProductOffer],
    ) -> list[MatchedOffer]:
        """
        Match multiple product offers against a single shopping item.

        Args:
            shopping_item: Normalized shopping item to be evaluated.
            product_offers: Normalized product offers to be evaluated.

        Returns:
            A list of matched offers sorted by confidence score descending.
        """
        matched_offers = [
            self.match_offer(shopping_item=shopping_item, product_offer=offer)
            for offer in product_offers
        ]

        return sorted(
            matched_offers,
            key=lambda matched_offer: matched_offer.confidence_score,
            reverse=True,
        )

    def _evaluate_match(
        self,
        shopping_item: ShoppingItem,
        product_offer: ProductOffer,
    ) -> MatchEvaluation:
        """
        Apply deterministic matching rules to a shopping item and product offer.

        Args:
            shopping_item: Normalized shopping item.
            product_offer: Normalized product offer.

        Returns:
            An internal evaluation result.
        """
        if not self._rules.is_offer_available(product_offer):
            return MatchEvaluation(
                match_type=MatchType.INVALID,
                confidence_score=0.0,
                notes="Offer is unavailable.",
            )

        if not self._rules.has_any_name_overlap(shopping_item, product_offer):
            return MatchEvaluation(
                match_type=MatchType.INVALID,
                confidence_score=0.0,
                notes="No relevant token overlap between item and offer.",
            )

        has_required_tokens = self._rules.has_required_name_tokens(
            shopping_item=shopping_item,
            product_offer=product_offer,
        )
        has_compatible_unit = self._rules.has_compatible_unit(
            shopping_item=shopping_item,
            product_offer=product_offer,
        )

        if has_required_tokens and has_compatible_unit:
            return MatchEvaluation(
                match_type=MatchType.EXACT,
                confidence_score=1.0,
                notes="All required name tokens are present and units are compatible.",
            )

        if has_required_tokens and not has_compatible_unit:
            return MatchEvaluation(
                match_type=MatchType.PARTIAL,
                confidence_score=0.5,
                notes="Name tokens match, but units are not directly compatible.",
            )

        return MatchEvaluation(
            match_type=MatchType.PARTIAL,
            confidence_score=0.5,
            notes="Partial textual overlap found, but exact token coverage is missing.",
        )