# Copyright (c) 2026 Renaud Guillon
"""The inference server: the brain on the GPU decides for every worker's episodes (D-274).

Without it, each worker runs its own copy of the brain on its CPU core, a third of its time. With
it, one process holds the brain on the GPU and answers the workers' questions in batches: a worker
writes what its episodes see into the shared rollout and asks "decide for episodes a to b at step
t" (t = -1: the value after the round's last decision); the server reads them there, decides,
writes the actions, their log-probabilities, the values and the memories back, and answers. It
keeps each episode's memory on the GPU, from one round to the next.

Each round, the learner sends it the weights (and the buffer to use) before the workers start;
the workers' questions of a round are all answered before the learner collects it.
"""

import pickle
import signal
import traceback
from dataclasses import dataclass
from multiprocessing.connection import Connection, wait
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ai.brain import Batch, Brain, BrainShape
from ai.observation import FIELD_COLS, FIELD_ROWS, FOVEA_SIZE, N_CHANNELS, N_STATE
from ai.rollout import Next, Rollout, RolloutBuffer


@dataclass
class Question:
    """A worker's question: decide for episodes `lo` to `hi` at step `t` (-1: after the round)."""

    conn: Connection
    lo: int
    hi: int
    t: int


class Server:
    """The brain on its device, the memory of every episode, and the round's buffers."""

    def __init__(self, shape: BrainShape, device: str, episodes: int, seed: int) -> None:
        self.device = torch.device(device)
        self.brain = Brain(shape).to(self.device)
        self.brain.eval()
        self.memory = torch.zeros(episodes, shape.hidden, device=self.device)
        self.generator = torch.Generator(device=self.device)
        self.generator.manual_seed(seed)
        self.out: Rollout | None = None
        self.after: Next | None = None
        # Where the batches are gathered: pinned, so they reach the GPU fast (big enough for all).
        pin = self.device.type == "cuda"
        self._staging = {
            "field": torch.empty(
                (episodes, N_CHANNELS, FIELD_ROWS, FIELD_COLS), dtype=torch.float16
            ),
            "fovea": torch.empty(
                (episodes, N_CHANNELS, FOVEA_SIZE, FOVEA_SIZE), dtype=torch.float16
            ),
            "state": torch.empty((episodes, N_STATE), dtype=torch.float32),
        }
        if pin:
            self._staging = {name: t.pin_memory() for name, t in self._staging.items()}

    def start_round(self, weights: dict[str, Any], out: Rollout, after: Next) -> None:
        """Play the next round with `weights`, into `out` and `after`."""
        self.brain.load_state_dict(weights)
        self.out = out
        self.after = after

    def answer(self, questions: list[Question]) -> None:
        """Decide for every episode asked about, in one batch, and answer each question.

        What they see is gathered into memory pinned for the GPU and copied in one go each; what
        was decided comes back in one copy.
        """
        out, after = self.out, self.after
        assert out is not None  # a round has started
        assert after is not None
        fields, foveas, states, starts, rows, playing = [], [], [], [], [], []
        for q in questions:
            source: Any = after if q.t < 0 else out
            part: Any = slice(q.lo, q.hi) if q.t < 0 else (q.t, slice(q.lo, q.hi))
            fields.append(source.field[part])
            foveas.append(source.fovea[part])
            states.append(source.state[part])
            starts.append(source.starts[part])
            rows.append(np.arange(q.lo, q.hi))
            playing.append(np.full(q.hi - q.lo, q.t >= 0))
        count = sum(q.hi - q.lo for q in questions)
        staged = self._staging
        for name, parts in (("field", fields), ("fovea", foveas), ("state", states)):
            np.concatenate(parts, out=staged[name].numpy()[:count])
        dev = self.device
        moved = {name: staged[name][:count].to(dev, non_blocking=True) for name in staged}
        index = torch.as_tensor(np.concatenate(rows)).to(dev, non_blocking=True)
        keep = torch.as_tensor(~np.concatenate(starts), dtype=torch.float32).to(dev)
        playing_rows = torch.as_tensor(np.concatenate(playing)).to(dev)
        memory = self.memory[index] * keep.unsqueeze(-1)
        with torch.no_grad():
            batch = Batch(moved["field"], moved["fovea"], moved["state"])
            decision, new_memory = self.brain(batch, memory)
            actions, log_probs = decision.sample_with_log_prob(self.generator)
            self.memory[index[playing_rows]] = new_memory[playing_rows]
            packed = (
                torch
                .cat([actions.float(), log_probs[:, None], decision.value[:, None], memory], dim=1)
                .cpu()
                .numpy()
            )
        first = 0
        for q in questions:
            got = packed[first : first + q.hi - q.lo]
            first += q.hi - q.lo
            if q.t < 0:
                out.last_values[q.lo : q.hi] = got[:, 4]
                continue
            out.actions[q.t, q.lo : q.hi] = got[:, :3]
            out.log_probs[q.t, q.lo : q.hi] = got[:, 3]
            out.values[q.t, q.lo : q.hi] = got[:, 4]
            out.memories[q.t, q.lo : q.hi] = got[:, 5:]
        for q in questions:
            q.conn.send_bytes(b"")


def _questions(ready: list[Any]) -> list[Question]:
    """Every question the ready workers have asked."""
    questions = []
    for conn in ready:
        while conn.poll():
            lo, hi, t = conn.recv()
            questions.append(Question(conn, lo, hi, t))
    return questions


def server_main(
    learner: Connection,
    workers: list[Connection],
    shape: BrainShape,
    device: str,
    buffers: list[tuple[Path, tuple[int, int, int]]],
    seed: int,
) -> None:
    """Answer the workers' questions, round after round, until the learner sends None.

    Each message of the learner is the index of the round's buffer and the weights; the server
    answers it (None) once it is ready for the round.
    """
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    torch.set_num_threads(1)
    try:
        shared = [RolloutBuffer(path, *spec, create=False) for path, spec in buffers]
        server = Server(shape, device, shared[0].spec[1], seed)
        while True:
            ready = wait([learner, *workers])
            if learner in ready:
                message = pickle.loads(learner.recv_bytes())  # noqa: S301  # from the learner
                if message is None:
                    break
                index, weights = message
                server.start_round(weights, shared[index].rollout(), shared[index].next())
                learner.send(None)  # ready for the round
                continue
            questions = _questions(ready)
            if questions:
                server.answer(questions)
    except (EOFError, BrokenPipeError):
        pass  # the learner or a worker is gone
    except Exception:  # noqa: BLE001  # the learner shows what went wrong in the server
        learner.send(traceback.format_exc())
    finally:
        for conn in (learner, *workers):
            conn.close()
