from dataclasses import dataclass


@dataclass
class ProductOffer:
    market_name: str
    product_name: str
    brand: str | None
    product_url: str
    price: float
    available_quantity: int