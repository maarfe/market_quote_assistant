from app.core.entities.shopping_item import ShoppingItem
from app.core.entities.product_offer import ProductOffer


def filter_offers(item: ShoppingItem, offers: list[ProductOffer]) -> list[ProductOffer]:
    filtered = offers

    # 1. brand
    if item.preferred_brand:
        brand = item.preferred_brand.lower()
        filtered = [
            o for o in filtered
            if o.brand and brand in o.brand.lower()
        ]
        if not filtered:
            return []

    # 2. exclude_terms (NOVO)
    if item.exclude_terms:
        filtered = _filter_exclusions(filtered, item.exclude_terms)

    # 3. type (opcional, pode até ignorar por enquanto)
    if item.preferred_type:
        filtered = [
            o for o in filtered
            if _is_type_match(o.product_name, item.preferred_type)
        ]

    return filtered


def _filter_exclusions(
    offers: list[ProductOffer],
    exclude_terms: list[str],
) -> list[ProductOffer]:

    terms = [t.lower() for t in exclude_terms]

    return [
        offer
        for offer in offers
        if not any(term in offer.product_name.lower() for term in terms)
    ]


def _is_type_match(product_name: str, preferred_type: str) -> bool:
    name = product_name.lower()

    # match direto
    if preferred_type in name:
        return True

    # match simples por palavras
    words = preferred_type.split()
    return all(word in name for word in words)