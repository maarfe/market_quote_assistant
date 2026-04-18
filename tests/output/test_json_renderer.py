"""Unit tests for the JSON renderer."""

from app.domain import ComparisonResult
from app.output.json_renderer import JsonRenderer
from tests.factories import create_market_quote


def test_render_comparison_result_should_return_serializable_dictionary():
    renderer = JsonRenderer()

    market_quote = create_market_quote(
        market_name="Market A",
        item_prices=[10.0, 5.0],
        delivery_fee=8.0,
    )

    comparison_result = ComparisonResult(
        market_quotes=[market_quote],
        best_single_market=market_quote,
        best_combined_option=None,
        best_final_recommendation={
            "strategy": "best_single_market",
            "market_name": "Market A",
            "total_cost": 23.0,
            "full_coverage": True,
            "reason": "Single market is more convenient.",
        },
        missing_items=[],
        summary_notes=["Example summary note."],
    )

    result = renderer.render_comparison_result(comparison_result)

    assert isinstance(result, dict)
    assert "market_quotes" in result
    assert "best_single_market" in result
    assert "best_final_recommendation" in result
    assert result["best_final_recommendation"]["strategy"] == "best_single_market"


def test_render_comparison_result_should_include_combined_option_when_present():
    renderer = JsonRenderer()

    comparison_result = ComparisonResult(
        best_combined_option={
            "strategy": "best_combined_option",
            "selected_offers": [],
            "missing_items": [],
            "used_markets": ["Market A", "Market B"],
            "subtotal": 18.0,
            "delivery_total": 19.0,
            "total_cost": 37.0,
            "full_coverage": True,
            "market_count": 2,
        }
    )

    result = renderer.render_comparison_result(comparison_result)

    assert result["best_combined_option"] is not None
    assert result["best_combined_option"]["strategy"] == "best_combined_option"
    assert result["best_combined_option"]["market_count"] == 2


def test_render_comparison_result_should_return_none_for_missing_optional_sections():
    renderer = JsonRenderer()

    comparison_result = ComparisonResult()

    result = renderer.render_comparison_result(comparison_result)

    assert result["best_single_market"] is None
    assert result["best_combined_option"] is None
    assert result["best_final_recommendation"] is None
    assert result["market_quotes"] == []
    assert result["missing_items"] == []