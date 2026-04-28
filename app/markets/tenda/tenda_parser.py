from __future__ import annotations

from typing import Any

from app.core.entities.coverage import CoverageResult, CoverageStatus
from app.core.entities.product_offer import ProductOffer
from app.core.entities.shipping_info import ShippingInfo

TENDA_MARKET_NAME = "Tenda"


def parse_coverage_response(response_json: dict[str, Any]) -> CoverageResult:
    """
    Interpreta coverage do endpoint shipping-options do Tenda.
    """
    try:
        delivery = response_json.get("delivery")

        if not isinstance(delivery, dict):
            return CoverageResult(status=CoverageStatus.UNKNOWN, has_delivery=False)

        available = delivery.get("available")

        if available is True:
            return CoverageResult(status=CoverageStatus.COVERED, has_delivery=True)

        if available is False:
            return CoverageResult(status=CoverageStatus.NOT_COVERED, has_delivery=False)

        return CoverageResult(status=CoverageStatus.UNKNOWN, has_delivery=False)

    except Exception:
        return CoverageResult(status=CoverageStatus.UNKNOWN, has_delivery=False)


def parse_shipping_response(response_json: dict[str, Any]) -> ShippingInfo:
    """
    Extrai frete e prazo do response de shipping-options do Tenda.
    """
    try:
        delivery = response_json.get("delivery")

        if not isinstance(delivery, dict):
            return ShippingInfo(price=None, delivery_estimate=None, raw_text=None)

        price = _parse_float(delivery.get("price"))
        minimum_date = delivery.get("minimumDate")
        expected_days = delivery.get("expectedDeliveryDays")

        delivery_estimate = None
        if isinstance(minimum_date, str) and minimum_date.strip():
            delivery_estimate = minimum_date.strip()
        elif expected_days is not None:
            delivery_estimate = f"{expected_days} dias úteis"

        raw_parts = []

        if price is not None:
            raw_parts.append(f"Frete: R$ {price:.2f}")

        if delivery_estimate:
            raw_parts.append(f"Prazo: {delivery_estimate}")

        return ShippingInfo(
            price=price,
            delivery_estimate=delivery_estimate,
            raw_text=" | ".join(raw_parts) if raw_parts else None,
        )

    except Exception:
        return ShippingInfo(price=None, delivery_estimate=None, raw_text=None)


def parse_products_response(response_json: dict[str, Any]) -> list[ProductOffer]:
    """
    Interpreta produtos retornados por /api/public/store/search.
    """
    offers: list[ProductOffer] = []

    products = response_json.get("products")
    if not isinstance(products, list):
        return []

    for product in products:
        if not isinstance(product, dict):
            continue

        if str(product.get("availability", "")).lower() != "in_stock":
            continue

        if product.get("deliveryAvailable") is False:
            continue

        product_name = product.get("name")
        product_url = product.get("url")
        price = _parse_float(product.get("price"))

        if not product_name or not product_url or price is None:
            continue

        available_quantity = _parse_int(product.get("totalStock")) or 0

        offers.append(
            ProductOffer(
                market_name=TENDA_MARKET_NAME,
                product_name=str(product_name).strip(),
                brand=str(product.get("brand")).strip() if product.get("brand") else None,
                product_url=_normalize_product_url(str(product_url)),
                price=price,
                available_quantity=available_quantity,
            )
        )

    return offers


def _normalize_product_url(url: str) -> str:
    normalized = url.strip()

    if normalized.startswith("http://") or normalized.startswith("https://"):
        return normalized

    if normalized.startswith("//"):
        return f"https:{normalized}"

    if not normalized.startswith("/"):
        normalized = f"/{normalized}"

    return f"https://www.tendaatacado.com.br{normalized}"


def _parse_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None