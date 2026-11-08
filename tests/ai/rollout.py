# Copyright (c) 2026 Renaud Guillon
"""Playing the game to learn from it: worker processes that each run a few episodes at once.

Each worker holds a copy of the brain (sent by the learner before each round), plays `steps`
decisions in each of its episodes, and sends back everything the learner needs: what was seen,
done, expected and got. An episode is a campaign from the first level (D-295); one that ends is
replaced by a new one.
"""

import dataclasses
import pickle
import random
import signal
import traceback
from collections import deque
from dataclasses import dataclass
from multiprocessing.connection import Connection
from pathlib import Path
from typing import Any, Protocol

import numpy as np
import torch
from numpy.typing import NDArray

from ai.brain import Batch, Brain, BrainShape
from ai.game_env import LEVEL_IDS, Action, EpisodeSetup, GameEnv
from ai.observation import FIELD_COLS, FIELD_ROWS, FOVEA_SIZE, N_CHANNELS, N_STATE, observe


@dataclass
class Curriculum:
    """How the learning episodes are drawn: each a campaign (D-295).

    From the first of `levels` with a fresh start (3 lives, 3 bombs, the first weapon at level 1,
    as when watched and rated, D-294), each level cleared going on to the next with what it ended
    with, until the game is over, a level takes too long or the last one is cleared. Always with
    the `ship` (the balanced one); the seed varies.
    """

    levels: tuple[str, ...] = LEVEL_IDS
    ship: str = "balanced"

    def draw(self, rng: random.Random) -> GameEnv:
        """Return the game of a new episode."""
        setup = EpisodeSetup(self.levels[0], seed=rng.randrange(1 << 30), ship_id=self.ship)
        return GameEnv(setup, campaign=self.levels)


@dataclass
class EpisodeReport:
    """How an episode (a campaign) went.

    `outcome`: "over" (no life left), "timeout" (a level took too long) or "complete" (the last
    level cleared). `reached`: the level it ended in; `cleared`: how many levels it cleared;
    `progress`: how far through the level it ended in.
    """

    ship_id: str
    outcome: str
    score: float
    reached: str
    cleared: int
    progress: float
    lives_lost: int
    decisions: int


@dataclass
class GameProgress:
    """A game still being played: the level it is in, the levels cleared, its score, its moves."""

    level: str
    cleared: int
    score: float
    decisions: int


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


# What a rollout holds for each episode after its last decision, for the inference server to
# work out the value of the round's end from (D-298): its name, type and shape.
_NEXT_ARRAYS: tuple[tuple[str, type, tuple[int, ...]], ...] = (
    ("next_field", np.float16, (N_CHANNELS, FIELD_ROWS, FIELD_COLS)),
    ("next_fovea", np.float16, (N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE)),
    ("next_state", np.float32, (N_STATE,)),
    ("next_starts", np.bool_, ()),
)


@dataclass
class Next:
    """What each episode sees after a round's last decision (`_NEXT_ARRAYS`).

    And whether it starts there.
    """

    field: NDArray[np.float16]
    fovea: NDArray[np.float16]
    state: NDArray[np.float32]
    starts: NDArray[np.bool_]


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
        layout.extend((name, dtype, (envs, *shape)) for name, dtype, shape in _NEXT_ARRAYS)
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

    def next(self, lo: int = 0, hi: int | None = None) -> Next:
        """Return what episodes `lo` to `hi` see after the round's last decision (views)."""
        part = slice(lo, hi)
        return Next(*(self._arrays[name][part] for name, _, _ in _NEXT_ARRAYS))


class Player:
    """A few episodes played side by side by one copy of the brain."""

    def __init__(self, shape: BrainShape, envs: int, seed: int, curriculum: Curriculum) -> None:
        self.brain = Brain(shape)
        self.brain.eval()
        self.rng = random.Random(seed)
        self.curriculum = curriculum
        self.envs = [curriculum.draw(self.rng) for _ in range(envs)]
        self.observations = [observe(env) for env in self.envs]
        self.memory = self.brain.initial_memory(envs)
        self.starts = np.ones(envs, np.bool_)
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
        self.observations[e] = observe(_play(self, e, action, out, t))


class _Episodes(Protocol):
    """The episodes a worker plays: `_play` steps them."""

    envs: list[GameEnv]
    starts: NDArray[np.bool_]
    decisions: NDArray[np.int64]
    rng: random.Random
    curriculum: Curriculum


def progress(owner: _Episodes) -> list[GameProgress]:
    """Return how each game a worker is playing stands."""
    return [
        GameProgress(env.setup.level_id, len(env.cleared), env.score, int(owner.decisions[e]))
        for e, env in enumerate(owner.envs)
    ]


def _play(owner: _Episodes, e: int, action: list[int], out: Rollout, t: int) -> GameEnv:
    """Play decision `t` of episode `e`, and write what it got into `out`.

    Returns the game it goes on with (a new one once it ends).
    """
    env = owner.envs[e]
    reward, _ = env.step(Action(action[0], action[1] == 1, action[2] == 1))
    out.rewards[t, e] = reward
    out.dones[t, e] = env.done
    owner.decisions[e] += 1
    owner.starts[e] = env.done
    if env.done:
        out.episodes.append(
            EpisodeReport(
                env.setup.ship_id,
                env.outcome,
                env.score,
                env.setup.level_id,
                len(env.cleared),
                env.progress_fraction,
                env.total_lives_lost,
                int(owner.decisions[e]),
            )
        )
        owner.decisions[e] = 0
        env = owner.curriculum.draw(owner.rng)
        owner.envs[e] = env
    return env


class ServedPlayer:
    """A few episodes played side by side, their decisions made by the inference server (D-298).

    They are in two groups: while the server decides for one, the worker plays the other's
    decisions, so neither waits for the other. What each episode sees goes into the shared rollout
    and the server writes its decisions there: only "decide for episodes a to b at step t" (and
    "done") go through the pipe. `offset`: the first of its episodes in the rollout.
    """

    def __init__(self, envs: int, seed: int, curriculum: Curriculum, offset: int) -> None:
        self.rng = random.Random(seed)
        self.curriculum = curriculum
        self.offset = offset
        self.envs = [curriculum.draw(self.rng) for _ in range(envs)]
        self.starts = np.ones(envs, np.bool_)
        self.decisions = np.zeros(envs, np.int64)
        half = (envs + 1) // 2
        self.groups = [(0, half), (half, envs)] if envs > 1 else [(0, envs)]

    def play(self, server: Connection, out: Rollout, after: Next) -> list[EpisodeReport]:
        """Play a round into `out` (and `after`: what is seen after it).

        Returns the episodes that ended.
        """
        steps = out.rewards.shape[0]
        out.episodes = []
        asked: deque[tuple[int, int]] = deque()
        for group in range(len(self.groups)):
            self._ask(server, out, after, group, 0)
            asked.append((group, 0))
        while asked:
            server.recv_bytes()  # the server answers in the order it was asked
            group, t = asked.popleft()
            if t == steps:
                continue  # the value of the round's end: nothing to play
            lo, hi = self.groups[group]
            for e in range(lo, hi):
                _play(self, e, out.actions[t, e].tolist(), out, t)
            self._ask(server, out, after, group, t + 1)
            asked.append((group, t + 1))
        return out.episodes

    def _ask(self, server: Connection, out: Rollout, after: Next, group: int, t: int) -> None:
        """Write what the group's episodes see at step `t`, and ask the server to decide."""
        lo, hi = self.groups[group]
        batch = Batch.of([observe(self.envs[e]) for e in range(lo, hi)])
        last = t == out.rewards.shape[0]
        if last:
            target: Any = after
            rows: Any = slice(lo, hi)
        else:
            target = out
            rows = (t, slice(lo, hi))
        target.field[rows] = batch.field.numpy()
        target.fovea[rows] = batch.fovea.numpy()
        target.state[rows] = batch.state.numpy()
        target.starts[rows] = self.starts[lo:hi]
        server.send((self.offset + lo, self.offset + hi, -1 if last else t))


def worker_main(
    conn: Connection,
    shape: BrainShape,
    envs: tuple[int, int],
    seed: int,
    curriculum: Curriculum,
    buffers: list[tuple[Path, tuple[int, int, int]]],
    server: Connection | None = None,
) -> None:
    """Play a round each time the learner asks, until it sends None (a worker process).

    The worker plays episodes `envs[0]` to `envs[1]` of the shared rollout buffers; each message
    is the index of the buffer to write the round into and the weights to play it with. With a
    `server` (the inference server, D-298) the weights are None: the server decides. Ctrl-C is the
    learner's to handle: it stops the workers once the brain is saved.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    torch.set_num_threads(1)
    try:
        lo, hi = envs
        shared = [RolloutBuffer(path, *spec, create=False) for path, spec in buffers]
        views = [buffer.rollout(lo, hi) for buffer in shared]
        afters = [buffer.next(lo, hi) for buffer in shared]
        player = Player(shape, hi - lo, seed, curriculum) if server is None else None
        served = ServedPlayer(hi - lo, seed, curriculum, lo) if server is not None else None
        while True:
            message = pickle.loads(conn.recv_bytes())  # noqa: S301  # from the learner
            if message is None:
                break
            index, weights = message
            if player is not None:
                conn.send((player.play(weights, views[index]), progress(player)))
                continue
            assert server is not None  # one of the two
            assert served is not None
            try:
                episodes = served.play(server, views[index], afters[index])
            except (EOFError, BrokenPipeError):
                conn.send("The inference server stopped (its error, if any, follows).")
                break
            conn.send((episodes, progress(served)))
    except (EOFError, BrokenPipeError):
        pass  # the learner is gone
    except Exception:  # noqa: BLE001  # the learner shows what went wrong in the worker
        conn.send(traceback.format_exc())
    finally:
        conn.close()
        if server is not None:
            server.close()
