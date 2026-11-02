# Copyright (c) 2026 Renaud Guillon
"""Small string storage, so app code does not depend on cookies and tests use a fake."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Protocol


class KeyValueStorage(Protocol):
    """Small string storage. Implementations are structural (no base class at run time)."""

    def get(self, key: str) -> str | None:
        """Return the stored value, or None when missing or unreadable."""
        ...

    def set(self, key: str, value: str) -> None:
        """Store `value` under `key`."""


# __pragma__ ("noskip")
