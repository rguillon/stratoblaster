"""Unit tests of `src/host/key_value_storage.py`."""

from host.key_value_storage import MemoryStorage


def test_p05_r07_a_missing_key_reads_as_none() -> None:
    assert MemoryStorage().get("ship") is None


def test_p05_r07_a_value_is_read_back_and_overwritten() -> None:
    storage = MemoryStorage()
    storage.set("ship", "1")
    storage.set("level", "2")
    storage.set("ship", "3")
    assert storage.get("ship") == "3"
    assert storage.get("level") == "2"


def test_p05_r07_keys_that_look_like_object_internals_are_plain_keys() -> None:
    storage = MemoryStorage()
    storage.set("__proto__", "x")
    storage.set("constructor", "y")
    assert storage.get("__proto__") == "x"
    assert storage.get("constructor") == "y"
