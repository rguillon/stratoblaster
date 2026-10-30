"""Object literals of the game's config tables (`src/game/config/`).

A TS object literal is a plain object whose fields are read as `CONFIG.field`. `record` keeps that
shape at run time (a Transcrypt dict is a plain JavaScript object) and types it as `Any` for mypy,
because the config's own types live in `core/` and are not repeated for every table.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def record(fields: dict[str, Any]) -> Any:
    """Returns `fields` as the object literal it stands for."""
    return fields


def merge(base: dict[str, Any], extra: dict[str, Any]) -> Any:
    """`{...base, ...extra}`: a copy of `base` with the fields of `extra` set over it."""
    result: Any = None
    __pragma__(
        "js",
        "{}",
        """
    result = Object.assign({}, base, extra);
    """,
    )
    return result


def concat(*parts: list[Any]) -> list[Any]:
    """`[...a, ...b]`: a new list with the items of each part, in order."""
    out: list[Any] = []
    for part in parts:
        out.extend(part)
    return out


def field(obj: Any, key: str, default: Any) -> Any:
    """`obj[key]`, or `default` when the record has no such field (`dict.get` is not on JS
    objects)."""
    value: Any = None
    __pragma__(
        "js",
        "{}",
        """
    value = obj[key];
    """,
    )
    return default if value == None else value  # noqa: E711 (undefined for an absent field)
