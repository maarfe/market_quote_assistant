"""Services responsible for building and comparing market quote scenarios."""

from app.comparison.combined_quote_builder import CombinedQuoteBuilder
from app.comparison.market_quote_builder import MarketQuoteBuilder
from app.domain import ComparisonResult, MarketQuote, MatchedOffer, ShoppingItem


class ComparisonService:
    """
    Compare market quote scenarios for a shopping list.

    This service evaluates both single-market and combined-market scenarios
    and returns the best available recommendation.
    """

    def __init__(self) -> None:
        """Initialize comparison service dependencies."""
        self._market_quote_builder = MarketQuoteBuilder()
        self._combined_quote_builder = CombinedQuoteBuilder()

    def compare_quotes(
        self,
        shopping_items: list[ShoppingItem],
        matched_offers: list[MatchedOffer],
        delivery_fees: dict[str, float] | None = None,
    ) -> ComparisonResult:
        """
        Build and compare single-market and combined-market quote scenarios.

        Args:
            shopping_items: Requested shopping items.
            matched_offers: All matched offers across all markets.
            delivery_fees: Optional delivery fee mapping by market name.

        Returns:
            A comparison result containing evaluated scenarios and the final
            recommendation.
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
        best_combined_option = self._combined_quote_builder.build(
            shopping_items=shopping_items,
            matched_offers=matched_offers,
            delivery_fees=delivery_fees,
        )

        best_final_recommendation = self._select_best_final_recommendation(
            best_single_market=best_single_market,
            best_combined_option=best_combined_option,
        )

        missing_items = self._extract_global_missing_items(
            best_single_market=best_single_market,
            best_combined_option=best_combined_option,
        )

        summary_notes = self._build_summary_notes(
            best_single_market=best_single_market,
            best_combined_option=best_combined_option,
            best_final_recommendation=best_final_recommendation,
        )

        return ComparisonResult(
            market_quotes=market_quotes,
            best_single_market=best_single_market,
            best_combined_option=best_combined_option,
            best_final_recommendation=best_final_recommendation,
            missing_items=missing_items,
            summary_notes=summary_notes,
        )

    def compare_single_market_quotes(
        self,
        shopping_items: list[ShoppingItem],
        matched_offers: list[MatchedOffer],
        delivery_fees: dict[str, float] | None = None,
    ) -> ComparisonResult:
        """
        Backward-compatible wrapper for single entrypoint migration.

        Args:
            shopping_items: Requested shopping items.
            matched_offers: All matched offers across all markets.
            delivery_fees: Optional delivery fee mapping by market name.

        Returns:
            A full comparison result.
        """
        return self.compare_quotes(
            shopping_items=shopping_items,
            matched_offers=matched_offers,
            delivery_fees=delivery_fees,
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

    def _select_best_final_recommendation(
        self,
        best_single_market: MarketQuote | None,
        best_combined_option: dict | None,
    ) -> dict | None:
        """
        Select the best final recommendation between single-market and combined strategies.

        Args:
            best_single_market: Best single-market scenario.
            best_combined_option: Best combined-market scenario.

        Returns:
            A dictionary describing the final recommendation, or None.
        """
        if best_single_market is None and best_combined_option is None:
            return None

        if best_single_market is None:
            return {
                "strategy": "best_combined_option",
                "total_cost": best_combined_option["total_cost"],
                "full_coverage": best_combined_option["full_coverage"],
                "market_count": best_combined_option["market_count"],
                "used_markets": best_combined_option["used_markets"],
            }

        if best_combined_option is None:
            return {
                "strategy": "best_single_market",
                "market_name": best_single_market.market_name,
                "total_cost": best_single_market.total_cost,
                "full_coverage": best_single_market.has_full_coverage(),
            }

        single_full_coverage = best_single_market.has_full_coverage()
        combined_full_coverage = bool(best_combined_option["full_coverage"])

        if combined_full_coverage and not single_full_coverage:
            return {
                "strategy": "best_combined_option",
                "total_cost": best_combined_option["total_cost"],
                "full_coverage": True,
                "market_count": best_combined_option["market_count"],
                "used_markets": best_combined_option["used_markets"],
            }

        if single_full_coverage and not combined_full_coverage:
            return {
                "strategy": "best_single_market",
                "market_name": best_single_market.market_name,
                "total_cost": best_single_market.total_cost,
                "full_coverage": True,
            }

        if best_combined_option["total_cost"] < best_single_market.total_cost:
            return {
                "strategy": "best_combined_option",
                "total_cost": best_combined_option["total_cost"],
                "full_coverage": best_combined_option["full_coverage"],
                "market_count": best_combined_option["market_count"],
                "used_markets": best_combined_option["used_markets"],
            }

        return {
            "strategy": "best_single_market",
            "market_name": best_single_market.market_name,
            "total_cost": best_single_market.total_cost,
            "full_coverage": best_single_market.has_full_coverage(),
        }

    def _extract_global_missing_items(
        self,
        best_single_market: MarketQuote | None,
        best_combined_option: dict | None,
    ) -> list[ShoppingItem]:
        """
        Extract missing items from the final best-coverage scenario.

        Args:
            best_single_market: Best single-market quote.
            best_combined_option: Best combined-market option.

        Returns:
            A list of missing shopping items.
        """
        single_missing = best_single_market.missing_items if best_single_market else []
        combined_missing = best_combined_option["missing_items"] if best_combined_option else []

        if len(combined_missing) < len(single_missing):
            return combined_missing

        return single_missing

    def _build_summary_notes(
        self,
        best_single_market: MarketQuote | None,
        best_combined_option: dict | None,
        best_final_recommendation: dict | None,
    ) -> list[str]:
        """
        Build human-readable summary notes for the comparison result.

        Args:
            best_single_market: Best single-market scenario.
            best_combined_option: Best combined-market scenario.
            best_final_recommendation: Final selected recommendation.

        Returns:
            A list of summary notes.
        """
        notes: list[str] = []

        if best_single_market is not None:
            notes.append(
                (
                    f"Best single market is '{best_single_market.market_name}' "
                    f"with total cost {best_single_market.total_cost:.2f} "
                    f"and full coverage={best_single_market.has_full_coverage()}."
                )
            )

        if best_combined_option is not None:
            notes.append(
                (
                    f"Best combined option uses {best_combined_option['market_count']} market(s) "
                    f"with total cost {best_combined_option['total_cost']:.2f} "
                    f"and full coverage={best_combined_option['full_coverage']}."
                )
            )

        if best_final_recommendation is not None:
            notes.append(
                f"Final recommendation selected strategy '{best_final_recommendation['strategy']}'."
            )

        if not notes:
            notes.append("No valid quote scenario could be generated.")

        return notes