"""The lives and bombs kept between levels, ported from `app/saved-supplies.ts`. Storage key
prefixed with the game's id.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from host.key_value_storage import KeyValueStorage  # noqa: E402

__pragma__("noskip")

from core.systems.level_run_types import Supplies  # noqa: E402


def saved_supplies_key(game_id: str) -> str:
    return game_id + "_supplies"


def parse_supplies(raw: str | None) -> Supplies | None:
    """Parses stored lives and bombs (`{"lives":4,"bombs":6}`). Anything else, or an unreadable
    value, reads as None: the player starts with the game's starting lives and bombs.
    """
    if raw is None:
        return None
    parsed = _read_supplies(raw)
    if parsed is None:
        return None
    return Supplies(parsed.lives, parsed.bombs)


def _read_supplies(raw: str) -> Supplies | None:
    # JSON.parse throws a native SyntaxError, which Python `except` cannot catch under Transcrypt.
    __pragma__(
        "js",
        "{}",
        "var value; try { value = JSON.parse(raw); } catch (error) { return null; }"
        " if (typeof value !== 'object' || value === null) return null;"
        " var lives = value.lives, bombs = value.bombs;"
        " return typeof lives === 'number' && Number.isInteger(lives) && lives >= 1"
        " && typeof bombs === 'number' && Number.isInteger(bombs) && bombs >= 0"
        " ? { lives: lives, bombs: bombs } : null;",
    )
    return None


def load_saved_supplies(storage: KeyValueStorage, game_id: str) -> Supplies | None:
    """The lives and bombs the player kept from the last level completed, or None."""
    return parse_supplies(storage.get(saved_supplies_key(game_id)))


def save_supplies(storage: KeyValueStorage, game_id: str, supplies: Supplies) -> None:
    """Keeps the player's lives and bombs when a level is completed, for the next levels."""
    storage.set(saved_supplies_key(game_id), _to_json(supplies))


def _to_json(supplies: Supplies) -> str:
    __pragma__(
        "js", "{}", "return JSON.stringify({ lives: supplies.lives, bombs: supplies.bombs });"
    )
    return ""
