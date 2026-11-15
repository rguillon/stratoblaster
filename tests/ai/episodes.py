# Copyright (c) 2026 Renaud Guillon
"""The games a worker plays and how they went, in pure Python (the workers run under PyPy, D-301).

An episode is a campaign from the first level (D-295); one that ends is replaced by a new one.
The reports are pickled from a worker (PyPy) to the learner (CPython): plain dataclasses of this
module, which both import.
"""

import random
from dataclasses import dataclass

from ai.game_env import LEVEL_IDS, Action, EpisodeSetup, GameEnv


@dataclass
class Curriculum:
    """How the learning episodes are drawn: each a campaign (D-295).

    From the first of `levels` with a fresh start (3 lives, 3 bombs, the first weapon at level 1,
    as when watched and rated, D-294), each level cleared going on to the next with what it ended
    with, until the game is over, a level takes too long or the last one is cleared. Always with
    the `ship` (the player ship); the seed varies.
    """

    levels: tuple[str, ...] = LEVEL_IDS
    ship: str = "player"

    def draw(self, rng: random.Random) -> GameEnv:
        """Return the game of a new episode."""
        setup = EpisodeSetup(self.levels[0], seed=rng.randrange(1 << 30), ship_id=self.ship)
        return GameEnv(setup, campaign=self.levels)


@dataclass
class EpisodeReport:
    """How an episode (a campaign) went.

    `outcome`: "over" (no life left), "timeout" (a level took too long) or "complete" (the last
    level cleared). `reached`: the level it ended in; `cleared`: how many levels it cleared;
    `progress`: how far through the level it ended in.
    """

    ship_id: str
    outcome: str
    score: float
    reached: str
    cleared: int
    progress: float
    lives_lost: int
    decisions: int


@dataclass
class GameProgress:
    """A game still being played: the level it is in, the levels cleared, its score, its moves."""

    level: str
    cleared: int
    score: float
    decisions: int


class Episodes:
    """A few episodes played side by side: each replaced by a new one when it ends."""

    def __init__(self, count: int, seed: int, curriculum: Curriculum) -> None:
        self.rng = random.Random(seed)
        self.curriculum = curriculum
        self.envs = [curriculum.draw(self.rng) for _ in range(count)]
        # Whether each episode starts at its next decision (its memory then starts afresh).
        self.starts = [True] * count
        self.decisions = [0] * count

    def play(
        self, e: int, action: tuple[int, int, int]
    ) -> tuple[float, bool, EpisodeReport | None]:
        """Play a decision of episode `e`: its reward, whether it ended, and how it went if so.

        An episode that ends is replaced by a new one.
        """
        env = self.envs[e]
        reward, _ = env.step(Action(action[0], action[1] == 1, action[2] == 1))
        self.decisions[e] += 1
        self.starts[e] = env.done
        if not env.done:
            return reward, False, None
        report = EpisodeReport(
            env.setup.ship_id,
            env.outcome,
            env.score,
            env.setup.level_id,
            len(env.cleared),
            env.progress_fraction,
            env.total_lives_lost,
            self.decisions[e],
        )
        self.decisions[e] = 0
        self.envs[e] = self.curriculum.draw(self.rng)
        return reward, True, report

    def progress(self) -> list[GameProgress]:
        """Return how each game stands."""
        return [
            GameProgress(env.setup.level_id, len(env.cleared), env.score, self.decisions[e])
            for e, env in enumerate(self.envs)
        ]
