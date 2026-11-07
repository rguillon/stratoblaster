# Copyright (c) 2026 Renaud Guillon
"""`make learn`: the brain learns to play the game (proximal policy optimisation, PPO).

Worker processes play the levels with the current brain (see `rollout.py`); the learner then
improves the brain from what they played, and sends them the new weights. It goes on for
`--minutes`, or until Ctrl-C, saving the brain under `data/` every few updates and at the end.
It starts from the saved brain when there is one (`--fresh` to start over).

With an NVIDIA GPU (and the CUDA build of torch: `make learn AI_TORCH=cuda`) the learner runs on
the GPU and nearly every CPU core plays; on a CPU only, a third of the cores play, the rest learn.

    uv run python -m ai.learn --minutes 120 [--device cuda]
"""

import argparse
import csv
import math
import multiprocessing as mp
import os
import pickle
import random
import shutil
import signal
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import torch
from numpy.typing import NDArray
from torch import nn

from ai import DATA
from ai.brain import (
    BRAIN_FILE,
    TRAINER_FILE,
    Batch,
    Brain,
    BrainShape,
    LearnStats,
    load_brain,
    save_brain,
)
from ai.rollout import Curriculum, EpisodeReport, Rollout, RolloutBuffer, worker_main

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

LOG_FILE = DATA / "learn-log.csv"
HISTORY_KEPT = 2000


CPUS = os.cpu_count() or 2


@dataclass
class Settings:
    """How the brain learns (see `for_device` for the defaults of a machine)."""

    workers: int = max(1, CPUS // 3)
    envs: int = 12  # episodes played side by side by each worker
    steps: int = 128  # decisions per episode per round
    chunk: int = 32  # decisions replayed in a row through the memory
    epochs: int = 2
    minibatches: int = 12  # per epoch: about 24 steps of the optimiser an update
    device: str = "cpu"
    learning_rate: float = 2.5e-4
    gamma: float = 0.995
    lam: float = 0.95
    clip: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    save_every: int = 10

    @staticmethod
    def for_device(device: str) -> "Settings":
        """Return the defaults for this machine, learning on `device` ("cpu" or "cuda").

        On a CPU, the learner's backward pass is the bottleneck: a third of the cores play, the
        rest learn. With a GPU, the learner is fast and playing is the bottleneck: every core but
        two plays, each with 8 episodes (a batch through the network) and rounds of 64 decisions,
        and the learner goes over each round 3 times instead of 2 in the time the next one is
        played (on an RTX 2060 with 64 cores: 11,000 decisions a second either way).
        """
        if device == "cuda":
            return Settings(workers=max(1, CPUS - 2), envs=8, steps=64, epochs=3, device=device)
        return Settings(device=device)


def advantages(
    rollout: Rollout, gamma: float, lam: float
) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """Generalised advantage estimation: the advantages and the returns, (T, E)."""
    steps = rollout.rewards.shape[0]
    adv = np.zeros_like(rollout.rewards)
    last = np.zeros(rollout.rewards.shape[1], np.float32)
    for t in reversed(range(steps)):
        next_value = rollout.last_values if t == steps - 1 else rollout.values[t + 1]
        alive = 1.0 - rollout.dones[t].astype(np.float32)
        delta = rollout.rewards[t] + gamma * next_value * alive - rollout.values[t]
        last = delta + gamma * lam * alive * last
        adv[t] = last
    return adv, adv + rollout.values


class Learner:
    """The brain, its optimiser and the PPO update."""

    def __init__(self, settings: Settings, fresh: bool) -> None:
        self.settings = settings
        self.device = torch.device(settings.device)
        if BRAIN_FILE.exists() and not fresh:
            self.brain, self.stats = load_brain()
            print(f"Resuming the brain of {BRAIN_FILE} ({self.stats.updates} updates)")
        else:
            self.brain, self.stats = Brain(BrainShape()), LearnStats()
            print("Starting a new brain")
        self.brain.to(self.device)
        self.optimizer = torch.optim.Adam(
            self.brain.parameters(), lr=settings.learning_rate, eps=1e-5
        )
        if TRAINER_FILE.exists() and not fresh and self.stats.updates > 0:
            saved = torch.load(TRAINER_FILE, map_location="cpu", weights_only=True)
            self.optimizer.load_state_dict(saved["optimizer"])

    def save(self) -> None:
        save_brain(self.brain, self.stats)
        tmp = TRAINER_FILE.with_suffix(".tmp")
        torch.save({"optimizer": self.optimizer.state_dict()}, tmp)
        tmp.replace(TRAINER_FILE)

    def weights(self) -> dict[str, Any]:
        return {k: v.detach().to("cpu", copy=True) for k, v in self.brain.state_dict().items()}

    def _on_device(self, data: Rollout, adv: Any, returns: Any) -> dict[str, torch.Tensor]:
        """Return the round as tensors on the learner's device (moved once per update).

        On a CPU the shared buffer is used in place, without a copy.
        """
        arrays = {
            name: getattr(data, name)
            for name in (
                "field",
                "fovea",
                "state",
                "actions",
                "log_probs",
                "values",
                "starts",
                "memories",
            )
        }
        arrays["adv"] = adv
        arrays["returns"] = returns
        return {k: torch.as_tensor(np.asarray(v)).to(self.device) for k, v in arrays.items()}

    def update(self, data: Rollout) -> dict[str, float]:
        """Improve the brain from a round of play (several epochs of minibatches of sequences)."""
        s = self.settings
        adv, returns = advantages(data, s.gamma, s.lam)
        steps, envs = data.rewards.shape
        chunk = min(s.chunk, steps)
        chunks = [(k * chunk, e) for k in range(steps // chunk) for e in range(envs)]
        per_minibatch = max(1, math.ceil(len(chunks) / s.minibatches))
        dev = self.device
        t = self._on_device(data, (adv - adv.mean()) / (adv.std() + 1e-8), returns)
        t_field, t_fovea, t_state = t["field"], t["fovea"], t["state"]
        t_actions, t_logp, t_values = t["actions"], t["log_probs"], t["values"]
        t_adv, t_ret, t_starts, t_mem = t["adv"], t["returns"], t["starts"], t["memories"]
        losses: dict[str, list[float]] = {"policy": [], "value": [], "entropy": [], "kl": []}
        self.brain.train()
        for _ in range(s.epochs):
            random.shuffle(chunks)
            for i in range(0, len(chunks), per_minibatch):
                picked = chunks[i : i + per_minibatch]
                t0 = torch.tensor([c[0] for c in picked], device=dev)
                env = torch.tensor([c[1] for c in picked], device=dev)
                times = (t0.unsqueeze(0) + torch.arange(chunk, device=dev).unsqueeze(1)).reshape(-1)
                envs_idx = env.repeat(chunk)

                def take(
                    t: torch.Tensor, ti: torch.Tensor = times, ei: torch.Tensor = envs_idx
                ) -> Any:
                    return t[ti, ei]

                batch = Batch(take(t_field), take(t_fovea), take(t_state))
                decision = self.brain.unroll(batch, t_mem[t0, env], take(t_starts), chunk)
                logp = decision.log_prob(take(t_actions))
                ratio = torch.exp(logp - take(t_logp))
                a = take(t_adv)
                policy_loss = -torch.min(
                    ratio * a, torch.clamp(ratio, 1 - s.clip, 1 + s.clip) * a
                ).mean()
                old_v = take(t_values)
                v_clipped = old_v + torch.clamp(decision.value - old_v, -s.clip * 10, s.clip * 10)
                ret = take(t_ret)
                value_loss = torch.max((decision.value - ret) ** 2, (v_clipped - ret) ** 2).mean()
                entropy = decision.entropy().mean()
                loss = policy_loss + s.value_coef * value_loss - s.entropy_coef * entropy
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.brain.parameters(), s.max_grad_norm)
                self.optimizer.step()
                with torch.no_grad():
                    kl = (take(t_logp) - logp).mean()
                losses["policy"].append(policy_loss.item())
                losses["value"].append(value_loss.item())
                losses["entropy"].append(entropy.item())
                losses["kl"].append(kl.item())
        self.brain.eval()
        return {k: float(np.mean(v)) for k, v in losses.items()}


def _summary(episodes: list[EpisodeReport]) -> dict[str, float]:
    if not episodes:
        return {}
    full = [e for e in episodes if not e.mid_start]
    return {
        "episodes": len(episodes),
        "reward": float(np.mean([e.reward for e in episodes])),
        "progress": float(np.mean([e.progress for e in episodes])),
        "complete": float(np.mean([e.outcome == "complete" for e in episodes])),
        "lives_lost": float(np.mean([e.lives_lost for e in episodes])),
    } | ({"full_progress": float(np.mean([e.progress for e in full]))} if full else {})


LOG_COLUMNS = (
    "update",
    "decisions",
    "hours",
    "decisions_per_s",
    "wait_s",
    "learn_s",
    "episodes",
    "reward",
    "progress",
    "complete",
    "lives_lost",
    "full_progress",
    "policy",
    "value",
    "entropy",
    "kl",
)


def _log(row: dict[str, float]) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    new = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS, restval="", extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerow(row)


def _shared_dir() -> Path:
    """Return a new folder for the rollout buffers: in memory (`/dev/shm`) where there is one."""
    shm = Path("/dev/shm")  # noqa: S108  # shared memory, made private by mkdtemp
    base = shm if shm.is_dir() and os.access(shm, os.W_OK) else None
    return Path(tempfile.mkdtemp(prefix="stratoblaster-ai-", dir=base))


class Workers:
    """The worker processes playing the game, writing into two shared rollout buffers in turn."""

    def __init__(self, settings: Settings, shape: BrainShape, seed: int) -> None:
        ctx = mp.get_context("spawn")
        self.conns: list[Connection] = []
        self.procs: list[Any] = []
        self.episodes: list[EpisodeReport] = []
        self._dir = _shared_dir()
        total = settings.workers * settings.envs
        spec = (settings.steps, total, shape.hidden)
        # Two buffers: the workers play into one while the learner learns from the other.
        self.buffers = [
            RolloutBuffer(self._dir / f"rollout-{i}.bin", *spec, create=True) for i in range(2)
        ]
        paths = [(buffer.path, spec) for buffer in self.buffers]
        self._round = 0
        curriculum = Curriculum()
        for i in range(settings.workers):
            parent, child = ctx.Pipe()
            envs = (i * settings.envs, (i + 1) * settings.envs)
            proc = ctx.Process(
                target=worker_main,
                args=(child, shape, envs, seed * 1000 + i, curriculum, paths),
                daemon=True,
            )
            proc.start()
            child.close()
            self.conns.append(parent)
            self.procs.append(proc)

    def start(self, weights: dict[str, Any]) -> None:
        """Have every worker play a round with `weights` (in the background)."""
        payload = pickle.dumps((self._round % 2, weights))  # pickled once for every worker
        for conn in self.conns:
            conn.send_bytes(payload)

    def collect(self) -> Rollout:
        """Wait for the round under way; return it (it stays valid until the next one starts)."""
        episodes: list[EpisodeReport] = []
        for conn in self.conns:
            got = conn.recv()
            if isinstance(got, str):
                msg = "A worker failed:\n" + got
                raise RuntimeError(msg)  # noqa: TRY004  # a worker's traceback, not a type error
            episodes.extend(got)
        rollout = self.buffers[self._round % 2].rollout()
        rollout.episodes = episodes
        self._round += 1
        return rollout

    def close(self) -> None:
        stop = pickle.dumps(None)
        for conn in self.conns:
            try:
                conn.send_bytes(stop)
            except (BrokenPipeError, OSError):
                pass
        for proc in self.procs:
            proc.join(timeout=10)
            if proc.is_alive():
                proc.terminate()
        shutil.rmtree(self._dir, ignore_errors=True)


def learn(settings: Settings, minutes: float, fresh: bool, seed: int) -> None:
    """Learn for `minutes` (or until Ctrl-C), saving the brain as it goes."""
    if settings.device == "cuda":
        torch.backends.cudnn.benchmark = True
        torch.set_num_threads(2)
    else:
        torch.set_num_threads(max(1, CPUS - settings.workers))
    learner = Learner(settings, fresh)
    workers = Workers(settings, learner.brain.shape, seed + learner.stats.updates)
    print(
        f"Learning on {settings.device} for {minutes:g} min with {settings.workers} workers x"
        f" {settings.envs}"
        f" episodes ({settings.workers * settings.envs * settings.steps} decisions per update)."
        " Ctrl-C stops (and saves)."
    )
    stop = _StopOnCtrlC()
    start = time.monotonic()
    last = start
    try:
        # The workers play a round while the brain learns from the one before (one update late:
        # the clipped ratio of PPO allows for it).
        workers.start(learner.weights())
        while time.monotonic() - start < minutes * 60 and not stop.requested:
            t0 = time.monotonic()
            data = workers.collect()
            workers.start(learner.weights())
            t1 = time.monotonic()
            losses = learner.update(data)
            t2 = time.monotonic()
            stats = learner.stats
            stats.updates += 1
            stats.decisions += int(data.rewards.size)
            stats.episodes += len(data.episodes)
            now = time.monotonic()
            stats.hours += (now - last) / 3600
            last = now
            row: dict[str, float] = {
                "update": stats.updates,
                "decisions": stats.decisions,
                "hours": round(stats.hours, 4),
                "decisions_per_s": round(data.rewards.size / max(1e-6, t2 - t0), 1),
                "wait_s": round(t1 - t0, 2),
                "learn_s": round(t2 - t1, 2),
                **_summary(data.episodes),
                **losses,
            }
            stats.history.append(row)
            del stats.history[:-HISTORY_KEPT]
            _log(row)
            _print(row)
            if stats.updates % settings.save_every == 0:
                learner.save()
    finally:
        stop.ignore()
        workers.close()
        learner.save()
        print(f"Brain saved in {BRAIN_FILE} ({learner.stats.updates} updates).", flush=True)


class _StopOnCtrlC:
    """Ctrl-C asks to stop once the update under way is done, so the brain is saved whole."""

    def __init__(self) -> None:
        self.requested = False
        signal.signal(signal.SIGINT, self._handle)

    def _handle(self, _signum: int, _frame: object) -> None:
        if not self.requested:
            print("\nStopping after this update (the brain is then saved)...", flush=True)
        self.requested = True

    def ignore(self) -> None:
        signal.signal(signal.SIGINT, signal.SIG_IGN)


def _print(row: dict[str, float]) -> None:
    parts = [
        f"#{int(row['update'])}",
        f"{row['decisions'] / 1e6:.2f}M dec",
        f"{row['decisions_per_s']:.0f}/s",
    ]
    if "episodes" in row:
        parts += [
            f"eps {int(row['episodes'])}",
            f"reward {row['reward']:+.2f}",
            f"progress {row['progress']:.0%}",
            f"done {row['complete']:.0%}",
            f"lives lost {row['lives_lost']:.2f}",
        ]
    parts += [
        f"entropy {row['entropy']:.2f}",
        f"kl {row['kl']:.4f}",
        f"wait {row['wait_s']:.1f}s learn {row['learn_s']:.1f}s",
    ]
    print(" | ".join(parts), flush=True)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="The brain learns to play the game.")
    parser.add_argument("--minutes", type=float, default=60.0, help="how long to learn for")
    parser.add_argument(
        "--device",
        choices=("auto", "cpu", "cuda"),
        default="auto",
        help="where the learner runs (auto: the GPU if torch sees one)",
    )
    parser.add_argument("--workers", type=int, help="processes playing (default: per device)")
    parser.add_argument("--envs", type=int, help="episodes each worker plays side by side")
    parser.add_argument("--steps", type=int, help="decisions per episode per round")
    parser.add_argument("--fresh", action="store_true", help="start a new brain")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)
    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    elif device == "cuda" and not torch.cuda.is_available():
        parser.error("torch sees no CUDA GPU: is it the CUDA build? (`make learn AI_TORCH=cuda`)")
    settings = Settings.for_device(device)
    given = {k: getattr(args, k) for k in ("workers", "envs", "steps") if getattr(args, k)}
    learn(replace(settings, **given), args.minutes, args.fresh, args.seed)


if __name__ == "__main__":
    main()
