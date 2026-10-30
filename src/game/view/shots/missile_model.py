"""A small missile with a reactor flame (P03-R03)

The body lies along +Z like the ship models: a tube, a red nose and four fins.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.ship_look import PLAYER_SHIP_SCALE  # noqa: E402
from game.config.shot_look import SHOT_LOOK  # noqa: E402
from game.view.reactor_flame import build_reactor_flame  # noqa: E402
from render.babylon import (  # noqa: E402
    color3,
    create_box,
    create_cylinder,
    new_standard_material,
    new_transform_node,
)

LOOK = SHOT_LOOK.missile
SIDES = 6
NOSE_FRACTION = 0.22
FIN_LENGTH_FRACTION = 0.25
FIN_THICKNESS = 0.03


def _tube_options(height: float, diameter: float) -> Any:
    """Options of the missile's tube (a cylinder of one diameter)."""
    __pragma__("js", "{}", "return {height: height, diameter: diameter, tessellation: SIDES};")
    return None


def _nose_options(height: float, diameter_bottom: float) -> Any:
    """Options of the missile's nose (a cone tapering to a point)."""
    __pragma__(
        "js",
        "{}",
        "return {height: height, diameterTop: 0, "
        + "diameterBottom: diameter_bottom, tessellation: SIDES};",
    )
    return None


def _box_options(width: float, height: float, depth: float) -> Any:
    """Options of a fin (a flat box)."""
    __pragma__("js", "{}", "return {width: width, height: height, depth: depth};")
    return None


def _flame_options(nozzle_z: float, flame: Any) -> Any:
    """The flame's options: its nozzle position, then the look's own values (as `{ ...flame }`)."""
    __pragma__("js", "{}", "return Object.assign({nozzleZ: nozzle_z}, flame);")
    return None


def materials(scene: Any) -> tuple[Any, Any]:
    """The body's material and the tip's material, in that order."""
    body = new_standard_material("missile-body", scene)
    body.diffuseColor = color3(LOOK.body[0], LOOK.body[1], LOOK.body[2])
    body.specularColor = color3(0.6, 0.6, 0.6)
    tip = new_standard_material("missile-tip", scene)
    tip.diffuseColor = color3(LOOK.tip[0], LOOK.tip[1], LOOK.tip[2])
    tip.emissiveColor = color3(LOOK.tip[0], LOOK.tip[1], LOOK.tip[2]).scale(0.5)
    return body, tip


def build_body(name: str, scene: Any, parent: Any) -> None:
    """Builds the missile body (along +Z, like the ship models): tube, red nose, four fins."""
    body_mat, tip_mat = materials(scene)
    nose_length = LOOK.length * NOSE_FRACTION
    tube_length = LOOK.length - nose_length
    tube = create_cylinder(name + "-tube", _tube_options(tube_length, LOOK.radius * 2), scene)
    tube.rotation.x = math.pi / 2
    tube.position.z = -nose_length / 2
    nose = create_cylinder(name + "-nose", _nose_options(nose_length, LOOK.radius * 2), scene)
    nose.rotation.x = math.pi / 2
    nose.position.z = LOOK.length / 2 - nose_length / 2
    tube.material = body_mat
    nose.material = tip_mat
    fin_length = LOOK.length * FIN_LENGTH_FRACTION
    fins = []
    for i, angle in enumerate([0, math.pi / 2]):
        fin = create_box(
            name + "-fin-" + str(i),
            _box_options(LOOK.finSpan * 2, FIN_THICKNESS, fin_length),
            scene,
        )
        fin.rotation.z = angle
        fin.position.z = -LOOK.length / 2 + fin_length / 2
        fin.material = body_mat
        fins.append(fin)
    for mesh in [tube, nose]:
        mesh.parent = parent
        mesh.isPickable = False
    for mesh in fins:
        mesh.parent = parent
        mesh.isPickable = False


def build_missile(name: str, scene: Any) -> Any:
    """A small missile with a reactor flame, seen from above on the playfield: the returned pivot
    lies in the XY plane and points to +Y; turn it about Z to follow the heading (P03-R03).
    """
    pivot = new_transform_node(name, scene)
    model = new_transform_node(name + "-model", scene)
    model.parent = pivot
    # Model +Z (nose) -> playfield +Y; model +Y (top) -> -Z, towards the camera.
    model.rotation.x = -math.pi / 2
    model.scaling.setAll(PLAYER_SHIP_SCALE)
    build_body(name, scene, model)
    build_reactor_flame(name + "-flame", _flame_options(-LOOK.length / 2, LOOK.flame), model)
    return pivot
