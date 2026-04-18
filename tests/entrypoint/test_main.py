"""Entrypoint output tests for app.main."""

import pytest

from app.main import main


def test_main_should_print_cli_output_when_output_mode_is_cli(
    default_shopping_list_path,
    default_delivery_fees_path,
    default_market_sources_path,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(default_shopping_list_path),
            "--delivery-fees",
            str(default_delivery_fees_path),
            "--market-sources",
            str(default_market_sources_path),
            "--output",
            "cli",
        ],
    )

    main()
    captured = capsys.readouterr()

    assert "Market Quote Assistant - comparison result" in captured.out
    assert "JSON preview:" not in captured.out


def test_main_should_print_json_output_when_output_mode_is_json(
    default_shopping_list_path,
    default_delivery_fees_path,
    default_market_sources_path,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(default_shopping_list_path),
            "--delivery-fees",
            str(default_delivery_fees_path),
            "--market-sources",
            str(default_market_sources_path),
            "--output",
            "json",
        ],
    )

    main()
    captured = capsys.readouterr()

    assert '"market_quotes"' in captured.out
    assert "Market Quote Assistant - comparison result" not in captured.out


def test_main_should_print_both_outputs_when_output_mode_is_both(
    default_shopping_list_path,
    default_delivery_fees_path,
    default_market_sources_path,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--shopping-list",
            str(default_shopping_list_path),
            "--delivery-fees",
            str(default_delivery_fees_path),
            "--market-sources",
            str(default_market_sources_path),
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