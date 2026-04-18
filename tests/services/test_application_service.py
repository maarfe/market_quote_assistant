"""Smoke tests for the application service."""

import json

import pytest

from app.services.application_service import ApplicationService
from tests.factories import (
    create_delivery_fees_file,
    create_market_data_file,
    create_market_sources_file,
    create_shopping_list_file,
)


def test_run_should_return_comparison_result_with_expected_scenarios(tmp_path):
    shopping_list_path = create_shopping_list_file(
        tmp_path,
        payload=[
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
        ],
    )

    delivery_fees_path = create_delivery_fees_file(
        tmp_path,
        payload={
            "Market A": 8.0,
            "Market B": 11.0,
        },
    )

    market_a_path = create_market_data_file(
        tmp_path,
        filename="market_a.json",
        payload=[
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
        ],
    )

    market_b_path = create_market_data_file(
        tmp_path,
        filename="market_b.json",
        payload=[
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
        ],
    )

    market_sources_path = create_market_sources_file(
        tmp_path,
        payload=[
            {
                "market_name": "Market A",
                "file_path": str(market_a_path),
            },
            {
                "market_name": "Market B",
                "file_path": str(market_b_path),
            },
        ],
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
    shopping_list_path = create_shopping_list_file(tmp_path, payload=[])
    delivery_fees_path = create_delivery_fees_file(tmp_path, payload={})

    service = ApplicationService()

    with pytest.raises(FileNotFoundError):
        service.run(
            shopping_list_path=str(shopping_list_path),
            delivery_fees_path=str(delivery_fees_path),
            market_sources_path=str(tmp_path / "missing_market_sources.json"),
        )