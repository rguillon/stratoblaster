# Copyright (c) 2026 Renaud Guillon
"""`make adjust-level`: tune a level's enemy count until the brain rates it at a target (D-305).

    uv run python -m ai.adjust --level 4-4 --target 90
    uv run python -m ai.adjust --all --first 10 --last 99   # `make adjust-levels`: every level

Every enemy and boss is the same in every level (D-307): what a level changes is how many enemies
it brings, its `LEVEL_ENEMIES` factor (1: its waves as `level_plan` composes them). Each step rates
the level with that factor, as `make rate` does (same loadout, same seeds every step, so two steps
differ by the factor alone), then picks the next:

- until the target is bracketed, the factor grows (or shrinks) by `STRIDE`, the way the ratings
  so far go with it (more enemies are harder, D-309, but it is not taken for granted);
- then it is interpolated between the closest ratings either side of the target.

Each rating plays `--episodes` episodes (100); they double once the target is bracketed, up to
`--max-episodes` (100 too: no doubling by default). It stops once a rating is within `--tolerance`
of the target (or within two standard errors of it at the most episodes), and writes the factor
into the level's line of `src/game/config/level_enemies.py`. More enemies have no limit (D-312):
it goes on until the target or `--max-steps`, when it keeps the closest. Fewer stop at `--lowest`
(a level too hard even then is left as it was).
"""

import argparse
import itertools
import json
import math
import os
import re
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path

from ai import DATA, REPO_ROOT, SRC
from ai.brain import BRAIN_FILE, load_brain
from ai.game_env import LEVEL_IDS, SHIP_IDS, level_enemies
from ai.rate import RatingSettings, play_all, rate_level, setups

# How much the factor grows (or shrinks) each step until the target is bracketed.
STRIDE = 1.4
# An interpolated factor stays this share of the bracket away from its ends, so a noisy end that is
# far off does not hold the search next to the other.
MARGIN = 0.1
# The factors are written to two decimals.
DECIMALS = 2


@dataclass
class Step:
    """One rating of the level with `enemies` times its composed enemies."""

    enemies: float
    episodes: int
    rating: float
    error: float  # standard error of the rating, in percent
    completed: float


@dataclass
class Search:
    """How the factor is searched."""

    target: float
    tolerance: float = 2.0
    # Each rating plays 100 episodes (D-310); `--episodes` lower and `--max-episodes` higher let
    # the episodes double from a few once the target is bracketed.
    episodes: int = 100
    max_episodes: int = 100
    # A safety net: the target is reached well before when it can be (D-312).
    max_steps: int = 20
    lowest: float = 0.25
    # No limit to the enemies by default (D-312).
    highest: float = math.inf


@dataclass
class Outcome:
    """How the search ended: `best` is the step closest to the target."""

    status: str  # "reached", "saturated" or "unfinished"
    best: Step
    steps: list[Step] = field(default_factory=list)


def rising(steps: list[Step]) -> bool:
    """Whether the ratings go up with the factor so far (least squares; up until two are known).

    More enemies are harder when they bring no more bonuses (D-309), but the search does not
    count on it.
    """
    if len({s.enemies for s in steps}) < 2:
        return True
    mean_x = sum(s.enemies for s in steps) / len(steps)
    mean_y = sum(s.rating for s in steps) / len(steps)
    return sum((s.enemies - mean_x) * (s.rating - mean_y) for s in steps) >= 0


def next_factor(steps: list[Step], target: float, low: float, high: float) -> float:
    """Return the next factor to rate, whichever way the ratings go with it."""
    up = rising(steps)
    if not bracketed(steps, target):
        # All too easy, or all too hard: go the way that changes the rating towards the target.
        harder = all(s.rating < target for s in steps)
        more = harder == up
        if more:
            return min(high, max(s.enemies for s in steps) * STRIDE)
        return max(low, min(s.enemies for s in steps) / STRIDE)
    ordered = sorted(steps, key=lambda s: s.enemies)
    pairs = [
        (a, b)
        for a, b in itertools.pairwise(ordered)
        if (a.rating < target) != (b.rating < target) and a.enemies < b.enemies
    ]
    if not pairs:  # the two sides were rated at the same factor
        return ordered[0].enemies
    a, b = min(pairs, key=lambda pair: pair[1].enemies - pair[0].enemies)
    span = b.enemies - a.enemies
    factor = a.enemies + (target - a.rating) * span / (b.rating - a.rating)
    return min(max(factor, a.enemies + MARGIN * span), b.enemies - MARGIN * span)


def bracketed(steps: list[Step], target: float) -> bool:
    """Whether some rating is below the target and some at or above it."""
    return any(s.rating < target for s in steps) and any(s.rating >= target for s in steps)


def close_enough(step: Step, search: Search) -> bool:
    """Whether `step` is within the tolerance, or within two standard errors at most episodes."""
    off = abs(step.rating - search.target)
    return off <= search.tolerance or (
        step.episodes >= search.max_episodes and off <= 2 * step.error
    )


RateFn = Callable[[float, int], tuple[float, float, float]]


def search_factor(
    start: float, search: Search, rate_at: RateFn, report: Callable[[Step], None] = print
) -> Outcome:
    """Search the enemies factor that rates the level at `search.target`, from `start`.

    `rate_at(enemies, episodes)` returns the rating, its standard error and the share completed.
    """
    low, high = search.lowest, search.highest
    steps: list[Step] = []
    enemies = round(min(max(start, low), high), DECIMALS)
    episodes = search.episodes
    status = "unfinished"
    for _ in range(search.max_steps):
        rating, error, completed = rate_at(enemies, episodes)
        step = Step(enemies, episodes, rating, error, completed)
        steps.append(step)
        report(step)
        if close_enough(step, search):
            status = "reached"
            break
        if bracketed(steps, search.target):
            episodes = min(search.max_episodes, episodes * 2)
        enemies = round(next_factor(steps, search.target, low, high), DECIMALS)
        if any(s.enemies == enemies for s in steps):
            # The factor cannot get any finer (it is written to two decimals), or is at a bound.
            status = "reached" if bracketed(steps, search.target) else "saturated"
            break
    best = min(steps, key=lambda s: abs(s.rating - search.target))
    return Outcome(status, best, steps)


def config_file(src: Path = SRC) -> Path:
    """Return the file that holds the levels' enemies factors."""
    return src / "game" / "config" / "level_enemies.py"


def write_factor(level_id: str, enemies: float, src: Path = SRC) -> Path:
    """Write `enemies` into the level's line of `LEVEL_ENEMIES`."""
    path = config_file(src)
    text = path.read_text()
    pattern = re.compile(r'("' + re.escape(level_id) + r'": )[0-9.]+')
    value = f"{round(enemies, DECIMALS):g}"
    new, count = pattern.subn(lambda m: m.group(1) + value, text)
    if count != 1:
        msg = f"Found {count} entries for {level_id} in {path}."
        raise ValueError(msg)
    path.write_text(new)
    return path


def _print_step(step: Step) -> None:
    print(
        f"enemies x{step.enemies:<5g} {step.rating:5.1f}% ±{step.error:4.1f}"
        f"  done {step.completed:4.0%}  ({step.episodes} episodes)",
        flush=True,
    )


def brain_rater(level_id: str, settings: RatingSettings, workers: int, path: Path) -> RateFn:
    """Return a `rate_at` that rates the level with the brain saved at `path`."""

    def rate_at(enemies: float, episodes: int) -> tuple[float, float, float]:
        every = setups(
            RatingSettings(episodes, settings.ship, settings.weapon_level, settings.greedy),
            [level_id],
            enemies,
        )
        rating = rate_level(level_id, play_all(every, settings.greedy, workers, path))
        return rating.difficulty, rating.spread / math.sqrt(episodes), rating.completed

    return rate_at


def adjust(
    level_id: str,
    search: Search,
    settings: RatingSettings,
    workers: int,
    path: Path,
) -> Outcome:
    """Search the level's enemies factor for the target with the brain at `path`, then write it."""
    if not path.exists():
        msg = f"No brain in {path}: run `make learn` first."
        raise SystemExit(msg)
    _, stats = load_brain(path)
    start = level_enemies(level_id)
    print(
        f"Adjusting {level_id} to {search.target:g}% with the brain of {path}"
        f" ({stats.updates} updates, {stats.hours:.1f} h of learning); now: enemies x{start:g}"
    )
    began = time.monotonic()
    outcome = search_factor(
        start, search, brain_rater(level_id, settings, workers, path), _print_step
    )
    print(f"({time.monotonic() - began:.0f} s)")
    best = outcome.best
    record = DATA / f"adjust-{level_id}.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "level": level_id,
        "search": asdict(search),
        "settings": asdict(settings),
        "status": outcome.status,
        "best": asdict(best),
        "steps": [asdict(s) for s in outcome.steps],
    }
    record.write_text(json.dumps(report, indent=2) + "\n")
    if outcome.status == "saturated":
        print(
            f"The enemies factor runs out before {search.target:g}%: the closest is"
            f" {best.rating:.1f}% with x{best.enemies:g}. Nothing written (see {record})."
        )
        return outcome
    if outcome.status == "unfinished":
        print(
            f"Not within {search.tolerance:g}% after {search.max_steps} steps: the closest is kept."
        )
    config = write_factor(level_id, best.enemies)
    print(
        f"{level_id}: enemies x{best.enemies:g} ({best.rating:.1f}% ±{best.error:.1f})"
        f" written to {config.relative_to(REPO_ROOT)}"
    )
    return outcome


def linear_targets(first: float, last: float, levels: list[str]) -> list[tuple[str, float]]:
    """Return each level's target, rising evenly from `first` (first level) to `last` (last)."""
    if len(levels) == 1:
        return [(levels[0], first)]
    step = (last - first) / (len(levels) - 1)
    return [(level_id, round(first + step * i, 1)) for i, level_id in enumerate(levels)]


def adjust_all(
    targets: list[tuple[str, float]],
    search: Search,
    settings: RatingSettings,
    workers: int,
    path: Path,
) -> list[Outcome]:
    """Adjust each level to its target in turn (`make adjust-levels`), then print a summary."""
    began = time.monotonic()
    outcomes = []
    for level_id, target in targets:
        print(f"\n=== {level_id}: {target:g}%", flush=True)
        outcomes.append(adjust(level_id, replace(search, target=target), settings, workers, path))
    print(f"\n{'Level':<6} {'Target':>7} {'Rated':>7} {'±':>5} {'Enemies':>8}  Outcome")
    for (level_id, target), outcome in zip(targets, outcomes, strict=True):
        best = outcome.best
        written = "" if outcome.status == "saturated" else "written"
        print(
            f"{level_id:<6} {target:>6.1f}% {best.rating:>6.1f}% {best.error:>5.1f}"
            f" {best.enemies:>7g}x  {outcome.status} {written}".rstrip()
        )
    print(f"({(time.monotonic() - began) / 60:.0f} min)")
    return outcomes


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tune levels' enemy counts to a difficulty.")
    parser.add_argument("--level", choices=LEVEL_IDS, help="the level to adjust")
    parser.add_argument("--target", type=float, help="its difficulty, in percent")
    parser.add_argument(
        "--all",
        action="store_true",
        help="adjust every level, from --first %% (1-1) to --last %% (4-5) evenly",
    )
    parser.add_argument("--first", type=float, default=10.0, help="--all: the first level's target")
    parser.add_argument("--last", type=float, default=99.0, help="--all: the last level's target")
    parser.add_argument("--tolerance", type=float, default=Search.tolerance)
    parser.add_argument("--episodes", type=int, default=Search.episodes)
    parser.add_argument("--max-episodes", type=int, default=Search.max_episodes)
    parser.add_argument("--max-steps", type=int, default=Search.max_steps)
    parser.add_argument("--lowest", type=float, default=Search.lowest, help="least enemies factor")
    parser.add_argument(
        "--highest", type=float, default=Search.highest, help="most enemies factor (default: none)"
    )
    parser.add_argument("--ship", choices=SHIP_IDS, default=RatingSettings.ship)
    parser.add_argument("--greedy", action="store_true")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--brain", type=Path, default=BRAIN_FILE)
    args = parser.parse_args(argv)
    if args.all:
        targets = linear_targets(args.first, args.last, list(LEVEL_IDS))
    elif args.level is not None and args.target is not None:
        targets = [(args.level, args.target)]
    else:
        parser.error("give --level and --target, or --all")
    if not all(0 < target < 100 for _, target in targets):
        parser.error("targets are percentages between 0 and 100")
    search = Search(
        targets[0][1],
        args.tolerance,
        args.episodes,
        max(args.episodes, args.max_episodes),
        args.max_steps,
        args.lowest,
        args.highest,
    )
    settings = RatingSettings(args.episodes, args.ship, None, args.greedy)
    if args.all:
        adjust_all(targets, search, settings, args.workers, args.brain)
    else:
        adjust(args.level, search, settings, args.workers, args.brain)


if __name__ == "__main__":
    main()
