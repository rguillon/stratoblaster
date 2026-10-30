"""Reading the config records (`game/config/`) the sim builds from: optional fields, and the keys
of a record. A record is a plain JavaScript object in the browser.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def opt(value: Any) -> Any:
    """The config's optional field `value`, or None when the config leaves it out."""
    if value == None:  # noqa: E711 (undefined or null: Transcrypt has both)
        return None
    return value


def keys_of(record: Any) -> list[str]:
    """The keys of a config record, in their order. A record is a plain JavaScript object, which
    has no `keys()` method under Transcrypt.
    """
    result: list[str] = []
    # CPython only (the unit tests): a dict's keys, as `Object.keys` gives them in the browser.
    __pragma__("skip")
    result = list(record.keys())
    __pragma__("noskip")
    __pragma__(
        "js",
        "{}",
        """
    result = Object.keys(record);
    """,
    )
    return result
