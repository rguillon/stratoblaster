"""Cars on the streets and main roads (Phase 4 review; D-211: futuristic hover cars, drawn as
imposters)

Sizes in model units (drawn at `CAR_RULES.scale`), standing on Y = 0; the front faces +Z, the way
they drive. The levels draw a picture of each car baked from these models (`imposter_bake_visual`),
so their triangles cost nothing in play. They hover on pads instead of wheels: chamfered wedge
hulls, glass canopies, fins, thrusters, neon strips. Their light bars, neon strips, the glow under
them and the beams on the road stay real geometry (the lights), so they glow at night.
"""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# Length of the headlight beams on the road, and their colour (dim, as the glow adds to it).
BEAM = 6
BEAM_LIGHT = [0.4, 0.33, 0.18]

# Kinds of cars: body length, width and height (`cabin` and `back`: where the cabin is, from the
# back).
SHAPES = {
    "sedan": {"length": 7, "width": 3.2, "height": 1.3, "cabin": 3.4, "back": 1.6},
    "van": {"length": 7.6, "width": 3.4, "height": 2.8, "cabin": 1.8, "back": 5.2},
    "truck": {"length": 10, "width": 3.6, "height": 3.4, "cabin": 2.2, "back": 7.6},
}

# The parts every car shares.
PAD = [0.1, 0.1, 0.12]
TRIM = [0.14, 0.15, 0.18]
NOZZLE = [0.25, 0.26, 0.3]
# Car glass, lighter than the buildings': seen from above, it shows the sky.
GLASS = [0.22, 0.3, 0.38]
# How high the hull floats over the road.
HOVER = 0.6


def ground(lights: SolidBuilder, size: list[float], z: float, color: list[float]) -> None:
    """A flat quad facing up just above the road, `w × d`, centred at Z = `z`."""
    w = size[0]
    d = size[1]
    x0 = -w / 2
    x1 = w / 2
    z0 = z - d / 2
    z1 = z + d / 2
    y = 0.1
    lights.face(
        [
            [x0, y, z0],
            [x0, y, z1],
            [x1, y, z1],
            [x1, y, z0],
        ],
        color,
    )


def side_profile(
    s: SolidBuilder, profile: list[list[float]], width: float, color: list[float]
) -> None:
    """A solid whose side view is `profile` (`[z, y]` points), `width` wide across X, centred."""
    # A slab is an outline in XZ pushed up Y; turned a quarter round Z, its Y goes across X and
    # its X (here minus the height) goes up.
    outline = [[-p[1], p[0]] for p in profile]
    s.slab(outline, [-width / 2, width / 2], color, Placement([0, 0, 0], 0, 0, -math.pi / 2))


def pads(s: SolidBuilder, width: float, axles: list[float]) -> None:
    """A hover pad under each corner (at Z `axles`): a flat dark block, tucked in under the hull
    (round ones read as wheels)."""
    for z in axles:
        for side in [-1, 1]:
            s.box([0.8, HOVER - 0.25, 1.1], PAD, Placement([side * width * 0.26, 0.25, z]))


def thrusters(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    lights: SolidBuilder,
    xs: list[float],
    y: float,
    z: float,
    accent: list[float],
) -> None:
    """Thrusters pointing back from Z `z`, at X `xs` and height `y`, each glowing at its mouth."""
    for x in xs:
        # A cylinder stands up Y; pitched a quarter turn, it lies along -Z from its foot.
        s.cylinder(0.32, 0.7, 8, NOZZLE, Placement([x, y, z + 0.6], 0, math.pi / 2, 0), 0.38)
        lights.cylinder(0.24, 0.05, 8, accent, Placement([x, y, z - 0.12], 0, math.pi / 2, 0))


def strips(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    lights: SolidBuilder,
    width: float,
    y: float,
    span: list[float],
    accent: list[float],
) -> None:
    """A neon strip along each side at height `y`, from Z `span[0]` to `span[1]`: painted on the
    hull (it shows by day) and lit over it (it glows at night)."""
    length = span[1] - span[0]
    z = (span[0] + span[1]) / 2
    for side in [-1, 1]:
        x = side * (width / 2)
        s.box([0.12, 0.3, length], accent, Placement([x, y, z]))
        lights.box([0.06, 0.22, length * 0.98], accent, Placement([x + side * 0.05, y + 0.04, z]))


def stripes(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    lights: SolidBuilder,
    xs: list[float],
    y: float,
    span: list[float],
    accent: list[float],
) -> None:
    """Neon stripes along the top at X `xs`, on a deck at height `y`, from Z `span[0]` to
    `span[1]`: seen from above, as the playfield camera sees the cars."""
    length = span[1] - span[0]
    z = (span[0] + span[1]) / 2
    for x in xs:
        s.box([0.3, 0.05, length], accent, Placement([x, y, z]))
        lights.box([0.22, 0.04, length * 0.98], accent, Placement([x, y + 0.05, z]))


def light_bars(lights: SolidBuilder, width: float, length: float, y: float) -> None:
    """A headlight bar and a tail light bar, `width` wide."""
    lights.box([width, 0.18, 0.12], L.window, Placement([0, y, length / 2 + 0.02]))
    lights.box([width * 1.1, 0.18, 0.12], L.red, Placement([0, y, -length / 2 - 0.02]))


def sedan(s: SolidBuilder, lights: SolidBuilder, paint: list[float], accent: list[float]) -> None:
    """A hover coupé: a chamfered wedge hull with a pointed nose, a teardrop glass canopy, twin
    fins carrying a wing, and two thrusters."""
    dims = SHAPES["sedan"]
    length = dims["length"]
    width = dims["width"]
    b = -length / 2
    f = length / 2
    hw = width / 2
    deck = HOVER + 0.75
    hull = [
        [-hw + 0.1, b],
        [hw - 0.1, b],
        [hw, b + 2],
        [hw - 0.2, f - 1.4],
        [0.7, f],
        [-0.7, f],
        [-hw + 0.2, f - 1.4],
        [-hw, b + 2],
    ]
    s.bevel_slab(hull, [HOVER, HOVER + 0.35, deck], [0.25, 0.35], paint)
    canopy = [[-1.05, -1.9], [1.05, -1.9], [1.15, 0], [0.55, 1.6], [-0.55, 1.6], [-1.15, 0]]
    s.bevel_slab(canopy, [deck, deck + 0.2, deck + 0.75], [0, 0.4], GLASS)
    # A spine over the canopy, and the wing on its fins.
    s.box([0.3, 0.08, 2.6], paint, Placement([0, deck + 0.72, -0.4]))
    for side in [-1, 1]:
        s.box([0.12, 0.7, 0.9], paint, Placement([side * (hw - 0.45), deck - 0.05, b + 0.6]))
    s.box([width * 0.82, 0.08, 0.7], TRIM, Placement([0, deck + 0.62, b + 0.55]))
    thrusters(s, lights, [-0.6, 0.6], HOVER + 0.4, b, accent)
    pads(s, width, [b + 1.3, f - 1.6])
    strips(s, lights, width - 0.3, HOVER + 0.35, [b + 0.6, f - 1.6], accent)
    stripes(s, lights, [-hw + 0.5, hw - 0.5], deck - 0.03, [b + 1.2, f - 1.7], accent)
    light_bars(lights, 1.3, length, HOVER + 0.4)


def van(s: SolidBuilder, lights: SolidBuilder, paint: list[float], accent: list[float]) -> None:
    """A hover van: a tall chamfered pod with a sloping nose, a band of glass wrapping round it, a
    roof light bar and thrusters under the tail."""
    dims = SHAPES["van"]
    length = dims["length"]
    width = dims["width"]
    h = dims["height"]
    b = -length / 2
    f = length / 2
    hw = width / 2
    top = HOVER + h
    body = [
        [-hw, b],
        [hw, b],
        [hw, f - 1.6],
        [hw - 0.4, f - 0.2],
        [-hw + 0.4, f - 0.2],
        [-hw, f - 1.6],
    ]
    s.bevel_slab(body, [HOVER, HOVER + 0.4, top - 0.9], [0.3, 0.1], paint)
    # The glass band, and the roof over it.
    band = [
        [-hw + 0.08, b + 0.3],
        [hw - 0.08, b + 0.3],
        [hw - 0.08, f - 1.4],
        [0, f - 0.3],
        [-hw + 0.08, f - 1.4],
    ]
    s.slab(band, [top - 0.9, top - 0.35], GLASS)
    roof = [[-hw + 0.1, b], [hw - 0.1, b], [hw - 0.1, f - 1.9], [-hw + 0.1, f - 1.9]]
    s.bevel_slab(roof, [top - 0.35, top - 0.3, top], [0, 0.25], paint)
    # A nose under the windscreen.
    nose = [[f - 1.6, HOVER + 0.2], [f - 1.6, HOVER + 1.4], [f, HOVER + 0.7], [f, HOVER + 0.2]]
    side_profile(s, nose, width - 0.8, paint)
    s.box([width * 0.5, 0.15, 0.25], TRIM, Placement([0, top, -0.5]))
    lights.box([width * 0.48, 0.1, 0.2], accent, Placement([0, top + 0.12, -0.5]))
    thrusters(s, lights, [-0.9, 0.9], HOVER + 0.5, b, accent)
    pads(s, width, [b + 1.3, f - 1.7])
    strips(s, lights, width, HOVER + 0.55, [b + 0.4, f - 1.8], accent)
    stripes(s, lights, [-hw + 0.45, hw - 0.45], top, [b + 0.3, f - 2.1], accent)
    light_bars(lights, width - 1, length - 0.4, HOVER + 0.7)


def truck(s: SolidBuilder, lights: SolidBuilder, paint: list[float], accent: list[float]) -> None:
    """A hover hauler: a pointed cab pod with a wraparound windscreen, a chamfered cargo pod with
    glowing seams, and three thrusters."""
    dims = SHAPES["truck"]
    length = dims["length"]
    width = dims["width"]
    h = dims["height"]
    b = -length / 2
    f = length / 2
    hw = width / 2
    top = HOVER + h
    c0 = f - 2.6
    cab = [
        [-hw, c0],
        [hw, c0],
        [hw - 0.2, f - 0.9],
        [0.6, f],
        [-0.6, f],
        [-hw + 0.2, f - 0.9],
    ]
    s.bevel_slab(cab, [HOVER, HOVER + 0.5, top - 0.6], [0.3, 0.6], C.white)
    glass = [
        [-hw + 0.3, c0 + 0.6],
        [hw - 0.3, c0 + 0.6],
        [hw - 0.5, f - 0.9],
        [0.4, f - 0.25],
        [-0.4, f - 0.25],
        [-hw + 0.5, f - 0.9],
    ]
    s.bevel_slab(glass, [top - 1.4, top - 1.0, top - 0.55], [0, 0.35], GLASS)
    # The cargo pod, joined to the cab by a dark neck.
    s.box([width * 0.6, 1.6, 0.5], TRIM, Placement([0, HOVER + 0.4, c0 - 0.15]))
    pod_end = c0 - 0.4
    pod = [[-hw, b], [hw, b], [hw, pod_end], [-hw, pod_end]]
    s.bevel_slab(pod, [HOVER + 0.2, HOVER + 0.6, top], [0.25, 0.3], paint, None, C.white)
    seams = 4
    for i in range(1, seams):
        z = b + (pod_end - b) * i / seams
        for side in [-1, 1]:
            s.box([0.1, h - 1.1, 0.25], accent, Placement([side * hw, HOVER + 0.75, z]))
            glow = Placement([side * (hw + 0.05), HOVER + 0.8, z])
            lights.box([0.05, h - 1.2, 0.18], accent, glow)
        # Over the roof too, where the camera sees it.
        s.box([width - 0.6, 0.05, 0.25], accent, Placement([0, top, z]))
        lights.box([width - 0.7, 0.04, 0.18], accent, Placement([0, top + 0.05, z]))
    s.box([width * 0.3, 0.1, pod_end - b - 0.6], TRIM, Placement([0, top, (b + pod_end) / 2]))
    thrusters(s, lights, [-1.1, 0, 1.1], HOVER + 0.6, b, accent)
    pads(s, width, [b + 1.2, b + 3.6, f - 1.4])
    strips(s, lights, width - 0.3, HOVER + 0.45, [c0 + 0.2, f - 1.0], accent)
    light_bars(lights, 1.6, length, HOVER + 0.55)


BODIES = {"sedan": sedan, "van": van, "truck": truck}


def build_car(shape: str, paint: list[float], accent: list[float] | None = None) -> PropGeometry:
    """A hover car of `shape` painted `paint`, its neon `accent` (cyan if None): its hull, and its
    lights with the glow under it and its beam."""
    if accent is None:
        accent = L.cyan
    s = SolidBuilder(True)
    lights = SolidBuilder(True)
    BODIES[shape](s, lights, paint, accent)
    dims = SHAPES[shape]
    length = dims["length"]
    width = dims["width"]
    # The beam on the road ahead, a red glow behind and the hover glow under the hull.
    ground(lights, [width * 0.9, BEAM], length / 2 + BEAM / 2 + 0.3, BEAM_LIGHT)
    ground(lights, [width * 0.7, 1], -length / 2 - 0.8, L.pinkDim)
    under = [accent[0] * 0.3, accent[1] * 0.3, accent[2] * 0.3]
    ground(lights, [width * 0.8, length * 0.7], 0, under)
    return PropGeometry(s.geometry, lights.geometry)
