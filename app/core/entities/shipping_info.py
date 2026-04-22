from dataclasses import dataclass


@dataclass
class ShippingInfo:
    """
    Representa informações de entrega de um mercado.
    """

    price: float | None
    delivery_estimate: str | None
    raw_text: str | None = None