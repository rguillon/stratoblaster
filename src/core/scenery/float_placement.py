"""Props that do not follow the roads (phase 8): floating ice on the sea, and lines of props along
the level (a pipeline); phase 9: set pieces at given places. Pure and deterministic for a given
seed."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")

from collections.abc import Callable  # noqa: E402

from core.scenery.height_field import HeightField  # noqa: E402
from core.scenery.scenery_level import FloatRules, Landmark, Meander, PropLine, PropRules  # noqa: E402

__pragma__("noskip")

from core.math.noise import hash_2d  # noqa: E402
from core.scenery.away_placement import Building  # noqa: E402
from core.scenery.draws import between, weighted  # noqa: E402
from core.scenery.ground_boxes import GroundArea, PropPlacement  # noqa: E402

# Draws per floating prop: position X, position Z, kind, scale, turn.
FLOAT_DRAWS = 5
# Hash stream of the number of floating props in a cell.
FLOAT_COUNT = 101


def _float_draws(r: Callable[[int], float], n: int) -> Callable[[int], float]:
    """The draws of floating prop `n` of a cell (a closure, not a default argument)."""

    def draw(k: int) -> float:
        return r(FLOAT_COUNT + 1 + n * FLOAT_DRAWS + k)

    return draw


def floating_props(
    rules: FloatRules,
    field: HeightField,
    sea_level: float,
    seed: int,
    i: int,
    j: int,
) -> list[PropPlacement]:
    """The floating props of cell (`i`, `j`) (P08-R07: ice floes, icebergs): up to `per_cell`, with
    the chance of their section's `float_density`, each where the sea is at least `depth` deep under
    its whole footprint. They float at `sea_level`."""
    cell_size = rules.cell_size
    section_density = field.section_at((j + 0.5) * cell_size).section.float_density
    density = section_density if section_density is not None else 0
    if density <= 0:
        return []

    def r(draw: int) -> float:
        return hash_2d(i, j, seed * 53 + draw)

    count = math.floor(r(FLOAT_COUNT) * (rules.per_cell + 1) * density)
    props: list[PropPlacement] = []
    for n in range(count):
        d = _float_draws(r, n)

        kind = weighted(rules.kinds, d(2))
        if kind is None:
            continue
        x = (i + d(0)) * cell_size
        z = (j + d(1)) * cell_size
        reach = kind.footprint
        limit = sea_level - rules.depth
        offsets = [(0, 0), (reach, 0), (-reach, 0), (0, reach), (0, -reach)]
        deep = True
        for dx, dz in offsets:
            if not field.height(x + dx, z + dz) <= limit:
                deep = False
                break
        if not deep:
            continue
        scale = between(kind.scale, d(3))
        props.append(PropPlacement(kind.id, x, sea_level, z, d(4) * 2 * math.pi, scale))
    return props


def floating_in(
    rules: FloatRules,
    field: HeightField,
    sea_level: float,
    seed: int,
    area: GroundArea,
) -> list[PropPlacement]:
    """The floating props of the cells whose corner lies in `area` (see `floating_props`)."""
    size = rules.cell_size
    i0 = math.ceil(area.x_min / size)
    i1 = math.ceil(area.x_max / size)
    j0 = math.ceil(area.z_min / size)
    j1 = math.ceil(area.z_max / size)
    placements: list[PropPlacement] = []
    for j in range(j0, j1):
        for i in range(i0, i1):
            placements.extend(floating_props(rules, field, sea_level, seed, i, j))
    return placements


class LinePiece:
    """A piece of a line of props, with the radius of ground it takes."""

    def __init__(self, placement: PropPlacement, footprint: float) -> None:
        self.placement = placement
        self.footprint = footprint


def _along_path(field: HeightField, path: Meander, z: float) -> float:
    """Turn of a model whose length runs along X so that X follows `path` at `z` (Z along the
    level)."""
    dx = field.path_x(path, z + 1) - field.path_x(path, z - 1)
    return math.atan2(-2, dx)


def _line_height(
    line: PropLine,
    field: HeightField,
    sea_level: float | None,
    x: float,
    z: float,
) -> float | None:
    """Where a piece of `line` stands at (`x`, `z`): on dry ground gentle enough, or at `sea_level`
    over the water if the line crosses water; None where it does not stand."""
    ground = field.height(x, z)
    if sea_level is not None and ground <= sea_level:
        return sea_level if line.over_water else None
    return None if field.slope(x, z, line.footprint) > line.max_slope else ground


def line_pieces(line: PropLine, field: HeightField, sea_level: float | None) -> list[LinePiece]:
    """The pieces of `line` over the whole level (P08-R03: a pipeline on stilts): one every
    `spacing` along its path, turned along it, where the ground is above `sea_level` and gentle
    enough, in the sections it runs through. A line `over_water` (phase 9) also crosses the water,
    its pieces at the sea level there."""
    pieces: list[LinePiece] = []
    step = line.spacing
    z = step / 2
    while z < field.length_:
        name = field.section_at(z).section.name
        if line.sections is None or name in line.sections:
            x = field.path_x(line.path, z)
            y = _line_height(line, field, sea_level, x, z)
            if y is not None:
                rotation = _along_path(field, line.path, z)
                pieces.append(
                    LinePiece(
                        PropPlacement(line.kind, x, y, z, rotation, 1),
                        line.footprint,
                    )
                )
        z += step
    return pieces


def place_landmark(landmark: Landmark, field: HeightField, sea_level: float | None) -> Building:
    """Where `landmark` stands (phase 9): at its `x`, or on its `path` turned across it; on the
    ground, or at `sea_level` when it is `on_water` (on the ground where that is higher). Returns
    the set piece with the box of ground it takes."""
    z = landmark.z
    path = landmark.path
    x = field.path_x(path, z) if path is not None else landmark.x if landmark.x is not None else 0
    ground = field.height(x, z)
    y = max(ground, sea_level) if landmark.on_water and sea_level is not None else ground
    # The model's width (X) lies across its path: a dam or a waterfall across a river.
    turn = _along_path(field, path, z) + math.pi / 2 if path is not None else 0
    half_x = landmark.footprint[0]
    half_z = landmark.footprint[1]
    rotation = landmark.rotation if landmark.rotation is not None else 0
    scale = landmark.scale if landmark.scale is not None else 1
    return Building(
        PropPlacement(landmark.kind, x, y, z, turn + rotation, scale),
        half_x,
        half_z,
    )


def fixed_pieces(rules: PropRules, field: HeightField, sea_level: float | None) -> list[Building]:
    """The props placed before everything else (phases 8, 9): the set pieces, whatever the ground,
    then the pieces of the lines, each with the box of ground it takes."""
    landmarks: list[Building] = []
    for landmark in rules.landmarks if rules.landmarks is not None else []:
        landmarks.append(place_landmark(landmark, field, sea_level))
    lines: list[Building] = []
    for line in rules.lines if rules.lines is not None else []:
        for piece in line_pieces(line, field, sea_level):
            lines.append(Building(piece.placement, piece.footprint, piece.footprint))
    landmarks.extend(lines)
    return landmarks
