# Copyright (c) 2026 Renaud Guillon
"""A worker playing the game for the learner, in pure Python: run under PyPy (D-301).

PyPy's JIT plays the game's simulation about five times faster than CPython, but has no PyTorch
(and a slow numpy). So a worker only plays: the inference server (CPython, `inference.py`) decides
for it. A worker writes what its episodes see straight into the shared rollout file (an `mmap`,
laid out by `layout.py`), asks the server "decide for episodes a to b at step t", reads the actions
the server wrote there, and plays them (D-298).

Its episodes are in two groups: while the server decides for one, the worker plays the other's
decisions, so neither waits for the other.

The learner starts it as `python -m ai.play_worker LEARNER_FD SERVER_FD` (`learn.py`): the file
descriptors of its two connections (`multiprocessing` pipes, which PyPy and CPython frame alike),
inherited from the learner. The learner sends its setup; then it plays a round each time the
learner sends the index of the buffer to play it into, until the learner sends None. Ctrl-C is
the learner's to handle.
"""

import mmap
import signal
import struct
import sys
import traceback
from collections import deque
from dataclasses import dataclass
from multiprocessing.connection import Connection
from pathlib import Path

from ai.episodes import Curriculum, EpisodeReport, Episodes
from ai.layout import ITEM_SIZE, Layout
from ai.sight import FIELD_CELLS, FIELD_WALLS, FOVEA_CELLS, N_STATE, Sight, scene_of, see


def _field_template() -> bytes:
    """Return the field grid with its walls (which never change) and nothing else, as float16."""
    cells = [0.0] * FIELD_CELLS
    for index, value in FIELD_WALLS.items():
        cells[index] = value
    return struct.pack(f"{FIELD_CELLS}e", *cells)


_FIELD_TEMPLATE = _field_template()
_FOVEA_EMPTY = bytes(FOVEA_CELLS * 2)


@dataclass
class WorkerSetup:
    """What the learner tells a worker: its episodes (`lo` to `hi` of the rollout), its seed.

    `buffers`: the paths of the shared rollout files; `layout`: their (steps, envs, hidden).
    """

    lo: int
    hi: int
    seed: int
    curriculum: Curriculum
    buffers: list[str]
    layout: tuple[int, int, int]


_HALF = struct.Struct("<e")
_FLOAT = struct.Struct("<f")
_BOOL = struct.Struct("<?")
_ACTION = struct.Struct("<3q")


class SharedRollout:
    """A shared rollout file, as the worker writes into it: an `mmap`, by `struct`.

    `struct.pack_into` on the map itself: under PyPy, several times faster than a `memoryview`'s
    items.
    """

    def __init__(self, path: str, layout: Layout) -> None:
        self.layout = layout
        with Path(path).open("r+b") as f:
            self._map = mmap.mmap(f.fileno(), layout.size)
        self._state = struct.Struct(f"<{N_STATE}f")

    def _at(self, name: str, *at: int) -> int:
        """Return the byte offset of `at`'s first item in array `name`."""
        fmt = self.layout.arrays[name][0]
        return self.layout.index(name, *at) * ITEM_SIZE[fmt]

    def write_sight(self, prefix: str, at: tuple[int, ...], sight: Sight, start: bool) -> None:
        """Write what an episode sees into `field`, `fovea`, `state`, `starts` (with `prefix`).

        `at`: (t, e) for a step of the round, (e,) for what it sees after the round (`next_`).
        """
        memory = self._map
        pack = _HALF.pack_into
        field = self._at(prefix + "field", *at)
        memory[field : field + len(_FIELD_TEMPLATE)] = _FIELD_TEMPLATE
        for index, value in sight.field.items():
            pack(memory, field + 2 * index, value)
        fovea = self._at(prefix + "fovea", *at)
        memory[fovea : fovea + len(_FOVEA_EMPTY)] = _FOVEA_EMPTY
        for index, value in sight.fovea.items():
            pack(memory, fovea + 2 * index, value)
        self._state.pack_into(memory, self._at(prefix + "state", *at), *sight.state)
        _BOOL.pack_into(memory, self._at(prefix + "starts", *at), start)

    def write_outcome(self, t: int, e: int, reward: float, done: bool) -> None:
        _FLOAT.pack_into(self._map, self._at("rewards", t, e), reward)
        _BOOL.pack_into(self._map, self._at("dones", t, e), done)

    def action(self, t: int, e: int) -> tuple[int, int, int]:
        """Return the action the server chose for episode `e` at step `t`."""
        move, bomb, switch = _ACTION.unpack_from(self._map, self._at("actions", t, e))
        return move, bomb, switch

    def close(self) -> None:
        self._map.close()


class Worker:
    """The episodes `lo` to `hi` of the shared rollouts, played side by side in two groups."""

    def __init__(self, setup: WorkerSetup) -> None:
        self.lo = setup.lo
        count = setup.hi - setup.lo
        self.episodes = Episodes(count, setup.seed, setup.curriculum)
        layout = Layout(*setup.layout)
        self.steps = layout.steps
        self.shared = [SharedRollout(path, layout) for path in setup.buffers]
        half = (count + 1) // 2
        self.groups = [(0, half), (half, count)] if count > 1 else [(0, count)]

    def play(self, server: Connection, index: int) -> list[EpisodeReport]:
        """Play a round into buffer `index`; return the episodes that ended."""
        out = self.shared[index]
        ended: list[EpisodeReport] = []
        asked: deque[tuple[int, int]] = deque()
        for group in range(len(self.groups)):
            self._ask(server, out, group, 0)
            asked.append((group, 0))
        while asked:
            server.recv_bytes()  # the server answers in the order it was asked
            group, t = asked.popleft()
            if t == self.steps:
                continue  # the value of the round's end: nothing to play
            lo, hi = self.groups[group]
            for e in range(lo, hi):
                reward, done, report = self.episodes.play(e, out.action(t, self.lo + e))
                out.write_outcome(t, self.lo + e, reward, done)
                if report is not None:
                    ended.append(report)
            self._ask(server, out, group, t + 1)
            asked.append((group, t + 1))
        return ended

    def _ask(self, server: Connection, out: SharedRollout, group: int, t: int) -> None:
        """Write what the group's episodes see at step `t`, and ask the server to decide."""
        lo, hi = self.groups[group]
        last = t == self.steps
        episodes = self.episodes
        for e in range(lo, hi):
            sight = see(scene_of(episodes.envs[e]))
            at = (self.lo + e,) if last else (t, self.lo + e)
            out.write_sight("next_" if last else "", at, sight, episodes.starts[e])
        server.send((self.lo + lo, self.lo + hi, -1 if last else t))

    def close(self) -> None:
        for shared in self.shared:
            shared.close()


def run(learner: Connection, server: Connection) -> None:
    """Play a round each time the learner asks, until it sends None."""
    worker: Worker | None = None
    try:
        setup: WorkerSetup = learner.recv()
        worker = Worker(setup)
        learner.send(True)  # ready
        while True:
            index = learner.recv()
            if index is None:
                break
            try:
                episodes = worker.play(server, index)
            except (EOFError, BrokenPipeError, ConnectionResetError):
                learner.send("The inference server stopped (its error, if any, follows).")
                break
            learner.send((episodes, worker.episodes.progress()))
    except (EOFError, BrokenPipeError, ConnectionResetError):
        pass  # the learner is gone
    except Exception:  # noqa: BLE001  # the learner shows what went wrong in the worker
        learner.send(traceback.format_exc())
    finally:
        if worker is not None:
            worker.close()
        server.close()
        learner.close()


def main(argv: list[str]) -> None:
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    run(Connection(int(argv[0])), Connection(int(argv[1])))


if __name__ == "__main__":
    main(sys.argv[1:])
