from app.core.entities.shopping_item import ShoppingItem
from app.core.entities.product_offer import ProductOffer
from app.core.text.text_normalizer import TextNormalizer


def filter_offers(item: ShoppingItem, offers: list[ProductOffer]) -> list[ProductOffer]:
    filtered = offers

    preferred_brand = TextNormalizer.normalize(item.preferred_brand)
    preferred_types = _normalize_preferred_types(item.preferred_type)
    exclude_terms = [
        TextNormalizer.normalize(term)
        for term in (item.exclude_terms or [])
        if isinstance(term, str) and term.strip()
    ]

    # 1. brand
    if preferred_brand:
        filtered = [
            offer
            for offer in filtered
            if preferred_brand in _build_search_text(offer)
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


def _normalize_preferred_types(preferred_type: str | list[str] | None) -> list[str]:
    if not preferred_type:
        return []

    if isinstance(preferred_type, str):
        normalized = TextNormalizer.normalize(preferred_type)
        return [normalized] if normalized else []

    if isinstance(preferred_type, list):
        terms: list[str] = []

        for value in preferred_type:
            if not isinstance(value, str):
                continue

            normalized = TextNormalizer.normalize(value)
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