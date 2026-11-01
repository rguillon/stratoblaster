"""Object literals with attribute access for the sample game's looks (CPython only: a field the
record lacks reads as None, as an absent field reads as undefined in the browser)."""

from typing import Any


class _Fields(dict):  # type: ignore[type-arg]
    """A dict whose fields read as attributes."""

    def __getattr__(self, key: str) -> Any:
        return self.get(key)


def record(fields: dict[str, Any]) -> Any:
    """`fields` as an object literal: every dict in it reads its fields as attributes."""
    if isinstance(fields, dict):
        return _Fields(
            {k: record(v) if isinstance(v, dict) else _items(v) for k, v in fields.items()}
        )
    return fields


def _items(value: Any) -> Any:
    """A list with its dicts turned into records; any other value as it is."""
    if isinstance(value, list):
        return [record(v) if isinstance(v, dict) else v for v in value]
    return value
