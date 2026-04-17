"""Application entry point for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector
from app.domain import ShoppingItem
from app.normalization import NormalizationService


def main() -> None:
    """Run a simple normalization validation flow."""
    normalization_service = NormalizationService()

    shopping_item = ShoppingItem(
        item_id="item-001",
        display_name="Leite Integral UHT",
        normalized_name="",
        requested_quantity=2,
        requested_unit="unidade",
    )

    normalized_item = normalization_service.normalize_shopping_item(shopping_item)

    market_a_collector = JsonMarketCollector(
        market_name="Market A",
        file_path="data/market_data/market_a.json",
    )
    market_a_offers = market_a_collector.collect_offers()

    normalized_offers = [
        normalization_service.normalize_product_offer(offer)
        for offer in market_a_offers
    ]

    print("Market Quote Assistant - normalization validation")
    print()
    print("Shopping item:")
    print(f"- original:   {shopping_item.display_name}")
    print(f"- normalized: {normalized_item.normalized_name}")
    print(f"- unit:       {normalized_item.requested_unit}")

    print()
    print("Market A normalized offers:")
    for offer in normalized_offers:
        print(
            f"- original: {offer.original_name} | "
            f"normalized: {offer.normalized_name} | "
            f"size: {offer.size_value} {offer.size_unit}"
        )


if __name__ == "__main__":
    main()