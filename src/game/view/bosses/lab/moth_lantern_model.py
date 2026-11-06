# Copyright (c) 2026 Renaud Guillon
"""MB-MOTH-LANTERN-01 to MB-MOTH-LANTERN-05: the Moth Lantern, the Lab's L-3 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A huge moth: a furry head with great glowing
compound eyes and feathered antennae, a broad furry thorax, the root of its abdomen; its wings
(`moth_lantern_wings`) are moving pieces of their own, its lantern abdomen and its eye-spot guns
its parts.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.moth_lantern import EYE_HEIGHT, MOTH_LANTERN, ROTOR_AT
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.moth_lantern_wings import moth_wings
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    graft,
    hide,
    polygon,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import SegmentedBody, carapace, organ, segmented_body, tendril
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["moth-lantern"]

# The thorax along Z (model): one broad, swollen segment, from the abdomen's root to the head.
THORAX = {"tail": -12, "nose": 28, "width": 14, "bottom": -2, "top": 13}
# The head, in front of it.
HEAD = {"tail": 25, "nose": 46, "width": 9, "bottom": -1, "top": 9}
# The lantern abdomen (the part, MB-MOTH-LANTERN-03), along Z from its root to its glowing tip.
LANTERN_Z = [-20, -66]
LANTERN_WIDTH = 11.5
LANTERN_Y = [-1, 12.6]


def _draw_head(p: Any) -> None:
    """Draw its head: a furry dome, great glowing compound eyes, feathered antennae, front legs."""
    hide(
        p,
        {
            "tail": HEAD["tail"],
            "nose": HEAD["nose"],
            "width": HEAD["width"],
            "bottom": HEAD["bottom"],
            "top": HEAD["top"],
            "segments": 1,
            "shell": [F.slate, F.graphite],
            "belly": F.graphite,
        },
    )
    for s in SIDES:
        organ(p.vein, 3.6, 7, N, Placement([s * 7.2, 1.5, 38]), 0.9)
        # A feathered antenna: a bone shaft curving out and forward, plumes along it.
        root = [s * 3, 8, 42]
        tip = [s * 19, 9.5, 64]
        tentacle(p, root, tip, [s * 4, 2, 0], [0.9, 0.3], F.bone, 4)
        for k in range(1, 5):
            t = k / 5
            q = 4 * t * (1 - t)
            at = [
                root[0] + (tip[0] - root[0]) * t + s * 4 * q,
                root[1] + (tip[1] - root[1]) * t + 2 * q,
                root[2] + (tip[2] - root[2]) * t,
            ]
            length = 4.5 * (1 - abs(t - 0.45))
            for side in [-1, 1]:
                end = [at[0] + side * length * 0.8, at[1] - 0.4, at[2] - length * 0.6]
                tendril(p.flesh, [at, end], [0.5, 0], 3, F.sinew)
        p.neon.box([1, 1, 1], N, Placement([tip[0], tip[1] - 0.5, tip[2]]))
        # Its forelegs, folded under the head.
        tentacle(p, [s * 7, 0, 30], [s * 13, 1, 40], [s * 2, 1, 0], [1.2, 0.6], F.sinew, 4)
        tentacle(p, [s * 13, 1, 40], [s * 10, -1, 47], [0, 0, 0], [0.6, 0.2], F.bone, 3)
    vein_line(p, [0, 9, 30], [0, 8.5, 44], [0, 0.6, 0], 0.9, N)


def _draw_thorax(p: Any) -> None:
    """Draw its thorax: a broad furry carapace, a fur collar, a glowing spine, grafted plates."""
    hide(
        p,
        {
            "tail": THORAX["tail"],
            "nose": THORAX["nose"],
            "width": THORAX["width"],
            "bottom": THORAX["bottom"],
            "top": THORAX["top"],
            "segments": 1,
            "shell": [F.slate, F.membrane],
            "belly": F.graphite,
        },
    )
    # The fur collar behind the head and tufts down its back.
    barbs(p, [0, 8, 26], {"count": 7, "spacing": 2.6, "size": 4, "dir": [0, 0.6, -0.8]}, F.sinew)
    for z in [16, 4]:
        barbs(p, [0, 11.5, z], {"count": 4, "spacing": 5, "size": 3, "dir": [0, 0.5, -0.9]})
    spine(p, [0, 12.6, 22], [0, 12.6, 18], {"color": N, "width": 1.2, "bow": 0.4})
    spine(p, [0, 12.6, 6], [0, 11.4, -8], {"color": N, "width": 1.2, "bow": 0.6})
    for s in SIDES:
        # Grafted plates on its shoulders, and its middle and hind legs folded under it.
        graft(p, polygon(5, 3.6, [1.3, 1]), [9.4, 10.6], [s * 7, 0, 18], {"yaw": s * 0.4})
        vein_line(p, [s * 4, 12.4, 10], [s * 11, 7, 2], [s * 1, 1.5, 0], 0.9, N)
        for z in [8, -2]:
            knee = [s * 17, 2, z - 4]
            tentacle(p, [s * 10, 0, z], knee, [0, 1, 0], [1.2, 0.8], F.sinew, 4)
            tentacle(p, knee, [s * 18, -1.5, z - 12], [0, 0, 0], [0.8, 0.2], F.bone, 3)


def _draw_abdomen_root(p: Any) -> None:
    """Draw the root of its abdomen behind the thorax, a grafted coupling the lantern hangs on."""
    segmented_body(p.flesh, SegmentedBody(-26, -6, 2, 8.5, -1, 9, 0.25), F.slate)
    p.hull.cylinder(7.4, 2.2, 10, M.panel, Placement([0, 4, -18], 0, math.pi / 2))
    p.neon.ring(7.6, 0.5, 10, N, Placement([0, 4, -17.4], 0, math.pi / 2))
    # The stalk the spore mortar stands on, inside the lantern (its stump stays on it).
    segmented_body(p.flesh, SegmentedBody(-40, -24, 1, 6, 0, 8, 0.2), F.graphite)
    p.hull.cylinder(3.2, 7.4, 8, M.base, Placement([0, 5.8, -34]), 2.6)


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over its thorax rotor (BOSS-58): an armoured cap, a seam of light round it.

    It bursts off as the rotor comes into use.
    """
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(polygon(8, 6.2), [12.2, 12.2, 13.8], [0, 0.8], M.panel, Placement(at))
    p.hull.bevel_slab(polygon(8, 4.2), [13.8, 13.8, 15], [0, 0.6], M.base, Placement(at))
    p.neon.ring(6, 0.25, 8, N, Placement([at[0], 13.4, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.8, 1.2, 16, M.base, Placement([at[0], 12.4, at[2]]))
    p.neon.ring(5.8, 0.3, 16, N, Placement([at[0], 13.4, at[2]]))


def _eye_gun(p: Any, at: Vec3) -> None:
    """Add an eye-spot gun (MB-MOTH-LANTERN-03): a swollen eye on the forewing.

    A dark bulb on the wing's eye-spot ring, a glowing iris round its turret (the pupil).
    """
    organ(p.flesh, 7.6, 10, F.slate, Placement([at[0], 8, at[2]], math.pi / 10), 0.26)
    organ(p.vein, 5.6, 12, N, Placement([at[0], EYE_HEIGHT - 1.4, at[2]]), 0.14)
    p.hull.cylinder(4.2, 1.2, 10, M.base, Placement([at[0], EYE_HEIGHT - 1, at[2]]))


def _lantern(p: Any, _at: Vec3) -> None:
    """Add the lantern (MB-MOTH-LANTERN-03): its long glowing abdomen, the spore mortar on it.

    A glowing body under dark, pinched carapace plates (the light shows between them and along
    its flanks), grafted metal bands, and a great glowing bulb at its tip.
    """
    z0 = LANTERN_Z[0]
    z1 = LANTERN_Z[1]
    y0 = LANTERN_Y[0]
    y1 = LANTERN_Y[1]
    segmented_body(p.vein, SegmentedBody(z1 + 2, z0, 4, LANTERN_WIDTH, y0, y1 - 3, 0.2), N)
    carapace(
        p.flesh,
        SegmentedBody(z1, z0, 4, LANTERN_WIDTH * 0.95, (y0 + y1) / 2 - 1, y1, 0.55),
        [F.slate, F.graphite],
    )
    for z in [-31.5, -43, -54.5]:
        p.hull.cylinder(
            LANTERN_WIDTH * 0.62, 1.6, 10, M.panel, Placement([0, 5, z], 0, math.pi / 2)
        )
    organ(p.vein, 6.5, 8, N, Placement([0, 1, z1 - 1], 0, math.pi / 2), 0.8)
    barbs(p, [0, 4, z1 - 1], {"count": 2, "spacing": 6, "size": 5, "dir": [0, 0.2, -1]})
    # The spore mortar's seat on its back (its mount, BOSS-58).
    graft(p, polygon(6, 5.5), [y1 - 0.6, y1 + 0.6], [0, 0, -34], {"color": M.base})


def build_moth_lantern(scene: Any) -> Any:
    """MB-MOTH-LANTERN-01, MB-MOTH-LANTERN-04: the Moth Lantern.

    A huge moth with lilac veins (shown green), its wings folded back at rest, an eye-spot gun on
    each forewing and a long glowing lantern abdomen behind it.
    """

    def core(p: Any) -> None:
        _draw_head(p)
        _draw_thorax(p)
        _draw_abdomen_root(p)

    armour = moth_wings()
    armour["rotor-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return build_boss_model(
        MOTH_LANTERN,
        scene,
        N,
        {
            "core": core,
            "parts": {"eye-left": _eye_gun, "eye-right": _eye_gun, "lantern": _lantern},
            "armour": armour,
        },
    )
