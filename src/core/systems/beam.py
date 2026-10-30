"""The beam of a beam weapon (P03-R02), ported from `core/systems/beam.ts`."""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.shot_target import is_alive

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.entities.shot_target import ShotTarget  # noqa: E402
from core.entities.weapon import BeamLevel  # noqa: E402

__pragma__("noskip")


class BeamSegment:
    """A straight piece of beam, from `y0` up to `y1`, at a given level (1-based). `hit` says
    whether the segment ends on a target (otherwise it runs to the top).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, x: float, y0: float, y1: float, level: int, width: float, hit: bool
    ) -> None:
        self.x = x
        self.y0 = y0
        self.y1 = y1
        self.level = level
        self.width = width
        self.hit = hit


class BeamHit:
    """A target the beam touches, with the level of the segment that touches it."""

    def __init__(self, target: ShotTarget, level: int, y: float) -> None:
        self.target = target
        self.level = level
        self.y = y


class BeamTrace:
    """The segments of a traced beam and the targets it touches."""

    def __init__(self, segments: list[BeamSegment], hits: list[BeamHit]) -> None:
        self.segments = segments
        self.hits = hits


def _first_target_above(
    targets: Sequence[ShotTarget], x: float, from_y: float, width: float, done: set[ShotTarget]
) -> ShotTarget | None:
    """The lowest living target above `from_y`, not yet hit, that a beam of `width` at `x`
    touches.
    """
    best: ShotTarget | None = None
    for target in targets:
        if not is_alive(target) or target in done or target.y <= from_y:
            continue
        if abs(target.x - x) > target.radius + width / 2:
            continue
        if best is None or target.y < best.y:
            best = target
    return best


def trace_beam(
    levels: Sequence[BeamLevel],
    level: int,
    x: float,
    y: float,
    top: float,
    targets: Sequence[ShotTarget],
) -> BeamTrace:
    """Traces a beam fired straight up from (x, y) at `level` (P03-R02). At level 1 the beam stops
    at the first target it touches. Above, it goes through the target and continues from it one
    level lower, so a level-N beam touches at most N targets.
    """
    segments: list[BeamSegment] = []
    hits: list[BeamHit] = []
    done: set[ShotTarget] = set()
    current_from = y
    current = level
    while current >= 1:
        width = levels[current - 1].width if 0 <= current - 1 < len(levels) else 0
        target = _first_target_above(targets, x, current_from, width, done)
        if target is None:
            segments.append(BeamSegment(x, current_from, top, current, width, False))
            break
        contact = max(current_from, target.y - target.radius)
        segments.append(BeamSegment(x, current_from, contact, current, width, True))
        hits.append(BeamHit(target, current, contact))
        done.add(target)
        current_from = contact
        current -= 1
    return BeamTrace(segments, hits)
