"""Factories for quote-related test objects."""

from app.domain import MarketQuote
from tests.factories.domain_factories import create_matched_offer


def create_market_quote(
    market_name: str = "Market A",
    item_prices: list[float] | None = None,
    delivery_fee: float = 0.0,
) -> MarketQuote:
    """Create a market quote for tests."""
    item_prices = item_prices or []

    selected_offers = [
        create_matched_offer(total_price_unit=price)
        for price in item_prices
    ]

    return MarketQuote(
        market_name=market_name,
        selected_offers=selected_offers,
        missing_items=[],
        delivery_fee=delivery_fee,
    )