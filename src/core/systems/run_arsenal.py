"""The weapons of a run (phase 6 review)

The player switches between the weapons in order, each keeping its own level, and bonuses raise the
one in use. Its `snapshot` is what a checkpoint keeps (P07-R08).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.entities.weapon import WeaponDefinition  # noqa: E402
from core.systems.shot_world import ShotWorld  # noqa: E402

__pragma__("noskip")


class WeaponLevels:
    """The weapon in use (its id) and the level of each weapon used so far, by weapon id."""

    def __init__(self, weapon: str, levels: dict[str, float]) -> None:
        self.weapon = weapon
        self.levels = levels


class _LevelEntry:
    """The level of one weapon used so far (the weapon is compared by identity)."""

    def __init__(self, weapon: WeaponDefinition, level: float) -> None:
        self.weapon = weapon
        self.level = level


class RunArsenal:
    """The weapons of a run: `shots` is the ship's shot world, `weapons` the ones the player can
    switch between, and `start_level` the level a weapon starts at when first used.
    """

    def __init__(
        self,
        shots: ShotWorld,
        weapons: Sequence[WeaponDefinition],
        start_level: float,
    ) -> None:
        self._shots = shots
        self._weapons = list(weapons)
        self._start_level = start_level
        # The level of each weapon used so far. A list, not a map: weapons are compared by identity.
        self._levels: list[_LevelEntry] = []

    def switch_weapon(self) -> None:
        """The next weapon of the list, at its own level; shots in flight keep flying."""
        index = -1
        for i in range(len(self._weapons)):
            if self._weapons[i] is self._shots.weapon:
                index = i
                break
        next_weapon = self._shots.weapon
        if len(self._weapons) > 0:
            next_weapon = self._weapons[(index + 1) % len(self._weapons)]
        self._set_level(self._shots.weapon, self._shots.level)
        saved = self._level_of(next_weapon)
        self._shots.select(next_weapon, saved if saved is not None else self._start_level)

    def level_up(self, count: float) -> None:
        """`count` levels more for the weapon in use, up to its last; the new level fires at
        once."""
        if count > 0:
            self._shots.select(self._shots.weapon, self._shots.level + count)

    def snapshot(self) -> WeaponLevels:
        self._set_level(self._shots.weapon, self._shots.level)
        levels: dict[str, float] = {}
        for entry in self._levels:
            levels[entry.weapon.id] = entry.level
        return WeaponLevels(self._shots.weapon.id, levels)

    def restore(self, saved: WeaponLevels) -> None:
        """Back to the weapons of a `snapshot`."""
        self._levels = []
        for weapon in self._weapons:
            if weapon.id in saved.levels:
                self._set_level(weapon, saved.levels[weapon.id])
        weapon = self._shots.weapon
        for candidate in self._weapons:
            if candidate.id == saved.weapon:
                weapon = candidate
                break
        level = self._level_of(weapon)
        self._shots.select(weapon, level if level is not None else self._start_level)

    def _set_level(self, weapon: WeaponDefinition, level: float) -> None:
        for entry in self._levels:
            if entry.weapon is weapon:
                entry.level = level
                return
        self._levels.append(_LevelEntry(weapon, level))

    def _level_of(self, weapon: WeaponDefinition) -> float | None:
        for entry in self._levels:
            if entry.weapon is weapon:
                return entry.level
        return None
