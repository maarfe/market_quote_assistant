"""Application orchestration service for the Market Quote Assistant project."""

from app.collectors import JsonMarketCollector, SavegnagoOfferCollector
from app.comparison import ComparisonService
from app.matching import MatchingService
from app.normalization import NormalizationService
from app.providers.coverage.savegnago_coverage_provider import (
    SavegnagoCoverageProvider,
)
from app.services.coverage_discovery_service import CoverageDiscoveryService
from app.services.delivery_address_service import DeliveryAddressService
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
        self._delivery_address_service = DeliveryAddressService()

    def run(
        self,
        shopping_list_path: str,
        delivery_fees_path: str,
        market_sources_path: str,
        delivery_address_path: str | None = None,
    ):
        """
        Execute the full quote comparison workflow.

        Args:
            shopping_list_path: Path to the shopping list JSON file.
            delivery_fees_path: Path to the delivery fee JSON file.
            market_sources_path: Path to the market sources JSON file.
            delivery_address_path: Optional path to the user's address JSON file.

        Returns:
            A comparison result produced by the comparison engine.
        """
        delivery_address = None
        if delivery_address_path:
            delivery_address = self._delivery_address_service.load_from_file(
                delivery_address_path
            )

            coverage_service = CoverageDiscoveryService(
                providers=[SavegnagoCoverageProvider()]
            )
            covered_markets = coverage_service.get_covered_markets(delivery_address)

            print(
                f"Covered markets for {delivery_address.postal_code}: "
                f"{covered_markets}"
            )

        shopping_items = self._shopping_list_service.load_from_file(shopping_list_path)
        delivery_fees = self._delivery_fee_service.load_from_file(delivery_fees_path)
        market_sources = self._market_source_service.load_from_file(
            market_sources_path
        )

        normalized_items = [
            self._normalization_service.normalize_shopping_item(shopping_item)
            for shopping_item in shopping_items
        ]

        collectors = []

        collectors.extend(
            JsonMarketCollector(
                market_name=market_source.market_name,
                file_path=market_source.file_path,
            )
            for market_source in market_sources
        )

        if delivery_address:
            search_terms = list(
                {
                    item.display_name.strip()
                    for item in shopping_items
                    if item.display_name.strip()
                }
            )

            collectors.append(
                SavegnagoOfferCollector(
                    search_terms=search_terms,
                )
            )

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