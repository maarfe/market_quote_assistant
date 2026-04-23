from __future__ import annotations

import json
from pathlib import Path

from app.core.presentation.models import RunResult


class JsonExporter:
    """
    Responsável por exportar o resultado consolidado da execução em JSON.
    """

    def __init__(self, output_path: str = "data/last_run.json") -> None:
        self.output_path = Path(output_path)

    def export(self, run_result: RunResult) -> None:
        """
        Salva em JSON o resultado completo da execução.
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "markets": [
                {
                    "market_name": market_result.market_name,
                    "coverage": {
                        "status": market_result.coverage.status.value,
                        "has_delivery": market_result.coverage.has_delivery,
                    },
                    "shipping": {
                        "price": market_result.shipping.price,
                        "delivery_estimate": market_result.shipping.delivery_estimate,
                        "raw_text": market_result.shipping.raw_text,
                    },
                    "items": [
                        {
                            "item_name": item_result.item_name,
                            "offer_count": item_result.offer_count,
                            "lowest_price": item_result.lowest_price,
                            "offers": [
                                {
                                    "market_name": offer.market_name,
                                    "product_name": offer.product_name,
                                    "brand": offer.brand,
                                    "product_url": offer.product_url,
                                    "price": offer.price,
                                    "available_quantity": offer.available_quantity,
                                }
                                for offer in item_result.offers
                            ],
                        }
                        for item_result in market_result.items
                    ],
                }
                for market_result in run_result.markets
            ]
        }

        with self.output_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)