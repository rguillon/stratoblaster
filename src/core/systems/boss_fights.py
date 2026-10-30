"""The boss fights of a level (P07-R03, R06), ported from `core/systems/boss-fights.ts`.

When the level gets to a boss, it comes in, the track is held (the level's progress waits; the
ground goes on, eased to the boss's speed), and once the boss has blown up the ground eases back
and the level goes on. Pure and deterministic.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Literal, Protocol  # noqa: E402

from core.entities.boss import Boss  # noqa: E402
from core.entities.enemy import EnemySpawnArea  # noqa: E402
from core.scenery.scroll_track import ScrollTrack  # noqa: E402

# The two bosses of a level (GD-41): one around its middle, one at its end.
BossRank = Literal["mini", "final"]

__pragma__("noskip")

# Slack on distances (seeking to a boss's distance in seconds may round).
SLACK = 1e-6


class LevelBoss:
    """A boss of a level (P07-R06): its kind (the id of a `BossKindDefinition`), its rank, and how
    far into the level it comes: the level progress (world units, `ScrollTrack.progress`) where it
    arrives.
    """

    def __init__(self, kind: str, rank: "BossRank", at: float) -> None:
        self.kind = kind
        self.rank = rank
        self.at = at


__pragma__("skip")


class BossKindDefinition(Protocol):
    """A kind of boss a game offers (P07-R05)."""

    @property
    def id(self) -> str:
        """Stable identifier."""
        ...

    @property
    def name(self) -> str: ...

    def spawn(self, area: EnemySpawnArea) -> Boss:
        """Creates the boss just above the playfield."""
        ...


__pragma__("noskip")


class BossFightRules:
    """How fights go (engine timings, given by the game): `speed_ease_seconds` is the seconds the
    ground takes to change to the fight's speed, and back (P07-R03); `bar_fill_seconds` the seconds
    the health bar takes to fill up when a boss arrives (P07-R02).
    """

    def __init__(self, speed_ease_seconds: float, bar_fill_seconds: float) -> None:
        self.speed_ease_seconds = speed_ease_seconds
        self.bar_fill_seconds = bar_fill_seconds


class BossBar:
    """What the boss health bar shows (P07-R02). `share` is the part of the bar filled, 0..1: the
    health left over the full health, as it fills up. `notches` are where each destroyable part's
    share ends along the bar, 0..1 from the left.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
    """What `BossFights` needs from the level it runs in: `area` gives where bosses appear, `add`
    adds the boss to the level's enemies.
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
    """A copy sorted by distance: a stable insertion sort (as `Array.sort` is stable)."""
    sorted_bosses: list[LevelBoss] = []
    for boss in bosses:
        sorted_bosses.append(boss)
    for i in range(1, len(sorted_bosses)):
        j = i
        while j > 0 and sorted_bosses[j - 1].at > sorted_bosses[j].at:
            sorted_bosses[j - 1], sorted_bosses[j] = sorted_bosses[j], sorted_bosses[j - 1]
            j -= 1
    return sorted_bosses


class BossFights:
    """The boss fights of a level. `defeated` are the bosses destroyed so far, in order;
    `just_defeated` the boss destroyed during the last step, if any.
    """

    def __init__(
        self,
        bosses: Sequence[LevelBoss],
        kinds: Sequence[BossKindDefinition],
        rules: BossFightRules,
        hooks: BossFightHooks,
    ) -> None:
        kind_ids: list[str] = []
        for kind in kinds:
            kind_ids.append(kind.id)
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
        return any(boss.rank == "final" for boss in self._bosses)

    @property
    def final_defeated(self) -> bool:
        return any(boss.rank == "final" for boss in self.defeated)

    @property
    def bosses(self) -> list[LevelBoss]:
        """The level's bosses, in order."""
        return self._bosses

    def step(self, dt: float, track: ScrollTrack) -> None:
        """Starts the next boss once the level has got to it; ends the fight once it is gone."""
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
        """After a seek or a restart at `progress` (P06-R09, P07-R08): the boss being fought (if
        any) is dropped, the ground goes back to its speed, and the next boss is the first one at or
        after `progress`, or the one after the first `passed` when given.
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
