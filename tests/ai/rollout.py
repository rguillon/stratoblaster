# Copyright (c) 2026 Renaud Guillon
"""Playing the game to learn from it: worker processes that each run a few episodes at once.

Each worker holds a copy of the brain (sent by the learner before each round), plays `steps`
decisions in each of its episodes, and sends back everything the learner needs: what was seen,
done, expected and got. An episode that ends is replaced by a new one, drawn by the curriculum.
"""

import dataclasses
import pickle
import random
import signal
import traceback
from dataclasses import dataclass
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray

from ai.brain import Batch, Brain, BrainShape
from ai.game_env import (
    LEVEL_IDS,
    MAX_WEAPON_LEVEL,
    SHIP_IDS,
    WEAPON_IDS,
    Action,
    EpisodeSetup,
    GameEnv,
    level_seconds,
)
from ai.observation import FIELD_COLS, FIELD_ROWS, FOVEA_SIZE, N_CHANNELS, N_STATE, observe


@dataclass
class Curriculum:
    """How the learning episodes are drawn.

    A share start in the middle of a level (`mid_start`), anywhere up to its final boss, so the
    bosses and late waves come up as often as the first ones; with weapons, lives and bombs that
    vary, as a player may have there. The others are a fresh start, as when it is watched
    (`make serve-ai`) and rated: 3 lives, 3 bombs, the first weapon at level 1 (D-269). The ship
    varies.
    """

    levels: tuple[str, ...] = LEVEL_IDS
    mid_start: float = 0.6

    def draw(self, rng: random.Random) -> EpisodeSetup:
        level_id = rng.choice(self.levels)
        seconds = level_seconds(level_id)
        ship_id = rng.choice(SHIP_IDS)
        seed = rng.randrange(1 << 30)
        if rng.random() >= self.mid_start:
            return EpisodeSetup(level_id, seed=seed, ship_id=ship_id)  # a fresh start
        start = rng.uniform(0.0, seconds * 0.99)
        base = rng.randint(1, MAX_WEAPON_LEVEL)
        levels = {w: max(1, min(MAX_WEAPON_LEVEL, base + rng.randint(-1, 1))) for w in WEAPON_IDS}
        return EpisodeSetup(
            level_id,
            seed=seed,
            ship_id=ship_id,
            weapon=rng.choice(WEAPON_IDS),
            weapon_levels=levels,
            lives=rng.choice((1, 2, 3, 3, 3)),
            bombs=rng.randint(0, 3),
            start_time=start,
        )


@dataclass
class EpisodeReport:
    """How an episode went."""

    level_id: str
    outcome: str
    reward: float
    progress: float
    lives_lost: int
    decisions: int
    mid_start: bool


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


# What a rollout holds for each decision of each episode: its name, type and shape.
_STEP_ARRAYS: tuple[tuple[str, type, tuple[int, ...]], ...] = (
    ("field", np.float16, (N_CHANNELS, FIELD_ROWS, FIELD_COLS)),
    ("fovea", np.float16, (N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE)),
    ("state", np.float32, (N_STATE,)),
    ("actions", np.int64, (3,)),
    ("log_probs", np.float32, ()),
    ("values", np.float32, ()),
    ("rewards", np.float32, ()),
    ("dones", np.bool_, ()),
    ("starts", np.bool_, ()),
)


def _empty(steps: int, envs: int, hidden: int) -> Rollout:
    arrays = [np.zeros((steps, envs, *shape), dtype) for _, dtype, shape in _STEP_ARRAYS]
    memories = np.zeros((steps, envs, hidden), np.float32)
    return Rollout(*arrays, memories, np.zeros(envs, np.float32))


class RolloutBuffer:
    """A rollout in a file mapped in memory, shared by the learner and every worker.

    Each worker writes its episodes' slice of it in place, so a round of play (over a gigabyte with
    many workers) never goes through a pipe. `path` is best in `/dev/shm` (memory, not disk).
    """

    def __init__(self, path: Path, steps: int, envs: int, hidden: int, create: bool) -> None:
        self.path = path
        self.spec = (steps, envs, hidden)
        layout: list[tuple[str, Any, tuple[int, ...]]] = [
            (name, dtype, (steps, envs, *shape)) for name, dtype, shape in _STEP_ARRAYS
        ]
        layout.append(("memories", np.float32, (steps, envs, hidden)))
        layout.append(("last_values", np.float32, (envs,)))
        offsets: list[int] = []
        size = 0
        for _, dtype, shape in layout:
            offsets.append(size)
            nbytes = int(np.prod(shape)) * np.dtype(dtype).itemsize
            size += (nbytes + 63) // 64 * 64
        mode = "w+" if create else "r+"
        self._memory = np.memmap(path, dtype=np.uint8, mode=mode, shape=(size,))
        self._arrays: dict[str, Any] = {}
        for (name, dtype, shape), offset in zip(layout, offsets, strict=True):
            nbytes = int(np.prod(shape)) * np.dtype(dtype).itemsize
            raw = self._memory[offset : offset + nbytes]
            self._arrays[name] = np.ndarray(shape, dtype, buffer=raw)

    def rollout(self, lo: int = 0, hi: int | None = None) -> Rollout:
        """Return the rollout of episodes `lo` to `hi` (all by default): views, not copies."""
        a = self._arrays
        part = slice(lo, hi)
        steps = [a[name][:, part] for name, _, _ in _STEP_ARRAYS]
        return Rollout(*steps, a["memories"][:, part], a["last_values"][part])


class Player:
    """A few episodes played side by side by one copy of the brain."""

    def __init__(self, shape: BrainShape, envs: int, seed: int, curriculum: Curriculum) -> None:
        self.brain = Brain(shape)
        self.brain.eval()
        self.rng = random.Random(seed)
        self.curriculum = curriculum
        self.envs = [GameEnv(curriculum.draw(self.rng)) for _ in range(envs)]
        self.observations = [observe(env) for env in self.envs]
        self.memory = self.brain.initial_memory(envs)
        self.starts = np.ones(envs, np.bool_)
        self.returns = np.zeros(envs, np.float64)
        self.decisions = np.zeros(envs, np.int64)

    def play(self, weights: dict[str, Any], out: Rollout) -> list[EpisodeReport]:
        """Play a round with `weights`, written into `out`; return the episodes that ended.

        A round is as many decisions in each episode as `out` has steps.
        """
        self.brain.load_state_dict(weights)
        count = len(self.envs)
        out.episodes = []
        for t in range(out.rewards.shape[0]):
            keep = torch.as_tensor(~self.starts, dtype=torch.float32).unsqueeze(-1)
            self.memory = self.memory * keep
            batch = Batch.of(self.observations)
            out.field[t] = batch.field.numpy()
            out.fovea[t] = batch.fovea.numpy()
            out.state[t] = batch.state.numpy()
            out.starts[t] = self.starts
            out.memories[t] = self.memory.numpy()
            with torch.no_grad():
                decision, self.memory = self.brain(batch, self.memory)
                actions = decision.sample(greedy=False)
                out.log_probs[t] = decision.log_prob(actions).numpy()
                out.values[t] = decision.value.numpy()
            out.actions[t] = actions.numpy()
            for e in range(count):
                self._step(e, actions[e].tolist(), out, t)
        keep = torch.as_tensor(~self.starts, dtype=torch.float32).unsqueeze(-1)
        with torch.no_grad():
            decision, _ = self.brain(Batch.of(self.observations), self.memory * keep)
        out.last_values[:] = decision.value.numpy()
        return out.episodes

    def _step(self, e: int, action: list[int], out: Rollout, t: int) -> None:
        env = self.envs[e]
        reward, _ = env.step(Action(action[0], action[1] == 1, action[2] == 1))
        out.rewards[t, e] = reward
        out.dones[t, e] = env.done
        self.returns[e] += reward
        self.decisions[e] += 1
        self.starts[e] = env.done
        if env.done:
            out.episodes.append(
                EpisodeReport(
                    env.setup.level_id,
                    env.outcome,
                    float(self.returns[e]),
                    env.progress_fraction,
                    env.total_lives_lost,
                    int(self.decisions[e]),
                    env.setup.start_time > 0,
                )
            )
            self.returns[e] = 0.0
            self.decisions[e] = 0
            env = GameEnv(self.curriculum.draw(self.rng))
            self.envs[e] = env
        self.observations[e] = observe(env)


def worker_main(
    conn: Connection,
    shape: BrainShape,
    envs: tuple[int, int],
    seed: int,
    curriculum: Curriculum,
    buffers: list[tuple[Path, tuple[int, int, int]]],
) -> None:
    """Play a round each time the learner asks, until it sends None (a worker process).

    The worker plays episodes `envs[0]` to `envs[1]` of the shared rollout buffers; each message
    is the index of the buffer to write the round into and the weights to play it with. Ctrl-C is
    the learner's to handle: it stops the workers once the brain is saved.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    torch.set_num_threads(1)
    try:
        lo, hi = envs
        player = Player(shape, hi - lo, seed, curriculum)
        views = [RolloutBuffer(path, *spec, create=False).rollout(lo, hi) for path, spec in buffers]
        while True:
            message = pickle.loads(conn.recv_bytes())  # noqa: S301  # from the learner
            if message is None:
                break
            index, weights = message
            conn.send(player.play(weights, views[index]))
    except (EOFError, BrokenPipeError):
        pass  # the learner is gone
    except Exception:  # noqa: BLE001  # the learner shows what went wrong in the worker
        conn.send(traceback.format_exc())
    finally:
        conn.close()
