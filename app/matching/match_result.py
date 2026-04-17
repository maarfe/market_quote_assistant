"""Structured internal matching results for the matching engine."""

from dataclasses import dataclass

from app.domain import MatchType


@dataclass(slots=True)
class MatchEvaluation:
    """
    Represents the internal result of evaluating a shopping item against a product offer.

    Attributes:
        match_type: Final match classification.
        confidence_score: Confidence score between 0.0 and 1.0.
        notes: Human-readable explanation for the decision.
    """

    match_type: MatchType
    confidence_score: float
    notes: str