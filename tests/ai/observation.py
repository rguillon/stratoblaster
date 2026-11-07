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

import numpy as np
from numpy.typing import NDArray

from ai.game_env import BOUNDS, MAX_WEAPON_LEVEL, WEAPON_IDS, GameEnv, weapon_levels_of
from core.entities.boss import Boss
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


def _targets(env: GameEnv) -> list[tuple[float, float, float, float, bool]]:
    """Every enemy body and boss piece: x, y, radius, health fraction, whether it is a boss's."""
    out: list[tuple[float, float, float, float, bool]] = []
    for enemy in env.run.enemies.enemies:
        if enemy.gone:
            continue
        boss = isinstance(enemy, Boss)
        pieces = enemy.shot_targets if boss else [enemy]
        if boss and len(pieces) == 0:
            pieces = [enemy]
        for piece in pieces:
            full = piece.max_health if getattr(piece, "max_health", 0) else 1.0
            health = max(0.0, min(1.0, piece.health / full)) if full else 1.0
            out.append((piece.x, piece.y, piece.radius, health, boss))
    return out


def _shots(env: GameEnv) -> tuple[list[tuple[float, float, float, float]], ...]:
    shots = env.run.enemies.shots
    bullets = [
        (b.x, b.y, math.sin(b.heading) * b.speed, math.cos(b.heading) * b.speed)
        for b in shots.bullets
        if b.alive
    ]
    missiles = [
        (m.x, m.y, math.sin(m.heading) * m.speed, math.cos(m.heading) * m.speed)
        for m in shots.missiles
        if m.alive
    ]
    return bullets, missiles


def _draw_moving(grid: _Grid, shots: list[tuple[float, float, float, float]], channel: int) -> None:
    if not shots:
        return
    arr = np.asarray(shots, dtype=np.float64)
    xs, ys = arr[:, 0], arr[:, 1]
    grid.points(channel, xs, ys)
    grid.points(channel + 1, xs, ys, arr[:, 2] / SPEED_UNIT)
    grid.points(channel + 2, xs, ys, arr[:, 3] / SPEED_UNIT)


def _draw_lasers(grid: _Grid, env: GameEnv) -> None:
    for laser in env.run.enemies.shots.lasers:
        steps = max(1, int(laser.length / LASER_SAMPLE))
        t = np.linspace(0.0, laser.length, steps + 1)
        xs = laser.x + t * math.sin(laser.heading)
        ys = laser.y + t * math.cos(laser.heading)
        channel = CH["laser_beam"] if laser.phase == "firing" else CH["laser_warning"]
        grid.points(channel, xs, ys)


def _draw(
    grid: _Grid, env: GameEnv, targets: list[tuple[float, float, float, float, bool]]
) -> None:
    for x, y, radius, health, boss in targets:
        grid.disc(CH["boss"] if boss else CH["enemy"], x, y, radius, 1.0)
        grid.disc(CH["health"], x, y, radius, health)
    bullets, missiles = _shots(env)
    _draw_moving(grid, bullets, CH["bullet"])
    _draw_moving(grid, missiles, CH["missile"])
    _draw_lasers(grid, env)
    bonuses = env.run.bonuses
    if bonuses is not None:
        for bonus in bonuses.bonuses:
            channel = _BONUS_CHANNELS.get(bonus.kind)
            if channel is not None:
                grid.disc(channel, bonus.x, bonus.y, 11.0, 1.0)
    ship = env.run.ship
    grid.disc(CH["ship"], ship.x, ship.y, 8.0, 1.0)


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


def _state(env: GameEnv) -> NDArray[np.float32]:
    run = env.run
    ship = run.ship
    hull = run.hull
    state = np.zeros(N_STATE, dtype=np.float32)
    speed = max(1.0, ship.max_speed)
    weapon = run.shots.weapon.id
    levels = weapon_levels_of(run)
    fights = run.fights
    boss = fights.boss
    difficulty = env.level.difficulty
    values = [
        ship.x / _WIDTH,
        ship.y / _HEIGHT,
        ship.vx / speed,
        ship.vy / speed,
        (hull.health / hull.max_health) if hull is not None else 1.0,
        (hull.lives / 5.0) if hull is not None else 1.0,
        (run.bombs.count / 5.0) if run.bombs is not None else 0.0,
        1.0 if hull is not None and hull.invincible > 0 else 0.0,
        1.0 if run.bombs is not None and run.bombs.active is not None else 0.0,
        *[1.0 if weapon == w else 0.0 for w in WEAPON_IDS],
        *[levels[w] / MAX_WEAPON_LEVEL for w in WEAPON_IDS],
        run.track.progress / max(1.0, run.track.length_),
        1.0 if fights.active else 0.0,
        1.0 if fights.rank == "mini" else 0.0,
        1.0 if fights.rank == "final" else 0.0,
        (boss.health / boss.max_health) if boss is not None and boss.max_health else 0.0,
        difficulty.bullet_speed - 1.0,
        difficulty.fire_rate - 1.0,
        max(0.0, 1.0 - env.time / max(1.0, env.limit)),
        ship.max_speed / 400.0,
    ]
    state[: len(values)] = values
    return state


def observe(env: GameEnv) -> Observation:
    """Return what the brain sees of `env` now."""
    field = np.zeros((N_CHANNELS, FIELD_ROWS, FIELD_COLS), dtype=np.float32)
    field[CH["wall"]] = _FIELD_WALLS
    fovea = np.zeros((N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE), dtype=np.float32)
    ship = env.run.ship
    half = FOVEA_SIZE * FOVEA_CELL / 2
    field_grid = _Grid(field, 0.0, _HEIGHT, _CELL_W, _CELL_H)
    fovea_grid = _Grid(fovea, ship.x - half, ship.y + half, FOVEA_CELL, FOVEA_CELL)
    targets = _targets(env)
    _draw(field_grid, env, targets)
    _draw(fovea_grid, env, targets)
    _fovea_walls(fovea_grid)
    for grid in (field, fovea):
        for name in ("bullet", "missile", "laser_warning", "laser_beam"):
            np.minimum(grid[CH[name]], 3.0, out=grid[CH[name]])
    return Observation(field, fovea, _state(env))
