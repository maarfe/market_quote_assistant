"""Entrypoint output tests for app.main."""

import json

import pytest

from app.main import main


def test_main_should_print_cli_output_when_output_mode_is_cli(tmp_path, monkeypatch, capsys):
    shopping_list_path = tmp_path / "shopping_list.json"
    delivery_fees_path = tmp_path / "delivery_fees.json"
    market_sources_path = tmp_path / "market_sources.json"
    market_a_path = tmp_path / "market_a.json"

    shopping_list_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Leite Integral",
                    "requested_quantity": 1,
                    "requested_unit": "unit",
                }
            ]
        ),
        encoding="utf-8",
    )

    delivery_fees_path.write_text(
        json.dumps({"Market A": 8.0}),
        encoding="utf-8",
    )

    market_a_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Leite Integral UHT 1L Italac",
                    "price": 4.99,
                    "size_value": 1,
                    "size_unit": "l",
                }
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
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(shopping_list_path),
            "--delivery-fees",
            str(delivery_fees_path),
            "--market-sources",
            str(market_sources_path),
            "--output",
            "cli",
        ],
    )

    main()
    captured = capsys.readouterr()

    assert "Market Quote Assistant - comparison result" in captured.out
    assert "JSON preview:" not in captured.out


def test_main_should_print_json_output_when_output_mode_is_json(tmp_path, monkeypatch, capsys):
    shopping_list_path = tmp_path / "shopping_list.json"
    delivery_fees_path = tmp_path / "delivery_fees.json"
    market_sources_path = tmp_path / "market_sources.json"
    market_a_path = tmp_path / "market_a.json"

    shopping_list_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Leite Integral",
                    "requested_quantity": 1,
                    "requested_unit": "unit",
                }
            ]
        ),
        encoding="utf-8",
    )

    delivery_fees_path.write_text(
        json.dumps({"Market A": 8.0}),
        encoding="utf-8",
    )

    market_a_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Leite Integral UHT 1L Italac",
                    "price": 4.99,
                    "size_value": 1,
                    "size_unit": "l",
                }
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
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(shopping_list_path),
            "--delivery-fees",
            str(delivery_fees_path),
            "--market-sources",
            str(market_sources_path),
            "--output",
            "json",
        ],
    )

    main()
    captured = capsys.readouterr()

    assert '"market_quotes"' in captured.out
    assert "Market Quote Assistant - comparison result" not in captured.out


def test_main_should_print_both_outputs_when_output_mode_is_both(tmp_path, monkeypatch, capsys):
    shopping_list_path = tmp_path / "shopping_list.json"
    delivery_fees_path = tmp_path / "delivery_fees.json"
    market_sources_path = tmp_path / "market_sources.json"
    market_a_path = tmp_path / "market_a.json"

    shopping_list_path.write_text(
        json.dumps(
            [
                {
                    "item_id": "item-001",
                    "display_name": "Leite Integral",
                    "requested_quantity": 1,
                    "requested_unit": "unit",
                }
            ]
        ),
        encoding="utf-8",
    )

    delivery_fees_path.write_text(
        json.dumps({"Market A": 8.0}),
        encoding="utf-8",
    )

    market_a_path.write_text(
        json.dumps(
            [
                {
                    "original_name": "Leite Integral UHT 1L Italac",
                    "price": 4.99,
                    "size_value": 1,
                    "size_unit": "l",
                }
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
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(shopping_list_path),
            "--delivery-fees",
            str(delivery_fees_path),
            "--market-sources",
            str(market_sources_path),
            "--output",
            "both",
        ],
    )

    main()
    captured = capsys.readouterr()

    assert "Market Quote Assistant - comparison result" in captured.out
    assert "JSON preview:" in captured.out
    assert '"market_quotes"' in captured.out


def test_main_should_print_friendly_error_for_missing_file(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            "missing_shopping_list.json",
            "--output",
            "cli",
        ],
    )

    with pytest.raises(SystemExit) as error:
        main()

    captured = capsys.readouterr()

    assert error.value.code == 1
    assert "Error: required file not found:" in captured.out