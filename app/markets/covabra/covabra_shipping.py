from __future__ import annotations

from typing import Any

from app.core.entities.shipping_info import ShippingInfo


def parse_shipping_response(response_json: dict[str, Any]) -> ShippingInfo:
    """
    Extrai informações de frete e prazo de entrega a partir do response
    do endpoint de simulation do Covabra.

    Estratégia:
    - percorre logisticsInfo[].slas[]
    - considera apenas SLAs com deliveryChannel == "delivery"
    - escolhe a melhor opção disponível com menor preço
    - tenta aproveitar textos mais amigáveis quando existirem
    - fallback defensivo para None quando os campos não estiverem presentes
    """
    try:
        logistics_info = response_json.get("logisticsInfo")
        if not isinstance(logistics_info, list):
            return ShippingInfo(
                price=None,
                delivery_estimate=None,
                raw_text=None,
            )

        selected_price: float | None = None
        selected_estimate: str | None = None
        selected_raw_text: str | None = None

        for entry in logistics_info:
            if not isinstance(entry, dict):
                continue

            slas = entry.get("slas")
            if not isinstance(slas, list):
                continue

            for sla in slas:
                if not isinstance(sla, dict):
                    continue

                delivery_channel = str(sla.get("deliveryChannel", "")).strip().lower()
                if delivery_channel != "delivery":
                    continue

                price = _parse_price(sla.get("price"))
                estimate = _extract_delivery_estimate(sla)

                if selected_price is None:
                    selected_price = price
                    selected_estimate = estimate
                    selected_raw_text = _build_raw_text(price, estimate)
                    continue

                if price is not None and (
                    selected_price is None or price < selected_price
                ):
                    selected_price = price
                    selected_estimate = estimate
                    selected_raw_text = _build_raw_text(price, estimate)

        return ShippingInfo(
            price=selected_price,
            delivery_estimate=selected_estimate,
            raw_text=selected_raw_text,
        )

    except Exception:
        return ShippingInfo(
            price=None,
            delivery_estimate=None,
            raw_text=None,
        )


def _parse_price(value: Any) -> float | None:
    """
    Converte o preço do SLA para float.

    Em VTEX, price costuma vir em centavos.
    """
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None

    if parsed >= 100:
        return parsed / 100

    return parsed


def _extract_delivery_estimate(sla: dict[str, Any]) -> str | None:
    """
    Tenta obter a melhor representação possível do prazo.

    Ordem de preferência:
    - shippingEstimateDate
    - friendlyName
    - name
    - shippingEstimate
    """
    for key in ("shippingEstimateDate", "friendlyName", "name", "shippingEstimate"):
        value = sla.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _build_raw_text(price: float | None, estimate: str | None) -> str | None:
    parts: list[str] = []

    if price is not None:
        parts.append(f"Frete: R$ {price:.2f}")

    if estimate:
        parts.append(f"Prazo: {estimate}")

    if not parts:
        return None

    return " | ".join(parts)