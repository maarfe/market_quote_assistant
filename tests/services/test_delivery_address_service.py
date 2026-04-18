"""Unit tests for the delivery address service."""

import json

import pytest

from app.services.delivery_address_service import DeliveryAddressService
from app.shared import InvalidShoppingListError


def test_load_from_file_should_return_delivery_address(tmp_path):
    service = DeliveryAddressService()

    file_path = tmp_path / "delivery_address.json"
    file_path.write_text(
        json.dumps(
            {
                "label": "casa",
                "recipient_name": "Matheus Felipe",
                "street": "Rua Presbítero Evangelista do Nascimento Oliveira",
                "number": "544",
                "complement": "Bloco 7 Apto 14",
                "neighborhood": "Residencial Novo Tempo",
                "city": "Campinas",
                "state": "SP",
                "postal_code": "13056-682",
                "country": "BR",
            }
        ),
        encoding="utf-8",
    )

    result = service.load_from_file(file_path)

    assert result.label == "casa"
    assert result.recipient_name == "Matheus Felipe"
    assert result.street == "Rua Presbítero Evangelista do Nascimento Oliveira"
    assert result.number == "544"
    assert result.complement == "Bloco 7 Apto 14"
    assert result.neighborhood == "Residencial Novo Tempo"
    assert result.city == "Campinas"
    assert result.state == "SP"
    assert result.postal_code == "13056-682"
    assert result.country == "BR"


def test_load_from_file_should_raise_error_when_payload_is_not_a_dict(tmp_path):
    service = DeliveryAddressService()

    file_path = tmp_path / "delivery_address.json"
    file_path.write_text(
        json.dumps(["invalid"]),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_required_fields_are_missing(tmp_path):
    service = DeliveryAddressService()

    file_path = tmp_path / "delivery_address.json"
    file_path.write_text(
        json.dumps(
            {
                "label": "casa",
                "street": "Rua Exemplo",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_required_field_is_empty(tmp_path):
    service = DeliveryAddressService()

    file_path = tmp_path / "delivery_address.json"
    file_path.write_text(
        json.dumps(
            {
                "label": "",
                "recipient_name": "Matheus Felipe",
                "street": "Rua Exemplo",
                "number": "123",
                "complement": "",
                "neighborhood": "Centro",
                "city": "Campinas",
                "state": "SP",
                "postal_code": "13000-000",
                "country": "BR",
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidShoppingListError):
        service.load_from_file(file_path)


def test_load_from_file_should_allow_empty_complement(tmp_path):
    service = DeliveryAddressService()

    file_path = tmp_path / "delivery_address.json"
    file_path.write_text(
        json.dumps(
            {
                "label": "casa",
                "recipient_name": "Matheus Felipe",
                "street": "Rua Exemplo",
                "number": "123",
                "complement": "",
                "neighborhood": "Centro",
                "city": "Campinas",
                "state": "SP",
                "postal_code": "13000-000",
                "country": "BR",
            }
        ),
        encoding="utf-8",
    )

    result = service.load_from_file(file_path)

    assert result.complement == ""