# Copyright (c) 2026 Renaud Guillon
"""A `KeyValueStorage` kept in memory: the app tests' stand-in for the cookies (ENG-47)."""


class MemoryStorage:
    """Small string storage in a dict, read back as `CookieStorage` would."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def get(self, key: str) -> str | None:
        """Return the stored value of `key`, or None when missing."""
        return self.values.get(key)

    def set(self, key: str, value: str) -> None:
        """Store `value` under `key`."""
        self.values[key] = value
