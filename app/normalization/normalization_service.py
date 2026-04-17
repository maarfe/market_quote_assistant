"""Services that apply normalization rules to domain models."""

from app.domain import ProductOffer, ShoppingItem
from app.normalization.normalized_data import NormalizedTextData
from app.normalization.text_normalizer import TextNormalizer
from app.normalization.unit_normalizer import UnitNormalizer


class NormalizationService:
    """
    Apply normalization rules to shopping items and product offers.

    This service centralizes normalization orchestration while keeping text
    normalization and unit normalization delegated to specialized components.
    """

    def __init__(self) -> None:
        """Initialize the normalization service dependencies."""
        self._text_normalizer = TextNormalizer()
        self._unit_normalizer = UnitNormalizer()

    def normalize_shopping_item(self, shopping_item: ShoppingItem) -> ShoppingItem:
        """
        Return a normalized copy of a shopping item.

        Args:
            shopping_item: Shopping item to normalize.

        Returns:
            A new shopping item instance with normalized fields.
        """
        normalized_name = self._text_normalizer.normalize(shopping_item.display_name)
        normalized_unit = self._unit_normalizer.normalize_unit(
            shopping_item.requested_unit
        )

        return ShoppingItem(
            item_id=shopping_item.item_id,
            display_name=shopping_item.display_name,
            normalized_name=normalized_name,
            requested_quantity=shopping_item.requested_quantity,
            requested_unit=normalized_unit,
        )

    def normalize_product_offer(self, product_offer: ProductOffer) -> ProductOffer:
        """
        Return a normalized copy of a product offer.

        Args:
            product_offer: Product offer to normalize.

        Returns:
            A new product offer instance with normalized fields.
        """
        normalized_name = self._text_normalizer.normalize(product_offer.original_name)

        normalized_size_value = product_offer.size_value
        normalized_size_unit = product_offer.size_unit

        if product_offer.is_measurable():
            normalized_unit_data = self._unit_normalizer.normalize(
                value=product_offer.size_value,
                unit=product_offer.size_unit,
            )
            normalized_size_value = normalized_unit_data.value
            normalized_size_unit = normalized_unit_data.unit

        return ProductOffer(
            market_name=product_offer.market_name,
            original_name=product_offer.original_name,
            normalized_name=normalized_name,
            price=product_offer.price,
            currency=product_offer.currency,
            available=product_offer.available,
            url=product_offer.url,
            size_value=normalized_size_value,
            size_unit=normalized_size_unit,
            brand=product_offer.brand,
            raw_payload=product_offer.raw_payload,
        )

    def normalize_text(self, text: str) -> NormalizedTextData:
        """
        Return structured normalization data for a raw text.

        Args:
            text: Raw text to normalize.

        Returns:
            A structured normalized text result.
        """
        cleaned_text = self._text_normalizer.clean_text(text)
        canonical_text = self._text_normalizer.normalize(text)

        return NormalizedTextData(
            original_text=text,
            cleaned_text=cleaned_text,
            canonical_text=canonical_text,
        )