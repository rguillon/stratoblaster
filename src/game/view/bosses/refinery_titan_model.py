"""P07-R05, P16-R06: the Refinery Titan, World 1's 1-4 final boss Model space: logical pixels, nose
+Z (down the screen), Y up
towards the camera. A bloated industrial beetle: a huge shelled body plumbed with grafted pipes,
limbs cradling two glowing fuel bladders, smoking chimneys of flesh on its back, a fleshy apron in
front carrying the two rotary turrets.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.final_bosses import REFINERY_TITAN  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.refinery_titan_parts import (  # noqa: E402
    TITAN_DECK,
    TITAN_NEON,
    draw_missile_battery,
    draw_rotary,
    draw_tank,
    draw_turret,
)
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    hide,
    mantle,
    polygon,
    rib_cage,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    organ,
    segmented_body,
)
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The apron of flesh the turrets stand on.
SPONSON = [
    [-50, 12],
    [-50, 32],
    [-42, 40],
    [42, 40],
    [50, 32],
    [50, 12],
    [42, 4],
    [-42, 4],
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
    """The body (P16-R06): a huge shelled abdomen, ribs, a spine vein, armour plates grafted on."""
    hide(
        p,
        {
            "tail": -62,
            "nose": 68,
            "width": 36,
            "bottom": -8,
            "top": 18,
            "segments": 6,
            "shell": [F.sinew, F.crimson],
            "belly": F.purple,
        },
    )
    mantle(p, SPONSON, [-4, TITAN_DECK["sponson"]], F.crimson, TITAN_NEON)
    p.neon.box([72, 1.2, 0.8], TITAN_NEON, Placement([0, -0.6, 40.2]))
    rib_cage(p, [-46, -36, 50], {"halfWidth": 33, "y": 0, "height": 15, "thickness": 1.5})
    spine(p, [0, 18.5, -55], [0, 18.5, 25], {"color": TITAN_NEON, "width": 1.8})
    for s in SIDES:
        for z in [-48, 8]:
            graft(p, polygon(6, 6, [1.2, 1.8]), [13, 14.6], [s * 20, 0, z], {"color": M.base})
        for z in [-40, -18]:
            vein_line(p, [s * 12, 17, z], [s * 34, 4, z + 6], [s * 3, 4, 0], 1.4, TITAN_NEON)
        gland(p, [s * 28, 8, 34], 2, TITAN_NEON)


def _draw_cradles(p: Any) -> None:
    """The limbs holding the fuel bladders (P16-R06): a jointed bone-and-sinew limb out to each, its
    claw curled round the bladder's outer side, lit along its top."""
    for s in SIDES:
        for z in [-30, -6]:
            elbow = [s * 86, 14, z]
            tentacle(p, [s * 30, 6, z], elbow, [0, 8, 0], [4, 3], F.sinew, 5)
            tentacle(p, elbow, [s * 92, -3, z + 4], [s * 2, 0, 0], [3, 0.6], F.bone, 4)
            vein_line(p, [s * 40, 13, z], [s * 84, 17, z], [0, 5, 0], 1, TITAN_NEON)
        p.neon.box([1.6, 0.6, 30], TITAN_NEON, Placement([s * 88, 13, -18]))


def _draw_pipes(parts: Any) -> None:
    """The fuel lines: grafted pipes across into the bladders, along the back, with couplings."""
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
        p.flesh.lathe(COLUMN, 7, F.crimson, Placement(at))
        for dy in [5, 10]:
            p.neon.ring(4, 1, 7, TITAN_NEON, Placement([at[0], at[1] + dy, at[2]]))
        p.vein.ring(2.6, 0.8, 7, TITAN_NEON, Placement([at[0], at[1] + 16.6, at[2]]))
    p.hull.cylinder(1.6, 84, 6, M.dark, Placement([-42, 13, -34], 0, 0, -QUARTER))


def _draw_bridge(p: Any) -> None:
    """The head over the core (P16-R06): a plated skull with clustered eyes, two smoking spiracles,
    the twin cannon grafted under its brow (the core's weapon), mandibles at its front."""
    organ(p.flesh, 17, 8, F.crimson, Placement([0, 12, 2], math.pi / 8), 0.38)
    graft(p, polygon(6, 11, [1, 1.3]), [23, 24.5], [0, 0, 0])
    eyes(p, [0, 22, 15], {"count": 4, "size": 1.2, "spacing": 3.4}, TITAN_NEON)
    for s in SIDES:
        p.flesh.cylinder(3.2, 8, 6, F.sinew, Placement([s * 9, 22, -14]), 2.6)
        p.neon.ring(2.7, 0.8, 6, TITAN_NEON, Placement([s * 9, 29.5, -14]))
        # The twin cannon's barrels, out of a mantlet on the head's front.
        p.hull.cylinder(1.8, 14, 6, M.dark, Placement([s * 4.5, 19, 20], 0, QUARTER))
        p.charge.cylinder(2.2, 1.8, 6, WHITE, Placement([s * 4.5, 19, 34], 0, QUARTER))
        p.muzzle([s * 4.5, 19, 35.8], None)
        tentacle(p, [s * 8, 4, 62], [s * 3, 3, 70], [s * 3, 0, 0], [2.4, 0.2], F.bone, 4)
    p.hull.box([15, 4, 7], M.base, Placement([0, 17, 21]), M.panel)
    eyes(p, [0, 6.5, 60], {"count": 2, "size": 1.2, "spacing": 6}, TITAN_NEON)
    barbs(p, [0, 17, -50], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.5]})


def _draw_core(p: Any) -> None:
    """The core: body, cradles, pipes, head, chimneys, and four reactors at the tail in sacs."""
    _draw_structure(p)
    _draw_cradles(p)
    _draw_pipes(p)
    _draw_bridge(p)
    _draw_columns(p)
    for s in SIDES:
        segmented_body(
            p.flesh,
            SegmentedBody(-62, -30, 2, 8, -3, 12),
            F.crimson,
            Placement([s * 11, 0, 0]),
        )
        reactor_sac(p, [s * 11, 4, -62], 6, TITAN_NEON)
        reactor_sac(p, [s * 48, -1, -42], 4, TITAN_NEON)


def build_refinery_titan(scene: Any) -> Any:
    """P07-R05, P16-R06: the Refinery Titan, a bloated industrial beetle (5.5 L) with orange veins:
    two big fuel bladders glowing in its limbs, two rotary turrets on its front apron, a missile
    brood on its back, and its plated head with a twin cannon over the core."""
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
            "turrets": {"turret-left": draw_rotary, "turret-right": draw_rotary},
        },
    )
