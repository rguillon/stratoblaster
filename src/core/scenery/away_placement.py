"""Lone buildings and hamlets away from the roads (phase 6 review). Ported from
`core/scenery/away-placement.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Protocol  # noqa: E402

from core.scenery.scenery_level import (  # noqa: E402
    HamletRules,
    Loners,
    PropGroupRule,
    PropKindRule,
    TerrainSection,
)

Draw = Callable[[int], float]
__pragma__("noskip")

from core.math.noise import hash_2d  # noqa: E402
from core.scenery.draws import between, weighted  # noqa: E402
from core.scenery.ground_boxes import PropPlacement  # noqa: E402

# Lone buildings and hamlets stand within this share of `offscreen_x` of the level's middle…
AWAY_SPREAD = 0.5
# …and from this far before the level to this far after it (seen at its ends).
AWAY_MARGIN = 400
# Places a hamlet's centre is tried at.
HAMLET_TRIES = 6
# Tries per building of a hamlet, and draws per try (direction, distance, kind, scale).
BUILDING_TRIES = 4
BUILDING_DRAWS = 4
# Turns of the buildings of a hamlet around its common heading, in radians.
HAMLET_SKEW = 0.3


class Building:
    """A building with the half-extents (X, Z) of the box of ground it takes."""

    def __init__(self, placement: PropPlacement, half_x: float, half_z: float) -> None:
        self.placement = placement
        self.half_x = half_x
        self.half_z = half_z


__pragma__("skip")


class AwaySite(Protocol):
    """What placing buildings away from the roads needs from the prop placer."""

    @property
    def length_(self) -> float:
        """Length of the level along Z."""
        ...

    @property
    def offscreen_x(self) -> float:
        """Roads start and end beyond X = ±offscreen_x."""
        ...

    @property
    def seed(self) -> int: ...

    def section_at(self, z: float) -> TerrainSection:
        """The section under `z`."""
        ...

    def group_at(self, x: float, z: float, section: TerrainSection) -> PropGroupRule | None:
        """The building group of the area around (`x`, `z`), among those `section` allows."""
        ...

    def clear_of_roads(self, x: float, z: float, clearance: float) -> bool:
        """Whether (`x`, `z`) is at least `clearance` from every road edge."""
        ...

    def ground(self, x: float, z: float, radius: float) -> float | None:
        """Height of the flat enough ground under a footprint of `radius`, or None."""
        ...

    def add(self, building: Building, gap: float | None) -> bool:
        """Adds `building` if it keeps `gap` (None: the road setback) from the others."""
        ...


__pragma__("noskip")


class Candidate:
    """A building to try: its kind, place, turn and scale."""

    def __init__(
        self, kind: PropKindRule, x: float, z: float, rotation: float, scale: float
    ) -> None:
        self.kind = kind
        self.x = x
        self.z = z
        self.rotation = rotation
        self.scale = scale


class ZSpan:
    """A stretch of the level along Z, from `from_` (included) to `to`."""

    def __init__(self, from_: float, to: float) -> None:
        self.from_ = from_
        self.to = to


class _Centre:
    def __init__(self, x: float, z: float) -> None:
        self.x = x
        self.z = z


def _round(v: float) -> int:
    """`Math.round` of JavaScript (halves go up)."""
    return math.floor(v + 0.5)


def _standalone(site: AwaySite, c: Candidate, clearance: float) -> Building | None:
    """`c` standing on its own, at least `clearance` from every road edge, or None when the roads
    or the ground do not allow it."""
    kind = c.kind
    reach = kind.footprint if kind.frontage is None else kind.frontage * c.scale
    if not site.clear_of_roads(c.x, c.z, reach + clearance):
        return None
    y = site.ground(c.x, c.z, kind.footprint)
    if y is None:
        return None
    turned = abs(math.cos(c.rotation)) + abs(math.sin(c.rotation))
    half = kind.footprint if kind.frontage is None else kind.frontage * c.scale * turned
    return Building(
        PropPlacement(kind.id, c.x, y, c.z, c.rotation, c.scale),
        half,
        half,
    )


def _try_place(site: AwaySite, c: Candidate, clearance: float, gap: float | None) -> bool:
    """Places `c` away from the roads if it fits; whether it did."""
    building = _standalone(site, c, clearance)
    return building is not None and site.add(building, gap)


def place_hamlets(site: AwaySite, hamlets: HamletRules, span: ZSpan) -> None:
    """Hamlets every `spacing` along the level (phase 6 review, see `HamletRules`), those in
    `span` (reviewer, 2026-10-28: the runout's are placed apart)."""

    def r(n: int, draw: int) -> float:
        return hash_2d(n, draw, site.seed * 47 + 13)

    z = -AWAY_MARGIN + between(hamlets.spacing, r(0, 0))
    n = 1
    while z < site.length_ + AWAY_MARGIN:
        if z >= span.from_ and z < span.to:
            _hamlet(site, hamlets, z, _draws(r, n))
        z += between(hamlets.spacing, r(n, 0))
        n += 1


def _draws(r: Callable[[int, int], float], n: int) -> Draw:
    """The draws of hamlet `n`: `r` with its number fixed."""

    def draw(d: int) -> float:
        return r(n, d)

    return draw


def _hamlet_centre(
    site: AwaySite,
    hamlets: HamletRules,
    z: float,
    r: Draw,
) -> _Centre | None:
    """Where a hamlet about `z` can stand: away from the roads, on flat ground."""
    radius = hamlets.radius
    clearance = hamlets.clearance
    half = site.offscreen_x * AWAY_SPREAD - radius
    candidates: list[_Centre] = []
    for t in range(HAMLET_TRIES):
        candidates.append(
            _Centre(
                (2 * r(1 + t) - 1) * half,
                z + (r(1 + HAMLET_TRIES + t) - 0.5) * radius,
            )
        )
    for c in candidates:
        if site.clear_of_roads(c.x, c.z, radius + clearance) and (
            site.ground(c.x, c.z, radius / 2) is not None
        ):
            return c
    return None


def _building_draws(r: Draw, k: int) -> Callable[[int], float]:
    """The draws of hamlet building `k`: `r` with its stream fixed (a closure, not a default)."""

    def draw(d: int) -> float:
        return r(30 + k * BUILDING_DRAWS + d)

    return draw


def _hamlet(site: AwaySite, hamlets: HamletRules, z: float, r: Draw) -> None:
    """A hamlet about `z`, if its section has buildings and a place away from the roads."""
    section = site.section_at(z)
    if section.streets is not None or section.building_density <= 0:
        return
    centre = _hamlet_centre(site, hamlets, z, r)
    if centre is None:
        return
    group = site.group_at(centre.x, centre.z, section)
    if group is None:
        return
    count = _round(between(hamlets.buildings, r(20)))
    # All turned about the same way, as in a village.
    heading = math.floor(r(21) * 4) * (math.pi / 2)
    placed = 0
    k = 0
    while placed < count and k < count * BUILDING_TRIES:
        d = _building_draws(r, k)

        kind = weighted(group.kinds, d(2))
        if kind is None:
            return
        angle = d(0) * 2 * math.pi
        distance = math.sqrt(d(1)) * hamlets.radius
        candidate = Candidate(
            kind,
            centre.x + math.sin(angle) * distance,
            centre.z + math.cos(angle) * distance,
            heading + (d(3) - 0.5) * HAMLET_SKEW,
            between(kind.scale, d(3)),
        )
        if _try_place(site, candidate, hamlets.clearance, hamlets.gap):
            placed += 1
        k += 1


def place_loners(site: AwaySite, loners: Loners, span: ZSpan) -> None:
    """A few lone buildings away from the roads (phase 6 review, see `PropRules.loners`), those in
    `span`."""
    cell = loners.cell
    half = site.offscreen_x * AWAY_SPREAD
    i0 = math.floor(-half / cell)
    i1 = math.ceil(half / cell)
    j0 = max(math.floor(-AWAY_MARGIN / cell), math.floor(span.from_ / cell))
    j1 = min(math.ceil((site.length_ + AWAY_MARGIN) / cell), math.ceil(span.to / cell))
    for j in range(j0, j1):
        for i in range(i0, i1):
            _loner(site, loners, i, j, span)


def _loner(site: AwaySite, loners: Loners, i: int, j: int, span: ZSpan) -> None:
    """The lone building of cell (`i`, `j`), if it gets one."""
    cell = loners.cell

    def r(draw: int) -> float:
        return hash_2d(i, j, site.seed * 43 + 7 + draw)

    x = (i + r(0)) * cell
    z = (j + r(1)) * cell
    if z < span.from_ or z >= span.to:
        return
    section = site.section_at(z)
    if section.streets is not None or r(2) >= loners.chance * section.building_density:
        return
    group = site.group_at(x, z, section)
    kinds: Sequence[PropKindRule] = group.kinds if group is not None else []
    kind = weighted(kinds, r(3))
    if kind is None:
        return
    rotation = r(4) * 2 * math.pi
    _try_place(
        site,
        Candidate(kind, x, z, rotation, between(kind.scale, r(5))),
        loners.clearance,
        None,
    )
