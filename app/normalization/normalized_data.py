"""Structured normalized data models used by the normalization layer."""

from dataclasses import dataclass


@dataclass(slots=True)
class NormalizedTextData:
    """
    Represents the result of normalizing a product-related text.

    Attributes:
        original_text: Original raw text before normalization.
        cleaned_text: Cleaned text after basic normalization rules.
        canonical_text: Canonical text after removing irrelevant tokens.
    """

    original_text: str
    cleaned_text: str
    canonical_text: str