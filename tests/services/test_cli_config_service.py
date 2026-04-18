"""Unit tests for the CLI configuration service."""

from app.services.cli_config_service import CliConfigService


def test_parse_args_should_return_default_values(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        ["prog"],
    )

    service = CliConfigService()
    result = service.parse_args()

    assert result.shopping_list_path == "data/shopping_lists/default_shopping_list.json"
    assert result.delivery_fees_path == "data/delivery_fees/default_delivery_fees.json"
    assert result.market_sources_path == "data/market_sources/default_market_sources.json"
    assert result.output_mode == "both"
    assert result.delivery_address_path is None


def test_parse_args_should_return_explicit_values(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            "custom/shopping.json",
            "--delivery-fees",
            "custom/delivery.json",
            "--market-sources",
            "custom/markets.json",
            "--output",
            "cli",
        ],
    )

    service = CliConfigService()
    result = service.parse_args()

    assert result.shopping_list_path == "custom/shopping.json"
    assert result.delivery_fees_path == "custom/delivery.json"
    assert result.market_sources_path == "custom/markets.json"
    assert result.output_mode == "cli"


def test_parse_args_should_return_delivery_address_when_explicitly_provided(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--delivery-address",
            "custom/address.json",
        ],
    )

    service = CliConfigService()
    result = service.parse_args()

    assert result.delivery_address_path == "custom/address.json"