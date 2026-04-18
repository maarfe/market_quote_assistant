"""Services for CLI argument parsing and runtime configuration."""

from dataclasses import dataclass
import argparse


@dataclass(slots=True)
class CliConfig:
    """
    Represents runtime configuration loaded from CLI arguments.

    Attributes:
        shopping_list_path: Path to the shopping list JSON file.
        delivery_fees_path: Path to the delivery fee JSON file.
        market_sources_path: Path to the market sources JSON file.
        output_mode: Output mode to render.
    """

    shopping_list_path: str
    delivery_fees_path: str
    market_sources_path: str
    output_mode: str


class CliConfigService:
    """
    Parse and validate CLI arguments for the application.
    """

    def parse_args(self) -> CliConfig:
        """
        Parse CLI arguments and return a structured configuration object.

        Returns:
            A CLI configuration object.
        """
        parser = argparse.ArgumentParser(
            prog="market-quote-assistant",
            description="Compare grocery quotes across mock markets.",
        )

        parser.add_argument(
            "--shopping-list",
            dest="shopping_list_path",
            default="data/shopping_lists/default_shopping_list.json",
            help="Path to the shopping list JSON file.",
        )

        parser.add_argument(
            "--market-sources",
            dest="market_sources_path",
            default="data/market_sources/default_market_sources.json",
            help="Path to the market sources JSON file.",
        )

        parser.add_argument(
            "--delivery-fees",
            dest="delivery_fees_path",
            default="data/delivery_fees/default_delivery_fees.json",
            help="Path to the delivery fee JSON file.",
        )

        parser.add_argument(
            "--output",
            dest="output_mode",
            choices=("cli", "json", "both"),
            default="both",
            help="Output mode to render.",
        )

        args = parser.parse_args()

        return CliConfig(
            shopping_list_path=args.shopping_list_path,
            delivery_fees_path=args.delivery_fees_path,
            market_sources_path=args.market_sources_path,
            output_mode=args.output_mode,
        )