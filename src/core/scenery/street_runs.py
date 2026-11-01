# Copyright (c) 2026 Renaud Guillon
"""The straight runs of the street grids' built links (phase 4 review)."""

import math

from core.scenery.ordering import stable_sort_by
from core.scenery.street_links import to_fixed3

# isort: split
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Protocol


class GridNode(Protocol):
    """A point of the street network."""

    @property
    def x(self) -> float:
        """X of the crossing."""
        ...

    @property
    def z(self) -> float:
        """Z of the crossing."""
        ...


class GridLink(Protocol):
    """A built stretch of street between two neighbouring crossings."""

    @property
    def a(self) -> GridNode:
        """One end of the stretch."""
        ...

    @property
    def b(self) -> GridNode:
        """The other end of the stretch."""
        ...

    @property
    def across(self) -> bool:
        """Whether the stretch lies along X: its two ends share a Z."""
        ...


# __pragma__ ("noskip")


class Point:
    """A point of a straight run."""

    def __init__(self, x: float, z: float) -> None:
        self.x = x
        self.z = z


def _key(n: GridNode) -> str:
    return to_fixed3(n.x) + "," + to_fixed3(n.z)


def _same(a: GridNode, b: GridNode) -> bool:
    """Whether `a` and `b` are the same node: mostly the same object."""
    return a is b or _key(a) == _key(b)


def straight_runs(links: Sequence[GridLink], step: float) -> list[list[Point]]:
    """Maximal straight runs of the built links `links`, as points every `step`."""
    runs: list[list[Point]] = []
    lines: dict[str, list[GridLink]] = {}
    for link in links:
        line = "z" + to_fixed3(link.a.z) if link.across else "x" + to_fixed3(link.a.x)
        # Reviewer, 2026-10-28: added to the line's list, not copied into a new one each time.
        existing = lines.get(line)
        if existing is not None:
            existing.append(link)
        else:
            lines[line] = [link]
    for line_key in list(lines.keys()):
        ordered = stable_sort_by(lines[line_key], _along_key(lines[line_key][0].across))
        run: list[GridNode] = []
        for link in ordered:
            last = run[len(run) - 1] if len(run) > 0 else None
            if last is not None and _same(last, link.a):
                run.append(link.b)
            else:
                if len(run) > 1:
                    runs.append(_resample(run, step))
                run = [link.a, link.b]
        if len(run) > 1:
            runs.append(_resample(run, step))
    return runs


def _along(n: GridNode, across: bool) -> float:
    return n.x if across else n.z


def _along_key(across: bool) -> Callable[[GridLink], float]:
    """Return the sort key of a line of links: their start along the line."""

    def key(link: GridLink) -> float:
        return _along(link.a, across)

    return key


def _resample(run: Sequence[GridNode], step: float) -> list[Point]:
    """Points every about `step` from the first to the last node of a straight run."""
    if len(run) == 0:
        return []
    first = run[0]
    last = run[len(run) - 1]
    length = math.hypot(last.x - first.x, last.z - first.z)
    count = max(1, math.floor(length / step + 0.5))
    return [
        Point(
            first.x + ((last.x - first.x) * i) / count,
            first.z + ((last.z - first.z) * i) / count,
        )
        for i in range(count + 1)
    ]
