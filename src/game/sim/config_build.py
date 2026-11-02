# Copyright (c) 2026 Renaud Guillon
"""Shared helpers of the mapping layers that turn config records into `core/` objects.

The mapping layers are `game/sim/*_build.py`. The config keeps camelCase keys, `core/` takes
snake_case attributes and tests `is None` for an omitted optional field.

Under Transcrypt an omitted field is `undefined`, not `None`, so every optional field goes through
`opt` or `maybe` (ENG-161). Config keys that Transcrypt renames (`name`, `length`, `from`) are read
by subscript (`raw["name"]`) in the mapping modules, not by attribute (ENG-156).
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
# __pragma__ ("noskip")


def opt(value: Any) -> Any:
    """Return the config's optional field `value`, or None when the config leaves it out."""
    if value == None:
        return None
    return value


def maybe(value: Any, convert: Callable[[Any], Any]) -> Any:
    """`convert(value)`, or None when the config leaves the field out."""
    if value == None:
        return None
    return convert(value)


def mapped(items: Any, convert: Callable[[Any], Any]) -> list[Any]:
    """`convert` of each config item, in order (a config array, `[]` when there is none)."""
    if items == None:
        return []
    result: list[Any] = [convert(item) for item in items]
    return result
