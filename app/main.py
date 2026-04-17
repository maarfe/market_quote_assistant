"""Application entry point for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector


def main() -> None:
    """Run a simple mock collection flow for local validation."""
    market_a_collector = JsonMarketCollector(
        market_name="Market A",
        file_path="data/market_data/market_a.json",
    )
    market_b_collector = JsonMarketCollector(
        market_name="Market B",
        file_path="data/market_data/market_b.json",
    )

    market_a_offers = market_a_collector.collect_offers()
    market_b_offers = market_b_collector.collect_offers()

    print("Market Quote Assistant - mock collector validation")
    print()

    print("Market A offers:")
    for offer in market_a_offers:
        print(f"- {offer.describe()}")

    print()
    print("Market B offers:")
    for offer in market_b_offers:
        print(f"- {offer.describe()}")


if __name__ == "__main__":
    main()