# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/observation.py`: what the brain sees."""

import math

import numpy as np
from ai.game_env import Action, EpisodeSetup, GameEnv
from ai.observation import (
    CH,
    FIELD_COLS,
    FIELD_ROWS,
    FOVEA_CELL,
    FOVEA_SIZE,
    N_CHANNELS,
    N_STATE,
    observe,
)

from core.entities.enemy import EnemyBulletSpec, EnemyLaserSpec, EnemyMissileSpec
from core.entities.muzzle import PlanePoint

CELL_W = 1000 / FIELD_COLS
CELL_H = 720 / FIELD_ROWS


def _env() -> GameEnv:
    env = GameEnv(EpisodeSetup("1-1"))
    env.step(Action(0))
    env.run.enemies.clear()
    if env.run.bonuses is not None:
        env.run.bonuses.clear()
    return env


def _field_cell(x: float, y: float) -> tuple[int, int]:
    return int((720 - y) // CELL_H), int(x // CELL_W)


def test_the_grids_and_state_have_their_shapes() -> None:
    obs = observe(_env())
    assert obs.field.shape == (N_CHANNELS, FIELD_ROWS, FIELD_COLS)
    assert obs.fovea.shape == (N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE)
    assert obs.state.shape == (N_STATE,)
    assert obs.field.dtype == np.float32


def test_the_ship_is_in_the_field_and_at_the_centre_of_the_fovea() -> None:
    env = _env()
    obs = observe(env)
    row, col = _field_cell(env.run.ship.x, env.run.ship.y)
    assert obs.field[CH["ship"], row, col] == 1
    middle = FOVEA_SIZE // 2
    assert obs.fovea[CH["ship"], middle, middle] == 1
    assert obs.state[0] == np.float32(env.run.ship.x / 1000)


def test_a_bullet_shows_where_it_is_with_its_velocity() -> None:
    env = _env()
    ship = env.run.ship
    x, y = ship.x + 2 * FOVEA_CELL, ship.y + 3 * FOVEA_CELL
    env.run.enemies.shots.fire_bullet(x, y, math.pi, EnemyBulletSpec(200, 4, "b"))
    obs = observe(env)
    row, col = _field_cell(x, y)
    assert obs.field[CH["bullet"], row, col] == 1
    assert obs.field[CH["bullet_vy"], row, col] < 0  # going down
    middle = FOVEA_SIZE // 2
    assert obs.fovea[CH["bullet"], middle - 3, middle + 2] == 1


def test_a_missile_shows_in_its_own_channel() -> None:
    env = _env()
    spec = EnemyMissileSpec(100, 90, 2, 4, 10, "m")
    env.run.enemies.shots.fire_missile(500, 600, math.pi, spec)
    obs = observe(env)
    row, col = _field_cell(500, 600)
    assert obs.field[CH["missile"], row, col] == 1
    assert obs.field[CH["bullet"]].sum() == 0


class _Owner:
    def __init__(self) -> None:
        self.gone = False
        self.health = 1.0
        self.heading = math.pi
        self.emitter = PlanePoint(500, 700)


def test_a_laser_shows_its_warning_line_then_its_beam() -> None:
    env = _env()
    shots = env.run.enemies.shots
    shots.fire_laser(_Owner(), EnemyLaserSpec(1, 1, 10, "l"))  # type: ignore[arg-type]
    shots.step(0.01, 0, 0)
    obs = observe(env)
    _, col = _field_cell(500, 0)
    assert obs.field[CH["laser_warning"], :, col].sum() >= FIELD_ROWS - 1
    assert obs.field[CH["laser_beam"]].sum() == 0
    shots.step(1.0, 0, 0)
    obs = observe(env)
    assert obs.field[CH["laser_beam"], :, col].sum() >= FIELD_ROWS - 1


def test_bonuses_show_by_kind() -> None:
    env = _env()
    bonuses = env.run.bonuses
    assert bonuses is not None
    placed = (("weapon", 200), ("life", 500), ("bomb", 800), ("heal", 350))
    for kind, x in placed:
        bonuses.place(kind, PlanePoint(x, 400))
    obs = observe(env)
    for kind, x in placed:
        row, col = _field_cell(x, 400)
        assert obs.field[CH["bonus_" + kind], row, col] == 1


def test_an_enemy_shows_with_its_health() -> None:
    env = _env()
    kind = env.run._kinds["scout"]
    area_enemy = kind.spawn(_area())[0]
    area_enemy.x, area_enemy.y = 300, 500
    area_enemy.health = area_enemy.max_health / 2
    env.run.enemies.add(area_enemy)
    obs = observe(env)
    row, col = _field_cell(300, 500)
    assert obs.field[CH["enemy"], row, col] == 1
    assert obs.field[CH["health"], row, col] == 0.5


def _area() -> object:
    from core.entities.enemy import EnemySpawnArea  # noqa: PLC0415
    from core.math.rng import create_rng  # noqa: PLC0415

    return EnemySpawnArea(1000, 720, create_rng(1), None, (100, 900))


def test_the_walls_are_where_the_ship_cannot_fly() -> None:
    obs = observe(_env())
    walls = obs.field[CH["wall"]]
    assert walls[0].all()  # the top of the screen
    assert not walls[FIELD_ROWS - 2, FIELD_COLS // 2]  # the bottom middle
