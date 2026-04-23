from __future__ import annotations

from dataclasses import dataclass, field

from app.core.entities.coverage import CoverageResult
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shipping_info import ShippingInfo


@dataclass
class ItemResult:
    """
    Representa o resultado consolidado de um item para um mercado.
    """

    item_name: str
    offers: list[ProductOffer] = field(default_factory=list)

    @property
    def offer_count(self) -> int:
        """
        Retorna a quantidade de ofertas válidas encontradas para o item.
        """
        return len(self.offers)

    @property
    def lowest_price(self) -> float | None:
        """
        Retorna o menor preço entre as ofertas válidas do item.
        """
        if not self.offers:
            return None
        return min(offer.price for offer in self.offers)


@dataclass
class MarketResult:
    """
    Representa o resultado consolidado de um mercado na execução.
    """

    market_name: str
    coverage: CoverageResult
    shipping: ShippingInfo
    items: list[ItemResult] = field(default_factory=list)


@dataclass
class RunResult:
    """
    Representa o resultado completo da execução multi-mercado.
    """

    markets: list[MarketResult] = field(default_factory=list)