from dataclasses import dataclass


@dataclass(slots=True)
class MarketCoverage:
    """
    Represents delivery coverage status for a market.
    """

    provider: str
    market_name: str
    is_covered: bool
    supports_delivery: bool
    supports_pickup: bool
    coverage_status: str  # covered | not_covered | unknown