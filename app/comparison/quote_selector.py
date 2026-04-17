"""Selection utilities for choosing the best valid offer among matched offers."""

from app.domain import MatchedOffer


class QuoteSelector:
    """
    Select the best candidate among matched offers for a shopping item.

    Selection is deterministic and prioritizes:
    1. higher confidence score
    2. lower price
    """

    def select_best_offer(self, matched_offers: list[MatchedOffer]) -> MatchedOffer | None:
        """
        Select the best valid matched offer from a list of candidates.

        Args:
            matched_offers: Candidate matches for the same shopping item and market.

        Returns:
            The best valid matched offer, or None when no valid candidate exists.
        """
        valid_candidates = [
            matched_offer
            for matched_offer in matched_offers
            if matched_offer.is_valid_candidate()
        ]

        if not valid_candidates:
            return None

        return sorted(
            valid_candidates,
            key=lambda matched_offer: (
                -matched_offer.confidence_score,
                matched_offer.product_offer.price,
            ),
        )[0]