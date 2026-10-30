"""Python twins of the JavaScript-only helpers of `src/app/` (`__pragma__("js")` bodies, which
CPython does not run): the URL query, the number and regular-expression checks of the stored
values, the JSON reads and writes, and plain objects for the Babylon snapshots. The tests of those
modules install them with monkeypatch, so the logic around them is what is tested."""

import json
import math
import re
from typing import Any
from urllib.parse import parse_qs


def url_query(search: str, key: str) -> str | None:
    """`new URLSearchParams(search).get(key)`: the first value of `key`, or None."""
    values = parse_qs(search.lstrip("?"), keep_blank_values=True).get(key)
    return values[0] if values else None


def time_number(search: str) -> float:
    """`Number(query.get('t') ?? '0')`: NaN for text that is not a number."""
    text = url_query(search, "t")
    if text is None:
        text = "0"
    if text.strip() == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        return math.nan


def plain_score(raw: str) -> float:
    """`/^\\d{1,15}$/` on the trimmed text, read as a number; anything else is 0."""
    text = raw.strip()
    return float(text) if re.fullmatch(r"\d{1,15}", text) else 0


def step_text(text: str) -> bool:
    """`/^\\d{1,2}$/`."""
    return re.fullmatch(r"\d{1,2}", text) is not None


def _is_whole(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value == int(value)


def read_supplies(raw: str) -> dict[str, float] | None:
    """`{"lives": n, "bombs": m}` with lives >= 1 and bombs >= 0 as whole numbers, or None."""
    try:
        value = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(value, dict):
        return None
    lives, bombs = value.get("lives"), value.get("bombs")
    if not (_is_whole(lives) and lives >= 1 and _is_whole(bombs) and bombs >= 0):
        return None
    return {"lives": lives, "bombs": bombs}


def read_weapon_levels(raw: str) -> dict[str, Any] | None:
    """`{"weapon": s, "levels": {name: whole >= 1}}`, or None."""
    try:
        value = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(value, dict):
        return None
    weapon, levels = value.get("weapon"), value.get("levels")
    if not isinstance(weapon, str) or not isinstance(levels, dict):
        return None
    if not all(_is_whole(level) and level >= 1 for level in levels.values()):
        return None
    return {"weapon": weapon, "levels": dict(levels)}


def to_json(value: dict[str, Any]) -> str:
    return json.dumps(value, separators=(",", ":"))


def js_object() -> dict[str, Any]:
    """`{}`: a plain object the test reads back with its keys."""
    return {}


def js_set(target: dict[str, Any], key: str, value: Any) -> None:
    target[key] = value
