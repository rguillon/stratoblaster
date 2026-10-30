"""Bonuses (phase 6 review, GD-31, P11-R07), ported from `core/systems/bonus-world.ts`.

Some destroyed enemies drop one, it falls down the screen, and the ship picks it up by flying over
it.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Literal, Protocol  # noqa: E402

from core.entities.enemy import DropSource  # noqa: E402
from core.math.rng import Random  # noqa: E402

# What a bonus gives when picked up: a weapon level (phase 6 review, GD-31), a life (GD-20) or a
# bomb (GD-32, P11-R07).
BonusKind = Literal["weapon", "life", "bomb"]


class _Point(Protocol):
    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...


__pragma__("noskip")


class BonusChance:
    """Chance that a destroyed enemy drops a bonus: `per_health` × maxHealth, kept within
    [`min`, `max`], so tougher enemies drop one more often.
    """

    def __init__(self, per_health: float, min_chance: float, max_chance: float) -> None:
        self.per_health = per_health
        self.min = min_chance
        self.max = max_chance


class LifeAndBomb:
    """A pair of numbers, one for a life and one for a bomb (P11-R07): the chances of the special
    drops, or the points of their overflows.
    """

    def __init__(self, life: float, bomb: float) -> None:
        self.life = life
        self.bomb = bomb


class BonusRules:
    """The bonus rules.

    `chance`: see `BonusChance`. `fall_speed`: speed it falls down the screen at, in logical pixels
    a second. `pickup_radius`: the ship picks a bonus up when their centres are this close.
    `special`: chances that a destroyed enemy (not a boss or one of its parts) drops a life or a
    bomb bonus (P11-R07), drawn in that order before the weapon bonus's chance: an enemy drops at
    most one bonus. Weapon bonuses only when None. `overflow_points`: points scored for a life or
    bomb bonus picked up when the player has the most (P11-R07).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        chance: BonusChance,
        fall_speed: float,
        pickup_radius: float,
        special: LifeAndBomb | None = None,
        overflow_points: LifeAndBomb | None = None,
    ) -> None:
        self.chance = chance
        self.fall_speed = fall_speed
        self.pickup_radius = pickup_radius
        self.special = special
        self.overflow_points = overflow_points


class Bonus:
    """A bonus falling down the playfield. `age` is the seconds since it dropped (for its
    animation).
    """

    def __init__(self, id: int, x: float, y: float, age: float, kind: str) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.age = age
        self.kind = kind


def drop_chance(rules: BonusRules, target: DropSource) -> float:
    """The chance (0..1) that destroying `target` drops a bonus: its own chance if it has one (a
    boss's part, P07-R07), the rules' otherwise.
    """
    if target.drop_chance is not None:
        return target.drop_chance
    chance = rules.chance
    return min(chance.max, max(chance.min, chance.per_health * target.max_health))


class BonusWorld:
    """The bonuses of a level: dropped where enemies blew up (moved in sideways to where the ship
    can reach), falling, picked up by the ship or gone past the bottom edge. Pure and deterministic
    for a given random source.
    """

    def __init__(
        self,
        rules: BonusRules,
        random: Random,
        reach: tuple[float, float],
        cull_margin: float,
        special_random: Random | None = None,
    ) -> None:
        """`reach`: the X range the ship can reach: bonuses drop within it. `cull_margin`: bonuses
        this far under the bottom edge are removed. `special_random`: where the life and bomb draws
        come from (P11-R07): a source of their own, so the weapon bonuses drop as they did without
        them. `random` when None.
        """
        self.rules = rules
        self._random = random
        self._reach = reach
        self._cull_margin = cull_margin
        self._special_random = special_random if special_random is not None else random
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
        """Each of the destroyed `targets` drops a weapon bonus with its `drop_chance`; those that
        are `special` (enemies, not bosses or their parts) may drop a life or a bomb bonus instead
        (P11-R07).
        """
        for target in targets:
            is_special = special(target) if special is not None else False
            kind = self._kind_for(target, is_special)
            if kind:
                self.place(kind, target)

    def place(self, kind: str, at: _Point) -> None:
        """Drops a bonus of `kind` where `at` is, within the ship's reach."""
        x_min, x_max = self._reach
        x = min(x_max, max(x_min, at.x))
        self.bonuses.append(Bonus(self._next_id, x, at.y, 0, kind))
        self._next_id += 1
        self.dropped += 1

    def _kind_for(self, target: DropSource, special: bool) -> str | None:
        """The kind of bonus `target` drops, if any: at most one; life first, then bomb, then
        weapon.
        The weapon draw always happens, so the weapon bonuses' draws stay as without the others.
        """
        weapon = self._random() < drop_chance(self.rules, target)
        odds = self.rules.special if special else None
        if odds and self._special_random() < odds.life:
            return "life"
        if odds and self._special_random() < odds.bomb:
            return "bomb"
        return "weapon" if weapon else None

    def step(self, dt: float, ship: _Point | None = None) -> None:
        """Moves the bonuses by `dt` seconds; the ship at `ship` (if any) picks up those it
        touches."""
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
        """Removes every bonus."""
        self.bonuses.clear()
        self.picked = []
