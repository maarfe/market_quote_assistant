"""Unit tests for the comparison service."""

from app.comparison.comparison_service import ComparisonService
from tests.factories import create_matched_offer, create_shopping_item


def test_compare_quotes_should_return_single_and_combined_scenarios():
    service = ComparisonService()

    item_1 = create_shopping_item(item_id="item-001", display_name="Arroz")
    item_2 = create_shopping_item(item_id="item-002", display_name="Leite")

    market_a_item_1 = create_matched_offer(total_price_unit=10.0, market_name="Market A")
    market_a_item_1.shopping_item = item_1

    market_a_item_2 = create_matched_offer(total_price_unit=6.0, market_name="Market A")
    market_a_item_2.shopping_item = item_2

    market_b_item_1 = create_matched_offer(total_price_unit=8.0, market_name="Market B")
    market_b_item_1.shopping_item = item_1

    market_b_item_2 = create_matched_offer(total_price_unit=7.0, market_name="Market B")
    market_b_item_2.shopping_item = item_2

    result = service.compare_quotes(
        shopping_items=[item_1, item_2],
        matched_offers=[
            market_a_item_1,
            market_a_item_2,
            market_b_item_1,
            market_b_item_2,
        ],
        delivery_fees={
            "Market A": 8.0,
            "Market B": 11.0,
        },
    )

    assert len(result.market_quotes) == 2
    assert result.best_single_market is not None
    assert result.best_combined_option is not None
    assert result.best_final_recommendation is not None


def test_compare_quotes_should_return_summary_notes():
    service = ComparisonService()

    item = create_shopping_item(item_id="item-001", display_name="Arroz")
    match = create_matched_offer(total_price_unit=10.0, market_name="Market A")
    match.shopping_item = item

    result = service.compare_quotes(
        shopping_items=[item],
        matched_offers=[match],
        delivery_fees={"Market A": 8.0},
    )

    assert len(result.summary_notes) > 0