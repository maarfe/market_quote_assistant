"""Unit tests for the market data loader."""

import json

import pytest

from app.collectors.market_data_loader import MarketDataLoader


def test_load_should_return_raw_offer_list(tmp_path):
    file_path = tmp_path / "market_data.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Leite Integral UHT 1L",
                    "price": 4.99,
                }
            ]
        ),
        encoding="utf-8",
    )

    loader = MarketDataLoader(file_path=file_path)

    result = loader.load()

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["original_name"] == "Leite Integral UHT 1L"
    assert result[0]["price"] == 4.99


def test_load_should_raise_file_not_found_error_when_file_does_not_exist():
    loader = MarketDataLoader(file_path="nonexistent_market_data.json")

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_load_should_raise_value_error_when_payload_is_not_a_list(tmp_path):
    file_path = tmp_path / "market_data.json"
    file_path.write_text(
        json.dumps({"invalid": True}),
        encoding="utf-8",
    )

    loader = MarketDataLoader(file_path=file_path)

    with pytest.raises(ValueError):
        loader.load()