"""Shared helpers of the mapping layers (`game/sim/*_build.py`) that turn config records into
`core/` objects: the config keeps camelCase keys, `core/` takes snake_case
attributes and tests `is None` for an omitted optional field.

Under Transcrypt an omitted field is `undefined`, not `None`, so every optional field goes through
`opt` or `maybe`. Config keys that Transcrypt renames (`name`, `length`, `from`) are read by
subscript (`raw["name"]`) in the mapping modules, not by attribute.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def opt(value: Any) -> Any:
    """The config's optional field `value`, or None when the config leaves it out."""
    if value == None:  # noqa: E711 (undefined or null: Transcrypt has both)
        return None
    return value


def maybe(value: Any, convert: Callable[[Any], Any]) -> Any:
    """`convert(value)`, or None when the config leaves the field out."""
    if value == None:  # noqa: E711
        return None
    return convert(value)


def mapped(items: Any, convert: Callable[[Any], Any]) -> list[Any]:
    """`convert` of each config item, in order (a config array, `[]` when there is none)."""
    result: list[Any] = []
    if items == None:  # noqa: E711
        return result
    for item in items:
        result.append(convert(item))
    return result
