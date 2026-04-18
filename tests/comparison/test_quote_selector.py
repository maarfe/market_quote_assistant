"""Unit tests for the quote selector."""

from app.comparison.quote_selector import QuoteSelector
from app.domain import MatchType
from tests.factories import create_matched_offer


def test_select_best_offer_should_return_none_when_no_valid_candidate_exists():
    selector = QuoteSelector()

    invalid_offer = create_matched_offer(match_type=MatchType.INVALID)

    result = selector.select_best_offer([invalid_offer])

    assert result is None


def test_select_best_offer_should_prioritize_higher_confidence_score():
    selector = QuoteSelector()

    lower_confidence = create_matched_offer(total_price_unit=4.0)
    lower_confidence.confidence_score = 0.80

    higher_confidence = create_matched_offer(total_price_unit=6.0)
    higher_confidence.confidence_score = 0.95

    result = selector.select_best_offer([lower_confidence, higher_confidence])

    assert result is higher_confidence


def test_select_best_offer_should_use_lower_price_as_tiebreaker():
    selector = QuoteSelector()

    more_expensive = create_matched_offer(total_price_unit=6.0)
    cheaper = create_matched_offer(total_price_unit=4.0)

    more_expensive.confidence_score = 1.0
    cheaper.confidence_score = 1.0

    result = selector.select_best_offer([more_expensive, cheaper])

    assert result is cheaper