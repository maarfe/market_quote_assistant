"""Unit tests for the unit normalizer."""

import pytest

from app.normalization.unit_normalizer import UnitNormalizer
from app.shared import UnsupportedUnitError


def test_normalize_should_return_canonical_unit_data():
    normalizer = UnitNormalizer()

    result = normalizer.normalize(2, "litro")

    assert result.value == 2.0
    assert result.unit == "l"


def test_normalize_unit_should_return_canonical_unit():
    normalizer = UnitNormalizer()

    result = normalizer.normalize_unit("unidade")

    assert result == "unit"


def test_normalize_unit_should_raise_error_for_unsupported_unit():
    normalizer = UnitNormalizer()

    with pytest.raises(UnsupportedUnitError):
        normalizer.normalize_unit("caixao")