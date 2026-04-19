"""Mock implementation of a market coverage provider."""

from app.domain.delivery_address import DeliveryAddress
from app.domain.market_coverage import MarketCoverage
from app.providers.coverage.base_coverage_provider import BaseCoverageProvider


class MockCoverageProvider(BaseCoverageProvider):
    """
    Simulate market coverage results for local development and testing.

    This provider returns deterministic mock data and is useful while the
    project is still preparing the first real-world coverage integrations.
    """

    def check_coverage(self, address: DeliveryAddress) -> list[MarketCoverage]:
        """
        Return mock coverage results for the provided address.

        Args:
            address: Delivery address used as coverage input.

        Returns:
            A list of mock market coverage results.
        """
        return [
            MarketCoverage(
                provider="mock",
                market_name="Market A",
                is_covered=True,
                supports_delivery=True,
                supports_pickup=True,
                coverage_status="covered",
            ),
            MarketCoverage(
                provider="mock",
                market_name="Market B",
                is_covered=True,
                supports_delivery=True,
                supports_pickup=False,
                coverage_status="covered",
            ),
            MarketCoverage(
                provider="mock",
                market_name="Market C",
                is_covered=False,
                supports_delivery=False,
                supports_pickup=False,
                coverage_status="not_covered",
            ),
        ]