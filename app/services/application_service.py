"""Application orchestration service for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector
from app.comparison import ComparisonService
from app.matching import MatchingService
from app.normalization import NormalizationService
from app.services.delivery_fee_service import DeliveryFeeService
from app.services.market_source_service import MarketSourceService
from app.services.shopping_list_service import ShoppingListService


class ApplicationService:
    """
    Orchestrate the end-to-end quote comparison workflow.
    """

    def __init__(self) -> None:
        """Initialize application service dependencies."""
        self._shopping_list_service = ShoppingListService()
        self._delivery_fee_service = DeliveryFeeService()
        self._market_source_service = MarketSourceService()
        self._normalization_service = NormalizationService()
        self._matching_service = MatchingService()
        self._comparison_service = ComparisonService()

    def run(
        self,
        shopping_list_path: str,
        delivery_fees_path: str,
        market_sources_path: str,
    ):
        """
        Execute the full quote comparison workflow.

        Args:
            shopping_list_path: Path to the shopping list JSON file.
            delivery_fees_path: Path to the delivery fee JSON file.
            market_sources_path: Path to the market sources JSON file.

        Returns:
            A comparison result produced by the comparison engine.
        """
        shopping_items = self._shopping_list_service.load_from_file(shopping_list_path)
        delivery_fees = self._delivery_fee_service.load_from_file(delivery_fees_path)
        market_sources = self._market_source_service.load_from_file(
            market_sources_path
        )

        normalized_items = [
            self._normalization_service.normalize_shopping_item(shopping_item)
            for shopping_item in shopping_items
        ]

        collectors = [
            JsonMarketCollector(
                market_name=market_source.market_name,
                file_path=market_source.file_path,
            )
            for market_source in market_sources
        ]

        normalized_offers = []
        for collector in collectors:
            offers = collector.collect_offers()
            normalized_offers.extend(
                self._normalization_service.normalize_product_offer(offer)
                for offer in offers
            )

        matched_offers = []
        for shopping_item in normalized_items:
            matched_offers.extend(
                self._matching_service.match_offers(
                    shopping_item=shopping_item,
                    product_offers=normalized_offers,
                )
            )

        return self._comparison_service.compare_quotes(
            shopping_items=normalized_items,
            matched_offers=matched_offers,
            delivery_fees=delivery_fees,
        )