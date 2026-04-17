"""Domain types and enums for the Market Quote Assistant project."""

from enum import Enum


class MatchType(Enum):
    """Represents the compatibility level between a shopping item and a product offer."""

    EXACT = "exact_match"
    ADJUSTABLE = "adjustable_match"
    PARTIAL = "partial_match"
    INVALID = "invalid_match"