"""Runs a level's wave script (P06-R07, GD-40), ported from `core/systems/wave-runner.ts`.

Waves start when the level scrolls past their distance, and not before; the groups of a wave come
in one by one, so several waves can be on screen at once. The runner knows enemy kinds only by id:
the spawner brings the groups in. Pure and deterministic.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyEntry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

WaveScript = Sequence["Wave"]
WaveSpawner = Callable[[str, EnemyEntry], None]

__pragma__("noskip")

INFINITY = float("Infinity")


class Wave:
    """One wave of a level's script: when the level has scrolled `at` world units, `count` groups of
    the enemy kind `kind` come in at `entry`, one every `interval` seconds.

    `spread`: added to the entry position for each group after the first (e.g. a line of Scouts
    coming in across the screen), wrapped back into 0..1.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        at: float,
        kind: str,
        count: int,
        interval: float,
        entry: EnemyEntry,
        spread: float | None = None,
    ) -> None:
        self.at = at
        self.kind = kind
        self.count = count
        self.interval = interval
        self.entry = entry
        self.spread = spread


class _QueuedGroup:
    """A group waiting to come in: when, which kind, and where."""

    def __init__(self, time: float, kind: str, entry: EnemyEntry) -> None:
        self.time = time
        self.kind = kind
        self.entry = entry


def _is_integer(value: float) -> bool:
    """`Number.isInteger`."""
    # Finite first: `math.floor` raises on an infinite value (CPython; NaN fails the comparisons).
    return value < INFINITY and value > -INFINITY and math.floor(value) == value


def validate_wave_script(script: Sequence[Wave], kind_ids: Sequence[str]) -> None:
    """Throws a descriptive error for a wave with an unknown kind or impossible numbers."""
    for wave in script:
        where = 'Wave "' + wave.kind + '" at ' + str(wave.at)
        if wave.kind not in kind_ids:
            raise ValueError(where + ": unknown enemy kind")
        if not _is_integer(wave.count) or wave.count < 1:
            raise ValueError(where + ": bad count")
        if not (wave.at >= 0) or not (wave.interval >= 0):
            raise ValueError(where + ": bad timing")
        position = wave.entry.position
        if not (position >= 0 and position <= 1):
            raise ValueError(where + ": bad entry position")


def _group_entry(wave: Wave, index: int) -> EnemyEntry:
    """The entry of group `index` of `wave`."""
    # `!= None`: a config record leaves an absent spread undefined, which `is not None` takes for
    # a value (the strafers then entered at NaN, clamped to the bottom of the playfield).
    spread = wave.spread if wave.spread != None else 0  # noqa: E711
    shifted = wave.entry.position + spread * index
    return EnemyEntry(wave.entry.side, shifted - math.floor(shifted))


class WaveRunner:
    """Runs a wave script. `triggered` is the number of waves triggered so far."""

    def __init__(self, script: Sequence[Wave], spawn: WaveSpawner) -> None:
        self._waves = _sorted_by_at(script)
        self._queue: list[_QueuedGroup] = []
        self._next = 0
        self._time = 0.0
        self._stopped = False
        self._spawn = spawn

    @property
    def triggered(self) -> int:
        """Waves triggered so far."""
        return self._next

    @property
    def finished(self) -> bool:
        """Whether no group will come in any more: stopped, or every wave triggered and spawned."""
        return self._stopped or (self._next >= len(self._waves) and len(self._queue) == 0)

    def step(self, dt: float, distance: float) -> None:
        """Advances by `dt` seconds, the level having scrolled `distance`: triggers the waves passed
        and brings in the groups due.
        """
        if self._stopped:
            return
        self._time += dt
        while self._next < len(self._waves) and self._waves[self._next].at <= distance:
            wave = self._waves[self._next]
            for i in range(wave.count):
                time = self._time + i * wave.interval
                self._queue.append(_QueuedGroup(time, wave.kind, _group_entry(wave, i)))
            self._next += 1
        _sort_queue(self._queue)
        while len(self._queue) > 0 and self._queue[0].time <= self._time:
            group = self._queue.pop(0)
            self._spawn(group.kind, group.entry)

    def stop(self) -> None:
        """No group comes in after this, not even the rest of a started wave (P06-R03)."""
        self._stopped = True
        self._queue.clear()

    def skip_to(self, distance: float) -> None:
        """Starts again at `distance`, as if the level began there: the waves before it are skipped,
        the groups waiting are dropped, and the later waves trigger as usual (P06-R09).
        """
        self._queue.clear()
        self._stopped = False
        next_index = -1
        for i in range(len(self._waves)):
            if self._waves[i].at >= distance:
                next_index = i
                break
        self._next = len(self._waves) if next_index < 0 else next_index


def _sorted_by_at(script: Sequence[Wave]) -> list[Wave]:
    """A copy sorted by distance: a stable insertion sort (as `Array.sort` is stable)."""
    waves: list[Wave] = []
    for wave in script:
        waves.append(wave)
    for i in range(1, len(waves)):
        j = i
        while j > 0 and waves[j - 1].at > waves[j].at:
            waves[j - 1], waves[j] = waves[j], waves[j - 1]
            j -= 1
    return waves


def _sort_queue(queue: list[_QueuedGroup]) -> None:
    """Sorts the waiting groups by time: a stable insertion sort (as `Array.sort` is stable)."""
    for i in range(1, len(queue)):
        j = i
        while j > 0 and queue[j - 1].time > queue[j].time:
            queue[j - 1], queue[j] = queue[j], queue[j - 1]
            j -= 1
