"""Utilities for deterministic product text normalization."""

import re
import unicodedata


class TextNormalizer:
    """
    Normalize product-related texts in a deterministic and explainable way.

    This class is responsible for cleaning noisy text, removing accents,
    standardizing casing, and reducing irrelevant formatting differences.
    """

    _IRRELEVANT_TOKENS = {
        "tipo",
        "uht",
    }

    def normalize(self, text: str) -> str:
        """
        Normalize a raw text into a canonical comparison-friendly format.

        Args:
            text: Raw text to normalize.

        Returns:
            A normalized canonical string.
        """
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        relevant_tokens = self.remove_irrelevant_tokens(tokens)
        return " ".join(relevant_tokens).strip()

    def clean_text(self, text: str) -> str:
        """
        Apply basic text cleaning operations.

        Args:
            text: Raw text to clean.

        Returns:
            A cleaned text string.
        """
        normalized_text = self._remove_accents(text.lower())
        normalized_text = normalized_text.replace("-", " ")
        normalized_text = normalized_text.replace("/", " ")
        normalized_text = re.sub(r"[^\w\s]", " ", normalized_text)
        normalized_text = re.sub(r"\s+", " ", normalized_text)
        return normalized_text.strip()

    def tokenize(self, text: str) -> list[str]:
        """
        Split a cleaned text into comparison tokens.

        Args:
            text: Text to tokenize.

        Returns:
            A list of text tokens.
        """
        return [token for token in text.split(" ") if token]

    def remove_irrelevant_tokens(self, tokens: list[str]) -> list[str]:
        """
        Remove tokens that do not add relevant comparison meaning.

        Args:
            tokens: Input tokens.

        Returns:
            A filtered token list.
        """
        return [token for token in tokens if token not in self._IRRELEVANT_TOKENS]

    def _remove_accents(self, text: str) -> str:
        """
        Remove accents from text.

        Args:
            text: Input text.

        Returns:
            Accent-free text.
        """
        return "".join(
            character
            for character in unicodedata.normalize("NFKD", text)
            if not unicodedata.combining(character)
        )