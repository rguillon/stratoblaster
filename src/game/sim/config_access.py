# Copyright (c) 2026 Renaud Guillon
"""Reading the config records (`game/config/`) the sim builds from: optional fields.

And the keys of a record. A record is a plain JavaScript object in the browser.
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def opt(value: Any) -> Any:
    """Return the config's optional field `value`, or None when the config leaves it out."""
    if value == None:
        return None
    return value


def keys_of(record: Any) -> list[str]:
    """Return the keys of a config record, in their order.

    A record is a plain JavaScript object, which has no `keys()` method under Transcrypt (ENG-159);
    a Python twin gives the same keys under CPython (ENG-160).
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
