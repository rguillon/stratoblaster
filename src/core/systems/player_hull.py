# Copyright (c) 2026 Renaud Guillon
"""The player's health and lives (`specs/gameplay/lives-and-damage.md`)."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Literal

HullEvent = Literal["ignored", "hit", "lifeLost", "gameOver"]
# __pragma__ ("noskip")


INFINITY = float("Infinity")


class HullDamage:
    """Damage of an enemy bullet, a missile, a laser beam (once per beam).

    And a collision (GAME-LIFE-03).
    """

    def __init__(self, bullet: float, missile: float, laser: float, collision: float) -> None:
        self.bullet = bullet
        self.missile = missile
        self.laser = laser
        self.collision = collision


class HullRules:
    """What hurts the player and how much.

    And its lives (GAME-LIFE-02, GAME-LIFE-03; phase 6 review).

    `max_lives`: most lives the player can have with life bonuses (GAME-BONUS-10); no limit when
    None.
    """

    def __init__(
        self,
        lives: float,
        invincible_seconds: float,
        hit_radius: float,
        damage: HullDamage,
        ram_damage: float,
        max_lives: float | None = None,
    ) -> None:
        """`lives`: lives at the start of a level (GAME-LIFE-02).

        `invincible_seconds`: seconds the ship cannot be hurt after a hit (GAME-LIFE-07).
        `hit_radius`: radius of the ship's hitbox, much smaller than its model (GAME-SHIP-06).
        `ram_damage`: damage an enemy takes when the ship rams it (GAME-LIFE-05).
        """
        self.lives = lives
        self.invincible_seconds = invincible_seconds
        self.hit_radius = hit_radius
        self.damage = damage
        self.ram_damage = ram_damage
        self.max_lives = max_lives


class PlayerHull:
    """The player ship's health and lives (GAME-LIFE-01, GAME-LIFE-08).

    A hit takes health and makes the ship invincible for a while; when the health runs out a life is
    lost and the ship comes back with full health (still invincible); with no life left, the game is
    over. Pure.
    """

    def __init__(self, rules: HullRules, max_health: float, lives: float | None = None) -> None:
        """Start with `lives`: the rules' (GAME-LIFE-02), or those kept from the level before."""
        self._rules = rules
        self.max_health = max_health
        self.health = max_health
        self.lives = rules.lives if lives is None else lives
        # Seconds of invincibility left.
        self.invincible = 0.0

    @property
    def out(self) -> bool:
        """Whether the game is over (no life left)."""
        return self.lives <= 0

    def hit(self, damage: float) -> HullEvent:
        """Take `damage`, unless invincible or out."""
        if self.invincible > 0 or self.out:
            return "ignored"
        self.health = max(0, self.health - damage)
        self.invincible = self._rules.invincible_seconds
        if self.health > 0:
            return "hit"
        self.lives -= 1
        if self.lives <= 0:
            return "gameOver"
        self.health = self.max_health
        return "lifeLost"

    def add_life(self) -> bool:
        """Return a life bonus (GAME-BONUS-09): one more life, up to the most if any.

        Returns whether it was added.
        """
        most = self._rules.max_lives if self._rules.max_lives is not None else INFINITY
        if self.out or self.lives >= most:
            return False
        self.lives += 1
        return True

    def step(self, dt: float) -> None:
        """Count down the invincibility."""
        self.invincible = max(0, self.invincible - dt)
