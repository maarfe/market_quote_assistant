"""Application entry point for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector
from app.domain import ShoppingItem
from app.matching import MatchingService
from app.normalization import NormalizationService


def main() -> None:
    """Run a simple matching validation flow."""
    normalization_service = NormalizationService()
    matching_service = MatchingService()

    shopping_item = ShoppingItem(
        item_id="item-001",
        display_name="Leite Integral",
        normalized_name="",
        requested_quantity=2,
        requested_unit="unit",
    )

    normalized_item = normalization_service.normalize_shopping_item(shopping_item)

    market_a_collector = JsonMarketCollector(
        market_name="Market A",
        file_path="data/market_data/market_a.json",
    )
    market_b_collector = JsonMarketCollector(
        market_name="Market B",
        file_path="data/market_data/market_b.json",
    )

    market_a_offers = [
        normalization_service.normalize_product_offer(offer)
        for offer in market_a_collector.collect_offers()
    ]
    market_b_offers = [
        normalization_service.normalize_product_offer(offer)
        for offer in market_b_collector.collect_offers()
    ]

    matched_offers = matching_service.match_offers(
        shopping_item=normalized_item,
        product_offers=market_a_offers + market_b_offers,
    )

    print("Market Quote Assistant - matching validation")
    print()
    print(f"Shopping item: {normalized_item.describe()}")
    print()

    for matched_offer in matched_offers:
        print(
            f"- {matched_offer.product_offer.market_name} | "
            f"{matched_offer.product_offer.original_name} | "
            f"{matched_offer.match_type.value} | "
            f"{matched_offer.confidence_score:.2f} | "
            f"{matched_offer.notes}"
        )


if __name__ == "__main__":
    main()