# Copyright (c) 2026 Renaud Guillon
"""What the brain sees of the playfield: two grids of channels and a vector of numbers.

- The **field** grid covers the whole playfield (1000 x 720) in `FIELD_ROWS` x `FIELD_COLS` cells:
  where everything is, for planning (which enemy to go for, which bonus to pick up).
- The **fovea** grid is centred on the ship, `FOVEA_SIZE` cells of `FOVEA_CELL` px each way: the
  shots close to it in detail, for dodging.
- The **state** vector: the ship (position, speed, health, lives, bombs, invincibility), its
  weapons, the level's progress, the boss fought and the level's difficulty.

Each grid has the same channels (`CHANNELS`): enemies and boss pieces, their health, the three kinds
of enemy shot (bullets, missiles, lasers, each with their direction of travel), the three kinds of
bonus, the ship itself and where the ship cannot fly.
"""

import math
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ai.game_env import BOUNDS, MAX_WEAPON_LEVEL, WEAPON_IDS, GameEnv
from debug import play_scene as play_scene_module
from game.index import GAME

CHANNELS: tuple[str, ...] = (
    "enemy",  # 0: an enemy's body (it rams the ship, and can be shot)
    "boss",  # 1: a boss's core and parts
    "health",  # 2: health left of what is there (a fraction of its full health)
    "bullet",  # 3: enemy bullets
    "bullet_vx",  # 4: their velocity across, in units of 400 px/s
    "bullet_vy",  # 5: and up
    "missile",  # 6: enemy homing missiles (they can be shot down)
    "missile_vx",  # 7
    "missile_vy",  # 8
    "laser_warning",  # 9: the warning line of a laser about to fire
    "laser_beam",  # 10: a laser beam firing
    "bonus_weapon",  # 11: bonuses
    "bonus_life",  # 12
    "bonus_bomb",  # 13
    "ship",  # 14: the player's ship
    "wall",  # 15: where the ship cannot fly
)
N_CHANNELS = len(CHANNELS)
CH = {name: i for i, name in enumerate(CHANNELS)}
FIELD_ROWS = 24
FIELD_COLS = 32
FOVEA_SIZE = 21
FOVEA_CELL = 12.0
N_STATE = 24
SPEED_UNIT = 400.0
LASER_SAMPLE = 6.0

_WIDTH = float(GAME.playfield.width)
_HEIGHT = float(GAME.playfield.height)
_CELL_W = _WIDTH / FIELD_COLS
_CELL_H = _HEIGHT / FIELD_ROWS
_BONUS_CHANNELS = {"weapon": CH["bonus_weapon"], "life": CH["bonus_life"], "bomb": CH["bonus_bomb"]}


def _can_fly(x: float, y: float) -> bool:
    if y < BOUNDS.min_y or y > BOUNDS.max_y:
        return False
    return abs(x - BOUNDS.center_x) <= BOUNDS.half_width_at(y)


def _field_walls() -> NDArray[np.float32]:
    walls = np.zeros((FIELD_ROWS, FIELD_COLS), dtype=np.float32)
    for row in range(FIELD_ROWS):
        y = _HEIGHT - (row + 0.5) * _CELL_H
        for col in range(FIELD_COLS):
            walls[row, col] = 0.0 if _can_fly((col + 0.5) * _CELL_W, y) else 1.0
    return walls


_FIELD_WALLS = _field_walls()


class _Grid:
    """A grid of cells over the playfield: `origin` its top-left corner, `cell` its cell sizes."""

    def __init__(
        self, data: NDArray[np.float32], left: float, top: float, cell_w: float, cell_h: float
    ) -> None:
        self.data = data
        self.left = left
        self.top = top
        self.cell_w = cell_w
        self.cell_h = cell_h
        self.rows = data.shape[1]
        self.cols = data.shape[2]

    def points(
        self,
        channel: int,
        xs: NDArray[np.float64],
        ys: NDArray[np.float64],
        values: NDArray[np.float64] | float = 1.0,
    ) -> None:
        """Add `values` at points (xs, ys) of the playfield: those outside the grid are left out."""
        if len(xs) == 0:
            return
        cols = np.floor((xs - self.left) / self.cell_w).astype(np.int64)
        rows = np.floor((self.top - ys) / self.cell_h).astype(np.int64)
        keep = (cols >= 0) & (cols < self.cols) & (rows >= 0) & (rows < self.rows)
        if not keep.any():
            return
        vals = values[keep] if isinstance(values, np.ndarray) else values
        np.add.at(self.data[channel], (rows[keep], cols[keep]), vals)

    def disc(self, channel: int, x: float, y: float, radius: float, value: float) -> None:
        """Set the cells a disc overlaps to at least `value`."""
        c0 = math.floor((x - radius - self.left) / self.cell_w)
        c1 = math.floor((x + radius - self.left) / self.cell_w)
        r0 = math.floor((self.top - y - radius) / self.cell_h)
        r1 = math.floor((self.top - y + radius) / self.cell_h)
        c0, c1 = max(0, c0), min(self.cols - 1, c1)
        r0, r1 = max(0, r0), min(self.rows - 1, r1)
        if c0 > c1 or r0 > r1:
            return
        cells = self.data[channel, r0 : r1 + 1, c0 : c1 + 1]
        np.maximum(cells, value, out=cells)


class Observation:
    """One observation: the `field` and `fovea` grids (channels first) and the `state` vector."""

    def __init__(
        self,
        field: NDArray[np.float32],
        fovea: NDArray[np.float32],
        state: NDArray[np.float32],
    ) -> None:
        self.field = field
        self.fovea = fovea
        self.state = state


class Scene:
    """What is on the playfield, with the level's difficulty and the share of the time left.

    `data` is as `src/debug/play_scene.py` gives it: from the Python simulation, or from the
    browser's `__GAME_TEST__.getScene()`.
    """

    def __init__(
        self, data: dict[str, Any], bullet_speed: float, fire_rate: float, time_left: float
    ) -> None:
        self.data = data
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate
        self.time_left = time_left


def _scene_object() -> dict[str, Any]:
    return {}


def _scene_set(target: dict[str, Any], key: str, value: Any) -> None:
    target[key] = value


# CPython twins of the JavaScript helpers `play_scene` builds its object with (`{}`, `o[k] = v`):
# the scene of a Python run is then the very one the browser gives.
play_scene_module.js_object = _scene_object  # type: ignore[assignment]
play_scene_module.js_set = _scene_set  # type: ignore[assignment]


def scene_of(env: GameEnv) -> Scene:
    """Return the scene of a Python episode."""
    difficulty = env.level.difficulty
    time_left = max(0.0, 1.0 - env.time / max(1.0, env.limit))
    return Scene(
        play_scene_module.play_scene(env.run),
        difficulty.bullet_speed,
        difficulty.fire_rate,
        time_left,
    )


Shot = tuple[float, float, float, float]


def _moving(shots: list[list[float]]) -> list[Shot]:
    """[x, y, heading, speed] as (x, y, vx, vy)."""
    return [(x, y, math.sin(h) * v, math.cos(h) * v) for x, y, h, v in shots]


def _draw_moving(grid: _Grid, shots: list[Shot], channel: int) -> None:
    if not shots:
        return
    arr = np.asarray(shots, dtype=np.float64)
    xs, ys = arr[:, 0], arr[:, 1]
    grid.points(channel, xs, ys)
    grid.points(channel + 1, xs, ys, arr[:, 2] / SPEED_UNIT)
    grid.points(channel + 2, xs, ys, arr[:, 3] / SPEED_UNIT)


def _draw_lasers(grid: _Grid, lasers: list[list[Any]]) -> None:
    for x, y, heading, length, firing in lasers:
        steps = max(1, int(length / LASER_SAMPLE))
        t = np.linspace(0.0, length, steps + 1)
        xs = x + t * math.sin(heading)
        ys = y + t * math.cos(heading)
        grid.points(CH["laser_beam"] if firing else CH["laser_warning"], xs, ys)


def _draw(grid: _Grid, data: dict[str, Any], moving: tuple[list[Shot], list[Shot]]) -> None:
    for x, y, radius, health, full, boss in data["targets"]:
        grid.disc(CH["boss"] if boss else CH["enemy"], x, y, radius, 1.0)
        grid.disc(CH["health"], x, y, radius, max(0.0, min(1.0, health / full)) if full else 1.0)
    _draw_moving(grid, moving[0], CH["bullet"])
    _draw_moving(grid, moving[1], CH["missile"])
    _draw_lasers(grid, data["lasers"])
    for x, y, kind in data["bonuses"]:
        channel = _BONUS_CHANNELS.get(kind)
        if channel is not None:
            grid.disc(channel, x, y, 11.0, 1.0)
    ship = data["ship"]
    grid.disc(CH["ship"], ship[0], ship[1], 8.0, 1.0)


def _fovea_walls(grid: _Grid) -> None:
    walls = grid.data[CH["wall"]]
    for row in range(grid.rows):
        y = grid.top - (row + 0.5) * grid.cell_h
        if y < BOUNDS.min_y or y > BOUNDS.max_y:
            walls[row, :] = 1.0
            continue
        half = BOUNDS.half_width_at(y)
        xs = grid.left + (np.arange(grid.cols) + 0.5) * grid.cell_w
        walls[row] = (np.abs(xs - BOUNDS.center_x) > half).astype(np.float32)


def _state(scene: Scene) -> NDArray[np.float32]:
    data = scene.data
    x, y, vx, vy, top_speed = data["ship"]
    hull = data["hull"]
    bombs = data["bombs"]
    levels = dict.fromkeys(WEAPON_IDS, 1.0)
    for weapon_id, level in data["weapons"]:
        levels[weapon_id] = float(level)
    progress, length = data["track"]
    fought, rank, boss_health, boss_full = data["boss"]
    speed = max(1.0, top_speed)
    values = [
        x / _WIDTH,
        y / _HEIGHT,
        vx / speed,
        vy / speed,
        (hull[0] / hull[1]) if hull is not None else 1.0,
        (hull[2] / 5.0) if hull is not None else 1.0,
        (bombs[0] / 5.0) if bombs is not None else 0.0,
        1.0 if hull is not None and hull[3] > 0 else 0.0,
        1.0 if bombs is not None and bombs[1] else 0.0,
        *[1.0 if data["weapon"] == w else 0.0 for w in WEAPON_IDS],
        *[levels[w] / MAX_WEAPON_LEVEL for w in WEAPON_IDS],
        progress / max(1.0, length),
        1.0 if fought else 0.0,
        1.0 if rank == "mini" else 0.0,
        1.0 if rank == "final" else 0.0,
        (boss_health / boss_full) if boss_full else 0.0,
        scene.bullet_speed - 1.0,
        scene.fire_rate - 1.0,
        scene.time_left,
        top_speed / 400.0,
    ]
    state = np.zeros(N_STATE, dtype=np.float32)
    state[: len(values)] = values
    return state


def observe_scene(scene: Scene) -> Observation:
    """Return what the brain sees of `scene`."""
    data = scene.data
    field = np.zeros((N_CHANNELS, FIELD_ROWS, FIELD_COLS), dtype=np.float32)
    field[CH["wall"]] = _FIELD_WALLS
    fovea = np.zeros((N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE), dtype=np.float32)
    ship_x, ship_y = data["ship"][0], data["ship"][1]
    half = FOVEA_SIZE * FOVEA_CELL / 2
    field_grid = _Grid(field, 0.0, _HEIGHT, _CELL_W, _CELL_H)
    fovea_grid = _Grid(fovea, ship_x - half, ship_y + half, FOVEA_CELL, FOVEA_CELL)
    moving = (_moving(data["bullets"]), _moving(data["missiles"]))
    _draw(field_grid, data, moving)
    _draw(fovea_grid, data, moving)
    _fovea_walls(fovea_grid)
    for grid in (field, fovea):
        for name in ("bullet", "missile", "laser_warning", "laser_beam"):
            np.minimum(grid[CH[name]], 3.0, out=grid[CH[name]])
    return Observation(field, fovea, _state(scene))


def observe(env: GameEnv) -> Observation:
    """Return what the brain sees of `env` now."""
    return observe_scene(scene_of(env))
