from app.domain.delivery_address import DeliveryAddress
from app.domain.market_coverage import MarketCoverage
from app.providers.coverage.base_coverage_provider import BaseCoverageProvider


class CoverageDiscoveryService:
    """
    Aggregate coverage results from multiple providers.
    """

    def __init__(self, providers: list[BaseCoverageProvider]) -> None:
        self._providers = providers

    def discover(self, address: DeliveryAddress) -> list[MarketCoverage]:
        """
        Discover coverage across all providers.
        """
        results: list[MarketCoverage] = []

        for provider in self._providers:
            results.extend(provider.check_coverage(address))

        return results

    def get_covered_markets(self, address: DeliveryAddress) -> list[str]:
        """
        Return only markets that support delivery.
        """
        coverage = self.discover(address)

        return [
            c.market_name
            for c in coverage
            if c.is_covered and c.supports_delivery
        ]