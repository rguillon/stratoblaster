# Copyright (c) 2026 Renaud Guillon
"""The data a level run takes and gives (`specs/gameplay/level-flow.md`).

The options are passed to `LevelRun` in the positional order of its constructor (see
`LevelRunOptions`).
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Literal

from core.entities.enemy import EnemyKindDefinition
from core.entities.muzzle import PlanePoint, PlayfieldEye
from core.entities.weapon import WeaponDefinition
from core.systems.bonus_world import BonusRules
from core.systems.boss_fights import BossFightRules, BossKindDefinition
from core.systems.player_bombs import BombRules
from core.systems.player_flight import FlightBounds, FlightInput
from core.systems.player_hull import HullRules
from core.systems.run_arsenal import WeaponLevels
from core.systems.ship_journey import JourneyRules

if TYPE_CHECKING:
    from collections.abc import Callable

    from core.content.game_definition import LogicalScreen
    from core.content.game_level import GameLevel
# Where a level stands (GAME-LEVEL-10); `over` once the player has lost every life (GAME-LIFE-09).
LevelPhase = Literal["playing", "clearing", "complete", "over"]
# What a hit that landed on the player is: see `PlayerHitKind` (player_hits).
PlayerHitKind = Literal["bullet", "missile", "laser", "collision"]
HullEvent = Literal["ignored", "hit", "lifeLost", "gameOver"]
# __pragma__ ("noskip")


class LevelCheckpoint:
    """Where a level can start again once its mini boss is destroyed (GAME-LEVEL-09).

    The level's progress just after it, the bosses passed, and the player's weapons at that moment.
    `score` is the score when the mini boss was destroyed: a Continue starts from it
    (GAME-SCORE-06).
    """

    def __init__(
        self, progress: float, bosses_passed: int, weapons: "WeaponLevels", score: float
    ) -> None:
        self.progress = progress
        self.bosses_passed = bosses_passed
        self.weapons = weapons
        self.score = score


class LevelResult:
    """What the "Level complete" (or "Game over") overlay shows (GAME-LEVEL-13).

    `outcome`: whether the level was completed, or the game is over (phase 6 review).
    `new_high_score` is set by the app when `score` beat the saved high score (GAME-SCORE-05).
    `checkpoint`: when the game is over after the mini boss, where it can go on from (GAME-LIFE-11).
    """

    def __init__(
        self,
        level_id: str,
        destroyed: int,
        spawned: int,
        outcome: str,
        score: float,
        new_high_score: bool | None = None,
        checkpoint: LevelCheckpoint | None = None,
    ) -> None:
        self.level_id = level_id
        self.destroyed = destroyed
        self.spawned = spawned
        self.outcome = outcome
        self.score = score
        self.new_high_score = new_high_score
        self.checkpoint = checkpoint


class LandedHit:
    """A hit that landed on the player during a step, and what it did."""

    def __init__(self, kind: str, x: float, y: float, event: str) -> None:
        self.kind = kind
        self.x = x
        self.y = y
        self.event = event


class LevelControls:
    """The player's controls for one step.

    `move` is the direction to fly in; `switch_weapon` (GAME-WPN-13) switches to the next weapon of
    `LevelRunOptions.weapons`; `bomb` (GAME-BOMB-03) sets a bomb off, once per press.
    """

    def __init__(
        self,
        move: "FlightInput",
        fire: bool,
        switch_weapon: bool | None = None,
        bomb: bool | None = None,
    ) -> None:
        self.move = move
        self.fire = fire
        self.switch_weapon = switch_weapon
        self.bomb = bomb


class RunShip:
    """The player ship of a run. Shots leave `muzzle_offset` above the ship's centre (its nose).

    `max_health` is its health (GAME-SHIP-03); 100 when None.
    """

    def __init__(
        self,
        start: PlanePoint,
        max_speed: float,
        acceleration_seconds: float,
        muzzle_offset: float,
        max_health: float | None = None,
    ) -> None:
        self.start = start
        self.max_speed = max_speed
        self.acceleration_seconds = acceleration_seconds
        self.muzzle_offset = muzzle_offset
        self.max_health = max_health


class Supplies:
    """The player's lives and bombs, kept from one level to the next (GAME-LIFE-12)."""

    def __init__(self, lives: float, bombs: float) -> None:
        self.lives = lives
        self.bombs = bombs


class LevelRunOptions:
    """What a level run takes.

    Its constructor takes these in order: the required ones first (`screen` to `seed`, with
    `weapon_level` and `max_enemy_age` / `end_wait` as numbers), then the optional ones, each `None`
    when omitted: `weapons` (the weapons the player can switch between, in order, each starting at
    `weapon_level`; only `weapon` when None), `start_weapons` (the weapons kept from the levels
    completed before), `start_supplies`, `eye` (the camera's eye, from which enemy shots are seen
    leaving their raised muzzles), `in_view` (whether a point of the playfield is on screen; the
    playfield's rectangle when None), `bonuses`, `bombs`, `hull` (the player cannot be hurt when
    None), `boss_kinds`, `boss_rules`, `checkpoint` (GAME-LIFE-11) and `journey` (the ship rises
    into the level and flies off it; it is at its start when None).
    """

    def __init__(
        self,
        screen: "LogicalScreen",
        level: "GameLevel",
        kinds: list[EnemyKindDefinition],
        weapon: WeaponDefinition,
        weapon_level: int,
        ship: RunShip,
        bounds: FlightBounds,
        cull_margin: float,
        max_enemy_age: float,
        end_wait: float,
        seed: int,
        weapons: list[WeaponDefinition] | None = None,
        start_weapons: WeaponLevels | None = None,
        start_supplies: Supplies | None = None,
        eye: PlayfieldEye | None = None,
        in_view: "Callable[[float, float], bool] | None" = None,
        bonuses: BonusRules | None = None,
        bombs: BombRules | None = None,
        hull: HullRules | None = None,
        boss_kinds: list[BossKindDefinition] | None = None,
        boss_rules: BossFightRules | None = None,
        checkpoint: LevelCheckpoint | None = None,
        journey: JourneyRules | None = None,
    ) -> None:
        self.screen = screen
        self.level = level
        self.kinds = kinds
        self.weapon = weapon
        self.weapon_level = weapon_level
        self.ship = ship
        self.bounds = bounds
        self.cull_margin = cull_margin
        self.max_enemy_age = max_enemy_age
        self.end_wait = end_wait
        self.seed = seed
        self.weapons = weapons
        self.start_weapons = start_weapons
        self.start_supplies = start_supplies
        self.eye = eye
        self.in_view = in_view
        self.bonuses = bonuses
        self.bombs = bombs
        self.hull = hull
        self.boss_kinds = boss_kinds
        self.boss_rules = boss_rules
        self.checkpoint = checkpoint
        self.journey = journey
