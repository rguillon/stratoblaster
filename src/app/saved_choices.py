"""What the menus keep between visits: the high score and the last ship, ported from
`app/saved-choices.ts`. Keys are prefixed with the game's id so several games can share a domain.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from host.key_value_storage import KeyValueStorage  # noqa: E402

__pragma__("noskip")


class SavedChoices:
    """What the menus read from storage at start-up."""

    def __init__(self, high_score: float, last_ship_id: str | None) -> None:
        # Best score so far, 0 when none or unreadable (P01-R04).
        self.high_score = high_score
        # Ship chosen last time (P01-R14), or None.
        self.last_ship_id = last_ship_id


class ChoiceKeys:
    """The storage keys of a game's choices."""

    def __init__(self, high_score: str, last_ship: str) -> None:
        self.high_score = high_score
        self.last_ship = last_ship


def saved_choice_keys(game_id: str) -> ChoiceKeys:
    return ChoiceKeys(game_id + "_high_score", game_id + "_last_ship")


def parse_high_score(raw: str | None) -> float:
    """Parses a stored high score. Anything but a plain non-negative integer reads as 0."""
    if raw is None:
        return 0
    return _plain_score(raw)


def _plain_score(raw: str) -> float:
    # /^\d{1,15}$/ on the trimmed text, as in the TypeScript (a regular expression is JavaScript).
    __pragma__(
        "js", "{}", "var text = raw.trim(); return /^\\d{1,15}$/.test(text) ? Number(text) : 0;"
    )
    return 0


def load_saved_choices(storage: KeyValueStorage, game_id: str) -> SavedChoices:
    keys = saved_choice_keys(game_id)
    return SavedChoices(parse_high_score(storage.get(keys.high_score)), storage.get(keys.last_ship))


def save_last_ship(storage: KeyValueStorage, game_id: str, ship_id: str) -> None:
    storage.set(saved_choice_keys(game_id).last_ship, ship_id)


def save_high_score(storage: KeyValueStorage, game_id: str, score: float) -> None:
    """Saves `score` as the new high score (GD-51, P11-R03)."""
    storage.set(saved_choice_keys(game_id).high_score, str(max(0, math.floor(score))))
