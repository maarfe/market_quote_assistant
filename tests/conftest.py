"""Shared pytest fixtures for the test suite."""

import pytest

from tests.factories import (
    create_delivery_fees_file,
    create_market_data_file,
    create_market_sources_file,
    create_shopping_list_file,
)


@pytest.fixture
def default_shopping_list_path(tmp_path):
    """Create a default shopping list file and return its path."""
    return create_shopping_list_file(tmp_path)


@pytest.fixture
def default_delivery_fees_path(tmp_path):
    """Create a default delivery fee file and return its path."""
    return create_delivery_fees_file(tmp_path)


@pytest.fixture
def default_market_a_path(tmp_path):
    """Create a default Market A data file and return its path."""
    return create_market_data_file(tmp_path, filename="market_a.json")


@pytest.fixture
def default_market_sources_path(tmp_path, default_market_a_path):
    """Create a default market sources file and return its path."""
    return create_market_sources_file(
        tmp_path,
        payload=[
            {
                "market_name": "Market A",
                "file_path": str(default_market_a_path),
            }
        ],
    )