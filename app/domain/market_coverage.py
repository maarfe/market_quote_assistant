"""Domain model for market delivery coverage results."""

from dataclasses import dataclass


@dataclass(slots=True)
class MarketCoverage:
    """
    Represent the delivery coverage status of a market provider.

    Attributes:
        provider: Technical or logical provider identifier.
        market_name: Human-readable market name.
        is_covered: Whether the market delivers to the provided address.
        supports_delivery: Whether home delivery is supported.
        supports_pickup: Whether store pickup is supported.
        coverage_status: Coverage classification, such as
            'covered', 'not_covered', or 'unknown'.
    """

    provider: str
    market_name: str
    is_covered: bool
    supports_delivery: bool
    supports_pickup: bool
    coverage_status: str