"""Unit tests for the match rules."""

from app.matching.match_rules import MatchRules
from tests.factories import create_product_offer, create_shopping_item


def test_has_required_name_tokens_should_return_true_when_all_item_tokens_exist():
    rules = MatchRules()

    shopping_item = create_shopping_item(
        display_name="Leite Integral",
        normalized_name="leite integral",
    )
    product_offer = create_product_offer(
        original_name="Leite Integral UHT 1L",
        normalized_name="leite integral 1l",
    )

    result = rules.has_required_name_tokens(shopping_item, product_offer)

    assert result is True


def test_has_required_name_tokens_should_return_false_when_any_item_token_is_missing():
    rules = MatchRules()

    shopping_item = create_shopping_item(
        display_name="Leite Desnatado",
        normalized_name="leite desnatado",
    )
    product_offer = create_product_offer(
        original_name="Leite Integral UHT 1L",
        normalized_name="leite integral 1l",
    )

    result = rules.has_required_name_tokens(shopping_item, product_offer)

    assert result is False


def test_has_any_name_overlap_should_return_true_when_texts_share_at_least_one_token():
    rules = MatchRules()

    shopping_item = create_shopping_item(normalized_name="banana prata")
    product_offer = create_product_offer(normalized_name="banana nanica kg")

    result = rules.has_any_name_overlap(shopping_item, product_offer)

    assert result is True


def test_has_any_name_overlap_should_return_false_when_texts_share_no_tokens():
    rules = MatchRules()

    shopping_item = create_shopping_item(normalized_name="banana")
    product_offer = create_product_offer(normalized_name="arroz branco 5kg")

    result = rules.has_any_name_overlap(shopping_item, product_offer)

    assert result is False


def test_has_compatible_unit_should_return_true_when_requested_unit_is_unit():
    rules = MatchRules()

    shopping_item = create_shopping_item(requested_unit="unit")
    product_offer = create_product_offer(size_unit="l")

    result = rules.has_compatible_unit(shopping_item, product_offer)

    assert result is True


def test_has_compatible_unit_should_return_true_when_units_match():
    rules = MatchRules()

    shopping_item = create_shopping_item(requested_unit="kg")
    product_offer = create_product_offer(size_unit="kg")

    result = rules.has_compatible_unit(shopping_item, product_offer)

    assert result is True


def test_has_compatible_unit_should_return_false_when_units_do_not_match():
    rules = MatchRules()

    shopping_item = create_shopping_item(requested_unit="kg")
    product_offer = create_product_offer(size_unit="l")

    result = rules.has_compatible_unit(shopping_item, product_offer)

    assert result is False


def test_has_compatible_unit_should_return_false_when_offer_unit_is_missing():
    rules = MatchRules()

    shopping_item = create_shopping_item(requested_unit="kg")
    product_offer = create_product_offer(size_unit=None)

    result = rules.has_compatible_unit(shopping_item, product_offer)

    assert result is False


def test_is_offer_available_should_return_true_for_available_offer():
    rules = MatchRules()

    product_offer = create_product_offer(available=True)

    result = rules.is_offer_available(product_offer)

    assert result is True


def test_is_offer_available_should_return_false_for_unavailable_offer():
    rules = MatchRules()

    product_offer = create_product_offer(available=False)

    result = rules.is_offer_available(product_offer)

    assert result is False