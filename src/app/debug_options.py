"""Reads the debug options of the game screen from a URL query (P06-R09):
`?level=1-3&t=120&ship=heavy` starts level 1-3 at 2:00 with the heavy
ship. `level` turns debug on; `t` (seconds, default 0) and `ship` (default: the first ship) are
optional. `boss=mini` or `boss=final` starts at that boss's arrival instead (P07-R09).
`weather=0` turns the weather off and `look=night` (or another time of day) forces the time of
day (P08-R12). `tiles=1` draws the grid of tiles over the districts (P15-R10).
Without `level`, or with a value that does not parse, there are no debug options.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.game_session import GameDebugOptions
from core.scenery.atmosphere import is_time_of_day


def _query_text(search: str, key: str) -> str | None:
    """`URLSearchParams.get`: the value of `key`, or None when it is missing."""
    __pragma__("js", "{}", "return new URLSearchParams(search).get(key);")
    return None


def _time_text(search: str) -> float:
    """`Number(query.get('t') ?? '0')`: NaN for text that is not a number."""
    __pragma__("js", "{}", "return Number(new URLSearchParams(search).get('t') ?? '0');")
    return 0


def _is_finite(value: float) -> bool:
    return value - value == 0


def parse_debug_options(search: str) -> GameDebugOptions | None:
    level_id = _query_text(search, "level")
    if not level_id:
        return None
    time = _time_text(search)
    return GameDebugOptions(
        level_id,
        time if _is_finite(time) and time > 0 else 0,
        _query_text(search, "ship"),
        _boss_of(_query_text(search, "boss")),
        _query_text(search, "weather") != "0",
        _time_of_day_of(_query_text(search, "look")),
        _query_text(search, "tiles") == "1",
    )


def _boss_of(value: str | None) -> str | None:
    return value if value in ["mini", "final"] else None


def _time_of_day_of(value: str | None) -> str | None:
    return value if value is not None and is_time_of_day(value) else None
