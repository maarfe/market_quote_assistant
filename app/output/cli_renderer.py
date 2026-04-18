"""CLI renderer for comparison results."""

from app.domain import ComparisonResult, MarketQuote
from app.output.output_formatter import OutputFormatter


class CliRenderer:
    """
    Render comparison results in a human-readable CLI format.
    """

    def __init__(self) -> None:
        """Initialize renderer dependencies."""
        self._formatter = OutputFormatter()

    def render_comparison_result(self, comparison_result: ComparisonResult) -> str:
        """
        Render a comparison result as a multiline CLI string.

        Args:
            comparison_result: Comparison result to render.

        Returns:
            A formatted multiline string for terminal display.
        """
        lines: list[str] = []
        lines.append("Market Quote Assistant - comparison result")
        lines.append("")

        for market_quote in comparison_result.market_quotes:
            lines.extend(self._render_market_quote(market_quote))
            lines.append("")

        lines.extend(self._render_best_single_market(comparison_result))
        lines.append("")
        lines.extend(self._render_best_combined_option(comparison_result))
        lines.append("")
        lines.extend(self._render_final_recommendation(comparison_result))
        lines.append("")
        lines.extend(self._render_summary_notes(comparison_result))

        return "\n".join(lines).strip()

    def _render_market_quote(self, market_quote: MarketQuote) -> list[str]:
        """
        Render a single market quote block.

        Args:
            market_quote: Market quote to render.

        Returns:
            A list of rendered lines.
        """
        lines = [
            self._formatter.format_market_quote_header(market_quote),
            f"- subtotal: {self._formatter.format_currency(market_quote.subtotal)}",
            f"- delivery fee: {self._formatter.format_currency(market_quote.delivery_fee)}",
            f"- total cost: {self._formatter.format_currency(market_quote.total_cost)}",
            f"- full coverage: {market_quote.has_full_coverage()}",
            "- selected offers:",
        ]

        if market_quote.selected_offers:
            for selected_offer in market_quote.selected_offers:
                lines.append(
                    f"  - {self._formatter.format_selected_offer(selected_offer)}"
                )
        else:
            lines.append("  - none")

        if market_quote.missing_items:
            lines.append("- missing items:")
            for missing_item in market_quote.missing_items:
                lines.append(
                    f"  - {self._formatter.format_shopping_item(missing_item)}"
                )

        return lines

    def _render_best_single_market(
        self,
        comparison_result: ComparisonResult,
    ) -> list[str]:
        """
        Render the best single-market section.

        Args:
            comparison_result: Comparison result to inspect.

        Returns:
            A list of rendered lines.
        """
        if comparison_result.best_single_market is None:
            return ["Best single market:", "- none"]

        best_market = comparison_result.best_single_market

        return [
            "Best single market:",
            (
                f"- {best_market.market_name} "
                f"({self._formatter.format_currency(best_market.total_cost)})"
            ),
        ]

    def _render_best_combined_option(
        self,
        comparison_result: ComparisonResult,
    ) -> list[str]:
        """
        Render the best combined-market section.

        Args:
            comparison_result: Comparison result to inspect.

        Returns:
            A list of rendered lines.
        """
        combined_option = comparison_result.best_combined_option

        if combined_option is None:
            return ["Best combined option:", "- none"]

        lines = [
            "Best combined option:",
            f"- subtotal: {self._formatter.format_currency(combined_option['subtotal'])}",
            f"- delivery total: {self._formatter.format_currency(combined_option['delivery_total'])}",
            f"- total cost: {self._formatter.format_currency(combined_option['total_cost'])}",
            f"- full coverage: {combined_option['full_coverage']}",
            f"- used markets: {', '.join(combined_option['used_markets']) or 'none'}",
            f"- market count: {combined_option['market_count']}",
            "- selected offers:",
        ]

        if combined_option["selected_offers"]:
            for selected_offer in combined_option["selected_offers"]:
                lines.append(
                    f"  - {self._formatter.format_selected_offer(selected_offer)}"
                )
        else:
            lines.append("  - none")

        if combined_option["missing_items"]:
            lines.append("- missing items:")
            for missing_item in combined_option["missing_items"]:
                lines.append(
                    f"  - {self._formatter.format_shopping_item(missing_item)}"
                )

        return lines

    def _render_final_recommendation(
        self,
        comparison_result: ComparisonResult,
    ) -> list[str]:
        """
        Render the final recommendation section.

        Args:
            comparison_result: Comparison result to inspect.

        Returns:
            A list of rendered lines.
        """
        recommendation = comparison_result.best_final_recommendation

        if recommendation is None:
            return ["Final recommendation:", "- none"]

        lines = [
            "Final recommendation:",
            f"- strategy: {recommendation['strategy']}",
            f"- total cost: {self._formatter.format_currency(recommendation['total_cost'])}",
            f"- full coverage: {recommendation['full_coverage']}",
        ]

        if recommendation["strategy"] == "best_single_market":
            lines.append(f"- market name: {recommendation['market_name']}")
        else:
            lines.append(f"- market count: {recommendation['market_count']}")
            lines.append(f"- used markets: {', '.join(recommendation['used_markets'])}")

        return lines

    def _render_summary_notes(
        self,
        comparison_result: ComparisonResult,
    ) -> list[str]:
        """
        Render summary notes.

        Args:
            comparison_result: Comparison result to inspect.

        Returns:
            A list of rendered lines.
        """
        lines = ["Summary notes:"]

        if not comparison_result.summary_notes:
            lines.append("- none")
            return lines

        for note in comparison_result.summary_notes:
            lines.append(f"- {note}")

        return lines