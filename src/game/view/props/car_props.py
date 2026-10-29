"""Cars on the streets and main roads (Phase 4 review), ported from `props/car-props.ts`.

Sizes in model units (drawn at half size), standing on Y = 0; the front faces +Z, the way they
drive.
"""

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


def build_car(shape: str, paint: list[float]) -> PropGeometry:
    """A low-poly car: wheels, a body, a glass cabin, headlights with beams, and tail lights."""
    s = SolidBuilder(True)
    lights = SolidBuilder(True)
    dims = SHAPES[shape]
    length = dims["length"]
    width = dims["width"]
    height = dims["height"]
    cabin = dims["cabin"]
    back = dims["back"]
    z0 = -length / 2
    s.box([width, height, length], paint, Placement([0, 0.4, 0], 0, 0, 0), paint)
    s.box(
        [width * 0.86, 1.1, cabin],
        C.glass,
        Placement([0, 0.4 + height, z0 + back + cabin / 2], 0, 0, 0),
    )
    # Few triangles (hundreds of cars are in view): one block for the wheels, one strip for the
    # headlights and one for the tail lights.
    s.box([width + 0.2, 0.9, length - 1.6], C.metalDark)
    lights.box([width * 0.8, 0.5, 0.2], L.window, Placement([0, 0.9, length / 2 + 0.1], 0, 0, 0))
    lights.box([width * 0.8, 0.5, 0.2], L.red, Placement([0, 0.9, z0 - 0.1], 0, 0, 0))
    # The headlight beam on the road ahead, and a red glow behind: flat quads facing up.
    ground(lights, [width * 0.9, BEAM], length / 2 + BEAM / 2 + 0.3, BEAM_LIGHT)
    ground(lights, [width * 0.7, 1], z0 - 0.8, L.pinkDim)
    return PropGeometry(s.geometry, lights.geometry)
