"""Smoke tests for the application service."""

import json

import pytest

from app.services.application_service import ApplicationService

def test_run_should_return_comparison_result_with_expected_scenarios(tmp_path):
    shopping_list_path = tmp_path / "shopping_list.json"
    delivery_fees_path = tmp_path / "delivery_fees.json"
    market_sources_path = tmp_path / "market_sources.json"
    market_a_path = tmp_path / "market_a.json"
    market_b_path = tmp_path / "market_b.json"

    shopping_list_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Arroz Branco",
                    "requested_quantity": 1,
                    "requested_unit": "unit",
                },
                {
                    "item_id": "item-002",
                    "display_name": "Leite Integral",
                    "requested_quantity": 2,
                    "requested_unit": "unit",
                },
            ]
        ),
        encoding="utf-8",
    )

    delivery_fees_path.write_text(
        json.dumps(
            {
                "Market A": 8.0,
                "Market B": 11.0,
            }
        ),
        encoding="utf-8",
    )

    market_a_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Arroz Branco Tipo 1 5kg Camil",
                    "price": 27.9,
                    "size_value": 5,
                    "size_unit": "kg",
                },
                {
                    "original_name": "Leite Integral UHT 1L Italac",
                    "price": 4.99,
                    "size_value": 1,
                    "size_unit": "l",
                },
            ]
        ),
        encoding="utf-8",
    )

    market_b_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Arroz Branco 5 KG Tio Joao",
                    "price": 26.4,
                    "size_value": 5,
                    "size_unit": "kg",
                },
                {
                    "original_name": "Leite UHT Integral Piracanjuba 1 Litro",
                    "price": 5.19,
                    "size_value": 1,
                    "size_unit": "l",
                },
            ]
        ),
        encoding="utf-8",
    )

    market_sources_path.write_text(
        json.dumps(
            [
                {
                    "market_name": "Market A",
                    "file_path": str(market_a_path),
                },
                {
                    "market_name": "Market B",
                    "file_path": str(market_b_path),
                },
            ]
        ),
        encoding="utf-8",
    )

    service = ApplicationService()

    result = service.run(
        shopping_list_path=str(shopping_list_path),
        delivery_fees_path=str(delivery_fees_path),
        market_sources_path=str(market_sources_path),
    )

    assert result.best_single_market is not None
    assert result.best_combined_option is not None
    assert result.best_final_recommendation is not None
    assert len(result.market_quotes) == 2
    assert len(result.summary_notes) > 0


def test_run_should_propagate_file_not_found_error_for_missing_input_file(tmp_path):
    shopping_list_path = tmp_path / "shopping_list.json"
    delivery_fees_path = tmp_path / "delivery_fees.json"

    shopping_list_path.write_text(json.dumps([]), encoding="utf-8")
    delivery_fees_path.write_text(json.dumps({}), encoding="utf-8")

    service = ApplicationService()

    missing_market_sources_path = tmp_path / "missing_market_sources.json"

    with pytest.raises(FileNotFoundError):
        service.run(
            shopping_list_path=str(shopping_list_path),
            delivery_fees_path=str(delivery_fees_path),
            market_sources_path=str(missing_market_sources_path),
        )