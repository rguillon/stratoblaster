"""Small string storage, so app code does not depend on cookies and tests use a fake."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Protocol  # noqa: E402


class KeyValueStorage(Protocol):
    """Small string storage. Implementations are structural (no base class at run time)."""

    def get(self, key: str) -> str | None:
        """The stored value, or None when missing or unreadable."""
        ...

    def set(self, key: str, value: str) -> None: ...


__pragma__("noskip")


class MemoryStorage:
    """In-memory storage, for tests and as a fallback.

    A Map would be the natural store here. A Transcrypt dict cannot hold the key `__proto__` (it
    writes the
    prototype), so the keys and values are kept in two parallel lists, looked up in turn.
    """

    def __init__(self) -> None:
        self._keys: list[str] = []
        self._values: list[str] = []

    def _index_of(self, key: str) -> int:
        for i in range(len(self._keys)):
            if self._keys[i] == key:
                return i
        return -1

    def get(self, key: str) -> str | None:
        index = self._index_of(key)
        if index < 0:
            return None
        return self._values[index]

    def set(self, key: str, value: str) -> None:
        index = self._index_of(key)
        if index < 0:
            self._keys.append(key)
            self._values.append(value)
        else:
            self._values[index] = value
