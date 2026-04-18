"""Unit tests for the normalization service."""

from app.normalization.normalization_service import NormalizationService
from tests.factories import create_product_offer, create_shopping_item


def test_normalize_shopping_item_should_return_normalized_copy():
    service = NormalizationService()

    shopping_item = create_shopping_item(
        display_name="Leíte Integral UHT",
        normalized_name="",
        requested_quantity=2,
        requested_unit="unidade",
    )

    result = service.normalize_shopping_item(shopping_item)

    assert result is not shopping_item
    assert result.display_name == "Leíte Integral UHT"
    assert result.normalized_name == "leite integral"
    assert result.requested_quantity == 2
    assert result.requested_unit == "unit"


def test_normalize_product_offer_should_return_normalized_copy():
    service = NormalizationService()

    product_offer = create_product_offer(
        original_name="Leíte Integral UHT 1L Italac",
        normalized_name="",
        price=4.99,
        size_value=1,
        size_unit="litro",
    )

    result = service.normalize_product_offer(product_offer)

    assert result is not product_offer
    assert result.original_name == "Leíte Integral UHT 1L Italac"
    assert result.normalized_name == "leite integral 1l italac"
    assert result.price == 4.99
    assert result.size_value == 1.0
    assert result.size_unit == "l"


def test_normalize_product_offer_should_preserve_missing_measurement_data():
    service = NormalizationService()

    product_offer = create_product_offer(
        original_name="Banana Nanica",
        normalized_name="",
        size_value=None,
        size_unit=None,
    )

    result = service.normalize_product_offer(product_offer)

    assert result.size_value is None
    assert result.size_unit is None
    assert result.normalized_name == "banana nanica"


def test_normalize_text_should_return_structured_normalized_text_data():
    service = NormalizationService()

    result = service.normalize_text("  Leíte Integral/UHT  ")

    assert result.original_text == "  Leíte Integral/UHT  "
    assert result.cleaned_text == "leite integral uht"
    assert result.canonical_text == "leite integral"