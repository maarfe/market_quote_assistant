"""Abstract contract for market coverage providers."""

from abc import ABC, abstractmethod

from app.domain.delivery_address import DeliveryAddress
from app.domain.market_coverage import MarketCoverage


class BaseCoverageProvider(ABC):
    """
    Define the contract for providers that can determine market coverage.

    Coverage providers are responsible for evaluating whether one or more
    markets support delivery or pickup for a given delivery address.
    """

    @abstractmethod
    def check_coverage(self, address: DeliveryAddress) -> list[MarketCoverage]:
        """
        Determine coverage results for the given delivery address.

        Args:
            address: Delivery address to evaluate.

        Returns:
            A list of coverage results returned by the provider.
        """