"""The districts of a level: the runs of sections with street grids (phase 4 review), split out of
and the parts of them laid apart (reviewer, 2026-10-28)."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.scenery_level import PlacedSection, StreetGrid  # noqa: E402

__pragma__("noskip")

INFINITY = float("Infinity")


class ZRange:
    """A stretch along Z."""

    def __init__(self, z_min: float, z_max: float) -> None:
        self.z_min = z_min
        self.z_max = z_max


class DistrictPart:
    """A part of a district: one section's street grid over its stretch along Z."""

    def __init__(self, grid: StreetGrid, z_min: float, z_max: float) -> None:
        self.grid = grid
        self.z_min = z_min
        self.z_max = z_max


class District:
    """A run of consecutive sections with street grids (phase 4 review)."""

    def __init__(
        self,
        z_min: float,
        z_max: float,
        parts: list[DistrictPart],
        continues: bool | None = None,
    ) -> None:
        """`continues`: it goes on from the district before it (the runout's, see
        `split_districts`): its first row is that district's last one, laid with it, and its
        columns start there."""
        self.z_min = z_min
        self.z_max = z_max
        self.parts = parts
        self.continues = continues


def find_districts(sections: Sequence[PlacedSection], span: ZRange) -> list[District]:
    """Runs of consecutive sections with a street grid. Districts at the ends of the level go on
    past them (to `span`), out of view."""
    districts: list[District] = []
    last = len(sections) - 1
    for i, placed in enumerate(sections):
        grid = placed.section.streets
        if grid is None:
            continue
        z_min = span.z_min if i == 0 else placed.start
        z_max = span.z_max if i == last else placed.end
        previous = districts[len(districts) - 1] if len(districts) > 0 else None
        if previous is not None and i > 0 and sections[i - 1].section.streets is not None:
            previous.parts.append(DistrictPart(grid, z_min, z_max))
            previous.z_max = z_max
        else:
            districts.append(District(z_min, z_max, [DistrictPart(grid, z_min, z_max)]))
    return districts


def _cut(d: District, from_: float, to: float) -> District | None:
    """The part of `d` between `from_` and `to`, if any (its own ends where they are closer)."""
    if d.z_max <= from_ or d.z_min >= to:
        return None
    if d.z_min >= from_ and d.z_max <= to:
        return d
    parts = [
        DistrictPart(p.grid, max(p.z_min, from_), min(p.z_max, to))
        for p in d.parts
        if p.z_max > from_ and p.z_min < to
    ]
    return District(max(d.z_min, from_), min(d.z_max, to), parts)


def districts_from(districts: Sequence[District], z: float) -> list[District]:
    """`districts` from `z` on (reviewer, 2026-10-28): one that reaches lower starts at `z`, with a
    full row there."""
    result: list[District] = []
    for d in districts:
        cut = _cut(d, z, INFINITY)
        if cut is not None:
            result.append(cut)
    return result


def split_districts(
    districts: Sequence[District], z: float
) -> tuple[list[District], list[District]]:
    """`districts` cut where the runout starts, at `z` (reviewer, 2026-10-28): the districts
    before it, ending with a full row at `z`, and those after it, which go on from that row
    (`continues`). Returns (before, after)."""
    before: list[District] = []
    after: list[District] = []
    for d in districts:
        head = _cut(d, -INFINITY, z)
        if head is not None:
            before.append(head)
        rest = _cut(d, z, INFINITY)
        if rest is not None:
            if rest.z_min > d.z_min:
                after.append(District(rest.z_min, rest.z_max, rest.parts, True))
            else:
                after.append(rest)
    return before, after


def laid_districts(
    districts: Sequence[District],
    streets_from: float | None = None,
    runout_from: float | None = None,
) -> tuple[list[District], list[District]]:
    """The parts of `districts` laid as the level is generated: from `streets_from` on, before the
    runout (`before`) and in it (`after`, laid later), when the level has one at `runout_from`.
    Returns (before, after)."""
    laid = list(districts) if streets_from is None else districts_from(districts, streets_from)
    if runout_from is None:
        return laid, []
    return split_districts(laid, runout_from)
