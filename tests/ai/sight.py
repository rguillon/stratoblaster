# Copyright (c) 2026 Renaud Guillon
"""What the brain sees of the playfield, in pure Python: the workers build it under PyPy (D-301).

Two grids of channels and a vector of numbers:

- The **field** grid covers the whole playfield in `FIELD_ROWS` x `FIELD_COLS` square cells:
  where everything is, for planning (which enemy to go for, which bonus to pick up).
- The **fovea** grid is centred on the ship, `FOVEA_SIZE` cells of `FOVEA_CELL` px each way: the
  shots close to it in detail, for dodging.
- The **state** vector: the ship (position, speed, health, lives, bombs, invincibility), its
  weapons, the level's progress, the boss fought and the level's difficulty.

Each grid has the same channels (`CHANNELS`): enemies and boss pieces, their health, the three kinds
of enemy shot (bullets, missiles, lasers, each with their direction of travel), the four kinds of
bonus, the ship itself and where the ship cannot fly.

The grids are mostly empty, so a `Sight` holds only the cells that are not zero, by their index in
the flat grid (channel, then row, then column): the field's walls, which never change, are in
`FIELD_WALLS` rather than in each sight. `observation.py` makes numpy arrays of them for PyTorch;
the workers write them straight into the shared rollout (`rollout_layout.py`).
"""

import math
from typing import Any

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
    "bonus_heal",  # 16: healing bonuses (D-282; last, so the brains before it load, see `brain.py`)
)
N_CHANNELS = len(CHANNELS)
CH = {name: i for i, name in enumerate(CHANNELS)}
FIELD_ROWS = 24
WIDTH = float(GAME.playfield.width)
HEIGHT = float(GAME.playfield.height)
# Square cells: 18 columns of 30 px on the 540 x 720 playfield.
FIELD_COLS = round(FIELD_ROWS * WIDTH / HEIGHT)
FOVEA_SIZE = 21
FOVEA_CELL = 12.0
N_STATE = 24
# Where the state vector holds the bombs left (/5) and whether one is going off (D-315).
STATE_BOMBS = 6
STATE_BOMB_ACTIVE = 8
SPEED_UNIT = 400.0
LASER_SAMPLE = 6.0
# The channels of counts (shots, laser samples): at most this many in a cell.
MOST = 3.0
CELL_W = WIDTH / FIELD_COLS
CELL_H = HEIGHT / FIELD_ROWS
FIELD_CELLS = N_CHANNELS * FIELD_ROWS * FIELD_COLS
FOVEA_CELLS = N_CHANNELS * FOVEA_SIZE * FOVEA_SIZE

_BONUS_CHANNELS = {
    "weapon": CH["bonus_weapon"],
    "life": CH["bonus_life"],
    "bomb": CH["bonus_bomb"],
    "heal": CH["bonus_heal"],
}
_COUNTED = tuple(CH[name] for name in ("bullet", "missile", "laser_warning", "laser_beam"))


def _can_fly(x: float, y: float) -> bool:
    if y < BOUNDS.min_y or y > BOUNDS.max_y:
        return False
    return abs(x - BOUNDS.center_x) <= BOUNDS.half_width_at(y)


def _field_walls() -> dict[int, float]:
    walls: dict[int, float] = {}
    base = CH["wall"] * FIELD_ROWS * FIELD_COLS
    for row in range(FIELD_ROWS):
        y = HEIGHT - (row + 0.5) * CELL_H
        for col in range(FIELD_COLS):
            if not _can_fly((col + 0.5) * CELL_W, y):
                walls[base + row * FIELD_COLS + col] = 1.0
    return walls


# The field's walls: the same in every sight (where the ship cannot fly does not move).
FIELD_WALLS = _field_walls()


class _Grid:
    """A grid of cells over the playfield, its non-zero cells in `cells` by flat index.

    `left`, `top`: its top-left corner on the playfield; `cell_w`, `cell_h`: its cells' sizes.
    """

    def __init__(
        self, rows: int, cols: int, left: float, top: float, cell_w: float, cell_h: float
    ) -> None:
        self.cells: dict[int, float] = {}
        self.rows = rows
        self.cols = cols
        self.plane = rows * cols
        self.left = left
        self.top = top
        self.cell_w = cell_w
        self.cell_h = cell_h

    def add(self, channel: int, x: float, y: float, value: float) -> None:
        """Add `value` at a point of the playfield (left out when it is off the grid)."""
        col = math.floor((x - self.left) / self.cell_w)
        row = math.floor((self.top - y) / self.cell_h)
        if 0 <= col < self.cols and 0 <= row < self.rows:
            index = channel * self.plane + row * self.cols + col
            cells = self.cells
            cells[index] = cells.get(index, 0.0) + value

    def moving(self, channel: int, shot: list[float]) -> None:
        """Add a shot in flight: 1 in `channel`, its velocity in the two channels after it."""
        x, y, heading, speed = shot[0], shot[1], shot[2], shot[3]
        col = math.floor((x - self.left) / self.cell_w)
        row = math.floor((self.top - y) / self.cell_h)
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return
        index = channel * self.plane + row * self.cols + col
        cells = self.cells
        plane = self.plane
        cells[index] = cells.get(index, 0.0) + 1.0
        across = math.sin(heading) * speed / SPEED_UNIT
        cells[index + plane] = cells.get(index + plane, 0.0) + across
        up = math.cos(heading) * speed / SPEED_UNIT
        cells[index + 2 * plane] = cells.get(index + 2 * plane, 0.0) + up

    def span(self, x: float, y: float, radius: float) -> tuple[int, int, int, int] | None:
        """Return the rows and columns a disc overlaps (first and last), None off the grid."""
        c0 = max(0, math.floor((x - radius - self.left) / self.cell_w))
        c1 = min(self.cols - 1, math.floor((x + radius - self.left) / self.cell_w))
        r0 = max(0, math.floor((self.top - y - radius) / self.cell_h))
        r1 = min(self.rows - 1, math.floor((self.top - y + radius) / self.cell_h))
        if c0 > c1 or r0 > r1:
            return None
        return r0, r1, c0, c1

    def raise_to(self, channel: int, span: tuple[int, int, int, int], value: float) -> None:
        """Set the cells of `span` in `channel` to at least `value`."""
        r0, r1, c0, c1 = span
        cells = self.cells
        base = channel * self.plane
        for row in range(r0, r1 + 1):
            first = base + row * self.cols
            for col in range(c0, c1 + 1):
                index = first + col
                if cells.get(index, 0.0) < value:
                    cells[index] = value

    def disc(self, channel: int, x: float, y: float, radius: float, value: float) -> None:
        """Set the cells a disc overlaps to at least `value`."""
        span = self.span(x, y, radius)
        if span is not None:
            self.raise_to(channel, span, value)

    def cap_counts(self) -> None:
        """Count at most `MOST` shots or laser samples in a cell."""
        cells = self.cells
        plane = self.plane
        for index, value in cells.items():
            if value > MOST and index // plane in _COUNTED:
                cells[index] = MOST


def _draw_lasers(grid: _Grid, lasers: list[list[Any]]) -> None:
    for x, y, heading, length, firing in lasers:
        steps = max(1, int(length / LASER_SAMPLE))
        channel = CH["laser_beam"] if firing else CH["laser_warning"]
        across = math.sin(heading)
        up = math.cos(heading)
        for i in range(steps + 1):
            t = length * i / steps
            grid.add(channel, x + t * across, y + t * up, 1.0)


def _draw(grid: _Grid, data: dict[str, Any]) -> None:
    for x, y, radius, health, full, boss in data["targets"]:
        span = grid.span(x, y, radius)
        if span is not None:
            grid.raise_to(CH["boss"] if boss else CH["enemy"], span, 1.0)
            share = max(0.0, min(1.0, health / full)) if full else 1.0
            grid.raise_to(CH["health"], span, share)
    for shot in data["bullets"]:
        grid.moving(CH["bullet"], shot)
    for shot in data["missiles"]:
        grid.moving(CH["missile"], shot)
    _draw_lasers(grid, data["lasers"])
    for x, y, kind in data["bonuses"]:
        channel = _BONUS_CHANNELS.get(kind)
        if channel is not None:
            grid.disc(channel, x, y, 11.0, 1.0)
    ship = data["ship"]
    grid.disc(CH["ship"], ship[0], ship[1], 8.0, 1.0)
    grid.cap_counts()


def _fovea_walls(grid: _Grid) -> None:
    """Mark where the ship cannot fly, around it."""
    cells = grid.cells
    base = CH["wall"] * grid.plane
    for row in range(grid.rows):
        y = grid.top - (row + 0.5) * grid.cell_h
        inside = BOUNDS.min_y <= y <= BOUNDS.max_y
        half = BOUNDS.half_width_at(y) if inside else -1.0
        first = base + row * grid.cols
        for col in range(grid.cols):
            x = grid.left + (col + 0.5) * grid.cell_w
            if abs(x - BOUNDS.center_x) > half:
                cells[first + col] = 1.0


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


# Python twins of the JavaScript helpers `play_scene` builds its object with (`{}`, `o[k] = v`):
# the scene of a Python run is then the very one the browser gives.
play_scene_module.js_object = _scene_object  # type: ignore[attr-defined]
play_scene_module.js_set = _scene_set  # type: ignore[attr-defined]


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


def state_of(scene: Scene) -> list[float]:
    """Return the state vector of `scene` (`N_STATE` numbers)."""
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
        x / WIDTH,
        y / HEIGHT,
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
    return [float(v) for v in values] + [0.0] * (N_STATE - len(values))


class Sight:
    """One observation: the non-zero cells of the field (walls aside) and of the fovea, the state.

    `field` and `fovea` map a cell's flat index (channel, row, column) to its value.
    """

    def __init__(
        self, field: dict[int, float], fovea: dict[int, float], state: list[float]
    ) -> None:
        self.field = field
        self.fovea = fovea
        self.state = state


def see(scene: Scene) -> Sight:
    """Return what the brain sees of `scene`."""
    data = scene.data
    ship_x, ship_y = data["ship"][0], data["ship"][1]
    half = FOVEA_SIZE * FOVEA_CELL / 2
    field = _Grid(FIELD_ROWS, FIELD_COLS, 0.0, HEIGHT, CELL_W, CELL_H)
    fovea = _Grid(FOVEA_SIZE, FOVEA_SIZE, ship_x - half, ship_y + half, FOVEA_CELL, FOVEA_CELL)
    _draw(field, data)
    _draw(fovea, data)
    _fovea_walls(fovea)
    return Sight(field.cells, fovea.cells, state_of(scene))
