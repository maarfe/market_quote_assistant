"""Builders for temporary JSON test files."""

import json
from pathlib import Path


def write_json_file(path: Path, payload) -> Path:
    """
    Write a JSON payload to disk and return the path.

    Args:
        path: Target file path.
        payload: Serializable JSON payload.

    Returns:
        The same path after writing.
    """
    path.write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return path


def create_shopping_list_file(tmp_path: Path, payload: list[dict] | None = None) -> Path:
    """
    Create a shopping list JSON file for tests.

    Args:
        tmp_path: Temporary directory provided by pytest.
        payload: Optional custom shopping list payload.

    Returns:
        Path to the created shopping list file.
    """
    payload = payload or [
        {
            "item_id": "item-001",
            "display_name": "Leite Integral",
            "requested_quantity": 1,
            "requested_unit": "unit",
        }
    ]
    return write_json_file(tmp_path / "shopping_list.json", payload)


def create_delivery_fees_file(tmp_path: Path, payload: dict | None = None) -> Path:
    """
    Create a delivery fee JSON file for tests.

    Args:
        tmp_path: Temporary directory provided by pytest.
        payload: Optional custom delivery fee payload.

    Returns:
        Path to the created delivery fee file.
    """
    payload = payload or {
        "Market A": 8.0,
    }
    return write_json_file(tmp_path / "delivery_fees.json", payload)


def create_market_data_file(tmp_path: Path, filename: str, payload: list[dict] | None = None) -> Path:
    """
    Create a market data JSON file for tests.

    Args:
        tmp_path: Temporary directory provided by pytest.
        filename: Name of the market data file.
        payload: Optional custom market data payload.

    Returns:
        Path to the created market data file.
    """
    payload = payload or [
        {
            "original_name": "Leite Integral UHT 1L Italac",
            "price": 4.99,
            "size_value": 1,
            "size_unit": "l",
        }
    ]
    return write_json_file(tmp_path / filename, payload)


def create_market_sources_file(tmp_path: Path, payload: list[dict] | None = None) -> Path:
    """
    Create a market sources JSON file for tests.

    Args:
        tmp_path: Temporary directory provided by pytest.
        payload: Optional custom market sources payload.

    Returns:
        Path to the created market sources file.
    """
    payload = payload or [
        {
            "market_name": "Market A",
            "file_path": str(tmp_path / "market_a.json"),
        }
    ]
    return write_json_file(tmp_path / "market_sources.json", payload)