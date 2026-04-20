from abc import ABC, abstractmethod

from app.core.entities.address import Address
from app.core.entities.coverage import CoverageResult
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shopping_item import ShoppingItem


class MarketClient(ABC):
    @abstractmethod
    def get_market_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def check_coverage(self, address: Address) -> CoverageResult:
        raise NotImplementedError

    @abstractmethod
    def search_products(self, item: ShoppingItem, address: Address) -> list[ProductOffer]:
        raise NotImplementedError