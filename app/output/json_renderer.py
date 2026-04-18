"""JSON renderer for comparison results."""

from app.domain import ComparisonResult, MarketQuote, MatchedOffer, ShoppingItem


class JsonRenderer:
    """
    Render comparison results as JSON-serializable dictionaries.
    """

    def render_comparison_result(self, comparison_result: ComparisonResult) -> dict:
        """
        Convert a comparison result into a serializable dictionary.

        Args:
            comparison_result: Comparison result to serialize.

        Returns:
            A JSON-serializable dictionary.
        """
        return {
            "market_quotes": [
                self._serialize_market_quote(market_quote)
                for market_quote in comparison_result.market_quotes
            ],
            "best_single_market": (
                self._serialize_market_quote(comparison_result.best_single_market)
                if comparison_result.best_single_market is not None
                else None
            ),
            "best_combined_option": comparison_result.best_combined_option,
            "best_final_recommendation": comparison_result.best_final_recommendation,
            "missing_items": [
                self._serialize_shopping_item(item)
                for item in comparison_result.missing_items
            ],
            "summary_notes": comparison_result.summary_notes,
        }

    def _serialize_market_quote(self, market_quote: MarketQuote) -> dict:
        """
        Serialize a market quote.

        Args:
            market_quote: Market quote to serialize.

        Returns:
            A dictionary representation of the market quote.
        """
        return {
            "market_name": market_quote.market_name,
            "selected_offers": [
                self._serialize_matched_offer(selected_offer)
                for selected_offer in market_quote.selected_offers
            ],
            "missing_items": [
                self._serialize_shopping_item(item)
                for item in market_quote.missing_items
            ],
            "subtotal": market_quote.subtotal,
            "delivery_fee": market_quote.delivery_fee,
            "total_cost": market_quote.total_cost,
            "full_coverage": market_quote.has_full_coverage(),
        }

    def _serialize_matched_offer(self, matched_offer: MatchedOffer) -> dict:
        """
        Serialize a matched offer.

        Args:
            matched_offer: Matched offer to serialize.

        Returns:
            A dictionary representation of the matched offer.
        """
        return {
            "shopping_item": self._serialize_shopping_item(matched_offer.shopping_item),
            "product_offer": {
                "market_name": matched_offer.product_offer.market_name,
                "original_name": matched_offer.product_offer.original_name,
                "normalized_name": matched_offer.product_offer.normalized_name,
                "price": matched_offer.product_offer.price,
                "currency": matched_offer.product_offer.currency,
                "available": matched_offer.product_offer.available,
                "url": matched_offer.product_offer.url,
                "size_value": matched_offer.product_offer.size_value,
                "size_unit": matched_offer.product_offer.size_unit,
                "brand": matched_offer.product_offer.brand,
            },
            "match_type": matched_offer.match_type.value,
            "confidence_score": matched_offer.confidence_score,
            "notes": matched_offer.notes,
        }

    def _serialize_shopping_item(self, shopping_item: ShoppingItem) -> dict:
        """
        Serialize a shopping item.

        Args:
            shopping_item: Shopping item to serialize.

        Returns:
            A dictionary representation of the shopping item.
        """
        return {
            "item_id": shopping_item.item_id,
            "display_name": shopping_item.display_name,
            "normalized_name": shopping_item.normalized_name,
            "requested_quantity": shopping_item.requested_quantity,
            "requested_unit": shopping_item.requested_unit,
        }