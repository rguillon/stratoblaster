# Copyright (c) 2026 Renaud Guillon
"""The game as an environment for the brain: a level run, headless, at full speed.

It builds a `LevelRun` as the game screen does (`src/app/game_play.py`), with the same playfield,
ship, weapons, bonuses, bombs, hull, bosses and camera framing (for where the ship may fly and what
is on screen), but no rendering and no clock: each `step` advances the simulation by
`frame_skip` fixed steps of 1/60 s, as fast as the CPU goes.

One level, or a campaign (D-295): the levels one after the other from the first, each cleared one
going on to the next with the weapons, lives and bombs it ended with, as the game does, until the
game is over, a level takes too long, or the last one is cleared.
"""

import functools
import math
from dataclasses import dataclass, field, replace
from typing import Any

import ai  # noqa: F401  # puts src/ and the Transcrypt stubs on the path
from config.game_controls import GAME_CONTROLS_CONFIG
from config.game_play import GAME_PLAY_CONFIG
from core.content.game_level import GameLevel
from core.entities.muzzle import PlanePoint
from core.entities.player_ship import find_player_ship, ship_max_speed_px_per_sec
from core.scenery.scenery_level import level_length
from core.systems.enemy_world import EnemyDifficulty
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelControls, LevelRunOptions, RunShip, Supplies
from core.systems.player_flight import FlightInput
from core.systems.run_arsenal import WeaponLevels
from game.config.scenery_look import PLAYFIELD_CAMERA
from game.index import GAME
from render.scenery.playfield_framing import frame_playfield, playfield_eye, visible_half_width

STEP_SECONDS = 1 / GAME_PLAY_CONFIG.step_hz
# The ship's nose above its centre (the game measures it on the 3D model; about this for each).
MUZZLE_OFFSET = 30.0
# The nine directions the brain can fly in: still, then N, NE, E, SE, S, SW, W, NW.
_DIAG = math.sqrt(0.5)
MOVES: tuple[tuple[float, float], ...] = (
    (0.0, 0.0),
    (0.0, 1.0),
    (_DIAG, _DIAG),
    (1.0, 0.0),
    (_DIAG, -_DIAG),
    (0.0, -1.0),
    (-_DIAG, -_DIAG),
    (-1.0, 0.0),
    (-_DIAG, _DIAG),
)
WEAPON_IDS: tuple[str, ...] = tuple(w.id for w in GAME.player_weapons)
SHIP_IDS: tuple[str, ...] = tuple(s.id for s in GAME.player_ships.ships)
LEVEL_IDS: tuple[str, ...] = tuple(level.id for level in GAME.game_levels)
MAX_WEAPON_LEVEL = max(len(w.levels) for w in GAME.player_weapons)


class _Record(dict[str, Any]):
    """A config record whose fields read as attributes, as JavaScript objects do in the browser."""

    __getattr__ = dict.get  # not a method calling it: read in the simulation's hottest loops


def _as_record(value: Any) -> Any:
    if isinstance(value, dict):
        return _Record({k: _as_record(v) for k, v in value.items()})
    if isinstance(value, list):
        return [_as_record(v) for v in value]
    return value


def _playable(level: GameLevel) -> GameLevel:
    """`level` with its wave script readable under CPython.

    The waves are object literals the browser reads as attributes; CPython builds them as plain
    dicts (only `record` turns them into attribute records), so they are wrapped here.
    """
    waves = [_as_record(w) if isinstance(w, dict) else w for w in level.waves]
    if all(a is b for a, b in zip(waves, level.waves, strict=True)):
        return level
    return GameLevel(level.id, level.scenery, waves, level.difficulty, level.bosses, level.runout)


_LEVELS: dict[str, GameLevel] = {level.id: _playable(level) for level in GAME.game_levels}


@functools.cache
def _tuned_level(level_id: str, factors: tuple[float, float, float]) -> GameLevel:
    """Return the level with other difficulty factors (bullet speed, fire rate, boss health)."""
    level = _LEVELS[level_id]
    return GameLevel(
        level.id,
        level.scenery,
        level.waves,
        EnemyDifficulty(*factors),
        level.bosses,
        level.runout,
    )


def level_difficulty(level_id: str) -> Any:
    """Return the level's enemy difficulty (`EnemyDifficulty`: bullet speed, fire rate, bosses)."""
    return _LEVELS[level_id].difficulty


def level_seconds(level_id: str) -> float:
    """How long the level scrolls for, bosses' fights aside."""
    scenery = _LEVELS[level_id].scenery
    return level_length(scenery) / scenery.scroll_speed


class _Bounds:
    """Where the ship may fly: what the tilted camera shows, less the margins (GAME-SCREEN-05)."""

    def __init__(self) -> None:
        screen = GAME.playfield
        margin = GAME_PLAY_CONFIG.ship_margin
        self._framing = frame_playfield(screen, PLAYFIELD_CAMERA)
        self._aspect = screen.width / screen.height
        self._side = margin.side
        self.min_y = margin.bottom
        self.max_y = screen.height - margin.top
        self.center_x = screen.width / 2
        self._height = screen.height
        framing = self._framing
        self._near = -framing.height * framing.direction[0]
        self._back = framing.back
        self._dz = framing.direction[1]
        self._tan = math.tan(framing.half_fov)

    def half_width_at(self, y: float) -> float:
        return visible_half_width(self._framing, self._aspect, y) - self._side

    def visible_half_width(self, y: float) -> float:
        return visible_half_width(self._framing, self._aspect, y)

    def in_view(self, x: float, y: float) -> bool:
        """Whether a playfield point is on screen (GAME-SCREEN-04).

        `visible_half_width`'s sums, in the same order, with its constants read once.
        """
        if y < 0 or y > self._height:
            return False
        depth = self._near + (y - self._back) * self._dz
        return abs(x - self.center_x) <= depth * self._tan * self._aspect

    @property
    def framing(self) -> Any:
        return self._framing


BOUNDS = _Bounds()


@dataclass
class EpisodeSetup:
    """How an episode starts.

    `start_time` is seconds into the level (the waves before it are skipped); `weapon_levels` the
    level of each weapon (by id), `weapon` the one in use; `lives` and `bombs` the supplies.
    `extra_seconds` is how long past the level's scroll the episode may last (boss fights).
    `difficulty`, when given, replaces the level's own: its bullet speed, fire rate and boss health
    factors (`make adjust-level` tries them, D-305); the next level of a campaign has its own.
    """

    level_id: str
    seed: int = 606
    ship_id: str = "balanced"
    weapon: str = "bullet"
    weapon_levels: dict[str, int] = field(default_factory=lambda: dict.fromkeys(WEAPON_IDS, 1))
    lives: int = 3
    bombs: int = 3
    start_time: float = 0.0
    extra_seconds: float = 240.0
    difficulty: tuple[float, float, float] | None = None


@dataclass
class Action:
    """What the brain does for one decision: a move (index in `MOVES`), a bomb, a weapon switch."""

    move: int
    bomb: bool = False
    switch: bool = False


@dataclass
class StepInfo:
    """What happened over a decision, and how the episode stands."""

    damage: float = 0.0
    lives_lost: int = 0
    score: float = 0.0
    dealt: float = 0.0
    progress: float = 0.0
    picked: list[str] = field(default_factory=list)
    bombed: bool = False
    cleared: str = ""  # the level of a campaign cleared over it (the next one then starts)
    outcome: str = ""  # "", "complete", "over" or "timeout"


@dataclass
class RewardWeights:
    """The reward of a decision: the points scored over it, and a little for staying alive (D-296).

    The best score is what the brain learns for (D-295), and what the best brain is chosen by;
    `alive` and the charges for damage only teach it sooner that it scores only while it
    survives. `alive` is worth a point a decision (15 a second of play); the health of a whole
    bar lost costs as much as 2,000 points, a life 2,000 more.
    """

    score: float = 1.0 / 2000  # per point scored
    alive: float = 0.0005  # per decision played
    damage: float = 1.0  # per bar of health lost
    life: float = 1.0  # per life lost


class GameEnv:
    """One level, or a campaign of levels, played by the brain: `step` until `done`.

    `campaign`: the levels to play in turn, from `setup`'s; a single level when empty.
    """

    def __init__(
        self, setup: EpisodeSetup, frame_skip: int = 4, campaign: tuple[str, ...] = ()
    ) -> None:
        self.first = setup
        self.setup = setup
        self.campaign = campaign
        self.frame_skip = frame_skip
        self.weights = RewardWeights()
        self.run: LevelRun = self._new_run()
        self.time = 0.0
        self.done = False
        self.outcome = ""
        self.start_progress = 0.0
        self.limit = 0.0
        self.total_damage = 0.0
        self.total_lives_lost = 0
        self.max_budget = 1.0
        self.cleared: list[str] = []
        self._banked_score = 0.0
        self.reset()

    @property
    def level(self) -> GameLevel:
        factors = self.setup.difficulty
        if factors is None:
            return _LEVELS[self.setup.level_id]
        return _tuned_level(self.setup.level_id, factors)

    @property
    def length(self) -> float:
        return self.run.track.length_

    @property
    def max_health(self) -> float:
        return self.run.hull.max_health if self.run.hull is not None else 100.0

    def _new_run(self) -> LevelRun:
        setup = self.setup
        screen = GAME.playfield
        ship_def = find_player_ship(GAME.player_ships, setup.ship_id)
        ship = RunShip(
            PlanePoint(screen.width / 2, GAME_PLAY_CONFIG.ship_start_y),
            ship_max_speed_px_per_sec(GAME.player_ships, setup.ship_id),
            GAME_CONTROLS_CONFIG.acceleration_seconds,
            MUZZLE_OFFSET,
            ship_def.max_health,
        )
        weapons = GAME.player_weapons
        levels: dict[str, float] = {k: float(v) for k, v in setup.weapon_levels.items()}
        return LevelRun(
            LevelRunOptions(
                screen,
                self.level,
                GAME.enemy_kinds,
                weapons[0],
                1,
                ship,
                BOUNDS,
                GAME_PLAY_CONFIG.cull_margin,
                GAME_PLAY_CONFIG.max_enemy_age,
                GAME_PLAY_CONFIG.end_wait,
                setup.seed,
                weapons,
                WeaponLevels(setup.weapon, levels),
                Supplies(setup.lives, setup.bombs),
                playfield_eye(screen, BOUNDS.framing),
                BOUNDS.in_view,
                GAME.bonuses,
                GAME.bombs,
                GAME.hull,
                GAME.boss_kinds,
                GAME.boss_fights,
                None,
                None,  # no scripted fly-in / fly-off: the brain flies from the first step
            )
        )

    def reset(self) -> None:
        """Start the episode again from its setup (a campaign from its first level)."""
        self.setup = self.first
        self.cleared = []
        self._banked_score = 0.0
        self.total_damage = 0.0
        self.total_lives_lost = 0
        self._start_level()

    @property
    def score(self) -> float:
        """The points scored since the episode started (over every level of a campaign)."""
        return self._banked_score + self.run.score

    def next_level(self) -> str | None:
        """Return the level of the campaign after the one played, None after the last (or alone)."""
        if self.setup.level_id not in self.campaign:
            return None
        index = self.campaign.index(self.setup.level_id) + 1
        return self.campaign[index] if index < len(self.campaign) else None

    def _go_on(self, level_id: str) -> None:
        """Start `level_id` with what the level cleared ended with (GAME-WPN-15, GAME-LIFE-12)."""
        run = self.run
        self.cleared.append(self.setup.level_id)
        self._banked_score += run.score
        weapons = run.arsenal.snapshot()
        levels = weapon_levels_of(run)
        supplies = run.supplies
        self.setup = replace(
            self.setup,
            level_id=level_id,
            seed=self.first.seed + 7919 * len(self.cleared),
            weapon=weapons.weapon,
            weapon_levels={k: int(v) for k, v in levels.items()},
            lives=int(supplies.lives) if supplies is not None else self.setup.lives,
            bombs=int(supplies.bombs) if supplies is not None else self.setup.bombs,
            start_time=0.0,
            difficulty=None,
        )
        self._start_level()

    def _start_level(self) -> None:
        """Start the level of `setup`."""
        self.run = self._new_run()
        if self.setup.start_time > 0:
            self.run.seek(self.setup.start_time)
        self.time = 0.0
        self.done = False
        self.outcome = ""
        self.start_progress = self.run.track.progress
        remaining = level_seconds(self.setup.level_id) - self.setup.start_time
        self.limit = max(30.0, remaining) + self.setup.extra_seconds
        self.max_budget = self.health_budget()

    def health_budget(self) -> float:
        """Return the health the ship has left over all its lives."""
        hull = self.run.hull
        if hull is None or hull.lives <= 0:
            return 0.0
        return (hull.lives - 1) * hull.max_health + hull.health

    @property
    def progress_fraction(self) -> float:
        """How far through the level the episode went (0 at its start, 1 at the end)."""
        span = self.length - self.start_progress
        if self.outcome == "complete":
            return 1.0
        return 0.0 if span <= 0 else (self.run.track.progress - self.start_progress) / span

    def step(self, action: Action) -> tuple[float, StepInfo]:
        """Play one decision: `frame_skip` steps of the simulation. Returns the reward and info."""
        run = self.run
        info = StepInfo()
        hull = run.hull
        lives_before = hull.lives if hull is not None else 0
        budget_before = self.health_budget()
        score_before = run.score
        dealt_before = run.shots.total_damage
        progress_before = run.track.progress
        bombs_before = run.bombs.fired if run.bombs is not None else 0
        dx, dy = MOVES[action.move]
        move = FlightInput(dx, dy)
        for i in range(self.frame_skip):
            controls = LevelControls(move, True, action.switch and i == 0, action.bomb and i == 0)
            run.step(STEP_SECONDS, controls)
            self.time += STEP_SECONDS
            if run.bonuses is not None:
                info.picked.extend(b.kind for b in run.bonuses.picked)
            if run.phase in ("complete", "over"):
                break
        info.lives_lost = int(lives_before - (hull.lives if hull is not None else 0))
        # A life bonus raises the budget: only what was lost counts as damage.
        info.damage = max(0.0, budget_before - self.health_budget())
        info.score = run.score - score_before
        info.dealt = run.shots.total_damage - dealt_before
        info.progress = run.track.progress - progress_before
        info.bombed = (run.bombs.fired if run.bombs is not None else 0) > bombs_before
        if run.phase == "complete":
            info.outcome = "complete"
        elif run.phase == "over":
            info.outcome = "over"
        elif self.time >= self.limit:
            info.outcome = "timeout"
        self.total_damage += info.damage
        self.total_lives_lost += info.lives_lost
        following = self.next_level() if info.outcome == "complete" else None
        if following is not None:
            info.cleared = self.setup.level_id
            info.outcome = ""
            self._go_on(following)
        if info.outcome:
            self.done = True
            self.outcome = info.outcome
        return self.reward(info), info

    def reward(self, info: StepInfo) -> float:
        w = self.weights
        reward = w.score * info.score + w.alive
        reward -= w.damage * info.damage / self.max_health
        return reward - w.life * info.lives_lost


def weapon_levels_of(run: LevelRun) -> dict[str, float]:
    """Return the level of each weapon now (that of a weapon not used yet is 1)."""
    levels = dict.fromkeys(WEAPON_IDS, 1.0)
    for key, value in run.arsenal.snapshot().levels.items():
        levels[key] = float(value)
    return levels
