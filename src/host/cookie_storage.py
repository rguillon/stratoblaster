"""Cookie-backed storage (GD-51, vision: persistence uses cookies), ported from
`platform/cookie-storage.ts`.

It is a `KeyValueStorage` by shape (see `key_value_storage.py`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Protocol  # noqa: E402


class CookieDocument(Protocol):
    """The part of the document this storage uses: its `cookie` string."""

    cookie: str


__pragma__("noskip")

SECONDS_PER_DAY = 86400


def encode_uri_component(text: str) -> str:
    """`encodeURIComponent(text)`."""
    __pragma__("js", "{}", "return encodeURIComponent(text);")
    return ""


def decode_uri_component(text: str) -> str:
    """`decodeURIComponent(text)`: throws (URIError) on a malformed escape."""
    __pragma__("js", "{}", "return decodeURIComponent(text);")
    return ""


class CookieStorage:
    """Cookie-backed storage. The max age is in days."""

    def __init__(self, doc: CookieDocument, max_age_days: float) -> None:
        self._doc = doc
        self._max_age_days = max_age_days

    def get(self, key: str) -> str | None:
        prefix = encode_uri_component(key) + "="
        for part in self._doc.cookie.split(";"):
            cookie = part.strip()
            if not cookie.startswith(prefix):
                continue
            try:
                return decode_uri_component(cookie[len(prefix) :])
            except:  # noqa: E722 (any malformed escape gives null, as in the TypeScript)
                return None
        return None

    def set(self, key: str, value: str) -> None:
        max_age = math.floor(self._max_age_days * SECONDS_PER_DAY + 0.5)
        self._doc.cookie = (
            encode_uri_component(key)
            + "="
            + encode_uri_component(value)
            + "; max-age="
            + str(max_age)
            + "; SameSite=Lax"
        )
