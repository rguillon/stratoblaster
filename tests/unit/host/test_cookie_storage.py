"""Unit tests of `src/host/cookie_storage.py`."""

from urllib.parse import quote, unquote

import pytest

from host import cookie_storage
from host.cookie_storage import CookieStorage


class FakeDocument:
    def __init__(self, cookie: str = "") -> None:
        self.cookie = cookie


@pytest.fixture(autouse=True)
def uri_component_codec(monkeypatch: pytest.MonkeyPatch) -> None:
    """The `encodeURIComponent` / `decodeURIComponent` calls are JavaScript only: CPython gets
    the standard library's percent-encoding, which is the same for the characters used here."""
    monkeypatch.setattr(cookie_storage, "encode_uri_component", lambda text: quote(text, safe=""))
    monkeypatch.setattr(cookie_storage, "decode_uri_component", unquote)


def test_p05_r07_a_stored_value_is_written_as_an_encoded_cookie_with_max_age() -> None:
    doc = FakeDocument()
    CookieStorage(doc, 365).set("high score", "1200")
    assert doc.cookie == "high%20score=1200; max-age=31536000; SameSite=Lax"


def test_p05_r07_max_age_is_rounded_to_whole_seconds() -> None:
    doc = FakeDocument()
    CookieStorage(doc, 0.5).set("k", "v")
    assert "max-age=43200;" in doc.cookie


def test_p05_r07_a_value_is_read_back_decoded() -> None:
    doc = FakeDocument()
    storage = CookieStorage(doc, 1)
    storage.set("ship", "a=b; c")
    assert storage.get("ship") == "a=b; c"


def test_p05_r07_the_key_is_matched_among_several_cookies() -> None:
    storage = CookieStorage(FakeDocument("theme=dark; ship=3;  level=7"), 1)
    assert storage.get("ship") == "3"
    assert storage.get("level") == "7"


def test_p05_r07_a_missing_key_reads_as_none() -> None:
    storage = CookieStorage(FakeDocument("theme=dark"), 1)
    assert storage.get("ship") is None
    assert CookieStorage(FakeDocument(""), 1).get("ship") is None


def test_p05_r07_a_key_that_only_shares_a_prefix_is_not_a_match() -> None:
    storage = CookieStorage(FakeDocument("shipper=9"), 1)
    assert storage.get("ship") is None


def test_p05_r07_an_unreadable_value_reads_as_none(monkeypatch: pytest.MonkeyPatch) -> None:
    def broken(text: str) -> str:
        raise ValueError("URIError")

    monkeypatch.setattr(cookie_storage, "decode_uri_component", broken)
    assert CookieStorage(FakeDocument("ship=%E0%A4%A"), 1).get("ship") is None
