from __future__ import annotations

from typing import Any

from app.core.entities.product_offer import ProductOffer


def parse_vtex_products_response(
    response_json: dict[str, Any],
    market_name: str,
    base_url: str,
) -> list[ProductOffer]:
    """
    Interpreta a resposta do GraphQL VTEX productSearchV3.

    Regras:
    - caminho esperado: data.productSearch.products
    - considerar somente itens com AvailableQuantity > 0
    - parsing defensivo, ignorando produtos quebrados
    """
    offers: list[ProductOffer] = []

    try:
        products = (
            response_json.get("data", {})
            .get("productSearch", {})
            .get("products", [])
        )

        if not isinstance(products, list):
            return []

        for product in products:
            if not isinstance(product, dict):
                continue

            product_name = product.get("productName")
            brand = product.get("brand")
            link = product.get("link")

            items = product.get("items")
            if not isinstance(items, list) or not items:
                continue

            selected_item = None

            for item in items:
                if not isinstance(item, dict):
                    continue

                sellers = item.get("sellers")
                if not isinstance(sellers, list) or not sellers:
                    continue

                first_seller = sellers[0]
                if not isinstance(first_seller, dict):
                    continue

                commercial_offer = first_seller.get("commertialOffer", {})
                if not isinstance(commercial_offer, dict):
                    continue

                available_quantity = commercial_offer.get("AvailableQuantity", 0)

                try:
                    available_quantity = int(available_quantity)
                except (TypeError, ValueError):
                    available_quantity = 0

                if available_quantity > 0:
                    selected_item = {
                        "item": item,
                        "seller": first_seller,
                        "commercial_offer": commercial_offer,
                        "available_quantity": available_quantity,
                    }
                    break

            if not selected_item:
                continue

            commercial_offer = selected_item["commercial_offer"]
            price = commercial_offer.get("Price")

            try:
                price = float(price)
            except (TypeError, ValueError):
                continue

            if not product_name or not link:
                continue

            offers.append(
                ProductOffer(
                    market_name=market_name,
                    product_name=str(product_name).strip(),
                    brand=str(brand).strip() if brand else None,
                    product_url=build_product_url(
                        link=str(link),
                        base_url=base_url,
                    ),
                    price=price,
                    available_quantity=selected_item["available_quantity"],
                )
            )

        return offers

    except Exception:
        return []


def build_product_url(link: str, base_url: str) -> str:
    """
    Normaliza o link do produto retornado pela API.
    """
    normalized_link = link.strip()

    if not normalized_link:
        return ""

    if normalized_link.startswith("http://") or normalized_link.startswith("https://"):
        return normalized_link

    if not normalized_link.startswith("/"):
        normalized_link = f"/{normalized_link}"

    return f"{base_url}{normalized_link}"