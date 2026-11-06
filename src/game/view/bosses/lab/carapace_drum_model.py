# Copyright (c) 2026 Renaud Guillon
"""MB-CARAPACE-DRUM-01 to MB-CARAPACE-DRUM-05, Lab L-1: the Carapace Drum.

A squat barnacle drum with aqua veins: a shelled drum under a domed lid round its operculum, on a
thick turning rim of barnacle plates carrying three barnacle rotor pods. Logical pixels, nose +Z,
Y up (towards the camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.carapace_drum import (
    CARAPACE_DRUM,
    DRUM_TOP,
    HUB_TOP,
    LID_HOLE,
    LID_RADIUS,
    MOUTH_HEIGHT,
    POD_ROTOR_HEIGHT,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    gland,
    graft,
    polygon,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES, around
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


AQUA = BOSS_LOOK.neon["carapace-drum"]

# The drum (a lathe profile, radius and height): a squat shelled cylinder, its top flat under the
# lid, its shoulder sloping out to its belly, sunk into the turning rim.
DRUM = [
    [0, -4],
    [25, -4],
    [30, -1.5],
    [31.5, 3],
    [30, 7],
    [26.5, DRUM_TOP],
    [0, DRUM_TOP],
]
# The operculum: the hub at the lid's middle, standing from the drum's top, its crown rotor's seat.
HUB = [
    [LID_HOLE - 0.4, DRUM_TOP - 0.5],
    [LID_HOLE - 0.6, HUB_TOP - 1.5],
    [LID_HOLE - 1.4, HUB_TOP],
    [0, HUB_TOP],
]
# The lid (the armour it sheds, MB-CARAPACE-DRUM-05): a domed shell of revolution round the hub,
# from its rim sunk into the drum's top up to the hub (a closed lathe profile).
LID = [
    [LID_RADIUS, DRUM_TOP - 0.6],
    [LID_RADIUS + 0.4, DRUM_TOP + 1.2],
    [20, DRUM_TOP + 3.6],
    [15.5, DRUM_TOP + 6.2],
    [10.5, HUB_TOP - 1.4],
    [LID_HOLE + 0.2, HUB_TOP - 0.6],
    [LID_HOLE + 0.2, HUB_TOP - 2],
    [10.5, HUB_TOP - 2.8],
    [15.5, DRUM_TOP + 4.6],
    [20, DRUM_TOP + 2.2],
    [LID_RADIUS, DRUM_TOP - 0.6],
]
# The turning rim (a closed lathe profile): a thick ring of barnacle plates round the drum.
RIM = [
    [32, -3],
    [45, -3],
    [48, 0.5],
    [46.5, 4.5],
    [42, 5.6],
    [34.5, 5.2],
    [32, 3.5],
    [32, -3],
]
RIM_TOP = 5.4
# A pod's barnacle cone (a lathe profile, open at its crater): its wall plates rise to the crater
# its rotor sits in (its mount, BOSS-58).
CONE = [
    [10.5, RIM_TOP - 1.5],
    [10, RIM_TOP + 1.2],
    [7.4, RIM_TOP + 3.6],
    [5.2, POD_ROTOR_HEIGHT - 0.2],
    [4.2, POD_ROTOR_HEIGHT + 0.1],
    [3.4, POD_ROTOR_HEIGHT - 0.6],
]
# One of a cone's wall plates, around its foot: a tall wedge leaning in.
WALL_PLATE = [[-3.2, 0], [3.2, 0], [1.8, 5.6], [-1.8, 5.6]]


def _draw_core(p: Any) -> None:
    """Draw the core (MB-CARAPACE-DRUM-02): a squat shelled drum, the operculum on its middle.

    The drum's side clad in leaning shell plates over dark flesh, a plate on its front shoulder
    seating the mouth turret, a cluster of eyes under it, reactor sacs at its tail and aqua veins
    over its shoulder.
    """
    p.flesh.lathe(DRUM, 14, F.sinew, Placement(None, math.pi / 14))
    p.flesh.lathe(HUB, 8, F.slate, Placement(None, math.pi / 8))
    p.neon.ring(LID_HOLE - 0.5, 0.6, 8, AQUA, Placement([0, HUB_TOP - 3, 0], math.pi / 8))
    # Shell plates leaning on the drum's shoulder, dark flesh showing between them (BOSS-49).
    for a in around(12):
        x = math.sin(a)
        z = math.cos(a)
        if z > 0.9:
            continue
        p.flesh.bevel_slab(
            [[-4.4, -1.6], [4.4, -1.6], [3.4, 1.6], [-3.4, 1.6]],
            [0, 0.6, 1.6],
            [0.3, 0.5],
            F.bone,
            Placement([x * 29.6, 3.2, z * 29.6], a, 1.2),
            F.slate,
        )
    # The mouth: a plate grafted on the front shoulder, the turret on it (BOSS-58), eyes below.
    graft(p, polygon(6, 5.6, [1.2, 0.8]), [MOUTH_HEIGHT - 2, MOUTH_HEIGHT], [0, 0, 26])
    eyes(p, [0, 5.5, 30.6], {"count": 3, "size": 1, "spacing": 3.4}, AQUA)
    for s in SIDES:
        reactor_sac(p, [s * 9, 2.5, -30], 2.4, AQUA)
        vein_line(
            p, [s * 8, DRUM_TOP + 0.2, 24], [s * 24, DRUM_TOP - 0.5, 12], [0, 1, 0], 0.8, AQUA
        )
        gland(p, [s * 27, 7.2, -10], 1.4, AQUA)


def _draw_lid(p: Any) -> None:
    """Draw the lid (MB-CARAPACE-DRUM-05): the armour it sheds at its transformation.

    A domed shell round the operculum, bone ribs radiating down it, riveted plates between them and
    an aqua vein down each side.
    """
    p.flesh.lathe(LID, 12, F.slate, Placement(None, math.pi / 12), False)
    for a in around(6):
        x = math.sin(a + math.pi / 6)
        z = math.cos(a + math.pi / 6)
        tentacle(
            p,
            [x * 8, HUB_TOP - 0.6, z * 8],
            [x * 22.6, DRUM_TOP + 1.4, z * 22.6],
            [0, 2.2, 0],
            [1.1, 0.7],
            F.bone,
            3,
        )
        graft(
            p,
            polygon(4, 3, [0.9, 1.5]),
            [DRUM_TOP + 3.2, DRUM_TOP + 4.4],
            [math.sin(a) * 17, 0, math.cos(a) * 17],
            {"yaw": a},
        )
    for s in SIDES:
        vein_line(p, [s * 5, HUB_TOP, 6], [s * 15, DRUM_TOP + 4.8, 15], [0, 1.5, 0], 0.8, AQUA)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the crown rotor (BOSS-58): an armoured cap, a seam of light round it.

    It bursts off as the rotor comes into use, in its last stage.
    """
    graft(p, polygon(8, 6.6), [HUB_TOP - 0.2, HUB_TOP + 1.4], [0, 0, 0], {"color": M.panel})
    graft(p, polygon(8, 4.2), [HUB_TOP + 1.4, HUB_TOP + 2.8], [0, 0, 0], {"color": M.base})
    p.neon.ring(6.4, 0.25, 8, AQUA, Placement([0, HUB_TOP + 1.1, 0], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    p.hull.ring(6.2, 0.9, 16, M.base, Placement([0, HUB_TOP - 0.5, 0]))
    p.neon.ring(6.2, 0.3, 16, AQUA, Placement([0, HUB_TOP + 0.3, 0]))


def _draw_rim(p: Any) -> None:
    """Draw the turning rim (MB-CARAPACE-DRUM-02): a thick ring of barnacle plates round the drum.

    Riveted shell plates on its top between the pods, bone spurs out of its edge, an aqua vein
    along its outer lip.
    """
    p.flesh.lathe(RIM, 18, F.graphite, None, False)
    p.neon.ring(47.6, 0.8, 18, AQUA, Placement([0, 0.4, 0]))
    for k in range(9):
        if k % 3 == 0:
            continue
        a = (k * 2 * math.pi) / 9
        x = math.sin(a)
        z = math.cos(a)
        graft(
            p,
            polygon(5, 4.4, [1.3, 0.8]),
            [RIM_TOP - 0.6, RIM_TOP + 0.6],
            [x * 39.5, 0, z * 39.5],
            {"yaw": a},
        )
        tentacle(p, [x * 46, 1, z * 46], [x * 51, 2.2, z * 51], [0, 0, 0], [1.2, 0], F.bone, 3)
    for a in around(3):
        mid = a + math.pi / 3
        vein_line(
            p,
            [math.sin(mid - 0.5) * 41, RIM_TOP + 0.4, math.cos(mid - 0.5) * 41],
            [math.sin(mid + 0.5) * 41, RIM_TOP + 0.4, math.cos(mid + 0.5) * 41],
            [0, 0.6, 0],
            0.6,
            AQUA,
        )


def _pod(p: Any, at: Vec3) -> None:
    """Add a barnacle rotor pod on the rim (MB-CARAPACE-DRUM-03).

    A cone of leaning wall plates, its crater holding its rotor (its mount, BOSS-58), a glowing
    vein ring round its foot and spawn sacs clinging to its outer side.
    """
    yaw = math.atan2(at[0], at[2])
    p.flesh.lathe(CONE, 9, F.slate, Placement([at[0], 0, at[2]], math.pi / 9), False)
    p.vein.ring(10.2, 0.7, 9, AQUA, Placement([at[0], RIM_TOP - 0.4, at[2]], math.pi / 9))
    for k in range(6):
        a = yaw + (k * math.pi) / 3
        foot = [at[0] + math.sin(a) * 7.6, RIM_TOP - 0.4, at[2] + math.cos(a) * 7.6]
        p.flesh.bevel_slab(
            WALL_PLATE,
            [-0.3, 0, 0.9],
            [0.2, 0.3],
            F.bone,
            Placement(foot, a + math.pi, -0.95),
            F.sinew,
        )
    out = [math.sin(yaw), 0, math.cos(yaw)]
    organ(
        p.flesh,
        2.6,
        6,
        F.sinew,
        Placement([at[0] + out[0] * 9, RIM_TOP - 1, at[2] + out[2] * 9]),
        0.7,
    )


def build_carapace_drum(scene: Any) -> Any:
    """MB-CARAPACE-DRUM-01, MB-CARAPACE-DRUM-04: the Carapace Drum, with aqua veins.

    A shelled barnacle drum under a domed lid, on a thick turning rim carrying three barnacle
    rotor pods.
    """
    return build_boss_model(
        CARAPACE_DRUM,
        scene,
        AQUA,
        {
            "core": _draw_core,
            "ring": _draw_rim,
            "parts": {"pod-1": _pod, "pod-2": _pod, "pod-3": _pod},
            "armour": {
                "lid": {"whole": _draw_lid},
                "crown-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
