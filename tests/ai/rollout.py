# Copyright (c) 2026 Renaud Guillon
"""A round of play as the learner and the inference server see it: numpy arrays in shared memory.

The workers (`play_worker.py`, under PyPy) write each round into a file mapped in memory, laid
out by `layout.py`: what each episode saw, did and got. The learner and the inference server see
the same file as numpy arrays here, so a round of play (over a gigabyte with many workers) never
goes through a pipe.
"""

import dataclasses
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ai.episodes import Curriculum, EpisodeReport, GameProgress
from ai.layout import NEXT_ARRAYS, STEP_ARRAYS, Layout

__all__ = [
    "Curriculum",
    "EpisodeReport",
    "GameProgress",
    "Next",
    "Rollout",
    "RolloutBuffer",
]

_DTYPES = {"e": np.float16, "f": np.float32, "q": np.int64, "?": np.bool_}


@dataclass
class Rollout:
    """`steps` decisions of `envs` episodes, time first (T, E, ...)."""

    field: NDArray[np.float16]
    fovea: NDArray[np.float16]
    state: NDArray[np.float32]
    actions: NDArray[np.int64]
    log_probs: NDArray[np.float32]
    values: NDArray[np.float32]
    rewards: NDArray[np.float32]
    dones: NDArray[np.bool_]
    starts: NDArray[np.bool_]
    memories: NDArray[np.float32]
    last_values: NDArray[np.float32]
    episodes: list[EpisodeReport] = dataclasses.field(default_factory=list)
    # The games still being played once the round is over.
    playing: list[GameProgress] = dataclasses.field(default_factory=list)


@dataclass
class Next:
    """What each episode sees after a round's last decision, and whether it starts there."""

    field: NDArray[np.float16]
    fovea: NDArray[np.float16]
    state: NDArray[np.float32]
    starts: NDArray[np.bool_]


class RolloutBuffer:
    """A rollout in a file mapped in memory, shared by the learner, the server and every worker.

    `path` is best in `/dev/shm` (memory, not disk).
    """

    def __init__(self, path: Path, steps: int, envs: int, hidden: int, create: bool) -> None:
        self.path = path
        self.spec = (steps, envs, hidden)
        self.layout = Layout(steps, envs, hidden)
        mode = "w+" if create else "r+"
        self._memory = np.memmap(path, dtype=np.uint8, mode=mode, shape=(self.layout.size,))
        self._arrays: dict[str, Any] = {}
        for name, (fmt, shape, offset) in self.layout.arrays.items():
            raw = self._memory[offset : offset + self.layout.nbytes(name)]
            self._arrays[name] = np.ndarray(shape, _DTYPES[fmt], buffer=raw)

    def rollout(self, lo: int = 0, hi: int | None = None) -> Rollout:
        """Return the rollout of episodes `lo` to `hi` (all by default): views, not copies."""
        a = self._arrays
        part = slice(lo, hi)
        steps = [a[name][:, part] for name, _, _ in STEP_ARRAYS]
        return Rollout(*steps, a["memories"][:, part], a["last_values"][part])

    def next(self, lo: int = 0, hi: int | None = None) -> Next:
        """Return what episodes `lo` to `hi` see after the round's last decision (views)."""
        part = slice(lo, hi)
        return Next(*(self._arrays[name][part] for name, _, _ in NEXT_ARRAYS))
