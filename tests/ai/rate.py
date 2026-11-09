# Copyright (c) 2026 Renaud Guillon
"""`make rate`: the brain plays every level and rates how hard each one is, as a percentage.

Each level is played `--episodes` times (different seeds: the enemies' random choices differ) from
its start, with the same loadout for every level of a world: 3 lives, 3 bombs, and every weapon at
the level of the world (1 in world 1, 2 in world 2, 3 in world 3, 4 in world 4: what a player has
earned by then, D-304), more only from the bonuses picked up. `--ship` changes the ship, and
`--weapon-level` gives every level the same weapon level.

An episode's difficulty is `1 - (progress + health left) / 2`:

- `progress` is how far through the level the brain got (1 when it completed it);
- `health left` is the share of its health, over all its lives, the ship still has at the end
  (0 when the game is over).

So 0 % is a level the brain clears without a scratch, 50 % one it clears with none of its health
left (or one where it dies at the very end), 100 % one where it dies at once. A level's rating is
the mean over its episodes. The ratings are relative to the brain's skill: a better brain rates
every level easier, and the order of the levels is what tells how the difficulty is balanced.

    uv run python -m ai.rate --episodes 8
"""

import argparse
import json
import multiprocessing as mp
import os
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch

from ai import DATA
from ai.brain import BRAIN_FILE, Batch, Brain, load_brain
from ai.game_env import (
    LEVEL_IDS,
    MAX_WEAPON_LEVEL,
    SHIP_IDS,
    WEAPON_IDS,
    Action,
    EpisodeSetup,
    GameEnv,
)
from ai.observation import observe

RATINGS_FILE = DATA / "ratings.json"


@dataclass
class RatingSettings:
    """How the levels are rated."""

    episodes: int = 8
    ship: str = "balanced"
    # Every weapon's level in every level; None: the level of the level's world (D-304).
    weapon_level: int | None = None
    # Moves drawn from the brain's choices, as it learned to play (seeded: the ratings repeat).
    # Always taking its likeliest move plays worse: a brain still learning spreads its choices, and
    # the likeliest alone can be "hold one direction" (D-292).
    greedy: bool = False
    seed: int = 1000


@dataclass
class EpisodeResult:
    """How one rating episode went."""

    level_id: str
    seed: int
    outcome: str
    progress: float
    health_left: float
    lives_lost: int
    seconds: float
    score: float

    @property
    def difficulty(self) -> float:
        return 1.0 - (self.progress + self.health_left) / 2


@dataclass
class LevelRating:
    """A level's rating, in percent, and what it comes from."""

    level_id: str
    difficulty: float
    spread: float
    completed: float
    progress: float
    health_left: float
    lives_lost: float
    seconds: float


def _result(env: GameEnv) -> EpisodeResult:
    setup = env.setup
    health_left = 0.0 if env.outcome == "over" else env.health_budget() / env.max_budget
    return EpisodeResult(
        setup.level_id,
        setup.seed,
        env.outcome,
        env.progress_fraction,
        max(0.0, min(1.0, health_left)),
        env.total_lives_lost,
        env.time,
        env.run.score,
    )


def play_episodes(brain: Brain, setups: list[EpisodeSetup], greedy: bool) -> list[EpisodeResult]:
    """Play episodes side by side with `brain` (one batch through the network), each to its end."""
    envs = [GameEnv(setup) for setup in setups]
    memory = brain.initial_memory(len(envs))
    # One generator per episode, seeded by it: its moves are the same whatever it is played with.
    generators = [torch.Generator().manual_seed(setup.seed) for setup in setups]
    playing = list(range(len(envs)))
    with torch.no_grad():
        while playing:
            batch = Batch.of([observe(envs[i]) for i in playing])
            decision, new_memory = brain(batch, memory[playing])
            memory[playing] = new_memory
            for row, i in enumerate(playing):
                one = decision.row(row)
                move, bomb, switch = one.sample(greedy, generators[i])[0].tolist()
                envs[i].step(Action(move, bomb == 1, switch == 1))
            playing = [i for i in playing if not envs[i].done]
    return [_result(env) for env in envs]


def play_episode(brain: Brain, setup: EpisodeSetup, greedy: bool) -> EpisodeResult:
    """Play one episode of `setup` with `brain`, to its end."""
    return play_episodes(brain, [setup], greedy)[0]


# The most episodes a rating worker plays side by side (one batch through the network). A call to
# the network costs nearly the same for 1 episode as for 32 (D-303): the more, the faster.
GROUP = 32


def group_size(episodes: int, workers: int) -> int:
    """Return how many episodes to play side by side so every worker has some to play.

    Batches play faster per episode, but with too few groups some workers have none.
    """
    return max(1, min(GROUP, -(-episodes // workers)))


_brain: Brain | None = None


def _init_worker(path: Path) -> None:
    global _brain  # one brain per worker process, loaded once
    torch.set_num_threads(1)
    _brain, _ = load_brain(path)
    _brain.eval()


def _play(job: tuple[list[EpisodeSetup], bool]) -> list[EpisodeResult]:
    group, greedy = job
    assert _brain is not None
    return play_episodes(_brain, group, greedy)


def world_weapon_level(level_id: str) -> int:
    """Return the weapons' level a level of world N is rated with: N (D-304), at most the top."""
    world = int(level_id.split("-", maxsplit=1)[0])
    return max(1, min(world, MAX_WEAPON_LEVEL))


def setups(settings: RatingSettings, levels: list[str]) -> list[EpisodeSetup]:
    """Return the rating episodes: `settings.episodes` per level, the same loadout for each."""
    return [
        EpisodeSetup(
            level_id,
            seed=settings.seed + k,
            ship_id=settings.ship,
            weapon=WEAPON_IDS[0],
            weapon_levels=dict.fromkeys(
                WEAPON_IDS,
                settings.weapon_level
                if settings.weapon_level is not None
                else world_weapon_level(level_id),
            ),
            lives=3,
            bombs=3,
        )
        for level_id in levels
        for k in range(settings.episodes)
    ]


def rate_level(level_id: str, results: list[EpisodeResult]) -> LevelRating:
    """Return a level's rating from its episodes."""
    mine = [r for r in results if r.level_id == level_id]
    difficulty = np.array([r.difficulty for r in mine])
    return LevelRating(
        level_id,
        round(100 * float(difficulty.mean()), 1),
        round(100 * float(difficulty.std()), 1),
        round(float(np.mean([r.outcome == "complete" for r in mine])), 3),
        round(float(np.mean([r.progress for r in mine])), 3),
        round(float(np.mean([r.health_left for r in mine])), 3),
        round(float(np.mean([r.lives_lost for r in mine])), 2),
        round(float(np.mean([r.seconds for r in mine])), 1),
    )


def _bar(percent: float, width: int = 20) -> str:
    filled = round(percent / 100 * width)
    return "#" * filled + "." * (width - filled)


def _print_table(ratings: list[LevelRating]) -> None:
    print(
        f"{'Level':<6} {'Difficulty':>10}  {'':<20} {'±':>5} {'Done':>5} {'Prog':>5}"
        f" {'Health':>6} {'Lives':>5}"
    )
    for r in ratings:
        print(
            f"{r.level_id:<6} {r.difficulty:>9.1f}%  {_bar(r.difficulty)} {r.spread:>5.1f}"
            f" {r.completed:>5.0%} {r.progress:>5.0%} {r.health_left:>6.0%} {r.lives_lost:>5.2f}"
        )


def rate(
    settings: RatingSettings, levels: list[str], workers: int, path: Path
) -> list[LevelRating]:
    """Rate `levels` with the brain saved at `path`; write the ratings next to it."""
    if not path.exists():
        msg = f"No brain in {path}: run `make learn` first."
        raise SystemExit(msg)
    _, stats = load_brain(path)
    every = setups(settings, levels)
    size = group_size(len(every), workers)
    jobs = [(every[i : i + size], settings.greedy) for i in range(0, len(every), size)]
    print(
        f"Rating {len(levels)} levels x {settings.episodes} episodes with the brain of {path}"
        f" ({stats.updates} updates, {stats.decisions / 1e6:.1f}M decisions,"
        f" {stats.hours:.1f} h of learning)"
    )
    start = time.monotonic()
    ctx = mp.get_context("spawn")
    with ctx.Pool(workers, initializer=_init_worker, initargs=(path,)) as pool:
        results = [r for group in pool.imap_unordered(_play, jobs) for r in group]
    ratings = [rate_level(level_id, results) for level_id in levels]
    _print_table(ratings)
    print(f"({time.monotonic() - start:.0f} s)")
    RATINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "date": datetime.now(UTC).isoformat(timespec="seconds"),
        "brain": {"updates": stats.updates, "decisions": stats.decisions, "hours": stats.hours},
        "settings": asdict(settings),
        "levels": [asdict(r) for r in ratings],
        "episodes": [asdict(r) | {"difficulty": r.difficulty} for r in results],
    }
    RATINGS_FILE.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Ratings written to {RATINGS_FILE}")
    return ratings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Rate the difficulty of each level.")
    parser.add_argument("--episodes", type=int, default=RatingSettings.episodes)
    parser.add_argument("--ship", choices=SHIP_IDS, default=RatingSettings.ship)
    parser.add_argument(
        "--weapon-level",
        type=int,
        choices=range(1, MAX_WEAPON_LEVEL + 1),
        default=RatingSettings.weapon_level,
        help="every weapon's level in every level (default: the level's world: 1 to 4, D-304)",
    )
    parser.add_argument("--levels", nargs="*", choices=LEVEL_IDS, default=list(LEVEL_IDS))
    parser.add_argument(
        "--greedy",
        action="store_true",
        help="the likeliest move only (default: moves drawn as the brain learned to play)",
    )
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    parser.add_argument("--brain", type=Path, default=BRAIN_FILE)
    args = parser.parse_args(argv)
    settings = RatingSettings(args.episodes, args.ship, args.weapon_level, args.greedy)
    rate(settings, args.levels, args.workers, args.brain)


if __name__ == "__main__":
    main()
