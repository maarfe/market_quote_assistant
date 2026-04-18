"""Shared helpers for monetary calculations and rounding."""

from decimal import Decimal, ROUND_HALF_UP


class MoneyHelper:
    """
    Centralize money-related rounding rules for the application.
    """

    @staticmethod
    def round_currency(value: float) -> float:
        """
        Round a numeric value to two decimal places using financial rounding.

        Args:
            value: Raw numeric value.

        Returns:
            A float rounded to two decimal places.
        """
        decimal_value = Decimal(str(value)).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
        return float(decimal_value)