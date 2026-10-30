"""The data a level run takes and gives (P06-R03)

The options are passed to `LevelRun` in the positional order of its constructor (see
`LevelRunOptions`).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Literal  # noqa: E402

from core.content.game_definition import LogicalScreen  # noqa: E402
from core.content.game_level import GameLevel  # noqa: E402
from core.entities.enemy import EnemyKindDefinition  # noqa: E402
from core.entities.muzzle import PlanePoint, PlayfieldEye  # noqa: E402
from core.entities.weapon import WeaponDefinition  # noqa: E402
from core.systems.bonus_world import BonusRules  # noqa: E402
from core.systems.boss_fights import BossFightRules, BossKindDefinition  # noqa: E402
from core.systems.player_bombs import BombRules  # noqa: E402
from core.systems.player_flight import FlightBounds, FlightInput  # noqa: E402
from core.systems.player_hull import HullRules  # noqa: E402
from core.systems.run_arsenal import WeaponLevels  # noqa: E402
from core.systems.ship_journey import JourneyRules  # noqa: E402

# Where a level stands (P06-R03); `over` once the player has lost every life (GD-20).
LevelPhase = Literal["playing", "clearing", "complete", "over"]
# What a hit that landed on the player is: see `PlayerHitKind` (player_hits).
PlayerHitKind = Literal["bullet", "missile", "laser", "collision"]
HullEvent = Literal["ignored", "hit", "lifeLost", "gameOver"]

__pragma__("noskip")


class LevelCheckpoint:
    """Where a level can start again once its mini boss is destroyed (P07-R08, GD-42): the level's
    progress just after it, the bosses passed, and the player's weapons at that moment. `score` is
    the score when the mini boss was destroyed: a Continue starts from it (P11-R04).
    """

    def __init__(
        self, progress: float, bosses_passed: int, weapons: "WeaponLevels", score: float
    ) -> None:
        self.progress = progress
        self.bosses_passed = bosses_passed
        self.weapons = weapons
        self.score = score


class LevelResult:
    """What the "Level complete" (or "Game over") overlay shows (P06-R03). `outcome`: whether the
    level was completed, or the game is over (phase 6 review). `new_high_score` is set by the app
    when `score` beat the saved high score (P11-R03). `checkpoint`: when the game is over after the
    mini boss, where it can go on from (P07-R08).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
    """The player's controls for one step: `move` is the direction to fly in; `switch_weapon` (phase
    6 review) switches to the next weapon of `LevelRunOptions.weapons`; `bomb` (P11-R05) sets a bomb
    off, once per press.
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
    `max_health` is its health (GD-20); 100 when None.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
    """The player's lives and bombs, kept from one level to the next (reviewer, 2026-10-28)."""

    def __init__(self, lives: float, bombs: float) -> None:
        self.lives = lives
        self.bombs = bombs


class LevelRunOptions:
    """What a level run takes. Its constructor takes these in order: the required ones first
    (`screen` to `seed`, with `weapon_level` and `max_enemy_age` / `end_wait` as numbers), then the
    optional ones, each `None` when omitted: `weapons` (the weapons the player can switch between,
    in order, each starting at `weapon_level`; only `weapon` when None), `start_weapons` (the
    weapons kept from the levels completed before), `start_supplies`, `eye` (the camera's eye, from
    which enemy shots are seen leaving their raised muzzles), `in_view` (whether a point of the
    playfield is on screen; the playfield's rectangle when None), `bonuses`, `bombs`, `hull` (the
    player cannot be hurt when None), `boss_kinds`, `boss_rules`, `checkpoint` (P07-R08) and
    `journey` (the ship rises into the level and flies off it; it is at its start when None).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
