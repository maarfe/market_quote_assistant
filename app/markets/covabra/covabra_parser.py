from __future__ import annotations

from typing import Any

from app.core.entities.coverage import CoverageResult, CoverageStatus
from app.core.entities.product_offer import ProductOffer


def parse_coverage_response(response_json: dict[str, Any]) -> CoverageResult:
    """
    Interpreta a resposta do endpoint de simulation do Covabra.

    Regra inicial:
    - COVERED: existe logisticsInfo[].slas[] com deliveryChannel == "delivery"
    - NOT_COVERED: slas vazio E availability == "withoutStock"
    - UNKNOWN: qualquer ambiguidade, estrutura inesperada ou erro de parsing

    Observação:
    - essa regra ainda precisa ser validada depois com um CEP claramente não coberto
    """
    try:
        logistics_info = response_json.get("logisticsInfo")

        if not isinstance(logistics_info, list):
            return CoverageResult(
                status=CoverageStatus.UNKNOWN,
                has_delivery=False,
            )

        found_delivery = False
        found_without_stock_and_empty_slas = False

        for entry in logistics_info:
            if not isinstance(entry, dict):
                continue

            slas = entry.get("slas")
            availability = entry.get("availability")

            if isinstance(slas, list):
                for sla in slas:
                    if not isinstance(sla, dict):
                        continue

                    delivery_channel = str(sla.get("deliveryChannel", "")).strip().lower()
                    if delivery_channel == "delivery":
                        found_delivery = True
                        break

            if found_delivery:
                break

            if isinstance(slas, list) and len(slas) == 0 and availability == "withoutStock":
                found_without_stock_and_empty_slas = True

        if found_delivery:
            return CoverageResult(
                status=CoverageStatus.COVERED,
                has_delivery=True,
            )

        if found_without_stock_and_empty_slas:
            return CoverageResult(
                status=CoverageStatus.NOT_COVERED,
                has_delivery=False,
            )

        return CoverageResult(
            status=CoverageStatus.UNKNOWN,
            has_delivery=False,
        )

    except Exception:
        return CoverageResult(
            status=CoverageStatus.UNKNOWN,
            has_delivery=False,
        )


def parse_products_response(response_json: dict[str, Any]) -> list[ProductOffer]:
    """
    Interpreta a resposta do GraphQL productSearchV3 do Covabra.

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
                    market_name="Covabra",
                    product_name=str(product_name).strip(),
                    brand=str(brand).strip() if brand else None,
                    product_url=_build_product_url(str(link)),
                    price=price,
                    available_quantity=selected_item["available_quantity"],
                )
            )

        return offers

    except Exception:
        return []


def _build_product_url(link: str) -> str:
    link = link.strip()

    if not link:
        return ""

    if link.startswith("http://") or link.startswith("https://"):
        return link

    if not link.startswith("/"):
        link = f"/{link}"

    return f"https://www.covabra.com.br{link}"