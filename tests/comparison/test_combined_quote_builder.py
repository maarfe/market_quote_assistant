"""Unit tests for the combined quote builder."""

from app.comparison.combined_quote_builder import CombinedQuoteBuilder
from tests.factories import create_matched_offer, create_shopping_item


def test_build_should_select_best_offer_across_markets_for_each_item():
    builder = CombinedQuoteBuilder()

    item_1 = create_shopping_item(item_id="item-001", display_name="Arroz")
    item_2 = create_shopping_item(item_id="item-002", display_name="Leite")

    market_a_item_1 = create_matched_offer(total_price_unit=10.0, market_name="Market A")
    market_a_item_1.shopping_item = item_1

    market_b_item_1 = create_matched_offer(total_price_unit=8.0, market_name="Market B")
    market_b_item_1.shopping_item = item_1

    market_a_item_2 = create_matched_offer(total_price_unit=5.0, market_name="Market A")
    market_a_item_2.shopping_item = item_2

    result = builder.build(
        shopping_items=[item_1, item_2],
        matched_offers=[market_a_item_1, market_b_item_1, market_a_item_2],
        delivery_fees={
            "Market A": 8.0,
            "Market B": 11.0,
        },
    )

    assert result["strategy"] == "best_combined_option"
    assert len(result["selected_offers"]) == 2
    assert result["used_markets"] == ["Market A", "Market B"]
    assert result["market_count"] == 2
    assert result["full_coverage"] is True


def test_build_should_mark_missing_items_when_item_has_no_match():
    builder = CombinedQuoteBuilder()

    item = create_shopping_item(item_id="item-001", display_name="Arroz")

    result = builder.build(
        shopping_items=[item],
        matched_offers=[],
        delivery_fees={},
    )

    assert len(result["selected_offers"]) == 0
    assert len(result["missing_items"]) == 1
    assert result["full_coverage"] is False