"""The towers of the city blocks (phase 4 review), split out of `prop-placement.ts`. Ported from
`core/scenery/block-towers.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from core.scenery.scenery_level import PropGroupRule, PropKindRule  # noqa: E402
from core.scenery.street_links import Block  # noqa: E402

__pragma__("noskip")

from core.scenery.away_placement import Building  # noqa: E402
from core.scenery.ground_boxes import PropPlacement  # noqa: E402

# Gap between a tower and the edge of its part of the podium roof.
TOWER_MARGIN = 1
# Towers are drawn among the kinds at least this share of the largest one that fits.
LARGEST_SHARE = 0.75

INFINITY = float("Infinity")


class _Fit:
    """A kind that fits a part of a block, at its scale."""

    def __init__(self, kind: PropKindRule, scale: float) -> None:
        self.kind = kind
        self.scale = scale


def _reach(kind: PropKindRule) -> float:
    return kind.frontage if kind.frontage is not None else kind.footprint


def tower_in(
    part: Block,
    groups: Sequence[PropGroupRule],
    y: float,
    r: float,
) -> Building | None:
    """The largest kind of `groups` that fits `part`, standing at `y`, with the ground it takes."""
    half = min(part.x_max - part.x_min, part.z_max - part.z_min) / 2 - TOWER_MARGIN
    fitting: list[_Fit] = []
    for g in groups:
        for kind in g.kinds:
            frontage_or_footprint = (
                kind.frontage if kind.frontage is not None else kind.footprint / kind.scale[1]
            )
            scale = min(kind.scale[1], half / frontage_or_footprint)
            if scale >= kind.scale[0]:
                fitting.append(_Fit(kind, scale))
    largest = -INFINITY
    for f in fitting:
        largest = max(largest, _reach(f.kind) * f.scale)
    choices = [f for f in fitting if _reach(f.kind) * f.scale >= largest * LARGEST_SHARE]
    index = math.floor(r * len(choices))
    if len(choices) == 0 or index >= len(choices):
        return None
    choice = choices[index]
    # Shifted within the room its part leaves around it, so towers do not line up (review).
    size = _reach(choice.kind) * choice.scale

    def shift(low: float, high: float, t: float) -> float:
        return (low + high) / 2 + (t - 0.5) * max(0, high - low - 2 * (size + TOWER_MARGIN))

    placement = PropPlacement(
        choice.kind.id,
        shift(part.x_min, part.x_max, _fraction(r * 31)),
        y,
        shift(part.z_min, part.z_max, _fraction(r * 57)),
        (math.floor(r * 4 * 7919) % 4) * (math.pi / 2),
        choice.scale,
    )
    return Building(placement, size, size)


def _fraction(v: float) -> float:
    """`v % 1` for a positive `v`, exactly."""
    return v - math.floor(v)
