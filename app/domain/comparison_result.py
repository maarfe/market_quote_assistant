"""Domain model that represents the final comparison result across markets."""

from dataclasses import dataclass, field

from app.domain.market_quote import MarketQuote
from app.domain.shopping_item import ShoppingItem


@dataclass(slots=True)
class ComparisonResult:
    """
    Represents the final outcome of comparing multiple market quotes.

    Attributes:
        market_quotes: All evaluated market quotes.
        best_single_market: Best quote considering one market only.
        best_combined_option: Optional structure representing the best multi-market strategy.
        best_final_recommendation: Final recommendation payload for the user.
        missing_items: Items that could not be covered by the evaluated scenarios.
        summary_notes: Optional explanatory notes about the result.
    """

    market_quotes: list[MarketQuote] = field(default_factory=list)
    best_single_market: MarketQuote | None = None
    best_combined_option: dict | None = None
    best_final_recommendation: dict | None = None
    missing_items: list[ShoppingItem] = field(default_factory=list)
    summary_notes: list[str] = field(default_factory=list)

    def has_recommendation(self) -> bool:
        """
        Indicate whether a final recommendation is available.

        Returns:
            True when a final recommendation exists, otherwise False.
        """
        return self.best_final_recommendation is not None