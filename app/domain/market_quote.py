"""Domain model that represents a market quote for a shopping list."""

from dataclasses import dataclass, field

from app.domain.matched_offer import MatchedOffer
from app.domain.shopping_item import ShoppingItem
from app.shared import MoneyHelper


@dataclass(slots=True)
class MarketQuote:
    """
    Represents the consolidated quote of a single market for a shopping list.

    Attributes:
        market_name: Name of the market being evaluated.
        selected_offers: Offers selected for the market quote.
        missing_items: Shopping items not covered by the market.
        delivery_fee: Optional delivery fee associated with the market.
    """

    market_name: str
    selected_offers: list[MatchedOffer] = field(default_factory=list)
    missing_items: list[ShoppingItem] = field(default_factory=list)
    delivery_fee: float = 0.0

    @property
    def subtotal(self) -> float:
        """
        Calculate the subtotal of selected offers considering requested quantities.

        Returns:
            The sum of selected offer total prices.
        """
        return MoneyHelper.round_currency(
            sum(
                matched_offer.calculate_total_price()
                for matched_offer in self.selected_offers
            )
        )

    @property
    def total_cost(self) -> float:
        """
        Calculate the total cost including delivery fee.

        Returns:
            The final market total cost.
        """
        return MoneyHelper.round_currency(self.subtotal + self.delivery_fee)

    def has_full_coverage(self) -> bool:
        """
        Indicate whether the market covers all requested items.

        Returns:
            True when there are no missing items, otherwise False.
        """
        return len(self.missing_items) == 0

    def selected_item_count(self) -> int:
        """
        Return the number of selected offers in this quote.

        Returns:
            The number of selected matched offers.
        """
        return len(self.selected_offers)