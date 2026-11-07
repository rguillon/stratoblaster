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

    def start_round(self, weights: dict[str, Any], out: Rollout, after: Next) -> None:
        """Play the next round with `weights`, into `out` and `after`."""
        self.brain.load_state_dict(weights)
        self.out = out
        self.after = after

    def answer(self, questions: list[Question]) -> None:
        """Decide for every episode asked about, in one batch, and answer each question."""
        out, after = self.out, self.after
        assert out is not None  # a round has started
        assert after is not None
        fields, foveas, states, starts, rows = [], [], [], [], []
        for q in questions:
            source: Any = after if q.t < 0 else out
            part: Any = slice(q.lo, q.hi) if q.t < 0 else (q.t, slice(q.lo, q.hi))
            fields.append(source.field[part])
            foveas.append(source.fovea[part])
            states.append(source.state[part])
            starts.append(source.starts[part])
            rows.append(np.arange(q.lo, q.hi))
        dev = self.device
        index = torch.as_tensor(np.concatenate(rows), device=dev)
        batch = Batch(
            torch.as_tensor(np.concatenate(fields)).to(dev),
            torch.as_tensor(np.concatenate(foveas)).to(dev),
            torch.as_tensor(np.concatenate(states)).to(dev),
        )
        keep = torch.as_tensor(~np.concatenate(starts), dtype=torch.float32, device=dev)
        memory = self.memory[index] * keep.unsqueeze(-1)
        with torch.no_grad():
            decision, new_memory = self.brain(batch, memory)
            actions = decision.sample(greedy=False, generator=self.generator)
            log_probs = decision.log_prob(actions)
        playing = torch.as_tensor([q.t >= 0 for q in questions for _ in range(q.hi - q.lo)])
        playing = playing.to(dev)
        self.memory[index[playing]] = new_memory[playing]
        got = {
            "actions": actions.cpu().numpy(),
            "log_probs": log_probs.cpu().numpy(),
            "values": decision.value.cpu().numpy(),
            "memories": memory.cpu().numpy(),
        }
        first = 0
        for q in questions:
            span = slice(first, first + q.hi - q.lo)
            first = span.stop
            if q.t < 0:
                out.last_values[q.lo : q.hi] = got["values"][span]
                continue
            for name in ("actions", "log_probs", "values", "memories"):
                getattr(out, name)[q.t, q.lo : q.hi] = got[name][span]
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
