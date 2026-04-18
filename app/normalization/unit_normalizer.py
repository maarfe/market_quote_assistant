"""Utilities for unit normalization and standardization."""

from dataclasses import dataclass
from app.shared import UnsupportedUnitError


@dataclass(slots=True)
class NormalizedUnitData:
    """
    Represents normalized measurement data.

    Attributes:
        value: Numeric value of the measurement.
        unit: Canonical unit representation.
    """

    value: float
    unit: str


class UnitNormalizer:
    """
    Normalize product units into canonical forms.

    This class standardizes known unit aliases so future comparison logic can
    operate on predictable values.
    """

    _UNIT_ALIASES = {
        "kg": "kg",
        "quilo": "kg",
        "quilos": "kg",
        "g": "g",
        "grama": "g",
        "gramas": "g",
        "l": "l",
        "lt": "l",
        "litro": "l",
        "litros": "l",
        "ml": "ml",
        "mililitro": "ml",
        "mililitros": "ml",
        "un": "unit",
        "und": "unit",
        "unidade": "unit",
        "unidades": "unit",
        "unit": "unit",
    }

    def normalize(self, value: float, unit: str) -> NormalizedUnitData:
        """
        Normalize a measurement value and unit into canonical form.

        Args:
            value: Raw numeric value.
            unit: Raw measurement unit.

        Returns:
            A normalized unit data object.

        Raises:
            ValueError: If the unit is not supported.
        """
        normalized_unit = self._normalize_unit(unit)

        return NormalizedUnitData(
            value=float(value),
            unit=normalized_unit,
        )

    def normalize_unit(self, unit: str) -> str:
        """
        Public helper for unit-only normalization.

        Args:
            unit: Raw unit string.

        Returns:
            A canonical unit representation.
        """
        return self._normalize_unit(unit)

    def _normalize_unit(self, unit: str) -> str:
        """
        Convert a raw unit alias to its canonical representation.

        Args:
            unit: Raw unit string.

        Returns:
            A canonical unit string.

        Raises:
            ValueError: If the unit is not supported.
        """
        normalized_key = unit.strip().lower()

        if normalized_key not in self._UNIT_ALIASES:
            raise UnsupportedUnitError(f"Unsupported unit '{unit}'.")

        return self._UNIT_ALIASES[normalized_key]