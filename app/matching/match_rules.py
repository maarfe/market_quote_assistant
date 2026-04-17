"""Deterministic rules used by the matching engine."""

from app.domain import ProductOffer, ShoppingItem


class MatchRules:
    """
    Encapsulate deterministic rules for evaluating compatibility between
    shopping items and product offers.
    """

    def has_required_name_tokens(
        self,
        shopping_item: ShoppingItem,
        product_offer: ProductOffer,
    ) -> bool:
        """
        Check whether all shopping item tokens are present in the offer tokens.

        Args:
            shopping_item: Normalized shopping item.
            product_offer: Normalized product offer.

        Returns:
            True when all item tokens are found in the offer text, otherwise False.
        """
        item_tokens = self._tokenize(shopping_item.normalized_name)
        offer_tokens = self._tokenize(product_offer.normalized_name)

        return all(token in offer_tokens for token in item_tokens)

    def has_any_name_overlap(
        self,
        shopping_item: ShoppingItem,
        product_offer: ProductOffer,
    ) -> bool:
        """
        Check whether item and offer texts share at least one token.

        Args:
            shopping_item: Normalized shopping item.
            product_offer: Normalized product offer.

        Returns:
            True when there is token overlap, otherwise False.
        """
        item_tokens = set(self._tokenize(shopping_item.normalized_name))
        offer_tokens = set(self._tokenize(product_offer.normalized_name))

        return len(item_tokens.intersection(offer_tokens)) > 0

    def has_compatible_unit(
        self,
        shopping_item: ShoppingItem,
        product_offer: ProductOffer,
    ) -> bool:
        """
        Check whether requested unit and offer unit are directly compatible.

        Args:
            shopping_item: Normalized shopping item.
            product_offer: Normalized product offer.

        Returns:
            True when units are directly compatible, otherwise False.
        """
        requested_unit = shopping_item.requested_unit
        offer_unit = product_offer.size_unit

        if requested_unit == "unit":
            return True

        if offer_unit is None:
            return False

        return requested_unit == offer_unit

    def is_offer_available(self, product_offer: ProductOffer) -> bool:
        """
        Check whether the offer is available.

        Args:
            product_offer: Product offer being evaluated.

        Returns:
            True when the offer is available, otherwise False.
        """
        return product_offer.available

    def _tokenize(self, text: str) -> list[str]:
        """
        Split a normalized text into tokens.

        Args:
            text: Input normalized text.

        Returns:
            A list of tokens.
        """
        return [token for token in text.split(" ") if token]