# Copyright (c) 2026 Renaud Guillon
"""`make learn`: the brain learns to play the game (proximal policy optimisation, PPO).

Worker processes play the levels with the current brain (see `rollout.py`); the learner then
improves the brain from what they played, and sends them the new weights. It goes on for
`--minutes`, or until Ctrl-C, saving the brain under `data/` every few updates and at the end.
It starts from the saved brain when there is one (`--fresh` to start over).

    uv run python -m ai.learn --minutes 120
"""

import argparse
import csv
import multiprocessing as mp
import os
import random
import signal
import time
from dataclasses import dataclass
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
from ai.rollout import Curriculum, EpisodeReport, Rollout, worker_main

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

LOG_FILE = DATA / "learn-log.csv"
HISTORY_KEPT = 2000


@dataclass
class Settings:
    """How the brain learns."""

    # The workers play a round faster than the learner learns from it (the network's backward pass
    # is the costly part on a CPU): a third of the cores play, the rest learn.
    workers: int = max(1, (os.cpu_count() or 3) // 3)
    envs: int = 12  # episodes played side by side by each worker
    steps: int = 128  # decisions per episode per round
    chunk: int = 32  # decisions replayed in a row through the memory
    epochs: int = 2
    # 256 decisions a minibatch: about 24 steps of the optimiser an update.
    minibatch_chunks: int = 8
    learning_rate: float = 2.5e-4
    gamma: float = 0.995
    lam: float = 0.95
    clip: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    save_every: int = 10


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


def _join(rollouts: list[Rollout]) -> Rollout:
    """Return the rollouts of every worker as one, their episodes side by side."""

    def cat(name: str, axis: int = 1) -> Any:
        return np.concatenate([getattr(r, name) for r in rollouts], axis=axis)

    episodes: list[EpisodeReport] = []
    for r in rollouts:
        episodes.extend(r.episodes)
    return Rollout(
        cat("field"),
        cat("fovea"),
        cat("state"),
        cat("actions"),
        cat("log_probs"),
        cat("values"),
        cat("rewards"),
        cat("dones"),
        cat("starts"),
        cat("memories"),
        cat("last_values", 0),
        episodes,
    )


class Learner:
    """The brain, its optimiser and the PPO update."""

    def __init__(self, settings: Settings, fresh: bool) -> None:
        self.settings = settings
        if BRAIN_FILE.exists() and not fresh:
            self.brain, self.stats = load_brain()
            print(f"Resuming the brain of {BRAIN_FILE} ({self.stats.updates} updates)")
        else:
            self.brain, self.stats = Brain(BrainShape()), LearnStats()
            print("Starting a new brain")
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
        return {k: v.detach().clone() for k, v in self.brain.state_dict().items()}

    def update(self, data: Rollout) -> dict[str, float]:
        """Improve the brain from a round of play (several epochs of minibatches of sequences)."""
        s = self.settings
        adv, returns = advantages(data, s.gamma, s.lam)
        steps, envs = data.rewards.shape
        chunk = min(s.chunk, steps)
        chunks = [(k * chunk, e) for k in range(steps // chunk) for e in range(envs)]
        t_field = torch.as_tensor(data.field)
        t_fovea = torch.as_tensor(data.fovea)
        t_state = torch.as_tensor(data.state)
        t_actions = torch.as_tensor(data.actions)
        t_logp = torch.as_tensor(data.log_probs)
        t_values = torch.as_tensor(data.values)
        t_adv = torch.as_tensor((adv - adv.mean()) / (adv.std() + 1e-8))
        t_ret = torch.as_tensor(returns)
        t_starts = torch.as_tensor(data.starts)
        t_mem = torch.as_tensor(data.memories)
        losses: dict[str, list[float]] = {"policy": [], "value": [], "entropy": [], "kl": []}
        self.brain.train()
        for _ in range(s.epochs):
            random.shuffle(chunks)
            for i in range(0, len(chunks), s.minibatch_chunks):
                picked = chunks[i : i + s.minibatch_chunks]
                t0 = torch.tensor([c[0] for c in picked])
                env = torch.tensor([c[1] for c in picked])
                times = (t0.unsqueeze(0) + torch.arange(chunk).unsqueeze(1)).reshape(-1)
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


class Workers:
    """The worker processes playing the game."""

    def __init__(self, settings: Settings, shape: BrainShape, seed: int) -> None:
        ctx = mp.get_context("spawn")
        self.conns: list[Connection] = []
        self.procs: list[Any] = []
        curriculum = Curriculum()
        for i in range(settings.workers):
            parent, child = ctx.Pipe()
            proc = ctx.Process(
                target=worker_main,
                args=(child, shape, settings.envs, seed * 1000 + i, curriculum),
                daemon=True,
            )
            proc.start()
            child.close()
            self.conns.append(parent)
            self.procs.append(proc)

    def start(self, weights: dict[str, Any], steps: int) -> None:
        """Have every worker play a round with `weights` (in the background)."""
        for conn in self.conns:
            conn.send((weights, steps))

    def collect(self) -> list[Rollout]:
        """Wait for the round every worker is playing."""
        rollouts: list[Rollout] = []
        for conn in self.conns:
            got = conn.recv()
            if isinstance(got, str):
                msg = "A worker failed:\n" + got
                raise RuntimeError(msg)  # noqa: TRY004  # a worker's traceback, not a type error
            rollouts.append(got)
        return rollouts

    def close(self) -> None:
        for conn in self.conns:
            try:
                conn.send(None)
            except (BrokenPipeError, OSError):
                pass
        for proc in self.procs:
            proc.join(timeout=5)
            if proc.is_alive():
                proc.terminate()


def learn(settings: Settings, minutes: float, fresh: bool, seed: int) -> None:
    """Learn for `minutes` (or until Ctrl-C), saving the brain as it goes."""
    torch.set_num_threads(max(1, (os.cpu_count() or 2) - settings.workers))
    learner = Learner(settings, fresh)
    workers = Workers(settings, learner.brain.shape, seed + learner.stats.updates)
    print(
        f"Learning for {minutes:g} min with {settings.workers} workers x {settings.envs}"
        f" episodes ({settings.workers * settings.envs * settings.steps} decisions per update)."
        " Ctrl-C stops (and saves)."
    )
    stop = _StopOnCtrlC()
    start = time.monotonic()
    last = start
    try:
        # The workers play a round while the brain learns from the one before (one update late:
        # the clipped ratio of PPO allows for it).
        workers.start(learner.weights(), settings.steps)
        while time.monotonic() - start < minutes * 60 and not stop.requested:
            t0 = time.monotonic()
            data = _join(workers.collect())
            workers.start(learner.weights(), settings.steps)
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
    parser.add_argument("--workers", type=int, default=Settings.workers)
    parser.add_argument("--envs", type=int, default=Settings.envs)
    parser.add_argument("--steps", type=int, default=Settings.steps)
    parser.add_argument("--fresh", action="store_true", help="start a new brain")
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args(argv)
    settings = Settings(workers=args.workers, envs=args.envs, steps=args.steps)
    learn(settings, args.minutes, args.fresh, args.seed)


if __name__ == "__main__":
    main()
