# Copyright (c) 2026 Renaud Guillon
"""`make adjust-level`: tune a level until the brain rates it at a target difficulty (D-305).

    uv run python -m ai.adjust --level 4-4 --target 90

One dial, `k`, multiplies the level's three difficulty factors together: its enemies' bullet speed,
their fire rate and its bosses' health (k = 1: the level as it is). Each step rates the level with
the brain, as `make rate` does (same loadout, same seeds every step, so two steps differ by `k`
alone), then picks the next `k`:

- until the target is bracketed, `k` grows (or shrinks) by `STRIDE`;
- then it is interpolated between the closest ratings either side of the target.

The episodes double once the target is bracketed, up to `--max-episodes`. It stops once a rating is
within `--tolerance` of the target (or within two standard errors of it at the most episodes), and
writes the factors into the level's line of `src/game/config/world_N/difficulty.py`. When the dial
runs out (a factor would pass `MAX_FACTOR`, or `k` its bounds) before reaching the target, it says
so and writes nothing. The level's spec (its "Difficulty" requirement) is the human's to update.
"""

import argparse
import itertools
import json
import math
import os
import re
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from pathlib import Path

from ai import DATA, REPO_ROOT, SRC
from ai.brain import BRAIN_FILE, load_brain
from ai.game_env import LEVEL_IDS, SHIP_IDS, level_difficulty
from ai.rate import RatingSettings, play_all, rate_level, setups

# The most a factor may be: the config checks' ceiling (twice the base, ENM-22).
MAX_FACTOR = 2.0
# How much `k` grows (or shrinks) each step until the target is bracketed.
STRIDE = 1.25
# An interpolated `k` stays this share of the bracket away from its ends, so a noisy end that is
# far off does not hold the search next to the other.
MARGIN = 0.1

Factors = tuple[float, float, float]


@dataclass
class Step:
    """One rating of the level at `k`."""

    k: float
    factors: Factors
    episodes: int
    rating: float
    error: float  # standard error of the rating, in percent
    completed: float


@dataclass
class Search:
    """How the dial is searched."""

    target: float
    tolerance: float = 2.0
    episodes: int = 16
    max_episodes: int = 64
    max_steps: int = 10
    min_k: float = 0.5
    max_k: float = 2.0


@dataclass
class Outcome:
    """How the search ended: `best` is the step closest to the target."""

    status: str  # "reached", "saturated" or "unfinished"
    best: Step
    steps: list[Step] = field(default_factory=list)


def base_factors(level_id: str) -> Factors:
    """Return the level's own bullet speed, fire rate and boss health factors."""
    difficulty = level_difficulty(level_id)
    return (
        float(difficulty.bullet_speed),
        float(difficulty.fire_rate),
        float(difficulty.boss_health),
    )


def scaled(base: Factors, k: float) -> Factors:
    """Return the factors at `k`, rounded as the config writes them."""
    return (round(base[0] * k, 2), round(base[1] * k, 2), round(base[2] * k, 2))


def k_range(base: Factors, search: Search) -> tuple[float, float]:
    """Return the lowest and highest `k`: within its bounds, no factor past `MAX_FACTOR`."""
    return search.min_k, min(search.max_k, MAX_FACTOR / max(base))


def next_k(steps: list[Step], target: float, low: float, high: float) -> float:
    """Return the next `k` to rate (ratings go up with `k`: a higher `k` is harder)."""
    below = [s for s in steps if s.rating < target]
    above = [s for s in steps if s.rating >= target]
    if not above:
        return min(high, max(s.k for s in steps) * STRIDE)
    if not below:
        return max(low, min(s.k for s in steps) / STRIDE)
    easy = max(below, key=lambda s: s.k)
    hard = min(above, key=lambda s: s.k)
    if easy.k >= hard.k or hard.rating == easy.rating:
        # Noise put them the wrong way round: try halfway.
        return (easy.k + hard.k) / 2
    k = easy.k + (target - easy.rating) * (hard.k - easy.k) / (hard.rating - easy.rating)
    margin = MARGIN * (hard.k - easy.k)
    return min(max(k, easy.k + margin), hard.k - margin)


def bracketed(steps: list[Step], target: float) -> bool:
    """Whether some rating is below the target and some at or above it."""
    return any(s.rating < target for s in steps) and any(s.rating >= target for s in steps)


def close_enough(step: Step, search: Search) -> bool:
    """Whether `step` is within the tolerance, or within two standard errors at most episodes."""
    off = abs(step.rating - search.target)
    return off <= search.tolerance or (
        step.episodes >= search.max_episodes and off <= 2 * step.error
    )


RateFn = Callable[[Factors, int], tuple[float, float, float]]


def search_dial(
    base: Factors, search: Search, rate_at: RateFn, report: Callable[[Step], None] = print
) -> Outcome:
    """Search the `k` that rates the level at `search.target`.

    `rate_at(factors, episodes)` returns the rating, its standard error and the share completed.
    """
    low, high = k_range(base, search)
    steps: list[Step] = []
    k = min(1.0, high)
    episodes = search.episodes
    status = "unfinished"
    for _ in range(search.max_steps):
        factors = scaled(base, k)
        rating, error, completed = rate_at(factors, episodes)
        step = Step(k, factors, episodes, rating, error, completed)
        steps.append(step)
        report(step)
        if close_enough(step, search):
            status = "reached"
            break
        if bracketed(steps, search.target):
            episodes = min(search.max_episodes, episodes * 2)
        else:
            at_bound = (k >= high and rating < search.target) or (
                k <= low and rating >= search.target
            )
            if at_bound:
                status = "saturated"
                break
        k = next_k(steps, search.target, low, high)
        if any(s.factors == scaled(base, k) for s in steps):
            # The factors cannot get any finer (they are rounded to 0.01).
            status = "reached" if bracketed(steps, search.target) else "saturated"
            break
    best = min(steps, key=lambda s: abs(s.rating - search.target))
    return Outcome(status, best, steps)


def _number(value: float) -> str:
    return f"{round(value, 2):g}"


def config_file(level_id: str, src: Path = SRC) -> Path:
    """Return the file that holds the level's difficulty factors."""
    world = level_id.split("-", maxsplit=1)[0]
    return src / "game" / "config" / f"world_{world}" / "difficulty.py"


def write_factors(level_id: str, factors: Factors, src: Path = SRC) -> Path:
    """Write `factors` into the level's line of its world's difficulty table; keep its comment."""
    path = config_file(level_id, src)
    text = path.read_text()
    entry = (
        f'{{"bulletSpeed": {_number(factors[0])}, "fireRate": {_number(factors[1])},'
        f' "bossHealth": {_number(factors[2])}}}'
    )
    pattern = re.compile(r'("' + re.escape(level_id) + r'": )\{[^}]*\}')
    new, count = pattern.subn(lambda m: m.group(1) + entry, text)
    if count != 1:
        msg = f"Found {count} entries for {level_id} in {path}."
        raise ValueError(msg)
    path.write_text(new)
    return path


def ordering_breaks(level_id: str, factors: Factors) -> list[str]:
    """Return how `factors` break "bullet speed and fire rate never go down" within the world."""
    world = level_id.split("-", maxsplit=1)[0]
    mine = [i for i in LEVEL_IDS if i.split("-", maxsplit=1)[0] == world]
    tables = {i: base_factors(i) for i in mine} | {level_id: factors}
    breaks = []
    for before, after in itertools.pairwise(mine):
        for index, name in ((0, "bullet speed"), (1, "fire rate")):
            if tables[after][index] < tables[before][index]:
                breaks.append(
                    f"{name}: {after} ({tables[after][index]:g}) is below"
                    f" {before} ({tables[before][index]:g})"
                )
    return breaks


def spec_files(level_id: str) -> list[Path]:
    """Return the level's spec file and its world's (the tunable values table)."""
    world = REPO_ROOT / "specs" / "worlds" / f"world-{level_id.split('-', maxsplit=1)[0]}"
    return [*sorted(world.glob(f"{level_id}-*.md")), world / "world.md"]


def _print_step(step: Step) -> None:
    bullets, fire, boss = step.factors
    print(
        f"k {step.k:5.3f}  bullets x{bullets:<5g} fire x{fire:<5g} boss HP x{boss:<5g}"
        f"  {step.rating:5.1f}% ±{step.error:4.1f}  done {step.completed:4.0%}"
        f"  ({step.episodes} episodes)",
        flush=True,
    )


def brain_rater(level_id: str, settings: RatingSettings, workers: int, path: Path) -> RateFn:
    """Return a `rate_at` that rates the level with the brain saved at `path`."""

    def rate_at(factors: Factors, episodes: int) -> tuple[float, float, float]:
        every = setups(
            RatingSettings(episodes, settings.ship, settings.weapon_level, settings.greedy),
            [level_id],
            factors,
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
    """Search the level's factors for the target with the brain at `path`, then write them."""
    if not path.exists():
        msg = f"No brain in {path}: run `make learn` first."
        raise SystemExit(msg)
    _, stats = load_brain(path)
    base = base_factors(level_id)
    print(
        f"Adjusting {level_id} to {search.target:g}% with the brain of {path}"
        f" ({stats.updates} updates, {stats.hours:.1f} h of learning); now: bullets x{base[0]:g},"
        f" fire x{base[1]:g}, boss HP x{base[2]:g}"
    )
    start = time.monotonic()
    outcome = search_dial(base, search, brain_rater(level_id, settings, workers, path), _print_step)
    print(f"({time.monotonic() - start:.0f} s)")
    best = outcome.best
    record = DATA / f"adjust-{level_id}.json"
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(
        json.dumps(
            {
                "level": level_id,
                "search": asdict(search),
                "settings": asdict(settings),
                "status": outcome.status,
                "best": asdict(best),
                "steps": [asdict(s) for s in outcome.steps],
            },
            indent=2,
        )
        + "\n"
    )
    if outcome.status == "saturated":
        print(
            f"The dial runs out before {search.target:g}%: the closest is {best.rating:.1f}%"
            f" at k {best.k:.3f}. Nothing written (see {record})."
        )
        return outcome
    if outcome.status == "unfinished":
        print(
            f"Not within {search.tolerance:g}% after {search.max_steps} steps: the closest is kept."
        )
    config = write_factors(level_id, best.factors)
    print(
        f"{level_id}: bullets x{best.factors[0]:g}, fire x{best.factors[1]:g},"
        f" boss HP x{best.factors[2]:g} ({best.rating:.1f}% ±{best.error:.1f}) written to"
        f" {config.relative_to(REPO_ROOT)}"
    )
    for problem in ordering_breaks(level_id, best.factors):
        print(f"Warning, the factors must never go down within a world: {problem}")
    print("To update by hand (specs are human-owned): the level's Difficulty requirement in")
    for spec in spec_files(level_id):
        print(f"  {spec.relative_to(REPO_ROOT)}")
    return outcome


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Tune a level to a target difficulty.")
    parser.add_argument("--level", required=True, choices=LEVEL_IDS)
    parser.add_argument("--target", required=True, type=float, help="difficulty, in percent")
    parser.add_argument("--tolerance", type=float, default=Search.tolerance)
    parser.add_argument("--episodes", type=int, default=Search.episodes)
    parser.add_argument("--max-episodes", type=int, default=Search.max_episodes)
    parser.add_argument("--max-steps", type=int, default=Search.max_steps)
    parser.add_argument("--min-k", type=float, default=Search.min_k)
    parser.add_argument("--max-k", type=float, default=Search.max_k)
    parser.add_argument("--ship", choices=SHIP_IDS, default=RatingSettings.ship)
    parser.add_argument("--greedy", action="store_true")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--brain", type=Path, default=BRAIN_FILE)
    args = parser.parse_args(argv)
    if not 0 < args.target < 100:
        parser.error("--target is a percentage between 0 and 100")
    search = Search(
        args.target,
        args.tolerance,
        args.episodes,
        max(args.episodes, args.max_episodes),
        args.max_steps,
        args.min_k,
        args.max_k,
    )
    settings = RatingSettings(args.episodes, args.ship, None, args.greedy)
    adjust(args.level, search, settings, args.workers, args.brain)


if __name__ == "__main__":
    main()
