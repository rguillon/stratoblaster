# Copyright (c) 2026 Renaud Guillon
"""Bonuses (`specs/gameplay/bonuses.md`).

Some destroyed enemies drop one, it falls down the screen, and the ship picks it up by flying over
it.
"""

import math

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Literal, Protocol

from core.entities.enemy import DropSource
from core.math.rng import Random

# What a bonus gives when picked up (GAME-BONUS-01, GAME-BONUS-09): a weapon level, a life, a
# bomb or health (GAME-BONUS-11).
BonusKind = Literal["weapon", "life", "bomb", "heal"]


class _Point(Protocol):
    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...


# __pragma__ ("noskip")


class BonusChance:
    """Chance that a destroyed enemy drops a bonus.

    `per_health` x maxHealth, kept within [`min`, `max`], so tougher enemies drop one more often
    (GAME-BONUS-02).
    """

    def __init__(self, per_health: float, min_chance: float, max_chance: float) -> None:
        self.per_health = per_health
        self.min = min_chance
        self.max = max_chance


class LifeAndBomb:
    """A pair of numbers, one for a life and one for a bomb (GAME-BONUS-03).

    The chances of the special drops, or the points of their overflows.
    """

    def __init__(self, life: float, bomb: float) -> None:
        self.life = life
        self.bomb = bomb


class HealRules:
    """The heal bonus (GAME-BONUS-11).

    `share`: the share (0..1) of the weapon bonuses that drop as heal bonuses instead. `amount`: the
    share (0..1) of the ship's full health a heal bonus gives back.
    """

    def __init__(self, share: float, amount: float) -> None:
        self.share = share
        self.amount = amount


class BonusRules:
    """The bonus rules.

    `chance`: see `BonusChance`. `fall_speed`: speed it falls down the screen at, in logical pixels
    a second. `pickup_radius`: the ship picks a bonus up when their centres are this close.
    `special`: chances that a destroyed enemy (not a boss or one of its parts) drops a life or a
    bomb bonus (GAME-BONUS-03), drawn in that order before the weapon bonus's chance: an enemy drops
    at most one bonus. Weapon bonuses only when None. `overflow_points`: points scored for a life or
    bomb bonus picked up when the player has the most (GAME-BONUS-10). `heal`: see `HealRules`; no
    heal bonus when None.
    """

    def __init__(
        self,
        chance: BonusChance,
        fall_speed: float,
        pickup_radius: float,
        special: LifeAndBomb | None = None,
        overflow_points: LifeAndBomb | None = None,
        heal: HealRules | None = None,
    ) -> None:
        self.chance = chance
        self.fall_speed = fall_speed
        self.pickup_radius = pickup_radius
        self.special = special
        self.overflow_points = overflow_points
        self.heal = heal


class Bonus:
    """A bonus falling down the playfield.

    `age` is the seconds since it dropped (for its animation).
    """

    def __init__(self, bonus_id: int, x: float, y: float, age: float, kind: str) -> None:
        self.id = bonus_id
        self.x = x
        self.y = y
        self.age = age
        self.kind = kind


def drop_chance(rules: BonusRules, target: DropSource, scale: float = 1) -> float:
    """Return the chance (0..1) that destroying `target` drops a bonus.

    Its own chance if it has one (a boss's part, BOSS-57), the rules' otherwise, times the level's
    `scale` (D-309).
    """
    if target.drop_chance is not None:
        return target.drop_chance
    chance = rules.chance
    return scale * min(chance.max, max(chance.min, chance.per_health * target.max_health))


class BonusWorld:
    """The bonuses of a level.

    Dropped where enemies blew up (moved in sideways to where the ship can reach), falling, picked
    up by the ship or gone past the bottom edge. Pure and deterministic for a given random source
    (GAME-BONUS-05).
    """

    def __init__(
        self,
        rules: BonusRules,
        random: Random,
        reach: tuple[float, float],
        cull_margin: float,
        special_random: Random | None = None,
        heal_random: Random | None = None,
        scale: float = 1,
    ) -> None:
        """`reach`: the X range the ship can reach: bonuses drop within it.

        `cull_margin`: bonuses this far under the bottom edge are removed. `special_random`: where
        the life and bomb draws come from (GAME-BONUS-03): a source of their own, so the weapon
        bonuses drop as they did without them. `random` when None. `heal_random`: where the draw
        that turns a weapon bonus into a heal bonus comes from (GAME-BONUS-11), a source of its own
        too; `special_random` when None. `scale`: the level's factor on the enemies' chances to drop
        a bonus, weapon, life and bomb alike (`GameLevel.bonus_scale`, D-309).
        """
        self.rules = rules
        self._random = random
        self._reach = reach
        self._cull_margin = cull_margin
        self._special_random = special_random if special_random is not None else random
        self._heal_random = heal_random if heal_random is not None else self._special_random
        self.scale = scale
        self.bonuses: list[Bonus] = []
        # Bonuses picked up during the last step.
        self.picked: list[Bonus] = []
        self.dropped = 0
        self.collected = 0
        self._next_id = 1

    def drop(
        self,
        targets: Sequence[DropSource],
        special: Callable[[DropSource], bool] | None = None,
    ) -> None:
        """Each of the destroyed `targets` drops a weapon bonus with its `drop_chance`.

        Those that are `special` (enemies, not bosses or their parts) may drop a life or a bomb
        bonus instead (GAME-BONUS-03).
        """
        for target in targets:
            is_special = special(target) if special is not None else False
            kind = self._kind_for(target, is_special)
            if kind:
                self.place(kind, target)

    def place(self, kind: str, at: _Point) -> None:
        """Drop a bonus of `kind` where `at` is, within the ship's reach (GAME-BONUS-07)."""
        x_min, x_max = self._reach
        x = min(x_max, max(x_min, at.x))
        self.bonuses.append(Bonus(self._next_id, x, at.y, 0, kind))
        self._next_id += 1
        self.dropped += 1

    def _kind_for(self, target: DropSource, special: bool) -> str | None:
        """Return the kind of bonus `target` drops, if any: at most one.

        Life first, then bomb, then weapon. The weapon draw always happens, so the weapon bonuses'
        draws stay as without the others. A weapon bonus then turns into a heal bonus with the heal
        share (GAME-BONUS-11).
        """
        weapon = self._random() < drop_chance(self.rules, target, self.scale)
        odds = self.rules.special if special else None
        if odds and self._special_random() < odds.life * self.scale:
            return "life"
        if odds and self._special_random() < odds.bomb * self.scale:
            return "bomb"
        if not weapon:
            return None
        heal = self.rules.heal
        if heal is not None and self._heal_random() < heal.share:
            return "heal"
        return "weapon"

    def step(self, dt: float, ship: _Point | None = None) -> None:
        """Move the bonuses by `dt` seconds.

        The ship at `ship` (if any) picks up those it touches (GAME-BONUS-08); those past the bottom
        edge go (GAME-SCREEN-07).
        """
        fall_speed = self.rules.fall_speed
        pickup_radius = self.rules.pickup_radius
        self.picked = []
        i = len(self.bonuses) - 1
        while i >= 0:
            bonus = self.bonuses[i]
            bonus.y -= fall_speed * dt
            bonus.age += dt
            touched = (
                ship is not None and math.hypot(bonus.x - ship.x, bonus.y - ship.y) <= pickup_radius
            )
            if touched:
                self.picked.append(bonus)
            if touched or bonus.y < -self._cull_margin:
                self.bonuses.pop(i)
            i -= 1
        self.collected += len(self.picked)

    def clear(self) -> None:
        """Remove every bonus."""
        self.bonuses.clear()
        self.picked = []
