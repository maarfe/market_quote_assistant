"""Domain package for the Market Quote Assistant project."""

from app.domain.comparison_result import ComparisonResult
from app.domain.market_quote import MarketQuote
from app.domain.matched_offer import MatchedOffer
from app.domain.product_offer import ProductOffer
from app.domain.shopping_item import ShoppingItem
from app.domain.types import MatchType

__all__ = [
    "ComparisonResult",
    "MarketQuote",
    "MatchedOffer",
    "MatchType",
    "ProductOffer",
    "ShoppingItem",
]