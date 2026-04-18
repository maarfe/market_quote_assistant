"""Unit tests for the shopping list service."""

import json

import pytest

from app.services.shopping_list_service import ShoppingListService
from app.shared import InvalidShoppingListError


def test_load_from_file_should_return_shopping_items(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Arroz Branco",
                    "requested_quantity": 2,
                    "requested_unit": "unit",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = service.load_from_file(file_path)

    assert len(result) == 1
    assert result[0].item_id == "item-001"
    assert result[0].display_name == "Arroz Branco"
    assert result[0].requested_quantity == 2.0
    assert result[0].requested_unit == "unit"


def test_load_from_file_should_raise_error_when_payload_is_not_a_list(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps({"invalid": True}),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_required_fields_are_missing(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "display_name": "Arroz Branco",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_item_id_is_empty(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "",
                    "display_name": "Arroz Branco",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_display_name_is_empty(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_requested_quantity_is_not_positive(tmp_path):
    service = ShoppingListService()

    file_path = tmp_path / "shopping_list.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Arroz Branco",
                    "requested_quantity": 0,
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)