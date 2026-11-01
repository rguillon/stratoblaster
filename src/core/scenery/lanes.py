# Copyright (c) 2026 Renaud Guillon
"""Phase 4 review: roads of one lane each way, and 2x2 roads (two lanes each way).

The first main roads, and some lines of the street grids (avenues); reviewer, 2026-10-28: 3x3 and
4x4 boulevards in the street grids (GFX-ROAD-09).
"""

import math

from core.math.noise import hash_2d
from core.scenery.road_types import RoadPoint

# isort: split
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Protocol

from core.scenery.scenery_level import RoadRules


class PointXZ(Protocol):
    """A point of a centre line, in the ground's X and Z."""

    @property
    def x(self) -> float:
        """X of the point."""
        ...

    @property
    def z(self) -> float:
        """Z of the point."""
        ...


Lanes = int  # 1 to 4 lanes each way
"""Lanes each way of a road."""
# __pragma__ ("noskip")


def lanes_of(rules: RoadRules, width: float) -> Lanes:
    """Lanes each way of a road `width` wide."""
    if rules.boulevards is not None:
        for b in rules.boulevards:
            if b.width == width:
                return b.lanes
    lanes: Lanes = 2 if width >= rules.dual.width else 1
    return lanes


def is_boulevard(rules: RoadRules, width: float) -> bool:
    """Whether `width` is a boulevard's (see `RoadRules.boulevards`)."""
    if rules.boulevards is None:
        return False
    return any(b.width == width for b in rules.boulevards)


def main_road_width(rules: RoadRules, index: int) -> float:
    """Width of main road number `index`: the first `dual.main_roads` are 2x2 (GFX-ROAD-01)."""
    return rules.dual.width if index < rules.dual.main_roads else rules.main_width


def street_width(rules: RoadRules, coord: float) -> float:
    """Width of the street along a line of a street grid (`coord`: X of a column, Z of a row).

    Decided by a hash of the line (GFX-ROAD-17): a share of the lines are boulevards, of each kind
    in turn, then a share `dual.avenues` 2x2 avenues, the others one lane each way.
    """
    h = hash_2d(math.floor(coord + 0.5), 17, 101)
    total = 0.0
    if rules.boulevards is not None:
        for b in rules.boulevards:
            if h < total + b.share:
                return b.width
            total += b.share
    return rules.dual.width if h < total + rules.dual.avenues else rules.main_width


def run_width(rules: RoadRules, run: Sequence[PointXZ]) -> float:
    """Width of a straight run of a street grid.

    A row (along X) or a column, as wide as its line.
    """
    if len(run) == 0:
        return rules.main_width
    a = run[0]
    b = run[len(run) - 1]
    return street_width(rules, a.z if a.z == b.z else a.x)


def with_width(points: Sequence[PointXZ], width: float) -> list[RoadPoint]:
    """`points` of a road `width` wide."""
    return [RoadPoint(p.x, p.z, width) for p in points]
