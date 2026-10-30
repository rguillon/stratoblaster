"""Cars on the streets and main roads (Phase 4 review; D-211: detailed, drawn as imposters)

Sizes in model units (drawn at `CAR_RULES.scale`), standing on Y = 0; the front faces +Z, the way
they drive. The levels draw a picture of each car baked from these models (`imposter_bake_visual`),
so their triangles cost nothing in play: they have wheels with hubs, bumpers, a grille, a glass
cabin between pillars, mirrors, lamps and plates. Their head and tail lights and the beams on the
road stay real geometry (the lights), so they glow at night.
"""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# Length of the headlight beams on the road, and their colour (dim, as the glow adds to it).
BEAM = 6
BEAM_LIGHT = [0.4, 0.33, 0.18]

# Kinds of cars: body length, width, height, cabin length and where it starts from the back.
SHAPES = {
    "sedan": {"length": 7, "width": 3.2, "height": 1.3, "cabin": 3.4, "back": 1.6},
    "van": {"length": 7.6, "width": 3.4, "height": 2.8, "cabin": 1.8, "back": 5.2},
    "truck": {"length": 10, "width": 3.6, "height": 3.4, "cabin": 2.2, "back": 7.6},
}

# The parts every car shares.
TYRE = [0.06, 0.06, 0.07]
HUB = C.silver
TRIM = [0.12, 0.12, 0.14]
LAMP = [0.95, 0.92, 0.8]
TAIL = [0.6, 0.06, 0.05]
PLATE = [0.85, 0.85, 0.8]
# Car glass, lighter than the buildings': seen from above, it shows the sky.
GLASS = [0.22, 0.27, 0.33]
# How high the body rides over the road (the wheels fill the gap).
CLEARANCE = 0.45
WHEEL = 0.62


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


def wheels(s: SolidBuilder, width: float, axles: list[float]) -> None:
    """A tyre with a hub at each end of each axle (at Z `axles`)."""
    for z in axles:
        for side in [-1, 1]:
            x = side * (width / 2 - 0.25)
            # A cylinder stands up Y; turned a quarter round Z, it lies across X from its foot.
            s.cylinder(WHEEL, 0.5, 10, TYRE, Placement([x - 0.25, WHEEL, z], 0, 0, -math.pi / 2))
            s.cylinder(
                WHEEL * 0.55, 0.54, 8, HUB, Placement([x - 0.27, WHEEL, z], 0, 0, -math.pi / 2)
            )


def ends(s: SolidBuilder, width: float, length: float, y: float) -> None:
    """Bumpers, a grille and number plates front and back, at height `y`."""
    front = length / 2
    back = -length / 2
    s.box([width + 0.1, 0.45, 0.35], TRIM, Placement([0, y, front - 0.1], 0, 0, 0))
    s.box([width + 0.1, 0.45, 0.35], TRIM, Placement([0, y, back + 0.1], 0, 0, 0))
    s.box([width * 0.45, 0.4, 0.1], TRIM, Placement([0, y + 0.5, front + 0.02], 0, 0, 0))
    s.box([0.9, 0.25, 0.06], PLATE, Placement([0, y + 0.08, front + 0.1], 0, 0, 0))
    s.box([0.9, 0.25, 0.06], PLATE, Placement([0, y + 0.08, back - 0.1], 0, 0, 0))


def lamps(s: SolidBuilder, width: float, length: float, y: float) -> None:
    """Headlamps and tail lamps on the corners (their glow is in the lights)."""
    for side in [-1, 1]:
        x = side * (width / 2 - 0.45)
        s.box([0.6, 0.3, 0.08], LAMP, Placement([x, y, length / 2 + 0.01], 0, 0, 0))
        s.box([0.6, 0.3, 0.08], TAIL, Placement([x, y, -length / 2 - 0.01], 0, 0, 0))


def mirrors(s: SolidBuilder, width: float, z: float, y: float, paint: list[float]) -> None:
    """A wing mirror each side at the foot of the windscreen."""
    for side in [-1, 1]:
        s.box([0.35, 0.25, 0.2], paint, Placement([side * (width / 2 + 0.12), y, z], 0, 0, 0))


def sedan(s: SolidBuilder, paint: list[float]) -> None:
    """A saloon: a low body with a bonnet and a boot, a glass cabin with pillars and a roof."""
    dims = SHAPES["sedan"]
    length = dims["length"]
    width = dims["width"]
    h = dims["height"]
    b = -length / 2
    f = length / 2
    belt = CLEARANCE + h
    top = belt + 1.05
    # Cabin: from the back of the boot lid to the foot of the windscreen.
    c0 = b + dims["back"] - 0.2
    c1 = c0 + dims["cabin"]
    side_profile(
        s,
        [
            [b, CLEARANCE + 0.15],
            [b + 0.1, belt - 0.05],
            [c0 - 0.4, belt],
            [c1 + 0.3, belt],
            [f - 0.3, belt - 0.2],
            [f, CLEARANCE + 0.55],
            [f, CLEARANCE + 0.15],
        ],
        width,
        paint,
    )
    greenhouse = [[c0, belt], [c0 + 0.7, top], [c1 - 0.9, top], [c1, belt]]
    side_profile(s, greenhouse, width * 0.86, GLASS)
    # The roof, and the pillars between the windows.
    s.box(
        [width * 0.88, 0.08, c1 - 0.9 - c0 - 0.7],
        paint,
        Placement([0, top, (c0 + c1 - 0.2) / 2], 0, 0, 0),
    )
    s.box(
        [width * 0.88, top - belt, 0.25], paint, Placement([0, belt, (c0 + c1) / 2 - 0.1], 0, 0, 0)
    )
    wheels(s, width, [b + 1.4, f - 1.4])
    ends(s, width, length, CLEARANCE)
    lamps(s, width, length, belt - 0.45)
    mirrors(s, width, c1 - 0.2, belt + 0.1, paint)


def van(s: SolidBuilder, paint: list[float]) -> None:
    """A van: a tall box with a short bonnet, a raked windscreen, side windows and a roof rack."""
    dims = SHAPES["van"]
    length = dims["length"]
    width = dims["width"]
    h = dims["height"]
    b = -length / 2
    f = length / 2
    top = CLEARANCE + h
    side_profile(
        s,
        [
            [b, CLEARANCE + 0.1],
            [b, top],
            [f - 1.7, top],
            [f - 0.8, CLEARANCE + 1.5],
            [f, CLEARANCE + 1.1],
            [f, CLEARANCE + 0.1],
        ],
        width,
        paint,
    )
    # The windscreen, just proud of the slope, and a band of side windows.
    side_profile(
        s,
        [
            [f - 1.75, top - 0.15],
            [f - 0.85, CLEARANCE + 1.55],
            [f - 0.75, CLEARANCE + 1.6],
            [f - 1.6, top - 0.1],
        ],
        width * 0.9,
        GLASS,
    )
    s.box(
        [width + 0.04, 0.7, length * 0.55],
        GLASS,
        Placement([0, top - 1.05, b + length * 0.4], 0, 0, 0),
    )
    for z in [b + 1, b + 2.6, b + 4.2]:
        s.box([width * 0.7, 0.12, 0.12], TRIM, Placement([0, top, z], 0, 0, 0))
    for side in [-1, 1]:
        s.box(
            [0.1, 0.1, length * 0.6],
            TRIM,
            Placement([side * width * 0.35, top + 0.12, b + length * 0.4], 0, 0, 0),
        )
    wheels(s, width, [b + 1.3, f - 1.4])
    ends(s, width, length, CLEARANCE)
    lamps(s, width, length, CLEARANCE + 0.85)
    mirrors(s, width, f - 1.6, CLEARANCE + 1.6, paint)


def truck(s: SolidBuilder, paint: list[float]) -> None:
    """A lorry: a cab with a windscreen and a sun visor, a ribbed cargo box, twin rear axles."""
    dims = SHAPES["truck"]
    length = dims["length"]
    width = dims["width"]
    h = dims["height"]
    b = -length / 2
    f = length / 2
    cab = 2.4
    top = CLEARANCE + h
    # The chassis under it all.
    s.box([width * 0.7, 0.4, length - 0.4], TRIM, Placement([0, CLEARANCE, 0], 0, 0, 0))
    # The cab, its roof a little lower than the box.
    side_profile(
        s,
        [
            [f - cab, CLEARANCE + 0.3],
            [f - cab, top - 0.3],
            [f - 0.5, top - 0.3],
            [f, top - 1.2],
            [f, CLEARANCE + 0.3],
        ],
        width,
        C.white,
    )
    side_profile(
        s,
        [
            [f - 0.55, top - 0.4],
            [f - 0.05, top - 1.25],
            [f + 0.02, top - 1.2],
            [f - 0.45, top - 0.35],
        ],
        width * 0.9,
        GLASS,
    )
    s.box([width * 0.9, 0.15, 0.5], TRIM, Placement([0, top - 0.32, f - 0.4], 0, 0, 0))
    # The cargo box, ribbed along its sides and roof.
    box_length = length - cab - 0.3
    box_z = b + box_length / 2
    s.box(
        [width, h - 0.2, box_length],
        paint,
        Placement([0, CLEARANCE + 0.5, box_z], 0, 0, 0),
        C.white,
    )
    ribs = 5
    for i in range(ribs + 1):
        z = b + 0.1 + (box_length - 0.2) * i / ribs
        s.box([width + 0.08, h - 0.15, 0.12], TRIM, Placement([0, CLEARANCE + 0.5, z], 0, 0, 0))
    wheels(s, width, [b + 1.1, b + 2.5, f - 1.4])
    ends(s, width, length, CLEARANCE)
    lamps(s, width, length, CLEARANCE + 0.8)
    mirrors(s, width, f - 0.5, top - 1.4, C.white)


BODIES = {"sedan": sedan, "van": van, "truck": truck}


def build_car(shape: str, paint: list[float]) -> PropGeometry:
    """A car of `shape` painted `paint`: its detailed body, and its lights with their beams."""
    s = SolidBuilder(True)
    lights = SolidBuilder(True)
    BODIES[shape](s, paint)
    dims = SHAPES[shape]
    length = dims["length"]
    width = dims["width"]
    z0 = -length / 2
    lights.box([width * 0.8, 0.5, 0.2], L.window, Placement([0, 0.9, length / 2 + 0.1], 0, 0, 0))
    lights.box([width * 0.8, 0.5, 0.2], L.red, Placement([0, 0.9, z0 - 0.1], 0, 0, 0))
    # The headlight beam on the road ahead, and a red glow behind: flat quads facing up.
    ground(lights, [width * 0.9, BEAM], length / 2 + BEAM / 2 + 0.3, BEAM_LIGHT)
    ground(lights, [width * 0.7, 1], z0 - 0.8, L.pinkDim)
    return PropGeometry(s.geometry, lights.geometry)
