# Copyright (c) 2026 Renaud Guillon
"""The boss fights of a level, one at a time (BOSS-02).

When the level gets to a boss, it comes in, the track is held (the level's progress waits,
GAME-LEVEL-06; the ground goes on, eased to the boss's speed, GAME-LEVEL-07), and once the boss has
blown up the ground eases back and the level goes on. Pure and deterministic.
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Literal, Protocol

from core.entities.boss import Boss
from core.entities.enemy import EnemySpawnArea
from core.scenery.scroll_track import ScrollTrack

# The two bosses of a level (GAME-LEVEL-04): one around its middle, one at its end.
BossRank = Literal["mini", "final"]
# __pragma__ ("noskip")


# Slack on distances (seeking to a boss's distance in seconds may round).
SLACK = 1e-6


class LevelBoss:
    """A boss of a level (GAME-LEVEL-04).

    Its kind (the id of a `BossKindDefinition`), its rank, and how far into the level it comes: the
    level progress (world units, `ScrollTrack.progress`) where it arrives.
    """

    def __init__(self, kind: str, rank: "BossRank", at: float) -> None:
        self.kind = kind
        self.rank = rank
        self.at = at


__pragma__("skip")


class BossKindDefinition(Protocol):
    """A kind of boss a game offers (BOSS-07)."""

    @property
    def id(self) -> str:
        """Stable identifier."""
        ...

    @property
    def name(self) -> str:
        """The kind's display name."""
        ...

    def spawn(self, area: EnemySpawnArea) -> Boss:
        """Create the boss just above the playfield."""
        ...


__pragma__("noskip")


class BossFightRules:
    """How fights go (engine timings, given by the game).

    `speed_ease_seconds` is the seconds the ground takes to change to the fight's speed, and back
    (GAME-LEVEL-07); `bar_fill_seconds` the seconds the health bar takes to fill up when a boss
    arrives (UI-HUD-14).
    """

    def __init__(self, speed_ease_seconds: float, bar_fill_seconds: float) -> None:
        self.speed_ease_seconds = speed_ease_seconds
        self.bar_fill_seconds = bar_fill_seconds


class BossBar:
    """What the boss health bar shows (BOSS-05, UI-HUD-13).

    `share` is the part of the bar filled, 0..1: the health left over the full health, as it fills
    up. `notches` are where each destroyable part's share ends along the bar, 0..1 from the left
    (UI-HUD-15).
    """

    def __init__(
        self,
        name: str,
        rank: "BossRank",
        share: float,
        health: float,
        full_health: float,
        notches: list[float],
    ) -> None:
        self.name = name
        self.rank = rank
        self.share = share
        self.health = health
        self.full_health = full_health
        self.notches = notches


def validate_level_bosses(bosses: Sequence[LevelBoss], kind_ids: Sequence[str]) -> None:
    """Throws a descriptive error for a level boss of an unknown kind."""
    for boss in bosses:
        if boss.kind not in kind_ids:
            raise ValueError('Unknown boss kind "' + boss.kind + '"')
        if not (boss.at >= 0):
            raise ValueError('Boss "' + boss.kind + '": bad distance')


class BossFightHooks:
    """What `BossFights` needs from the level it runs in: `area` gives where bosses appear.

    `add` adds the boss to the level's enemies.
    """

    def __init__(self, area: Callable[[], EnemySpawnArea], add: Callable[[Boss], None]) -> None:
        self.area = area
        self.add = add


class _Fight:
    """A boss being fought: `age` is the seconds since it arrived."""

    def __init__(self, boss: Boss, level: LevelBoss) -> None:
        self.boss = boss
        self.level = level
        self.age = 0.0


def _sorted_by_at(bosses: Sequence[LevelBoss]) -> list[LevelBoss]:
    """Return a copy sorted by distance: a stable insertion sort (as `Array.sort` is stable)."""
    sorted_bosses: list[LevelBoss] = list(bosses)
    for i in range(1, len(sorted_bosses)):
        j = i
        while j > 0 and sorted_bosses[j - 1].at > sorted_bosses[j].at:
            sorted_bosses[j - 1], sorted_bosses[j] = sorted_bosses[j], sorted_bosses[j - 1]
            j -= 1
    return sorted_bosses


class BossFights:
    """The boss fights of a level.

    `defeated` are the bosses destroyed so far, in order; `just_defeated` the boss destroyed during
    the last step, if any.
    """

    def __init__(
        self,
        bosses: Sequence[LevelBoss],
        kinds: Sequence[BossKindDefinition],
        rules: BossFightRules,
        hooks: BossFightHooks,
    ) -> None:
        kind_ids: list[str] = [kind.id for kind in kinds]
        validate_level_bosses(bosses, kind_ids)
        self.defeated: list[LevelBoss] = []
        self.just_defeated: LevelBoss | None = None
        self._bosses = _sorted_by_at(bosses)
        self._kinds = kinds
        self._rules = rules
        self._hooks = hooks
        self._next = 0
        self._fight: _Fight | None = None

    @property
    def boss(self) -> Boss | None:
        """The boss being fought, if any."""
        fight = self._fight
        return fight.boss if fight is not None else None

    @property
    def rank(self) -> BossRank | None:
        """The rank of the boss fight in progress, or None when no boss is being fought."""
        fight = self._fight
        return fight.level.rank if fight is not None else None

    @property
    def active(self) -> bool:
        """Whether a boss is being fought (from its arrival to the end of its death blasts)."""
        return self._fight is not None

    @property
    def passed(self) -> int:
        """Bosses passed so far: fought, or skipped by a seek."""
        return self._next

    @property
    def has_final(self) -> bool:
        """Whether one of the level's bosses is the final one."""
        return any(boss.rank == "final" for boss in self._bosses)

    @property
    def final_defeated(self) -> bool:
        """Whether the final boss has been defeated."""
        return any(boss.rank == "final" for boss in self.defeated)

    @property
    def bosses(self) -> list[LevelBoss]:
        """The level's bosses, in order."""
        return self._bosses

    def step(self, dt: float, track: ScrollTrack) -> None:
        """Start the next boss once the level has got to it; end the fight once it is gone."""
        self.just_defeated = None
        fight = self._fight
        if fight is not None:
            fight.age += dt
            if fight.boss.gone:
                self._end(fight, track)
            return
        if self._next < len(self._bosses):
            following = self._bosses[self._next]
            if track.progress >= following.at - SLACK:
                self._start(following, track)

    def skip_to(self, track: ScrollTrack, passed: int | None = None) -> None:
        """After a seek or a restart at `progress` (DEV-OPT-02, GAME-LIFE-11).

        The boss being fought (if any) is dropped, the ground goes back to its speed, and the next
        boss is the first one at or after `progress`, or the one after the first `passed` when
        given.
        """
        self._fight = None
        track.held = False
        track.set_speed_factor(1, 0)
        next_index = -1
        for i in range(len(self._bosses)):
            if self._bosses[i].at >= track.progress - SLACK:
                next_index = i
                break
        if passed is not None:
            self._next = passed
        else:
            self._next = len(self._bosses) if next_index < 0 else next_index

    @property
    def bar(self) -> BossBar | None:
        """What the health bar shows, while a boss is fought."""
        fight = self._fight
        if fight is None:
            return None
        boss = fight.boss
        full = boss.full_health
        fill = min(1, fight.age / self._rules.bar_fill_seconds)
        edge = 0.0
        notches: list[float] = []
        for part in boss.parts:
            edge += part.max_health / full
            notches.append(edge)
        remaining = boss.remaining_health
        return BossBar(
            boss.name,
            fight.level.rank,
            (remaining / full) * fill,
            remaining,
            full,
            notches,
        )

    def _start(self, level: LevelBoss, track: ScrollTrack) -> None:
        kind = None
        for candidate in self._kinds:
            if candidate.id == level.kind:
                kind = candidate
                break
        self._next += 1
        if kind is None:
            return
        boss = kind.spawn(self._hooks.area())
        self._hooks.add(boss)
        self._fight = _Fight(boss, level)
        track.held = True
        track.set_speed_factor(boss.ground_speed, self._rules.speed_ease_seconds)

    def _end(self, fight: _Fight, track: ScrollTrack) -> None:
        self._fight = None
        track.held = False
        track.set_speed_factor(1, self._rules.speed_ease_seconds)
        self.defeated.append(fight.level)
        self.just_defeated = fight.level
