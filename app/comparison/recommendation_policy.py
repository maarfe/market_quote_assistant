"""Policies for selecting the final recommendation between quote strategies."""

from dataclasses import dataclass

from app.domain import MarketQuote
from app.shared import MoneyHelper


@dataclass(slots=True)
class RecommendationPolicyConfig:
    """
    Configuration values for convenience-aware recommendation decisions.

    Attributes:
        minimum_savings_to_split: Minimum savings required to justify splitting
            the shopping across multiple markets.
    """

    minimum_savings_to_split: float = 8.0


class RecommendationPolicy:
    """
    Encapsulate convenience-aware rules for final recommendation selection.
    """

    def __init__(self, config: RecommendationPolicyConfig | None = None) -> None:
        """
        Initialize the recommendation policy.

        Args:
            config: Optional policy configuration. Defaults to standard values.
        """
        self._config = config or RecommendationPolicyConfig()

    def select_recommendation(
        self,
        best_single_market: MarketQuote | None,
        best_combined_option: dict | None,
    ) -> dict | None:
        """
        Select the final recommendation between single-market and combined options.

        Args:
            best_single_market: Best evaluated single-market quote.
            best_combined_option: Best evaluated combined-market quote.

        Returns:
            A dictionary describing the final recommendation, or None.
        """
        if best_single_market is None and best_combined_option is None:
            return None

        if best_single_market is None:
            return self._build_combined_recommendation(
                best_combined_option=best_combined_option,
                reason="Combined option is the only available scenario.",
            )

        if best_combined_option is None:
            return self._build_single_market_recommendation(
                best_single_market=best_single_market,
                reason="Single-market option is the only available scenario.",
            )

        single_full_coverage = best_single_market.has_full_coverage()
        combined_full_coverage = bool(best_combined_option["full_coverage"])

        if combined_full_coverage and not single_full_coverage:
            return self._build_combined_recommendation(
                best_combined_option=best_combined_option,
                reason="Combined option provides better coverage than the best single-market scenario.",
            )

        if single_full_coverage and not combined_full_coverage:
            return self._build_single_market_recommendation(
                best_single_market=best_single_market,
                reason="Best single-market scenario provides better coverage than the combined option.",
            )

        single_total = MoneyHelper.round_currency(best_single_market.total_cost)
        combined_total = MoneyHelper.round_currency(best_combined_option["total_cost"])
        cost_difference = MoneyHelper.round_currency(single_total - combined_total)

        if cost_difference > 0:
            if cost_difference >= self._config.minimum_savings_to_split:
                return self._build_combined_recommendation(
                    best_combined_option=best_combined_option,
                    reason=(
                        f"Combined option saves R$ {cost_difference:.2f} and exceeds the "
                        f"minimum split threshold of R$ {self._config.minimum_savings_to_split:.2f}."
                    ),
                )

            return self._build_single_market_recommendation(
                best_single_market=best_single_market,
                reason=(
                    f"Combined option saves R$ {cost_difference:.2f}, but this does not justify "
                    f"splitting the purchase across multiple markets."
                ),
            )

        if cost_difference == 0:
            return self._build_single_market_recommendation(
                best_single_market=best_single_market,
                reason=(
                    "Combined option has the same total cost as the best single market, "
                    "so the single-market strategy is more convenient."
                ),
            )

        combined_extra_cost = MoneyHelper.round_currency(abs(cost_difference))
        return self._build_single_market_recommendation(
            best_single_market=best_single_market,
            reason=(
                f"Combined option costs R$ {combined_extra_cost:.2f} more than the best single market, "
                "so splitting the purchase is not justified."
            ),
        )

    def _build_single_market_recommendation(
        self,
        best_single_market: MarketQuote,
        reason: str,
    ) -> dict:
        """
        Build a final recommendation payload for the best single-market option.

        Args:
            best_single_market: Best evaluated single-market quote.
            reason: Explanation for why this strategy was selected.

        Returns:
            A structured recommendation payload.
        """
        return {
            "strategy": "best_single_market",
            "market_name": best_single_market.market_name,
            "total_cost": MoneyHelper.round_currency(best_single_market.total_cost),
            "full_coverage": best_single_market.has_full_coverage(),
            "reason": reason,
        }

    def _build_combined_recommendation(
        self,
        best_combined_option: dict,
        reason: str,
    ) -> dict:
        """
        Build a final recommendation payload for the best combined option.

        Args:
            best_combined_option: Best evaluated combined-market scenario.
            reason: Explanation for why this strategy was selected.

        Returns:
            A structured recommendation payload.
        """
        return {
            "strategy": "best_combined_option",
            "total_cost": MoneyHelper.round_currency(best_combined_option["total_cost"]),
            "full_coverage": best_combined_option["full_coverage"],
            "market_count": best_combined_option["market_count"],
            "used_markets": best_combined_option["used_markets"],
            "reason": reason,
        }