"""Small text helpers used by the CMS when rendering and indexing articles."""
import re
import unicodedata

_WHITESPACE = re.compile(r"\s+")
_TAG = re.compile(r"<[^>]+>")


def normalize_whitespace(text: str) -> str:
    """Collapse runs of whitespace into single spaces and trim both ends."""
    return _WHITESPACE.sub(" ", text).strip()


def strip_tags(html: str) -> str:
    """Remove HTML tags, keeping their text content."""
    return normalize_whitespace(_TAG.sub(" ", html))


def truncate_words(text: str, max_chars: int, ellipsis: str = "…") -> str:
    """Shorten text to at most max_chars without cutting a word; append an ellipsis if shortened."""
    text = normalize_whitespace(text)
    if len(text) <= max_chars:
        return text
    cut = text[: max_chars - len(ellipsis) + 1].rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:.") + ellipsis


def strip_accents(text: str) -> str:
    """Remove combining accents: 'Café' -> 'Cafe'. Umlauts lose their dots: 'ü' -> 'u'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))
