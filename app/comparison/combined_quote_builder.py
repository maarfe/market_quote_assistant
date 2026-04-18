"""Builder responsible for creating combined multi-market quote scenarios."""

from app.comparison.quote_selector import QuoteSelector
from app.domain import MatchedOffer, ShoppingItem
from app.shared import MoneyHelper

class CombinedQuoteBuilder:
    """
    Build a combined quote scenario using the best valid offer for each item
    across all available markets.
    """

    def __init__(self) -> None:
        """Initialize builder dependencies."""
        self._quote_selector = QuoteSelector()

    def build(
        self,
        shopping_items: list[ShoppingItem],
        matched_offers: list[MatchedOffer],
        delivery_fees: dict[str, float] | None = None,
    ) -> dict:
        """
        Build the best combined multi-market quote scenario.

        Args:
            shopping_items: Requested shopping items.
            matched_offers: All matched offers across all markets.
            delivery_fees: Optional delivery fee mapping by market name.

        Returns:
            A dictionary describing the combined quote scenario.
        """
        delivery_fees = delivery_fees or {}

        selected_offers: list[MatchedOffer] = []
        missing_items: list[ShoppingItem] = []

        for shopping_item in shopping_items:
            item_matches = self._filter_matches_for_item(
                shopping_item=shopping_item,
                matched_offers=matched_offers,
            )

            best_offer = self._quote_selector.select_best_offer(item_matches)

            if best_offer is None:
                missing_items.append(shopping_item)
                continue

            selected_offers.append(best_offer)

        used_markets = self._extract_used_markets(selected_offers)
        subtotal = MoneyHelper.round_currency(
            sum(
                selected_offer.calculate_total_price()
                for selected_offer in selected_offers
            )
        )
        delivery_total = MoneyHelper.round_currency(
            sum(
                delivery_fees.get(market_name, 0.0)
                for market_name in used_markets
            )
        )
        total_cost = MoneyHelper.round_currency(subtotal + delivery_total)
        
        return {
            "strategy": "best_combined_option",
            "selected_offers": selected_offers,
            "missing_items": missing_items,
            "used_markets": used_markets,
            "subtotal": subtotal,
            "delivery_total": delivery_total,
            "total_cost": total_cost,
            "full_coverage": len(missing_items) == 0,
            "market_count": len(used_markets),
        }

    def _filter_matches_for_item(
        self,
        shopping_item: ShoppingItem,
        matched_offers: list[MatchedOffer],
    ) -> list[MatchedOffer]:
        """
        Filter matched offers for a specific shopping item.

        Args:
            shopping_item: Requested shopping item.
            matched_offers: All matched offers.

        Returns:
            A list of matched offers associated with the item.
        """
        return [
            matched_offer
            for matched_offer in matched_offers
            if matched_offer.shopping_item.item_id == shopping_item.item_id
        ]

    def _extract_used_markets(self, selected_offers: list[MatchedOffer]) -> list[str]:
        """
        Extract the distinct markets used by selected offers.

        Args:
            selected_offers: Offers selected for the combined strategy.

        Returns:
            A sorted list of used market names.
        """
        return sorted(
            {
                selected_offer.product_offer.market_name
                for selected_offer in selected_offers
            }
        )