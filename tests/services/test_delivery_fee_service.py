"""Unit tests for the delivery fee service."""

import json

import pytest

from app.services.delivery_fee_service import DeliveryFeeService
from app.shared import InvalidDeliveryFeeConfigError


def test_load_from_file_should_return_delivery_fee_mapping(tmp_path):
    service = DeliveryFeeService()

    file_path = tmp_path / "delivery_fees.json"
    file_path.write_text(
        json.dumps(
            {
                "Market A": 8.0,
                "Market B": 11.0,
            }
        ),
        encoding="utf-8",
    )

    result = service.load_from_file(file_path)

    assert result == {
        "Market A": 8.0,
        "Market B": 11.0,
    }


def test_load_from_file_should_raise_error_when_payload_is_not_a_dict(tmp_path):
    service = DeliveryFeeService()

    file_path = tmp_path / "delivery_fees.json"
    file_path.write_text(
        json.dumps(["invalid"]),
        encoding="utf-8",
    )

    with pytest.raises(InvalidDeliveryFeeConfigError):
        service.load_from_file(file_path)
        

def test_load_from_file_should_raise_error_when_market_name_is_empty(tmp_path):
    service = DeliveryFeeService()

    file_path = tmp_path / "delivery_fees.json"
    file_path.write_text(
        json.dumps(
            {
                "": 8.0,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidDeliveryFeeConfigError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_fee_is_negative(tmp_path):
    service = DeliveryFeeService()

    file_path = tmp_path / "delivery_fees.json"
    file_path.write_text(
        json.dumps(
            {
                "Market A": -1.0,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidDeliveryFeeConfigError):
        service.load_from_file(file_path)