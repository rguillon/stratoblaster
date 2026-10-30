"""The reactors and rotors of the enemy models (phase 5 review)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_materials import (  # noqa: E402
    enemy_color,
    flame_materials,
    mesh_of,
)
from game.view.reactor_flame import build_reactor_flame  # noqa: E402, E501
from render.babylon import (  # noqa: E402
    new_transform_node,
    node_name,
)
from render.geometry.solids import SolidBuilder  # noqa: E402
from render.model_animation import add_model_animation  # noqa: E402


class Reactor:
    """A reactor or a rotor: where, and how big."""

    def __init__(self, at: Vec3, radius: float) -> None:
        self.at = at
        self.radius = radius


def spin_animation(node: Any, spin_rad_per_sec: float) -> Any:
    """Turns the node around +Y as time passes."""

    def animate(dt: float) -> None:
        node.rotation.y = node.rotation.y + spin_rad_per_sec * dt

    return animate


def add_rotors(name: str, rotors: list[Reactor], material: Any, root: Any) -> None:
    """The rotors' blades and hubs, each on a node spun by a model animation."""
    look = ENEMY_LOOK.rotor
    scene = root.getScene()
    blade = [(-0.12, 0.3), (0.12, 0.3), (0.22, 0.92), (-0.08, 0.95)]
    for i, rotor in enumerate(rotors):
        x = rotor.at[0]
        y = rotor.at[1]
        z = rotor.at[2]
        radius = rotor.radius
        parts = SolidBuilder()
        for k in range(look.blades):
            outline = [[u * radius, v * radius] for (u, v) in blade]
            parts.slab(
                outline,
                [-0.08, 0.08],
                ENEMY_LOOK.hull.panel,
                Placement(None, (2 * math.pi * k) / look.blades),
            )
        parts.cylinder(
            radius * look.hub,
            radius * 0.3,
            4,
            ENEMY_LOOK.hull.dark,
            Placement([0, -radius * 0.15, 0]),
        )
        node = new_transform_node(name + "-rotor-" + str(i), scene)
        node.position.set(x, y, z)
        node.parent = root
        mesh_of(node_name(node) + "-blades", parts.geometry, material, scene).parent = node
        add_model_animation(node, spin_animation(node, look.spinRadPerSec))


def add_reactors(name: str, reactors: list[Reactor], parts: Any, root: Any) -> None:
    """Nozzles in the hull, cores in the neon, and an animated flame per reactor under `root`."""
    look = ENEMY_LOOK.reactor
    color = enemy_color(look.color)
    behind = -math.pi / 2
    for i, reactor in enumerate(reactors):
        x = reactor.at[0]
        y = reactor.at[1]
        z = reactor.at[2]
        radius = reactor.radius
        depth = radius * look.depth
        # Pitched back, a band standing on `at` runs towards -Z: an open nozzle (no caps), with a
        # flat neon core across its mouth, facing back.
        place = Placement([x, y, z + depth], 0, behind)
        parts.hull.ring(radius, depth, look.sides, ENEMY_LOOK.hull.dark, place)
        core = []
        for k in range(look.sides):
            # Counter-clockwise seen from behind (-Z), so the face points back, out of the nozzle.
            a = (-2 * math.pi * k) / look.sides
            core.append(
                [
                    x + math.cos(a) * radius * look.core,
                    y + math.sin(a) * radius * look.core,
                    z,
                ]
            )
        # Folded with the rest of the neon (`inEnemyFamily`): the colour of the flame.
        parts.neon.face(core, look.color)
        node = new_transform_node(name + "-reactor-" + str(i), root.getScene())
        node.position.set(x, y, 0)
        node.parent = root
        options = {
            "nozzleZ": z - 0.05,
            "length": radius * look.flameLength,
            "diameter": radius * 2 * look.core * look.flameWidth,
            "puffDiameter": radius * look.puffSize,
            "sides": look.flameSides,
            "light": {"puffs": look.puffs},
        }
        build_reactor_flame(
            node_name(node),
            options,
            node,
            flame_materials(root.getScene(), color),
        )
