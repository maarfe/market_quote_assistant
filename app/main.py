"""Application entry point for the Market Quote Assistant project."""

import json

from app.collectors import JsonMarketCollector
from app.comparison import ComparisonService
from app.matching import MatchingService
from app.normalization import NormalizationService
from app.output import CliRenderer, JsonRenderer
from app.services import (
    CliConfigService,
    DeliveryFeeService,
    ShoppingListService,
)


def main() -> None:
    """Run the end-to-end MVP validation flow."""
    cli_config_service = CliConfigService()
    shopping_list_service = ShoppingListService()
    delivery_fee_service = DeliveryFeeService()
    normalization_service = NormalizationService()
    matching_service = MatchingService()
    comparison_service = ComparisonService()
    cli_renderer = CliRenderer()
    json_renderer = JsonRenderer()

    cli_config = cli_config_service.parse_args()

    shopping_items = shopping_list_service.load_from_file(
        cli_config.shopping_list_path
    )
    delivery_fees = delivery_fee_service.load_from_file(
        cli_config.delivery_fees_path
    )

    normalized_items = [
        normalization_service.normalize_shopping_item(shopping_item)
        for shopping_item in shopping_items
    ]

    collectors = [
        JsonMarketCollector(
            market_name="Market A",
            file_path="data/market_data/market_a.json",
        ),
        JsonMarketCollector(
            market_name="Market B",
            file_path="data/market_data/market_b.json",
        ),
    ]

    normalized_offers = []
    for collector in collectors:
        offers = collector.collect_offers()
        normalized_offers.extend(
            normalization_service.normalize_product_offer(offer)
            for offer in offers
        )

    matched_offers = []
    for shopping_item in normalized_items:
        matched_offers.extend(
            matching_service.match_offers(
                shopping_item=shopping_item,
                product_offers=normalized_offers,
            )
        )

    comparison_result = comparison_service.compare_quotes(
        shopping_items=normalized_items,
        matched_offers=matched_offers,
        delivery_fees=delivery_fees,
    )

    if cli_config.output_mode in {"cli", "both"}:
        cli_output = cli_renderer.render_comparison_result(comparison_result)
        print(cli_output)

    if cli_config.output_mode in {"json", "both"}:
        json_output = json_renderer.render_comparison_result(comparison_result)

        if cli_config.output_mode == "both":
            print()
            print("JSON preview:")

        print(json.dumps(json_output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()