# Copyright (c) 2026 Renaud Guillon
"""What the brain sees, as numpy arrays for PyTorch: the grids of `sight.py` filled in (D-301).

`sight.py` builds what the brain sees in pure Python (the workers do it under PyPy); here its cells
become arrays, for the brain deciding in CPython (`make rate`, `make serve-ai`, the tests).
"""

import numpy as np
from numpy.typing import NDArray

from ai.game_env import GameEnv
from ai.sight import (
    CH,
    CHANNELS,
    FIELD_COLS,
    FIELD_ROWS,
    FIELD_WALLS,
    FOVEA_CELL,
    FOVEA_SIZE,
    N_CHANNELS,
    N_STATE,
    STATE_BOMB_ACTIVE,
    STATE_BOMBS,
    Scene,
    Sight,
    scene_of,
    see,
)

__all__ = [
    "CH",
    "CHANNELS",
    "FIELD_COLS",
    "FIELD_ROWS",
    "FOVEA_CELL",
    "FOVEA_SIZE",
    "N_CHANNELS",
    "N_STATE",
    "STATE_BOMBS",
    "STATE_BOMB_ACTIVE",
    "Observation",
    "Scene",
    "observe",
    "observe_scene",
    "observe_sight",
]


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


def _filled(shape: tuple[int, ...], cells: dict[int, float]) -> NDArray[np.float32]:
    grid = np.zeros(shape, dtype=np.float32)
    if cells:
        flat = grid.reshape(-1)
        flat[np.fromiter(cells.keys(), np.int64, len(cells))] = np.fromiter(
            cells.values(), np.float32, len(cells)
        )
    return grid


_FIELD_WALLS = _filled((N_CHANNELS, FIELD_ROWS, FIELD_COLS), FIELD_WALLS)


def observe_sight(sight: Sight) -> Observation:
    """Return the arrays of `sight`."""
    field = _filled((N_CHANNELS, FIELD_ROWS, FIELD_COLS), sight.field)
    field += _FIELD_WALLS
    fovea = _filled((N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE), sight.fovea)
    return Observation(field, fovea, np.asarray(sight.state, dtype=np.float32))


def observe_scene(scene: Scene) -> Observation:
    """Return what the brain sees of `scene`."""
    return observe_sight(see(scene))


def observe(env: GameEnv) -> Observation:
    """Return what the brain sees of `env` now."""
    return observe_scene(scene_of(env))
