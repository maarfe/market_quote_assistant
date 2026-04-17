"""Services responsible for building and comparing market quote scenarios."""

from app.comparison.market_quote_builder import MarketQuoteBuilder
from app.domain import ComparisonResult, MarketQuote, MatchedOffer, ShoppingItem


class ComparisonService:
    """
    Compare market quote scenarios for a shopping list.

    The initial MVP scope of this service focuses on evaluating single-market
    scenarios and identifying the best overall market quote.
    """

    def __init__(self) -> None:
        """Initialize comparison service dependencies."""
        self._market_quote_builder = MarketQuoteBuilder()

    def compare_single_market_quotes(
        self,
        shopping_items: list[ShoppingItem],
        matched_offers: list[MatchedOffer],
        delivery_fees: dict[str, float] | None = None,
    ) -> ComparisonResult:
        """
        Build and compare single-market quotes.

        Args:
            shopping_items: Requested shopping items.
            matched_offers: All matched offers across all markets.
            delivery_fees: Optional delivery fee mapping by market name.

        Returns:
            A comparison result containing evaluated market quotes and the
            best single-market recommendation.
        """
        delivery_fees = delivery_fees or {}
        market_names = self._extract_market_names(matched_offers)

        market_quotes = [
            self._market_quote_builder.build(
                market_name=market_name,
                shopping_items=shopping_items,
                matched_offers=self._filter_matches_for_market(
                    market_name=market_name,
                    matched_offers=matched_offers,
                ),
                delivery_fee=delivery_fees.get(market_name, 0.0),
            )
            for market_name in market_names
        ]

        best_single_market = self._select_best_single_market(market_quotes)

        return ComparisonResult(
            market_quotes=market_quotes,
            best_single_market=best_single_market,
            best_combined_option=None,
            best_final_recommendation=self._build_final_recommendation(best_single_market),
            missing_items=self._extract_global_missing_items(best_single_market),
            summary_notes=self._build_summary_notes(best_single_market),
        )

    def _extract_market_names(self, matched_offers: list[MatchedOffer]) -> list[str]:
        """
        Extract distinct market names from matched offers.

        Args:
            matched_offers: All matched offers across markets.

        Returns:
            A sorted list of distinct market names.
        """
        return sorted(
            {
                matched_offer.product_offer.market_name
                for matched_offer in matched_offers
            }
        )

    def _filter_matches_for_market(
        self,
        market_name: str,
        matched_offers: list[MatchedOffer],
    ) -> list[MatchedOffer]:
        """
        Filter matched offers belonging to a specific market.

        Args:
            market_name: Market name to filter.
            matched_offers: All matched offers across markets.

        Returns:
            A list of matched offers for the specified market.
        """
        return [
            matched_offer
            for matched_offer in matched_offers
            if matched_offer.product_offer.market_name == market_name
        ]

    def _select_best_single_market(
        self,
        market_quotes: list[MarketQuote],
    ) -> MarketQuote | None:
        """
        Select the best market quote among single-market scenarios.

        Priority order:
        1. full coverage
        2. lower total cost
        3. fewer missing items
        4. lower total cost again as deterministic fallback

        Args:
            market_quotes: Consolidated market quotes.

        Returns:
            The best market quote, or None when no quotes are available.
        """
        if not market_quotes:
            return None

        return sorted(
            market_quotes,
            key=lambda market_quote: (
                not market_quote.has_full_coverage(),
                market_quote.total_cost,
                len(market_quote.missing_items),
                market_quote.total_cost,
            ),
        )[0]

    def _build_final_recommendation(
        self,
        best_single_market: MarketQuote | None,
    ) -> dict | None:
        """
        Build a simple final recommendation payload.

        Args:
            best_single_market: Best evaluated single-market quote.

        Returns:
            A dictionary payload describing the recommendation, or None.
        """
        if best_single_market is None:
            return None

        return {
            "strategy": "best_single_market",
            "market_name": best_single_market.market_name,
            "total_cost": best_single_market.total_cost,
            "full_coverage": best_single_market.has_full_coverage(),
        }

    def _extract_global_missing_items(
        self,
        best_single_market: MarketQuote | None,
    ) -> list[ShoppingItem]:
        """
        Extract missing items from the best single-market quote.

        Args:
            best_single_market: Best evaluated single-market quote.

        Returns:
            A list of missing shopping items.
        """
        if best_single_market is None:
            return []

        return best_single_market.missing_items

    def _build_summary_notes(
        self,
        best_single_market: MarketQuote | None,
    ) -> list[str]:
        """
        Build human-readable summary notes for the comparison result.

        Args:
            best_single_market: Best evaluated single-market quote.

        Returns:
            A list of summary notes.
        """
        if best_single_market is None:
            return ["No valid market quote could be generated."]

        if best_single_market.has_full_coverage():
            return [
                (
                    f"Best single market is '{best_single_market.market_name}' "
                    f"with full coverage and total cost {best_single_market.total_cost:.2f}."
                )
            ]

        return [
            (
                f"Best partial single market is '{best_single_market.market_name}' "
                f"covering {best_single_market.selected_item_count()} item(s) "
                f"with total cost {best_single_market.total_cost:.2f}."
            )
        ]