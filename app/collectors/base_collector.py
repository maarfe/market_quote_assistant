"""Base contract for market collectors."""

from abc import ABC, abstractmethod

from app.domain import ProductOffer


class BaseCollector(ABC):
    """
    Defines the contract for market data collectors.

    A collector is responsible for retrieving product offers from a specific
    source and converting them into domain objects.
    """

    @abstractmethod
    def collect_offers(self) -> list[ProductOffer]:
        """
        Collect product offers from the configured source.

        Returns:
            A list of product offers retrieved from the source.
        """
        raise NotImplementedError