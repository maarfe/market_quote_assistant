"""Unit tests for the output formatter."""

from app.output.output_formatter import OutputFormatter
from tests.factories import create_market_quote, create_matched_offer, create_shopping_item


def test_format_currency_should_return_brl_string():
    formatter = OutputFormatter()

    result = formatter.format_currency(58.88)

    assert result == "R$ 58.88"


def test_format_shopping_item_should_return_human_readable_description():
    formatter = OutputFormatter()
    shopping_item = create_shopping_item(
        display_name="Banana",
        requested_quantity=2,
        requested_unit="kg",
    )

    result = formatter.format_shopping_item(shopping_item)

    assert result == "Banana (2 kg)"


def test_format_selected_offer_should_include_unit_price_quantity_and_total():
    formatter = OutputFormatter()
    matched_offer = create_matched_offer(
        total_price_unit=6.5,
        requested_quantity=2,
    )
    matched_offer.shopping_item.display_name = "Banana"
    matched_offer.product_offer.original_name = "Banana Nanica Kg"

    result = formatter.format_selected_offer(matched_offer)

    assert "Banana -> Banana Nanica Kg" in result
    assert "unit price: R$ 6.50" in result
    assert "quantity: 2" in result
    assert "item total: R$ 13.00" in result


def test_format_market_quote_header_should_return_market_name_with_colon():
    formatter = OutputFormatter()
    market_quote = create_market_quote(market_name="Market A")

    result = formatter.format_market_quote_header(market_quote)

    assert result == "Market A:"