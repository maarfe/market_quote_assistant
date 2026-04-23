from __future__ import annotations

import csv
from pathlib import Path

from app.core.presentation.models import RunResult


class CsvExporter:
    """
    Responsável por exportar um CSV resumido e fácil de comparar no Excel.
    """

    def __init__(self, output_path: str = "data/market_comparison.csv") -> None:
        self.output_path = Path(output_path)

    def export(self, run_result: RunResult) -> None:
        """
        Salva um CSV achatado com uma linha por oferta.
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with self.output_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "market",
                    "item_name",
                    "product_name",
                    "brand",
                    "price",
                    "shipping_price",
                    "delivery_estimate",
                    "offer_count",
                    "available_quantity",
                    "product_url",
                ],
            )
            writer.writeheader()

            for market_result in run_result.markets:
                for item_result in market_result.items:
                    if not item_result.offers:
                        writer.writerow(
                            {
                                "market": market_result.market_name,
                                "item_name": item_result.item_name,
                                "product_name": "",
                                "brand": "",
                                "price": "",
                                "shipping_price": market_result.shipping.price,
                                "delivery_estimate": market_result.shipping.delivery_estimate or "",
                                "offer_count": item_result.offer_count,
                                "available_quantity": "",
                                "product_url": "",
                            }
                        )
                        continue

                    for offer in item_result.offers:
                        writer.writerow(
                            {
                                "market": market_result.market_name,
                                "item_name": item_result.item_name,
                                "product_name": offer.product_name,
                                "brand": offer.brand or "",
                                "price": offer.price,
                                "shipping_price": market_result.shipping.price,
                                "delivery_estimate": market_result.shipping.delivery_estimate or "",
                                "offer_count": item_result.offer_count,
                                "available_quantity": offer.available_quantity,
                                "product_url": offer.product_url,
                            }
                        )