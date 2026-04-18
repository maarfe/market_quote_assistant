"""Unit tests for the text normalizer."""

from app.normalization.text_normalizer import TextNormalizer


def test_clean_text_should_lowercase_remove_accents_and_normalize_spacing():
    normalizer = TextNormalizer()

    result = normalizer.clean_text("  Leíte   Integral/UHT  ")

    assert result == "leite integral uht"


def test_tokenize_should_split_text_into_tokens():
    normalizer = TextNormalizer()

    result = normalizer.tokenize("leite integral uht")

    assert result == ["leite", "integral", "uht"]


def test_remove_irrelevant_tokens_should_filter_known_noise_tokens():
    normalizer = TextNormalizer()

    result = normalizer.remove_irrelevant_tokens(
        ["arroz", "tipo", "1", "uht", "integral"]
    )

    assert result == ["arroz", "1", "integral"]


def test_normalize_should_return_canonical_text_without_irrelevant_tokens():
    normalizer = TextNormalizer()

    result = normalizer.normalize("Leite Integral UHT")

    assert result == "leite integral"


def test_normalize_should_handle_symbols_and_multiple_spaces():
    normalizer = TextNormalizer()

    result = normalizer.normalize("Arroz  Branco - Tipo / 1")

    assert result == "arroz branco 1"