# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/inference.py`: the brain deciding for every worker (D-274)."""

from pathlib import Path

import numpy as np
import pytest
import torch
from ai.brain import Batch, Brain, BrainShape
from ai.inference import Question, Server
from ai.learn import Settings, Workers
from ai.rollout import Curriculum, RolloutBuffer, ServedPlayer

SMALL = BrainShape(hidden=32, field_features=16, fovea_features=16, state_features=8)


class _Direct:
    """A worker's pipe to a server in the same process: each question is answered at once."""

    def __init__(self, server: Server) -> None:
        self.server = server
        self.answers = 0

    def send(self, question: tuple[int, int, int]) -> None:
        self.server.answer([Question(self, *question)])  # type: ignore[arg-type]

    def send_bytes(self, _data: bytes) -> None:
        self.answers += 1

    def recv_bytes(self) -> bytes:
        assert self.answers > 0
        self.answers -= 1
        return b""


def test_d_274_the_server_decides_as_the_brain_would_step_by_step(tmp_path: Path) -> None:
    torch.manual_seed(0)
    steps, envs = 6, 3
    buffer = RolloutBuffer(tmp_path / "rollout.bin", steps, envs + 2, SMALL.hidden, create=True)
    brain = Brain(SMALL)
    server = Server(SMALL, "cpu", envs + 2, seed=1)
    out, after = buffer.rollout(), buffer.next()
    server.start_round(brain.state_dict(), out, after)
    # Episodes 2 to 4 of the buffer: a worker's share starts at its offset.
    player = ServedPlayer(envs, 2, Curriculum(levels=("1-1",)), offset=2)
    assert player.groups == [(0, 2), (2, 3)]
    mine = buffer.rollout(2, 2 + envs)
    episodes = player.play(_Direct(server), mine, buffer.next(2, 2 + envs))  # type: ignore[arg-type]
    assert episodes == []
    assert mine.starts[0].all()
    assert not mine.starts[1:].any()
    # Replay each episode through the brain: the server's memories, values and log-probabilities.
    with torch.no_grad():
        for e in range(envs):
            memory = torch.as_tensor(mine.memories[0, e : e + 1])
            assert not memory.any()  # a new episode starts with an empty memory
            for t in range(steps):
                assert torch.allclose(torch.as_tensor(mine.memories[t, e : e + 1]), memory)
                batch = Batch(
                    torch.as_tensor(mine.field[t, e : e + 1]),
                    torch.as_tensor(mine.fovea[t, e : e + 1]),
                    torch.as_tensor(mine.state[t, e : e + 1]),
                )
                decision, memory = brain(batch, memory)
                assert decision.value.item() == pytest.approx(mine.values[t, e], abs=1e-5)
                actions = torch.as_tensor(mine.actions[t, e : e + 1])
                logp = decision.log_prob(actions).item()
                assert logp == pytest.approx(mine.log_probs[t, e], abs=1e-5)
            nxt = buffer.next(2, 2 + envs)
            batch = Batch(
                torch.as_tensor(nxt.field[e : e + 1]),
                torch.as_tensor(nxt.fovea[e : e + 1]),
                torch.as_tensor(nxt.state[e : e + 1]),
            )
            last, _ = brain(batch, memory)
            assert last.value.item() == pytest.approx(mine.last_values[e], abs=1e-5)
    # The episodes outside the worker's share are untouched.
    assert not buffer.rollout(0, 2).actions.any()


def test_d_274_with_a_server_the_workers_play_a_round() -> None:
    settings = Settings(workers=2, envs=2, steps=4, device="cpu", served=True)
    workers = Workers(settings, SMALL, seed=5)
    try:
        weights = Brain(SMALL).state_dict()
        for _ in range(2):  # both buffers
            workers.start(weights)
            rollout = workers.collect()
            assert rollout.actions.shape[:2] == (4, 4)
            assert np.isfinite(rollout.values).all()
            assert (rollout.last_values != 0).all()
            assert (rollout.log_probs < 0).all()
    finally:
        workers.close()


def test_d_274_a_gpu_learns_with_the_server_and_a_core_for_it() -> None:
    cuda = Settings.for_device("cuda")
    assert cuda.served
    assert cuda.mixed_precision
    assert (cuda.envs, cuda.steps) == (16, 32)
    assert not Settings.for_device("cpu").served
