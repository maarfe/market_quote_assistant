from app.core.entities.shopping_item import ShoppingItem
from app.core.entities.product_offer import ProductOffer
from app.core.text.text_normalizer import TextNormalizer


def filter_offers(item: ShoppingItem, offers: list[ProductOffer]) -> list[ProductOffer]:
    filtered = offers

    preferred_brands = _normalize_terms(item.preferred_brand)
    preferred_types = _normalize_terms(item.preferred_type)
    exclude_terms = _normalize_terms(item.exclude_terms)

    # 1. brand
    if preferred_brands:
        filtered = [
            offer
            for offer in filtered
            if any(brand in _build_search_text(offer) for brand in preferred_brands)
        ]
        if not filtered:
            return []

    # 2. exclude_terms
    if exclude_terms:
        filtered = _filter_exclusions(filtered, exclude_terms)

    # 3. type
    if preferred_types:
        filtered = [
            offer
            for offer in filtered
            if _is_type_match(offer, preferred_types)
        ]

    return filtered


def _build_search_text(offer: ProductOffer) -> str:
    combined = f"{offer.product_name} {offer.brand or ''}"
    return TextNormalizer.normalize(combined)


def _normalize_terms(value: str | list[str] | None) -> list[str]:
    if not value:
        return []

    if isinstance(value, str):
        normalized = TextNormalizer.normalize(value)
        return [normalized] if normalized else []

    if isinstance(value, list):
        terms: list[str] = []

        for item in value:
            if not isinstance(item, str):
                continue

            normalized = TextNormalizer.normalize(item)
            if normalized:
                terms.append(normalized)

        return terms

    return []


def _filter_exclusions(
    offers: list[ProductOffer],
    exclude_terms: list[str],
) -> list[ProductOffer]:
    return [
        offer
        for offer in offers
        if not any(term in _build_search_text(offer) for term in exclude_terms)
    ]


def _is_type_match(offer: ProductOffer, preferred_types: list[str]) -> bool:
    text = _build_search_text(offer)

    return any(_matches_term(text, preferred_type) for preferred_type in preferred_types)


def _matches_term(text: str, preferred_type: str) -> bool:
    if preferred_type in text:
        return True

    words = preferred_type.split()
    return all(word in text for word in words)