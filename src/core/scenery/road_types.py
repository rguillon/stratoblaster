"""The data of the road network (TypeScript `road-network.ts`, `RoadPoint`, `Road`, `RoadSlot`,
and `road-segments.ts`'s `RoadSnapshot`), split out so that `lanes`, `road-segments` and
`road-paths` can build them at runtime without an import cycle with `road-network`.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Any  # noqa: E402

Lanes = int  # Lanes each way of a road: 1 to 4 (also `lanes.Lanes`).

__pragma__("noskip")


class RoadPoint:
    """One point of a road's centre line."""

    def __init__(self, x: float, z: float, width: float) -> None:
        self.x = x
        self.z = z
        self.width = width
        """Width of the road there (paths widen where they meet a road)."""


class Road:
    """A piece of winding road (`main`, along the level), a path (`cross`, branching off a main
    road) or a straight street of a district (`street`). Every point of it is on buildable ground,
    and it starts and ends off the screen or at another road."""

    def __init__(
        self,
        index: int,
        kind: str,
        width: float,
        lanes: int,
        points: Sequence[RoadPoint],
    ) -> None:
        self.index = index
        self.kind = kind
        """`main`, `cross` or `street`."""
        self.width = width
        """Nominal width (paths are wider near their junction, see `RoadPoint.width`)."""
        self.lanes = lanes
        """Lanes each way: 2 on 2×2 roads (phase 4 review), 3 or 4 on boulevards."""
        self.points = points


class RoadSlot:
    """A spot by a road where a building may stand, on one side of it."""

    def __init__(
        self,
        road: Road,
        index: int,
        x: float,
        z: float,
        nx: float,
        nz: float,
    ) -> None:
        self.road = road
        self.index = index
        """Slot number along its road, for hashing."""
        self.x = x
        self.z = z
        """Point on the road's centre line."""
        self.nx = nx
        self.nz = nz
        """Unit vector across the road, towards the side of the slot."""


class RoadSnapshot:
    """What a `RoadNetwork` made (or what its runout added): enough to draw it and to place the
    buildings by it without generating it again (P13-R03). The blocks and the slots are kept too,
    so the buildings can be placed where the roads were not made (chunk by chunk, P04-R04)."""

    def __init__(self, roads: Sequence[Road], blocks: Sequence[Any], slots: Sequence[Any]) -> None:
        self.roads = roads
        self.blocks = blocks
        self.slots = slots
