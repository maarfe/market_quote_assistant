"""Builder responsible for creating market quotes from matched offers."""

from app.comparison.quote_selector import QuoteSelector
from app.domain import MarketQuote, MatchedOffer, ShoppingItem


class MarketQuoteBuilder:
    """
    Build a MarketQuote for a single market based on matched offers.

    This builder evaluates all requested shopping items against the matched
    offers available for a specific market and selects the best valid offer
    for each item whenever possible.
    """

    def __init__(self) -> None:
        """Initialize builder dependencies."""
        self._quote_selector = QuoteSelector()

    def build(
        self,
        market_name: str,
        shopping_items: list[ShoppingItem],
        matched_offers: list[MatchedOffer],
        delivery_fee: float = 0.0,
    ) -> MarketQuote:
        """
        Build a consolidated quote for a single market.

        Args:
            market_name: Market name to which the matched offers belong.
            shopping_items: Requested shopping items.
            matched_offers: Matched offers already associated with the market.
            delivery_fee: Optional delivery fee for the market.

        Returns:
            A consolidated market quote.
        """
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

        return MarketQuote(
            market_name=market_name,
            selected_offers=selected_offers,
            missing_items=missing_items,
            delivery_fee=delivery_fee,
        )

    def _filter_matches_for_item(
        self,
        shopping_item: ShoppingItem,
        matched_offers: list[MatchedOffer],
    ) -> list[MatchedOffer]:
        """
        Filter matched offers for a specific shopping item.

        Args:
            shopping_item: Requested shopping item.
            matched_offers: Available matched offers for the market.

        Returns:
            A list of matched offers associated with the shopping item.
        """
        return [
            matched_offer
            for matched_offer in matched_offers
            if matched_offer.shopping_item.item_id == shopping_item.item_id
        ]