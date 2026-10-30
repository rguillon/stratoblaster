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


# CPython only (the unit tests): Transcrypt skips these, and the browser's objects read their fields
# as attributes already.
__pragma__("skip")


class _Fields(dict):  # type: ignore[type-arg]
    """A record whose fields read as attributes, as they do in the browser. A field the record lacks
    reads as None, as an absent field reads as undefined there."""

    def __getattr__(self, key: str) -> Any:
        return self.get(key)


def fields_of(obj: Any) -> dict[str, Any]:
    """The fields of a record or of an object (`Object.assign({}, obj)` copies them)."""
    return dict(obj) if isinstance(obj, dict) else dict(vars(obj))


def _as_fields(value: Any) -> Any:
    """`value` with every dict in it a record (`_Fields`) and every list a list."""
    if isinstance(value, dict):
        return _Fields({k: _as_fields(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_as_fields(v) for v in value]
    return value


__pragma__("noskip")


def record(fields: dict[str, Any]) -> Any:
    """Returns `fields` as the object literal it stands for."""
    __pragma__("skip")
    return _as_fields(fields)
    __pragma__("noskip")
    return fields


def merge(base: dict[str, Any], extra: dict[str, Any]) -> Any:
    """`{...base, ...extra}`: a copy of `base` with the fields of `extra` set over it."""
    __pragma__("skip")
    return _as_fields({**base, **(extra or {})})
    __pragma__("noskip")
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
    __pragma__("skip")
    value = obj.get(key) if isinstance(obj, dict) else getattr(obj, key, None)
    __pragma__("noskip")
    __pragma__(
        "js",
        "{}",
        """
    value = obj[key];
    """,
    )
    return default if value == None else value  # noqa: E711 (undefined for an absent field)
