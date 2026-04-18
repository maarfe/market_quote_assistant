"""Unit tests for the CLI renderer."""

from app.domain import ComparisonResult
from app.output.cli_renderer import CliRenderer
from tests.factories import create_market_quote


def test_render_comparison_result_should_include_market_sections_and_summary():
    renderer = CliRenderer()

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
            "total_cost": 23.0,
            "full_coverage": True,
            "market_name": "Market A",
            "reason": "Single market is more convenient.",
        },
        missing_items=[],
        summary_notes=["Example summary note."],
    )

    output = renderer.render_comparison_result(comparison_result)

    assert "Market Quote Assistant - comparison result" in output
    assert "Market A:" in output
    assert "Best single market:" in output
    assert "Final recommendation:" in output
    assert "Summary notes:" in output
    assert "Example summary note." in output


def test_render_comparison_result_should_include_combined_option_section_when_present():
    renderer = CliRenderer()

    market_quote = create_market_quote(
        market_name="Market A",
        item_prices=[10.0],
        delivery_fee=8.0,
    )

    comparison_result = ComparisonResult(
        market_quotes=[market_quote],
        best_single_market=market_quote,
        best_combined_option={
            "subtotal": 18.0,
            "delivery_total": 19.0,
            "total_cost": 37.0,
            "full_coverage": True,
            "used_markets": ["Market A", "Market B"],
            "market_count": 2,
            "selected_offers": [],
            "missing_items": [],
        },
        best_final_recommendation={
            "strategy": "best_combined_option",
            "total_cost": 37.0,
            "full_coverage": True,
            "market_count": 2,
            "used_markets": ["Market A", "Market B"],
            "reason": "Combined option is cheaper.",
        },
        missing_items=[],
        summary_notes=[],
    )

    output = renderer.render_comparison_result(comparison_result)

    assert "Best combined option:" in output
    assert "used markets: Market A, Market B" in output
    assert "market count: 2" in output


def test_render_comparison_result_should_render_none_sections_when_data_is_missing():
    renderer = CliRenderer()

    comparison_result = ComparisonResult()

    output = renderer.render_comparison_result(comparison_result)

    assert "Best single market:" in output
    assert "- none" in output
    assert "Summary notes:" in output