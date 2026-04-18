"""Formatting helpers for output rendering."""

from app.domain import MarketQuote, MatchedOffer, ShoppingItem


class OutputFormatter:
    """
    Provide small reusable formatting helpers for output rendering.

    This class centralizes presentation-related formatting rules to avoid
    duplication across CLI and JSON output layers.
    """

    def format_currency(self, value: float) -> str:
        """
        Format a numeric value as BRL currency.

        Args:
            value: Numeric monetary value.

        Returns:
            A formatted currency string.
        """
        return f"R$ {value:.2f}"

    def format_shopping_item(self, shopping_item: ShoppingItem) -> str:
        """
        Format a shopping item for human-readable output.

        Args:
            shopping_item: Shopping item to format.

        Returns:
            A formatted shopping item description.
        """
        return (
            f"{shopping_item.display_name} "
            f"({shopping_item.requested_quantity:g} {shopping_item.requested_unit})"
        )

    def format_selected_offer(self, matched_offer: MatchedOffer) -> str:
        """
        Format a selected matched offer for CLI output.

        Args:
            matched_offer: Matched offer to format.

        Returns:
            A formatted selected-offer line.
        """
        return (
            f"{matched_offer.shopping_item.display_name} -> "
            f"{matched_offer.product_offer.original_name} "
            f"({self.format_currency(matched_offer.product_offer.price)})"
        )

    def format_market_quote_header(self, market_quote: MarketQuote) -> str:
        """
        Format a market quote title line.

        Args:
            market_quote: Market quote to format.

        Returns:
            A formatted header string.
        """
        return f"{market_quote.market_name}:"