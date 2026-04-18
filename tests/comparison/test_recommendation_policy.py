"""Unit tests for the recommendation policy."""

from app.comparison.recommendation_policy import (
    RecommendationPolicy,
    RecommendationPolicyConfig,
)
from app.domain.market_quote import MarketQuote


def test_should_select_combined_option_when_savings_exceed_threshold():
    policy = RecommendationPolicy(
        RecommendationPolicyConfig(minimum_savings_to_split=8.0)
    )

    best_single_market = MarketQuote(
        market_name="Market A",
        delivery_fee=0.0,
    )

    # simula um custo alto no single market
    best_single_market.selected_offers = []
    best_single_market._subtotal = 60.0

    best_combined_option = {
        "total_cost": 40.0,
        "full_coverage": True,
        "market_count": 2,
        "used_markets": ["Market A", "Market B"],
    }

    result = policy.select_recommendation(
        best_single_market=best_single_market,
        best_combined_option=best_combined_option,
    )

    assert result is not None
    assert result["strategy"] == "best_combined_option"

def test_should_select_single_market_when_combined_is_more_expensive():
    policy = RecommendationPolicy(
        RecommendationPolicyConfig(minimum_savings_to_split=8.0)
    )

    best_single_market = MarketQuote(
        market_name="Market A",
        delivery_fee=0.0,
    )
    best_single_market.selected_offers = []
    best_single_market.delivery_fee = 0.0

    best_combined_option = {
        "total_cost": 68.38,
        "full_coverage": True,
        "market_count": 2,
        "used_markets": ["Market A", "Market B"],
    }

    # force total_cost through selected offers + fee model
    best_single_market.delivery_fee = 58.88

    result = policy.select_recommendation(
        best_single_market=best_single_market,
        best_combined_option=best_combined_option,
    )

    assert result is not None
    assert result["strategy"] == "best_single_market"
    assert "costs R$" in result["reason"]


def test_should_select_single_market_when_combined_savings_are_below_threshold():
    policy = RecommendationPolicy(
        RecommendationPolicyConfig(minimum_savings_to_split=8.0)
    )

    best_single_market = MarketQuote(
        market_name="Market A",
        delivery_fee=50.0,
    )
    best_single_market.selected_offers = []

    best_combined_option = {
        "total_cost": 45.0,
        "full_coverage": True,
        "market_count": 2,
        "used_markets": ["Market A", "Market B"],
    }

    result = policy.select_recommendation(
        best_single_market=best_single_market,
        best_combined_option=best_combined_option,
    )

    assert result is not None
    assert result["strategy"] == "best_single_market"
    assert "does not justify splitting" in result["reason"]