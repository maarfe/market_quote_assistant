"""Unit tests for the JSON market collector."""

import json

from app.collectors.json_market_collector import JsonMarketCollector


def test_collect_offers_should_return_product_offer_list(tmp_path):
    file_path = tmp_path / "market_data.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Leite Integral UHT 1L Italac",
                    "normalized_name": "",
                    "price": 4.99,
                    "currency": "BRL",
                    "available": True,
                    "url": "https://mock.local/leite",
                    "size_value": 1,
                    "size_unit": "l",
                    "brand": "Italac",
                }
            ]
        ),
        encoding="utf-8",
    )

    collector = JsonMarketCollector(
        market_name="Market A",
        file_path=str(file_path),
    )

    result = collector.collect_offers()

    assert len(result) == 1
    assert result[0].market_name == "Market A"
    assert result[0].original_name == "Leite Integral UHT 1L Italac"
    assert result[0].price == 4.99
    assert result[0].currency == "BRL"
    assert result[0].available is True
    assert result[0].size_value == 1.0
    assert result[0].size_unit == "l"
    assert result[0].brand == "Italac"


def test_collect_offers_should_apply_default_values_when_optional_fields_are_missing(tmp_path):
    file_path = tmp_path / "market_data.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Banana Nanica Kg",
                    "price": 6.5,
                }
            ]
        ),
        encoding="utf-8",
    )

    collector = JsonMarketCollector(
        market_name="Market A",
        file_path=str(file_path),
    )

    result = collector.collect_offers()

    assert len(result) == 1
    assert result[0].market_name == "Market A"
    assert result[0].normalized_name == ""
    assert result[0].currency == "BRL"
    assert result[0].available is True
    assert result[0].url is None
    assert result[0].size_value is None
    assert result[0].size_unit is None
    assert result[0].brand is None


def test_collect_offers_should_preserve_raw_payload(tmp_path):
    payload = [
        {
            "original_name": "Arroz Branco 5kg",
            "price": 27.9,
            "brand": "Camil",
        }
    ]

    file_path = tmp_path / "market_data.json"
    file_path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )

    collector = JsonMarketCollector(
        market_name="Market A",
        file_path=str(file_path),
    )

    result = collector.collect_offers()

    assert result[0].raw_payload == payload[0]