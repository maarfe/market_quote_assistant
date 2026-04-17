"""Application entry point for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector
from app.comparison import ComparisonService
from app.domain import ShoppingItem
from app.matching import MatchingService
from app.normalization import NormalizationService


def main() -> None:
    """Run a single-market comparison validation flow."""
    normalization_service = NormalizationService()
    matching_service = MatchingService()
    comparison_service = ComparisonService()

    shopping_items = [
        ShoppingItem(
            item_id="item-001",
            display_name="Arroz Branco",
            normalized_name="",
            requested_quantity=1,
            requested_unit="unit",
        ),
        ShoppingItem(
            item_id="item-002",
            display_name="Leite Integral",
            normalized_name="",
            requested_quantity=2,
            requested_unit="unit",
        ),
        ShoppingItem(
            item_id="item-003",
            display_name="Banana",
            normalized_name="",
            requested_quantity=1,
            requested_unit="kg",
        ),
    ]

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

    comparison_result = comparison_service.compare_single_market_quotes(
        shopping_items=normalized_items,
        matched_offers=matched_offers,
        delivery_fees={
            "Market A": 8.0,
            "Market B": 11.0,
        },
    )

    print("Market Quote Assistant - single market comparison validation")
    print()

    for market_quote in comparison_result.market_quotes:
        print(f"{market_quote.market_name}:")
        print(f"- subtotal: {market_quote.subtotal:.2f}")
        print(f"- delivery fee: {market_quote.delivery_fee:.2f}")
        print(f"- total cost: {market_quote.total_cost:.2f}")
        print(f"- full coverage: {market_quote.has_full_coverage()}")
        print("- selected offers:")
        for selected_offer in market_quote.selected_offers:
            print(
                f"  - {selected_offer.shopping_item.display_name} -> "
                f"{selected_offer.product_offer.original_name} "
                f"({selected_offer.product_offer.price:.2f})"
            )

        if market_quote.missing_items:
            print("- missing items:")
            for missing_item in market_quote.missing_items:
                print(f"  - {missing_item.display_name}")

        print()

    if comparison_result.best_single_market is not None:
        print("Best single market:")
        print(
            f"- {comparison_result.best_single_market.market_name} "
            f"({comparison_result.best_single_market.total_cost:.2f})"
        )

    print()
    print("Summary notes:")
    for note in comparison_result.summary_notes:
        print(f"- {note}")


if __name__ == "__main__":
    main()