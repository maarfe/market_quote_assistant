import unicodedata


class TextNormalizer:
    @staticmethod
    def normalize(text: str | None) -> str:
        if not text:
            return ""

        text = text.strip().lower()
        text = unicodedata.normalize("NFD", text)
        text = "".join(
            char for char in text
            if unicodedata.category(char) != "Mn"
        )
        text = " ".join(text.split())

        return text