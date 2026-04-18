"""Application entry point for the Market Quote Assistant project."""

import json

from app.collectors import JsonMarketCollector
from app.comparison import ComparisonService
from app.matching import MatchingService
from app.normalization import NormalizationService
from app.output import CliRenderer, JsonRenderer
from app.services import ShoppingListService


def main() -> None:
    """Run the end-to-end MVP validation flow."""
    shopping_list_service = ShoppingListService()
    normalization_service = NormalizationService()
    matching_service = MatchingService()
    comparison_service = ComparisonService()
    cli_renderer = CliRenderer()
    json_renderer = JsonRenderer()

    shopping_items = shopping_list_service.load_from_file(
        "data/shopping_lists/default_shopping_list.json"
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
        delivery_fees={
            "Market A": 8.0,
            "Market B": 11.0,
        },
    )

    cli_output = cli_renderer.render_comparison_result(comparison_result)
    json_output = json_renderer.render_comparison_result(comparison_result)

    print(cli_output)
    print()
    print("JSON preview:")
    print(json.dumps(json_output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()