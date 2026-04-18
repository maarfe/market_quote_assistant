"""Factories for domain objects used in tests."""

from app.domain import MatchType, MatchedOffer, ProductOffer, ShoppingItem


def create_shopping_item(
    item_id: str = "item-001",
    display_name: str = "Leite Integral",
    normalized_name: str = "leite integral",
    requested_quantity: float = 1.0,
    requested_unit: str = "unit",
) -> ShoppingItem:
    """Create a shopping item for tests."""
    return ShoppingItem(
        item_id=item_id,
        display_name=display_name,
        normalized_name=normalized_name,
        requested_quantity=requested_quantity,
        requested_unit=requested_unit,
    )


def create_product_offer(
    market_name: str = "Market A",
    original_name: str = "Leite Integral UHT 1L",
    normalized_name: str = "leite integral 1l",
    price: float = 5.0,
    currency: str = "BRL",
    available: bool = True,
    size_value: float | None = 1.0,
    size_unit: str | None = "l",
) -> ProductOffer:
    """Create a product offer for tests."""
    return ProductOffer(
        market_name=market_name,
        original_name=original_name,
        normalized_name=normalized_name,
        price=price,
        currency=currency,
        available=available,
        size_value=size_value,
        size_unit=size_unit,
    )


def create_matched_offer(
    total_price_unit: float = 5.0,
    requested_quantity: float = 1.0,
    match_type: MatchType = MatchType.EXACT,
    market_name: str = "Market A",
) -> MatchedOffer:
    """Create a matched offer for tests."""
    shopping_item = create_shopping_item(
        requested_quantity=requested_quantity,
    )
    product_offer = create_product_offer(
        market_name=market_name,
        price=total_price_unit,
    )

    return MatchedOffer(
        shopping_item=shopping_item,
        product_offer=product_offer,
        match_type=match_type,
        confidence_score=1.0,
        notes="Test matched offer.",
    )