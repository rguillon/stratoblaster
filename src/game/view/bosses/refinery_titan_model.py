# Copyright (c) 2026 Renaud Guillon
"""FB-REFINERY-TITAN-01 to FB-REFINERY-TITAN-04: the Refinery Titan, World 1's 1-4 final boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A bloated
industrial beetle: a huge shelled body plumbed with grafted pipes, limbs cradling two glowing fuel
bladders, smoking chimneys of flesh on its back, a fleshy apron in front carrying the two rotary
turrets' bases (their rotors, the missile brood's ports and the core's turret and rotor are its gun
mounts, drawn by `build_boss_model`, BOSS-58). Its back and spine plating are drawn as pieces of
their own (`refinery_titan_armour`, D-254).
"""

import math

from game.config.bosses.final_bosses import REFINERY_TITAN
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import sided
from game.view.bosses.refinery_titan_armour import (
    BOTTOM,
    MID,
    NOSE,
    SEGMENTS,
    TAIL,
    WIDTH,
    draw_rear_shell,
    titan_armour,
)
from game.view.bosses.refinery_titan_parts import (
    TITAN_DECK,
    TITAN_NEON,
    draw_missile_battery,
    draw_tank,
    draw_turret,
)
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    mantle,
    polygon,
    rib_cage,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import SegmentedBody, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


QUARTER = math.pi / 2

# The right lobe of the apron of flesh the turrets stand on, either side of the belly (the
# gatlings and orbs rise between the two lobes).
SPONSON = [
    [20, 40],
    [42, 40],
    [50, 32],
    [50, 12],
    [42, 4],
    [20, 4],
]
# A chimney of flesh (lathe profile, bottom to top).
COLUMN = [
    [5, 0],
    [4, 1.5],
    [3.4, 13],
    [4, 15],
    [2.5, 17],
]


def _draw_structure(p: Any) -> None:
    """Draw the body (FB-REFINERY-TITAN-02): a huge abdomen, its shell over the tail, ribs.

    A spine vein and armour plates grafted on; the rest of its shell is its armour.
    """
    segmented_body(
        p.flesh,
        SegmentedBody(TAIL, NOSE, SEGMENTS, WIDTH, BOTTOM, MID, 0.15),
        F.graphite,
    )
    draw_rear_shell(p)
    for s in SIDES:
        mantle(p, sided(SPONSON, s), [-4, TITAN_DECK["sponson"]], F.slate, TITAN_NEON)
        graft(p, polygon(6, 6, [1.2, 1.8]), [13, 14.6], [s * 20, 0, -48], {"color": M.base})
        vein_line(p, [s * 12, 17, -40], [s * 34, 4, -34], [s * 3, 4, 0], 1.4, TITAN_NEON)
        gland(p, [s * 28, 8, 34], 2, TITAN_NEON)
    p.neon.box([72, 1.2, 0.8], TITAN_NEON, Placement([0, -0.6, 40.2]))
    rib_cage(p, [-46, -36], {"halfWidth": 33, "y": 0, "height": 15, "thickness": 1.5})


def _draw_cradles(p: Any) -> None:
    """Draw the limbs holding the fuel bladders (FB-REFINERY-TITAN-02).

    A jointed bone-and-sinew limb out to each, its claw curled round the bladder's outer side, lit
    along its top.
    """
    for s in SIDES:
        for z in [-30, -6]:
            elbow = [s * 86, 14, z]
            tentacle(p, [s * 30, 6, z], elbow, [0, 8, 0], [4, 3], F.sinew, 5)
            tentacle(p, elbow, [s * 92, -3, z + 4], [s * 2, 0, 0], [3, 0.6], F.bone, 4)
            vein_line(p, [s * 40, 13, z], [s * 84, 17, z], [0, 5, 0], 1, TITAN_NEON)
        p.neon.box([1.6, 0.6, 30], TITAN_NEON, Placement([s * 88, 13, -18]))


def _draw_pipes(parts: Any) -> None:
    """Draw the fuel lines: grafted pipes, with couplings.

    The pipes run across into the bladders and along the back.
    """
    hull = parts.hull
    # Rolled a quarter turn, a cylinder runs along +X from where it stands.
    for z in [-10, -26]:
        hull.cylinder(2.2, 108, 6, M.panel, Placement([-54, 9, z], 0, 0, -QUARTER))
        for s in SIDES:
            hull.cylinder(3.1, 2.4, 6, M.dark, Placement([s * 44 - 1.2, 9, z], 0, 0, -QUARTER))


def _draw_columns(p: Any) -> None:
    """Two chimneys of flesh behind the body, ringed with neon, joined by a grafted pipe."""
    for s in SIDES:
        at = [s * 42, TITAN_DECK["beam"] - 0.5, -34]
        p.flesh.lathe(COLUMN, 7, F.slate, Placement(at))
        for dy in [5, 10]:
            p.neon.ring(4, 1, 7, TITAN_NEON, Placement([at[0], at[1] + dy, at[2]]))
        p.vein.ring(2.6, 0.8, 7, TITAN_NEON, Placement([at[0], at[1] + 16.6, at[2]]))
    p.hull.cylinder(1.6, 84, 6, M.dark, Placement([-42, 13, -34], 0, 0, -QUARTER))


def _draw_jaws(p: Any) -> None:
    """Draw the mandibles at its front and the barbs on its tail (FB-REFINERY-TITAN-02).

    The plated skull rides the back plating (`refinery_titan_armour`); the core's guns are its
    mounts on its rear shell (drawn by `build_boss_model`, BOSS-58).
    """
    for s in SIDES:
        tentacle(p, [s * 8, 4, 62], [s * 3, 3, 70], [s * 3, 0, 0], [2.4, 0.2], F.bone, 4)
    barbs(p, [0, 17, -50], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.5]})


def _draw_core(p: Any) -> None:
    """Draw the core: body, cradles, pipes, jaws and chimneys.

    Four reactors sit at the tail in sacs.
    """
    _draw_structure(p)
    _draw_cradles(p)
    _draw_pipes(p)
    _draw_jaws(p)
    _draw_columns(p)
    for s in SIDES:
        segmented_body(
            p.flesh,
            SegmentedBody(-62, -30, 2, 8, -3, 12),
            F.slate,
            Placement([s * 11, 0, 0]),
        )
        reactor_sac(p, [s * 11, 4, -62], 6, TITAN_NEON)
        reactor_sac(p, [s * 48, -1, -42], 4, TITAN_NEON)


def build_refinery_titan(scene: Any) -> Any:
    """Build the Refinery Titan (FB-REFINERY-TITAN-01, FB-REFINERY-TITAN-04).

    A bloated industrial beetle (5.5 L) with orange veins: two big fuel bladders glowing in its
    limbs, two rotary turrets on its front apron, a missile brood on its back, its plated head over
    the core, and the core's fan turret and rotor on its rear shell either side of the brood.
    """
    return build_boss_model(
        REFINERY_TITAN,
        scene,
        TITAN_NEON,
        {
            "core": _draw_core,
            "parts": {
                "tank-left": draw_tank,
                "tank-right": draw_tank,
                "turret-left": draw_turret,
                "turret-right": draw_turret,
                "missile-battery": draw_missile_battery,
            },
            "armour": titan_armour(),
        },
    )
