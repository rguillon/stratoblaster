# Copyright (c) 2026 Renaud Guillon
"""The storage of the AI player's page (`?ai`, D-294): in memory, every level a fresh start.

The AI player starts each level as from the level select with nothing kept: the starting lives
and bombs, every weapon at its first level, and more only from the bonuses it picks up. So the
weapons and supplies kept from the levels before (GAME-WPN-15, GAME-LIFE-12) are never stored;
everything else (the volumes, the last ship, the high score) is kept for the page's life only. The
player's own cookies are neither read nor written: the AI's games do not change the player's.
"""

from app.saved_supplies import saved_supplies_key
from app.saved_weapons import saved_weapons_key


class FreshStartStorage:
    """A `KeyValueStorage` in memory that keeps no weapons or supplies for `game_id`."""

    def __init__(self, game_id: str) -> None:
        self._values: dict[str, str] = {}
        self._never = [saved_weapons_key(game_id), saved_supplies_key(game_id)]

    def get(self, key: str) -> str | None:
        """Return the value stored under `key`, or None."""
        return self._values.get(key)

    def set(self, key: str, value: str) -> None:
        """Store `value` under `key`, unless it is kept weapons or supplies."""
        if key not in self._never:
            self._values[key] = value
