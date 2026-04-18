"""Summary renderer for concise comparison output."""

from app.domain import ComparisonResult
from app.output.output_formatter import OutputFormatter


class SummaryRenderer:
    """
    Render a concise summary of the comparison result.
    """

    def __init__(self) -> None:
        """Initialize renderer dependencies."""
        self.formatter = OutputFormatter()

    def render_comparison_result(self, result: ComparisonResult) -> str:
        """
        Render a summary view of the comparison result.

        Args:
            result: The comparison result.

        Returns:
            A formatted summary string.
        """
        lines: list[str] = []

        lines.append("Market Quote Assistant - summary")
        lines.append("")

        if result.best_final_recommendation:
            recommendation = result.best_final_recommendation

            lines.append(
                f"Recommended strategy: {recommendation.get('strategy')}"
            )
            lines.append(
                "Total cost: "
                f"{self.formatter.format_currency(recommendation.get('total_cost', 0))}"
            )
            lines.append(
                f"Full coverage: {recommendation.get('full_coverage')}"
            )
            lines.append("")

            lines.append("Why:")
            lines.append(f"- {recommendation.get('reason')}")
            lines.append("")

        else:
            lines.append("No recommendation available.")
            return "\n".join(lines)

        lines.append("Best single market:")

        if result.best_single_market:
            market = result.best_single_market
            lines.append(f"- {market.market_name}")
            lines.append(
                f"- Total: {self.formatter.format_currency(market.total_cost)}"
            )
        else:
            lines.append("- none")

        lines.append("")

        lines.append("Best combined option:")

        if result.best_combined_option:
            combined = result.best_combined_option

            markets = combined.get("used_markets", [])
            total_cost = combined.get("total_cost", 0)

            lines.append(f"- Markets: {', '.join(markets)}")
            lines.append(
                f"- Total: {self.formatter.format_currency(total_cost)}"
            )
        else:
            lines.append("- none")

        lines.append("")

        if result.missing_items:
            lines.append("Missing items:")
            for item in result.missing_items:
                lines.append(f"- {item.display_name}")
            lines.append("")

        return "\n".join(lines)