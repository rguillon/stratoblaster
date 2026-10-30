"""The weapons kept between levels Storage key prefixed with
the game's id.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from host.key_value_storage import KeyValueStorage  # noqa: E402

__pragma__("noskip")

from core.systems.run_arsenal import WeaponLevels  # noqa: E402


def saved_weapons_key(game_id: str) -> str:
    return game_id + "_weapons"


def parse_weapon_levels(raw: str | None) -> WeaponLevels | None:
    """Parses stored weapons (`{"weapon":"guns","levels":{"guns":3}}`). Anything else, or an
    unreadable value, reads as None: the player starts with the weapons at their first level.
    """
    if raw is None:
        return None
    parsed = _read_weapon_levels(raw)
    if parsed is None:
        return None
    return WeaponLevels(parsed.weapon, parsed.levels)


def _read_weapon_levels(raw: str) -> WeaponLevels | None:
    # Object.entries / Object.fromEntries keep the JSON object's keys.
    __pragma__(
        "js",
        "{}",
        "var value; try { value = JSON.parse(raw); } catch (error) { return null; }"
        " if (typeof value !== 'object' || value === null) return null;"
        " var weapon = value.weapon, levels = value.levels;"
        " if (typeof weapon !== 'string' || typeof levels !== 'object' || levels === null)"
        " return null;"
        " var entries = Object.entries(levels);"
        " var ok = entries.every(function (entry) { var level = entry[1];"
        " return typeof level === 'number' && Number.isInteger(level) && level >= 1; });"
        " return ok ? { weapon: weapon, levels: Object.fromEntries(entries) } : null;",
    )
    return None


def load_saved_weapons(storage: KeyValueStorage, game_id: str) -> WeaponLevels | None:
    """The weapons the player kept from the last level completed, or None."""
    return parse_weapon_levels(storage.get(saved_weapons_key(game_id)))


def save_weapons(storage: KeyValueStorage, game_id: str, weapons: WeaponLevels) -> None:
    """Keeps the player's weapons when a level is completed, for the next levels."""
    storage.set(saved_weapons_key(game_id), _to_json(weapons))


def _to_json(weapons: WeaponLevels) -> str:
    __pragma__(
        "js", "{}", "return JSON.stringify({ weapon: weapons.weapon, levels: weapons.levels });"
    )
    return ""
