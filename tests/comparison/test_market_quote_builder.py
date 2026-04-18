"""Unit tests for the market quote builder."""

from app.comparison.market_quote_builder import MarketQuoteBuilder
from tests.factories import create_matched_offer, create_shopping_item


def test_build_should_select_best_offer_for_each_item():
    builder = MarketQuoteBuilder()

    item_1 = create_shopping_item(item_id="item-001", display_name="Arroz")
    item_2 = create_shopping_item(item_id="item-002", display_name="Leite")

    match_item_1 = create_matched_offer(total_price_unit=10.0)
    match_item_1.shopping_item = item_1

    better_match_item_1 = create_matched_offer(total_price_unit=8.0)
    better_match_item_1.shopping_item = item_1

    match_item_2 = create_matched_offer(total_price_unit=5.0)
    match_item_2.shopping_item = item_2

    result = builder.build(
        market_name="Market A",
        shopping_items=[item_1, item_2],
        matched_offers=[match_item_1, better_match_item_1, match_item_2],
        delivery_fee=7.0,
    )

    assert result.market_name == "Market A"
    assert len(result.selected_offers) == 2
    assert result.delivery_fee == 7.0
    assert result.has_full_coverage() is True


def test_build_should_mark_item_as_missing_when_no_valid_offer_exists():
    builder = MarketQuoteBuilder()

    item = create_shopping_item(item_id="item-001", display_name="Arroz")

    result = builder.build(
        market_name="Market A",
        shopping_items=[item],
        matched_offers=[],
        delivery_fee=0.0,
    )

    assert len(result.selected_offers) == 0
    assert len(result.missing_items) == 1
    assert result.has_full_coverage() is False