"""Unit tests for the market source service."""

import json

import pytest

from app.services.market_source_service import MarketSourceService
from app.shared import InvalidMarketSourceConfigError


def test_load_from_file_should_return_market_sources(tmp_path):
    service = MarketSourceService()

    file_path = tmp_path / "market_sources.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "market_name": "Market A",
                    "file_path": "data/market_data/market_a.json",
                }
            ]
        ),
        encoding="utf-8",
    )

    result = service.load_from_file(file_path)

    assert len(result) == 1
    assert result[0].market_name == "Market A"
    assert result[0].file_path == "data/market_data/market_a.json"


def test_load_from_file_should_raise_error_when_payload_is_not_a_list(tmp_path):
    service = MarketSourceService()

    file_path = tmp_path / "market_sources.json"
    file_path.write_text(
        json.dumps({"invalid": True}),
        encoding="utf-8",
    )

    with pytest.raises(InvalidMarketSourceConfigError):
        service.load_from_file(file_path)


def test_load_from_file_should_raise_error_when_required_fields_are_missing(tmp_path):
    service = MarketSourceService()

    file_path = tmp_path / "market_sources.json"
    file_path.write_text(
        json.dumps(
            [
                {
                    "market_name": "Market A",
                }
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(InvalidMarketSourceConfigError):
        service.load_from_file(file_path)