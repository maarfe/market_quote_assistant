"""Unit tests for the matching service."""

from app.domain import MatchType
from app.matching.matching_service import MatchingService
from tests.factories import create_product_offer, create_shopping_item


def test_match_offer_should_return_invalid_when_offer_is_unavailable():
    service = MatchingService()

    shopping_item = create_shopping_item(normalized_name="leite integral")
    product_offer = create_product_offer(
        normalized_name="leite integral 1l",
        available=False,
    )

    result = service.match_offer(shopping_item, product_offer)

    assert result.match_type == MatchType.INVALID
    assert result.confidence_score == 0.0
    assert "unavailable" in result.notes.lower()


def test_match_offer_should_return_invalid_when_there_is_no_name_overlap():
    service = MatchingService()

    shopping_item = create_shopping_item(normalized_name="banana")
    product_offer = create_product_offer(normalized_name="arroz branco 5kg")

    result = service.match_offer(shopping_item, product_offer)

    assert result.match_type == MatchType.INVALID
    assert result.confidence_score == 0.0


def test_match_offer_should_return_exact_when_required_tokens_and_units_match():
    service = MatchingService()

    shopping_item = create_shopping_item(
        normalized_name="banana",
        requested_unit="kg",
    )
    product_offer = create_product_offer(
        normalized_name="banana nanica kg",
        size_unit="kg",
    )

    result = service.match_offer(shopping_item, product_offer)

    assert result.match_type == MatchType.EXACT
    assert result.confidence_score == 1.0


def test_match_offer_should_return_partial_when_required_tokens_match_but_units_do_not():
    service = MatchingService()

    shopping_item = create_shopping_item(
        normalized_name="banana",
        requested_unit="kg",
    )
    product_offer = create_product_offer(
        normalized_name="banana nanica 1l",
        size_unit="l",
    )

    result = service.match_offer(shopping_item, product_offer)

    assert result.match_type == MatchType.PARTIAL
    assert result.confidence_score == 0.5


def test_match_offer_should_return_partial_when_only_partial_name_overlap_exists():
    service = MatchingService()

    shopping_item = create_shopping_item(
        normalized_name="leite desnatado",
        requested_unit="unit",
    )
    product_offer = create_product_offer(
        normalized_name="leite integral 1l",
        size_unit="l",
    )

    result = service.match_offer(shopping_item, product_offer)

    assert result.match_type == MatchType.PARTIAL
    assert result.confidence_score == 0.5


def test_match_offers_should_return_results_sorted_by_confidence_descending():
    service = MatchingService()

    shopping_item = create_shopping_item(
        normalized_name="banana",
        requested_unit="kg",
    )

    exact_offer = create_product_offer(
        market_name="Market A",
        normalized_name="banana nanica kg",
        size_unit="kg",
    )
    invalid_offer = create_product_offer(
        market_name="Market B",
        normalized_name="arroz branco 5kg",
        size_unit="kg",
    )

    results = service.match_offers(
        shopping_item=shopping_item,
        product_offers=[invalid_offer, exact_offer],
    )

    assert len(results) == 2
    assert results[0].confidence_score >= results[1].confidence_score
    assert results[0].match_type == MatchType.EXACT