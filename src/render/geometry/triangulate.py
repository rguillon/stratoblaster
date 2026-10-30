"""Ear-clipping triangulation of a simple polygon (ported from `render/geometry/triangulate.ts`)."""

from org.transcrypt.stubs.browser import __pragma__

# OutlinePoint is a type alias, imported for annotations only (Transcrypt skips this block).
__pragma__("skip")
from render.geometry.outline import OutlinePoint  # noqa: E402

__pragma__("noskip")

from render.geometry.outline import ring_at  # noqa: E402

# A polygon left with fewer corners than this has no triangle to clip.
MIN_TRIANGLE_POINTS = 3


def _cross(o: OutlinePoint, a: OutlinePoint, b: OutlinePoint) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _in_triangle(p: OutlinePoint, a: OutlinePoint, b: OutlinePoint, c: OutlinePoint) -> bool:
    return _cross(a, b, p) >= 0 and _cross(b, c, p) >= 0 and _cross(c, a, p) >= 0


def _corner_at(ring: list[int], i: int) -> list[int]:
    return [ring_at(ring, i - 1), ring_at(ring, i), ring_at(ring, i + 1)]


def _is_ear(points: list[OutlinePoint], corner: list[int], ring: list[int]) -> bool:
    a = points[corner[0]]
    b = points[corner[1]]
    c = points[corner[2]]
    if _cross(a, b, c) <= 0:
        return False
    for j in ring:
        if j in corner:
            continue
        if _in_triangle(points[j], a, b, c):
            return False
    return True


def triangulate_polygon(points: list[OutlinePoint]) -> list[list[int]]:
    """Triangulates a simple polygon given counter-clockwise (ear clipping, O(n²)).

    Returns triangles as index triples into `points`, each counter-clockwise.
    """
    ring = [i for i in range(len(points))]
    triangles: list[list[int]] = []
    while len(ring) >= MIN_TRIANGLE_POINTS:
        ear = -1
        for i in range(len(ring)):
            if _is_ear(points, _corner_at(ring, i), ring):
                ear = i
                break
        if ear < 0:
            raise ValueError("The outline is not a simple polygon")
        triangles.append(_corner_at(ring, ear))
        ring.pop(ear)
    return triangles
