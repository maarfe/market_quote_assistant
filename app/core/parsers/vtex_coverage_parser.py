from __future__ import annotations

from typing import Any

from app.core.entities.coverage import CoverageResult, CoverageStatus


def parse_vtex_coverage_response(response_json: dict[str, Any]) -> CoverageResult:
    """
    Interpreta a resposta do endpoint VTEX de simulation.

    Regras:
    - COVERED: existe logisticsInfo[].slas[] com deliveryChannel == "delivery"
    - NOT_COVERED: slas vazio e availability == "withoutStock"
    - UNKNOWN: qualquer ambiguidade, estrutura inesperada ou erro de parsing
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