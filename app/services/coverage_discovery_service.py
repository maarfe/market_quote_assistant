"""Services for discovering market coverage across providers."""

from app.domain.delivery_address import DeliveryAddress
from app.domain.market_coverage import MarketCoverage
from app.providers.coverage.base_coverage_provider import BaseCoverageProvider


class CoverageDiscoveryService:
    """
    Aggregate coverage results from one or more coverage providers.

    This service is responsible for orchestrating provider calls and exposing
    helper methods for retrieving covered markets in a simplified way.
    """

    def __init__(self, providers: list[BaseCoverageProvider]) -> None:
        """
        Initialize the coverage discovery service.

        Args:
            providers: Coverage providers to be queried during discovery.
        """
        self._providers = providers

    def discover(self, address: DeliveryAddress) -> list[MarketCoverage]:
        """
        Discover market coverage across all configured providers.

        Args:
            address: Delivery address used for coverage discovery.

        Returns:
            A list containing all coverage results returned by the providers.
        """
        results: list[MarketCoverage] = []

        for provider in self._providers:
            results.extend(provider.check_coverage(address))

        return results

    def get_covered_markets(self, address: DeliveryAddress) -> list[str]:
        """
        Return only the names of markets that support home delivery.

        Args:
            address: Delivery address used for coverage discovery.

        Returns:
            A list of covered market names that support delivery.
        """
        coverage_results = self.discover(address)

        return [
            coverage.market_name
            for coverage in coverage_results
            if coverage.is_covered and coverage.supports_delivery
        ]