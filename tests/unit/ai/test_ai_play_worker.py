# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `tests/ai/play_worker.py`, `sight.py` and `layout.py`: the PyPy side (D-301)."""

import subprocess
import sys
from pathlib import Path

import numpy as np
from ai import REPO_ROOT
from ai.game_env import Action, EpisodeSetup, GameEnv
from ai.layout import Layout
from ai.observation import observe_sight
from ai.play_worker import SharedRollout
from ai.rollout import RolloutBuffer
from ai.sight import scene_of, see


def test_d_301_what_a_worker_writes_is_what_the_brain_sees(tmp_path: Path) -> None:
    steps, envs, hidden = 3, 4, 8
    buffer = RolloutBuffer(tmp_path / "rollout.bin", steps, envs, hidden, create=True)
    shared = SharedRollout(str(buffer.path), Layout(steps, envs, hidden))
    env = GameEnv(EpisodeSetup("1-1"))
    for _ in range(60):  # into the level: enemies, shots
        env.step(Action(3))
    sight = see(scene_of(env))
    shared.write_sight("", (1, 2), sight, start=True)
    shared.write_outcome(1, 2, 0.25, done=True)
    shared.write_sight("next_", (3,), sight, start=False)
    shared.close()
    expected = observe_sight(sight)
    rollout, after = buffer.rollout(), buffer.next()
    assert np.array_equal(rollout.field[1, 2], expected.field.astype(np.float16))
    assert np.array_equal(rollout.fovea[1, 2], expected.fovea.astype(np.float16))
    assert np.array_equal(rollout.state[1, 2], expected.state)
    assert rollout.starts[1, 2]
    assert rollout.rewards[1, 2] == 0.25
    assert rollout.dones[1, 2]
    # Nothing else was written.
    assert rollout.field[0].sum() == 0
    assert rollout.field[1, :2].sum() == 0
    assert rollout.rewards.sum() == 0.25
    assert np.array_equal(after.field[3], expected.field.astype(np.float16))
    assert not after.starts[3]


def test_d_301_a_worker_reads_the_actions_the_server_wrote(tmp_path: Path) -> None:
    buffer = RolloutBuffer(tmp_path / "rollout.bin", 2, 3, 4, create=True)
    buffer.rollout().actions[1, 2] = [7, 1, 0]
    shared = SharedRollout(str(buffer.path), Layout(2, 3, 4))
    assert shared.action(1, 2) == (7, 1, 0)
    assert shared.action(0, 0) == (0, 0, 0)
    shared.close()


def test_d_301_the_workers_modules_need_neither_numpy_nor_torch() -> None:
    """They run under PyPy, which has no PyTorch (and a slow numpy)."""
    code = (
        "import sys; import ai.play_worker, ai.episodes, ai.sight, ai.layout, ai.game_env;"
        "bad = [m for m in ('numpy', 'torch') if m in sys.modules];"
        "assert not bad, bad"
    )
    done = subprocess.run(  # noqa: S603  # this Python, fixed code
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT / "tests")},
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
