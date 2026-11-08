# Copyright (c) 2026 Renaud Guillon
"""`make learn`: the brain learns to play the game (proximal policy optimisation, PPO).

Worker processes play games (`play_worker.py`, under PyPy: about five times faster than CPython,
D-301), each from level 1-1 with 3 lives and 3 bombs, on through the levels with what it earned,
until the game is over (D-295). An inference server decides their moves with the current brain
(`inference.py`). The learner improves the brain from what they played, for the best score, and
sends the server the new weights. It goes on for `--minutes`, or until Ctrl-C, saving the brain
under `data/` every few updates and at the end; the brain whose games scored best on average is
kept too (`data/brain-best.pt`). It starts from the saved brain when there is one (`--fresh` to
start over).

Every 10 seconds it says how the games went (`--report-seconds`); `data/learn-log.csv` has the
details of each update.

With an NVIDIA GPU (and the CUDA build of torch: `make learn AI_TORCH=cuda`) the learner and the
server run on the GPU and nearly every CPU core plays; on a CPU only, half the cores play, the rest
decide and learn. Without PyPy (`uv python install pypy3.12`) the workers play in CPython.

    uv run python -m ai.learn --minutes 120 [--device cuda] [--worker-python PATH]
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
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import torch
from numpy.typing import NDArray
from torch import nn

from ai import DATA, REPO_ROOT, STUBS_VARIABLE, transcrypt_stubs
from ai.brain import (
    BEST_BRAIN_FILE,
    BRAIN_FILE,
    TRAINER_FILE,
    Batch,
    Brain,
    BrainShape,
    Decision,
    IncompatibleBrainError,
    LearnStats,
    load_brain,
    save_brain,
)
from ai.game_env import LEVEL_IDS
from ai.inference import server_main
from ai.play_worker import WorkerSetup
from ai.rollout import (
    Curriculum,
    EpisodeReport,
    GameProgress,
    Rollout,
    RolloutBuffer,
)

if TYPE_CHECKING:
    from multiprocessing.connection import Connection

LOG_FILE = DATA / "learn-log.csv"
HISTORY_KEPT = 2000
# Games a report needs for its average score to choose the best brain.
MIN_GAMES_FOR_BEST = 20


CPUS = os.cpu_count() or 2


# The PyPy the workers play in (D-301): `uv python install pypy3.12` installs it.
PYPY = "pypy3.12"


def find_pypy() -> str:
    """Return the path of PyPy (as `uv python find` sees it), '' when it is not installed."""
    found = shutil.which(PYPY)
    if found:
        return found
    try:
        done = subprocess.run(  # noqa: S603  # uv, with fixed arguments
            ["uv", "python", "find", PYPY],  # noqa: S607  # uv from the PATH, as make runs it
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout.strip()


@dataclass
class Settings:
    """How the brain learns (see `for_device` for the defaults of a machine)."""

    workers: int = max(1, CPUS // 2)
    envs: int = 16  # episodes played side by side by each worker
    steps: int = 64  # decisions per episode per round
    chunk: int = 32  # decisions replayed in a row through the memory
    epochs: int = 2
    minibatches: int = 12  # per epoch: about 24 steps of the optimiser an update
    device: str = "cpu"
    learning_rate: float = 2.5e-4
    gamma: float = 0.998  # about 30 s ahead: a life lost is the points it would have scored
    lam: float = 0.95
    clip: float = 0.2
    value_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    save_every: int = 10
    report_seconds: float = 10.0
    # The learner's sums in half precision where it is safe (PyTorch's autocast, the losses
    # scaled against underflow): a GPU's tensor cores do them several times faster (D-299).
    mixed_precision: bool = False
    # The Python the workers play in: PyPy plays about five times faster than CPython (D-301).
    # Empty: the learner's own (CPython).
    worker_python: str = ""
    # PyTorch's threads in the inference server, which decides for every worker (D-298).
    server_threads: int = 1

    @staticmethod
    def for_device(device: str) -> "Settings":
        """Return the defaults for this machine, learning on `device` ("cpu" or "cuda").

        The brain decides for every worker in one server process, on the learner's device
        (D-298). With a GPU, the learner is fast and playing is the bottleneck: every core but
        three plays, each with 16 episodes and rounds of 32 decisions (D-289, D-299). On a CPU,
        the server and the learner compute the brain themselves: half the cores play, a quarter
        decide, the rest learn.
        """
        if device == "cuda":
            workers = max(1, CPUS - 3)  # a core each for the learner and the inference server
            return Settings(
                workers=workers,
                envs=16,  # two halves of 8: the server's batches are bigger, and less often
                steps=32,  # a round as big as before (it goes to the GPU whole)
                device=device,
                mixed_precision=True,
            )
        return Settings(device=device, server_threads=max(1, CPUS // 4))


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


def _fits(optimizer: dict[str, Any], brain: Brain) -> bool:
    """Whether a saved Adam state is of parameters shaped as the brain's (in the same order)."""
    shapes = [p.shape for p in brain.parameters()]
    for index, state in optimizer["state"].items():
        moment = state.get("exp_avg")
        if moment is not None and (index >= len(shapes) or moment.shape != shapes[index]):
            return False
    return True


class Learner:
    """The brain, its optimiser and the PPO update."""

    def __init__(self, settings: Settings, fresh: bool) -> None:
        self.settings = settings
        self.device = torch.device(settings.device)
        if BRAIN_FILE.exists() and not fresh:
            try:
                self.brain, self.stats = load_brain(BRAIN_FILE)
            except IncompatibleBrainError as error:
                print(f"{error}\nStarting a new brain instead.")
                fresh = True
                self.brain, self.stats = Brain(BrainShape()), LearnStats()
            else:
                print(f"Resuming the brain of {BRAIN_FILE} ({self.stats.updates} updates)")
        else:
            self.brain, self.stats = Brain(BrainShape()), LearnStats()
            print("Starting a new brain")
        self.brain.to(self.device)
        self.optimizer = torch.optim.Adam(
            self.brain.parameters(), lr=settings.learning_rate, eps=1e-5
        )
        self.mixed = settings.mixed_precision and self.device.type == "cuda"
        self.scaler = torch.amp.GradScaler("cuda", enabled=self.mixed)
        if TRAINER_FILE.exists() and not fresh and self.stats.updates > 0:
            saved = torch.load(TRAINER_FILE, map_location="cpu", weights_only=True)
            if _fits(saved["optimizer"], self.brain):
                self.optimizer.load_state_dict(saved["optimizer"])
            else:  # a brain widened to new channels (`widen_inputs`): its moments start over
                print("The optimiser's state is of a smaller brain: starting it over")

    def save(self) -> None:
        save_brain(self.brain, self.stats, BRAIN_FILE)
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
        losses: dict[str, list[torch.Tensor]] = {"policy": [], "value": [], "entropy": [], "kl": []}
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
                with torch.autocast(dev.type, dtype=torch.float16, enabled=self.mixed):
                    half = self.brain.unroll(batch, t_mem[t0, env], take(t_starts), chunk)
                # The losses in full precision.
                decision = Decision(
                    half.move.float(), half.bomb.float(), half.switch.float(), half.value.float()
                )
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
                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                nn.utils.clip_grad_norm_(self.brain.parameters(), s.max_grad_norm)
                self.scaler.step(self.optimizer)
                self.scaler.update()
                with torch.no_grad():
                    kl = (take(t_logp) - logp).mean()
                # Kept on the device: read once at the end, not a wait for the GPU each time.
                losses["policy"].append(policy_loss.detach())
                losses["value"].append(value_loss.detach())
                losses["entropy"].append(entropy.detach())
                losses["kl"].append(kl)
        self.brain.eval()
        return {k: torch.stack(v).mean().item() for k, v in losses.items()}


def _summary(episodes: list[EpisodeReport]) -> dict[str, float]:
    """Return the games that ended in an update, summed up for the log."""
    if not episodes:
        return {}
    return {
        "games": len(episodes),
        "score": float(np.mean([e.score for e in episodes])),
        "best_score": float(max(e.score for e in episodes)),
        "cleared": float(np.mean([e.cleared for e in episodes])),
        "game_over": float(np.mean([e.outcome == "over" for e in episodes])),
        "too_slow": float(np.mean([e.outcome == "timeout" for e in episodes])),
        "finished": float(np.mean([e.outcome == "complete" for e in episodes])),
    }


LOG_COLUMNS = (
    "update",
    "decisions",
    "hours",
    "decisions_per_s",
    "wait_s",
    "learn_s",
    "games",
    "score",
    "best_score",
    "cleared",
    "game_over",
    "too_slow",
    "finished",
    "policy",
    "value",
    "entropy",
    "kl",
)


def _log(row: dict[str, float]) -> None:
    """Add `row` to the log; a log of other columns (an older `make learn`) is moved aside."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LOG_FILE.exists():
        with LOG_FILE.open(newline="") as f:
            header = next(csv.reader(f), [])
        if tuple(header) != LOG_COLUMNS:
            LOG_FILE.replace(LOG_FILE.with_suffix(".old.csv"))
    new = not LOG_FILE.exists()
    with LOG_FILE.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=LOG_COLUMNS, restval="", extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerow(row)


def _shown(path: Path) -> str:
    """Return `path` from the repository's root when it is in it (`data/brain.pt`)."""
    return str(path.relative_to(DATA.parent)) if path.is_relative_to(DATA.parent) else str(path)


def _level_after(cleared: int) -> str:
    """Return the level a game ended in after clearing `cleared` levels (the last: all cleared)."""
    return LEVEL_IDS[min(cleared, len(LEVEL_IDS) - 1)]


def _share(count: int, total: int) -> str:
    return f"{count} ({count / total:.0%})"


def _play_time(decisions: float) -> str:
    """Return the game time of `decisions` moves (15 a second), as minutes:seconds."""
    seconds = int(decisions / 15)
    return f"{seconds // 60}:{seconds % 60:02d}"


def _record_best_game(stats: LearnStats, games: list[EpisodeReport]) -> None:
    """Keep the game that scored the most so far in `stats` (it is saved with the brain)."""
    for game in games:
        if game.score > stats.best_game.get("score", 0):
            stats.best_game = {
                "score": game.score,
                "reached": game.reached,
                "cleared": game.cleared,
                "decisions": game.decisions,
                "outcome": game.outcome,
                "update": stats.updates,
            }


_ENDINGS = {
    "over": "ship lost",
    "timeout": "too slow on a level",
    "complete": "every level cleared",
}


def _playing_lines(playing: list[GameProgress]) -> list[str]:
    if not playing:
        return []
    count = len(playing)
    moves = float(np.mean([g.decisions for g in playing]))
    points = float(np.mean([g.score for g in playing]))
    past = sum(g.cleared > 0 for g in playing)
    lead = max(playing, key=lambda g: (g.score, g.cleared))
    furthest = max(playing, key=lambda g: g.cleared)
    now = (
        f"  Playing now    {count} games, on average {moves:,.0f} moves in ({_play_time(moves)} of"
        f" play) and {points:,.0f} points; {_share(past, count)} past {LEVEL_IDS[0]}, furthest in"
        f" {furthest.level}"
    )
    leading = (
        f"  Leading now    {lead.score:,.0f} points, in {lead.level} ({lead.cleared} levels"
        f" cleared, {_play_time(lead.decisions)} of play)"
    )
    return [now, leading]


def _ended_lines(games: list[EpisodeReport]) -> list[str]:
    if not games:
        return ["  Games ended    none since the last report (a game lasts until the ship is lost)"]
    count = len(games)
    over = sum(g.outcome == "over" for g in games)
    slow = sum(g.outcome == "timeout" for g in games)
    finished = sum(g.outcome == "complete" for g in games)
    cleared = [g.cleared for g in games]
    top = max(games, key=lambda g: (g.score, g.cleared))
    beyond_first = sum(c > 0 for c in cleared)
    ended = (
        f"  Games ended    {count} since the last report: {_share(over, count)} game over,"
        f" {_share(slow, count)} too slow on a level, {_share(finished, count)} cleared every"
        " level"
    )
    score = (
        f"  Their score    average {np.mean([g.score for g in games]):,.0f}, best"
        f" {top.score:,.0f} (reached {top.reached})"
    )
    levels = (
        f"  Their levels   {np.mean(cleared):.1f} cleared on average, furthest reached"
        f" {_level_after(max(cleared))}; {_share(beyond_first, count)} got past {LEVEL_IDS[0]}"
    )
    return [ended, score, levels]


def report(
    games: list[EpisodeReport],
    stats: LearnStats,
    seconds: float,
    per_second: float,
    best: bool,
    playing: list[GameProgress] | None = None,
) -> str:
    """Say in plain words how the games stand, how those that ended went, and the best one.

    The games being played now, those that ended since the last report, and the best game since
    learning started.
    """
    title = (
        f"{int(seconds) // 60}:{int(seconds) % 60:02d} in, {per_second:,.0f} moves a second"
        f" · in all: {stats.hours:.1f} h,"
        f" {stats.decisions / 1e6:.1f} M moves, {stats.updates} updates of the brain"
    )
    lines = [f"── {title} " + "─" * max(0, 96 - len(title))]
    lines += _playing_lines(playing or [])
    lines += _ended_lines(games)
    record = stats.best_game
    if record:
        lines.append(
            f"  Best game ever {record['score']:,.0f} points: reached {record['reached']}"
            f" ({record['cleared']} levels cleared), {_play_time(record['decisions'])} of play,"
            f" ended: {_ENDINGS.get(record['outcome'], record['outcome'])}, at update"
            f" {record['update']:,}"
        )
    if stats.best_score > 0:
        note = f"this brain, saved in {_shown(BEST_BRAIN_FILE)}" if best else "an earlier brain"
        lines.append(f"  Best average   {stats.best_score:,.0f} a game ({note})")
    return "\n".join(lines)


def _shared_dir() -> Path:
    """Return a new folder for the rollout buffers: in memory (`/dev/shm`) where there is one."""
    shm = Path("/dev/shm")  # noqa: S108  # shared memory, made private by mkdtemp
    base = shm if shm.is_dir() and os.access(shm, os.W_OK) else None
    return Path(tempfile.mkdtemp(prefix="stratoblaster-ai-", dir=base))


class Workers:
    """The worker processes playing the game, writing into two shared rollout buffers in turn.

    Each worker is a process of `settings.worker_python` (PyPy, D-301) running
    `ai.play_worker`; an inference server process decides for all of them (D-298). The learner
    and the server talk to each worker through `multiprocessing` pipes whose ends it inherits.
    """

    def __init__(self, settings: Settings, shape: BrainShape, seed: int) -> None:
        ctx = mp.get_context("spawn")
        self.conns: list[Connection] = []
        self.procs: list[Any] = []
        self.workers: list[subprocess.Popen[bytes]] = []
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
        server_ends: list[Connection] = []
        worker_server_ends: list[Connection] = []
        for _ in range(settings.workers):
            server_end, worker_end = ctx.Pipe()
            server_ends.append(server_end)
            worker_server_ends.append(worker_end)
        self.server, server_learner = ctx.Pipe()
        proc = ctx.Process(
            target=server_main,
            args=(
                server_learner,
                server_ends,
                shape,
                settings.device,
                paths,
                seed,
                settings.server_threads,
            ),
            daemon=True,
        )
        proc.start()
        self.procs.append(proc)
        for end in (server_learner, *server_ends):
            end.close()  # the server has its own copies
        python = settings.worker_python or sys.executable
        env = {
            # PyPy's young generation: set, it does not look for the CPU's cache sizes (and warns
            # where it cannot find them, as under WSL).
            "PYPY_GC_NURSERY": "4M",
            **os.environ,
            "PYTHONPATH": str(REPO_ROOT / "tests"),
            STUBS_VARIABLE: transcrypt_stubs(),
        }
        for i in range(settings.workers):
            mine, theirs = ctx.Pipe()
            fds = (theirs.fileno(), worker_server_ends[i].fileno())
            self.workers.append(
                subprocess.Popen(  # noqa: S603  # this repository's worker, by its module name
                    [python, "-m", "ai.play_worker", *(str(fd) for fd in fds)],
                    env=env,
                    cwd=REPO_ROOT,
                    pass_fds=fds,
                )
            )
            theirs.close()
            worker_server_ends[i].close()
            lo = i * settings.envs
            mine.send(
                WorkerSetup(
                    lo,
                    lo + settings.envs,
                    seed * 1000 + i,
                    Curriculum(),
                    [str(path) for path, _ in paths],
                    spec,
                )
            )
            self.conns.append(mine)
        for conn in self.conns:
            try:
                self._check(conn.recv(), "A worker")  # True: ready
            except EOFError:
                msg = f"A worker ({python}) stopped before it started: its error is above."
                raise RuntimeError(msg) from None

    def start(self, weights: dict[str, Any]) -> None:
        """Have every worker play a round with `weights` (in the background)."""
        index = self._round % 2
        self.server.send_bytes(pickle.dumps((index, weights)))
        self._check(self.server.recv(), "The inference server")
        for conn in self.conns:
            conn.send(index)  # the server decides: the workers need no weights

    def _check(self, got: Any, who: str) -> Any:
        """Return `got`, or raise with the traceback a process sent instead."""
        if isinstance(got, str):
            if self.server.poll():
                got += "\n" + str(self.server.recv())
            msg = f"{who} failed:\n{got}"
            raise RuntimeError(msg)  # noqa: TRY004  # a process's traceback, not a type error
        return got

    def collect(self) -> Rollout:
        """Wait for the round under way; return it (it stays valid until the next one starts)."""
        episodes: list[EpisodeReport] = []
        playing: list[GameProgress] = []
        for conn in self.conns:
            ended, going = self._check(conn.recv(), "A worker")
            episodes.extend(ended)
            playing.extend(going)
        rollout = self.buffers[self._round % 2].rollout()
        rollout.episodes = episodes
        rollout.playing = playing
        self._round += 1
        return rollout

    def close(self) -> None:
        for conn in self.conns:
            try:
                conn.send(None)
            except (BrokenPipeError, OSError):
                pass
        try:
            self.server.send_bytes(pickle.dumps(None))
        except (BrokenPipeError, OSError):
            pass
        for worker in self.workers:
            try:
                worker.wait(timeout=10)
            except subprocess.TimeoutExpired:
                worker.terminate()
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
        torch.set_num_threads(max(1, CPUS - settings.workers - settings.server_threads))
    learner = Learner(settings, fresh)
    workers = Workers(settings, learner.brain.shape, seed + learner.stats.updates)
    _introduce(settings, minutes)
    stop = _StopOnCtrlC()
    start = time.monotonic()
    last = start
    reporter = Reporter(settings.report_seconds, learner.stats)
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
            if stats.updates % settings.save_every == 0:
                learner.save()
            reporter.add(data.episodes, learner, data.playing)
    finally:
        stop.ignore()
        workers.close()
        learner.save()
        _farewell(learner.stats)


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


class Reporter:
    """Says how the games went every `seconds`, and keeps the brain that scored best."""

    def __init__(self, seconds: float, stats: LearnStats) -> None:
        self.seconds = seconds
        self.start = time.monotonic()
        self._last = self.start
        self._decisions = stats.decisions
        self._games: list[EpisodeReport] = []
        # The games of the brain's last few reports, until there are enough to judge it by.
        self._judged: list[EpisodeReport] = []

    def add(
        self,
        games: list[EpisodeReport],
        learner: Learner,
        playing: list[GameProgress] | None = None,
    ) -> None:
        """Count the games that ended in an update; report when it is time.

        `playing`: how the games still being played stand.
        """
        self._games.extend(games)
        _record_best_game(learner.stats, games)
        now = time.monotonic()
        if now - self._last < self.seconds:
            return
        stats = learner.stats
        per_second = (stats.decisions - self._decisions) / max(1e-6, now - self._last)
        self._judged.extend(self._games)
        best = _keep_if_best(learner, self._judged)
        if len(self._judged) >= MIN_GAMES_FOR_BEST:
            self._judged = []
        text = report(self._games, stats, now - self.start, per_second, best, playing or [])
        print(text, flush=True)
        self._games = []
        self._last = now
        self._decisions = stats.decisions


def _runtime(settings: Settings) -> str:
    """Return the name of the Python the workers play in ("PyPy" or "CPython")."""
    return "PyPy" if "pypy" in Path(settings.worker_python or sys.executable).name else "CPython"


def _introduce(settings: Settings, minutes: float) -> None:
    games = settings.workers * settings.envs
    print(
        f"The brain learns on the {settings.device.upper()} for {minutes:g} minutes: {games} games"
        f" at once ({settings.workers} {_runtime(settings)} processes x {settings.envs}), each from"
        f" {LEVEL_IDS[0]} with"
        " 3 lives and 3 bombs, on to the next level when one is cleared, until the ship is lost.\n"
        f"It learns to score the most. Every {settings.report_seconds:g} s: how the games went"
        f" (details in {_shown(LOG_FILE)}). Ctrl-C stops and saves.",
        flush=True,
    )


def _farewell(stats: LearnStats) -> None:
    print(
        f"The brain is saved in {_shown(BRAIN_FILE)}: {stats.updates}"
        f" updates, {stats.hours:.1f} h of learning in all.",
        flush=True,
    )
    if stats.best_score > 0:
        print(
            f"The best one so far (average score {stats.best_score:,.0f}) is in"
            f" {_shown(BEST_BRAIN_FILE)}.",
            flush=True,
        )


def _keep_if_best(learner: Learner, games: list[EpisodeReport]) -> bool:
    """Save the brain as the best when its games scored best on average so far (D-295).

    Only with enough games for the average to mean something. Returns whether it was saved.
    """
    if len(games) < MIN_GAMES_FOR_BEST:
        return False
    average = float(np.mean([g.score for g in games]))
    if average <= learner.stats.best_score:
        return False
    learner.stats.best_score = average
    save_brain(learner.brain, learner.stats, BEST_BRAIN_FILE)
    return True


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
    parser.add_argument(
        "--worker-python",
        default="auto",
        help="the Python the workers play in (auto: PyPy if installed, else this one)",
    )
    parser.add_argument("--fresh", action="store_true", help="start a new brain")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument(
        "--report-seconds", type=float, default=10.0, help="how often to say how the games went"
    )
    args = parser.parse_args(argv)
    device = args.device
    if device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    elif device == "cuda" and not torch.cuda.is_available():
        parser.error("torch sees no CUDA GPU: is it the CUDA build? (`make learn AI_TORCH=cuda`)")
    settings = Settings.for_device(device)
    given = {k: getattr(args, k) for k in ("workers", "envs", "steps") if getattr(args, k)}
    given["report_seconds"] = args.report_seconds
    worker_python = find_pypy() if args.worker_python == "auto" else args.worker_python
    if not worker_python:
        print(
            f"{PYPY} is not installed (`uv python install {PYPY}`): the workers play in CPython,"
            " about five times slower.",
            flush=True,
        )
    given["worker_python"] = worker_python
    learn(replace(settings, **given), args.minutes, args.fresh, args.seed)


if __name__ == "__main__":
    main()
