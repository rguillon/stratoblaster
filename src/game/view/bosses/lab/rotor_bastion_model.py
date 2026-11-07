# Copyright (c) 2026 Renaud Guillon
"""MB-ROTOR-BASTION-01 to MB-ROTOR-BASTION-05: the Rotor Bastion, the Lab's L-13 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A flying tower held up by four ducted rotors on
outrigger arms: a square armoured tower with a crenellated roof, corner pylons the arms hang from,
an armoured prow on its front and a gun balcony on its back. Its arms, ducts and blades are in
`rotor_bastion_rotors`; its front arms fold back as it transforms and its prow's armour bursts off.
"""

import math

from game.config.bosses.lab.rotor_bastion import (
    ARM_HIGH,
    BALCONY_BACK,
    BALCONY_GUN_AT,
    BALCONY_TOP,
    CROWN_AT,
    CROWN_GUN_HEIGHT,
    HUB_RADIUS,
    HUB_TOP,
    POD_GUN_HEIGHT,
    PROW,
    PROW_TOP,
    ROTOR_AT,
    ROTOR_BASTION,
    TOWER_HALF,
    TOWER_ROOF,
    TOWER_WALL,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, grille, plate, rect
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.rotor_bastion_rotors import (
    N,
    blade_triangles,
    build_blade_rig,
    draw_rear_rotors,
    model_outline,
    pt,
    rotor_arms,
)
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


CORNERS = [[1, 1], [1, -1], [-1, 1], [-1, -1]]


def _chamfered(half: float, cut: float) -> list[Any]:
    """Return a square `half` px either side of the centre, its corners cut `cut` px (config)."""
    return [
        [-half + cut, -half],
        [half - cut, -half],
        [half, -half + cut],
        [half, half - cut],
        [half - cut, half],
        [-half + cut, half],
        [-half, half - cut],
        [-half, -half + cut],
    ]


def _m(x: float, y: float) -> list[Any]:
    """Return the config point `(x, y)` as a model `[x, z]`."""
    return [-x, -y]


def _loop(outline: list[Any]) -> list[Any]:
    """Return a config outline as a closed model polyline (for `edge_strips`)."""
    points = [_m(q[0], q[1]) for q in outline]
    points.append(points[0])
    return points


def _draw_tower(p: Any) -> None:
    """Draw the tower (MB-ROTOR-BASTION-02): a flared skirt, plated walls, a crenellated roof.

    A lit line round the skirt and the roof's edge, window slits on its walls, plates and a vent
    grille on its roof, and the pylons at its corners the arms hang from.
    """
    h = TOWER_HALF
    p.hull.bevel_slab(
        model_outline(_chamfered(h + 2.5, 4)), [0, 5, 6.2], [1.5, 1], SHADE["dark"], None
    )
    edge_strips(p.neon, _loop(_chamfered(h + 1.6, 4)), 0.5, [6.2, 6.32], N)
    p.hull.bevel_slab(
        model_outline(_chamfered(h, 3)), [5.5, TOWER_WALL - 1, TOWER_WALL], [0, 0.8], SHADE["panel"]
    )
    # The roof: a dark deck sunk in a parapet, merlons round it.
    p.hull.slab(
        model_outline(_chamfered(h - 2, 2.4)), [TOWER_WALL - 0.4, TOWER_WALL + 0.3], SHADE["dark"]
    )
    for s in [-1, 1]:
        for k in range(4):
            t = -h + 4.5 + k * (2 * h - 9) / 3
            for q in [[s * (h - 1), t], [t, s * (h - 1)]]:
                p.hull.box(
                    [2.4, TOWER_ROOF - TOWER_WALL + 0.6, 2.4],
                    SHADE["mid"],
                    Placement(pt(q[0], q[1], TOWER_WALL - 0.3)),
                    SHADE["light"],
                )
    edge_strips(
        p.neon, _loop(_chamfered(h - 2.6, 2.2)), 0.45, [TOWER_WALL + 0.32, TOWER_WALL + 0.44], N
    )
    # Window slits on its walls, lit.
    for s in [-1, 1]:
        for k in [-1, 0, 1]:
            x = k * 7
            p.neon.box([2.2, 3.2, 0.3], N, Placement(pt(x, s * (h + 0.05), 12)))
            p.neon.box([0.3, 3.2, 2.2], N, Placement(pt(s * (h + 0.05), x, 12)))
    # The roof: plates on its flanks, a vent grille between the crown and the rotor hatch.
    for s in [-1, 1]:
        plate(p.hull, rect(_m(s * 9, 2), [4.6, 18]), TOWER_WALL + 0.3, SHADE["light"])
    grille(p.hull, _m(0, 3.4), [10, 3], [3, TOWER_WALL + 0.4])
    # The crown's seat and the collar the roof rotor rises out of (its hatch is drawn apart).
    p.hull.cylinder(
        7, 0.8, 8, SHADE["dark"], Placement(pt(CROWN_AT[0], CROWN_AT[1], TOWER_WALL), math.pi / 8)
    )
    p.hull.ring(5.2, 1, 12, SHADE["dark"], Placement(pt(ROTOR_AT[0], ROTOR_AT[1], TOWER_WALL)))
    # The corner pylons the arms hang from, a lit cap on each.
    for c in CORNERS:
        at = pt(c[0] * (h + 0.5), c[1] * (h + 0.5), 3)
        p.hull.cylinder(3.4, ARM_HIGH + 3, 8, SHADE["base"], Placement(at, math.pi / 8))
        p.neon.cylinder(1.3, 0.5, 6, N, Placement([at[0], ARM_HIGH + 6, at[2]]))


def _draw_balcony(p: Any) -> None:
    """Draw the gun balcony on the tower's back (the core's turret stands on it)."""
    deck = [[-9, TOWER_HALF - 1], [9, TOWER_HALF - 1], [7, BALCONY_BACK], [-7, BALCONY_BACK]]
    p.hull.bevel_slab(
        model_outline(deck),
        [3, BALCONY_TOP - 1, BALCONY_TOP],
        [1.4, 0.8],
        SHADE["base"],
        None,
        SHADE["mid"],
    )
    edge_strips(
        p.neon,
        [_m(-6.6, BALCONY_BACK + 0.1), _m(6.6, BALCONY_BACK + 0.1)],
        0.5,
        [BALCONY_TOP - 2.4, BALCONY_TOP - 1.6],
        N,
    )
    seat = pt(BALCONY_GUN_AT[0], BALCONY_GUN_AT[1], BALCONY_TOP - 0.4)
    p.hull.cylinder(5.4, 0.6, 8, SHADE["dark"], Placement(seat, math.pi / 8))
    # Struts down from its sides to the skirt.
    for s in [-1, 1]:
        p.hull.box(
            [1.6, BALCONY_TOP - 4, 1.6], SHADE["dark"], Placement(pt(s * 7.6, BALCONY_BACK - 2, 3))
        )


def _draw_prow_floor(p: Any) -> None:
    """Draw the prow's keel under its armour: what holds its frame to the tower once it is shed."""
    keel = [[-4, -TOWER_HALF], [4, -TOWER_HALF], [3, -31], [-3, -31]]
    p.hull.slab(model_outline(keel), [0.6, 2.4], SHADE["dark"])


def _draw_prow(p: Any) -> None:
    """Draw the prow's armour (MB-ROTOR-BASTION-10): a plated wedge of a bow, a ram on its nose.

    Lit chevrons down its back and a lit line round its foot; it bursts off as it transforms.
    """
    p.hull.bevel_slab(
        model_outline(PROW),
        [2, PROW_TOP - 2.4, PROW_TOP],
        [0, 3.2],
        SHADE["base"],
        None,
        SHADE["panel"],
    )
    for s in [-1, 1]:
        side = [
            [s * 2.5, -16.5],
            [s * 11, -16.5],
            [s * 9.5, -26.5],
            [s * 4.8, -29.6],
            [s * 2.5, -29.6],
        ]
        plate(p.hull, model_outline(side), PROW_TOP, SHADE["light"], 0.6)
    for k in range(3):
        y = -19 - k * 4
        edge_strips(
            p.neon,
            [_m(-5 + k * 0.8, y + 2), _m(0, y), _m(5 - k * 0.8, y + 2)],
            0.5,
            [PROW_TOP + 0.6, PROW_TOP + 0.72],
            N,
        )
    # The ram: a low blade on its nose.
    p.hull.bevel_slab(
        model_outline([[-3, -31], [3, -31], [0, -37]]), [2.5, 6.5, 8], [0, 1], SHADE["mid"]
    )
    edge_strips(p.neon, _loop(PROW), 0.5, [3.6, 4.4], N)


def _rotor_pod(p: Any, at: Vec3) -> None:
    """Add a front rotor's gun pod (MB-ROTOR-BASTION-03): an armoured cowl on its hub, lit.

    Its turret stands on it; once it is destroyed the hub nacelle is left under its stump.
    """
    x = at[0]
    z = at[2]
    p.hull.lathe(
        [
            [HUB_RADIUS + 1.6, HUB_TOP - 1.4],
            [HUB_RADIUS + 2, POD_GUN_HEIGHT - 1],
            [HUB_RADIUS + 1, POD_GUN_HEIGHT],
            [0, POD_GUN_HEIGHT],
        ],
        8,
        SHADE["panel"],
        Placement([x, 0, z], math.pi / 8),
    )
    p.neon.ring(HUB_RADIUS + 1.9, 0.5, 8, N, Placement([x, POD_GUN_HEIGHT - 2, z], math.pi / 8))
    for s in [-1, 1]:
        p.hull.box(
            [1.4, 3, 4], SHADE["mid"], Placement([x + s * (HUB_RADIUS + 2.2), HUB_TOP - 1, z])
        )


def _crown(p: Any, at: Vec3) -> None:
    """Add the crown (MB-ROTOR-BASTION-03): a battlemented cupola on the roof, its turret's seat."""
    x = at[0]
    z = at[2]
    top = CROWN_GUN_HEIGHT
    p.hull.lathe(
        [[7.2, TOWER_WALL], [7.2, top - 1.4], [6.4, top], [0, top]],
        8,
        SHADE["panel"],
        Placement([x, 0, z], math.pi / 8),
    )
    p.neon.ring(7.3, 0.6, 8, N, Placement([x, top - 2.6, z], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [x + math.cos(a) * 6.6, top - 0.6, z + math.sin(a) * 6.6]
        p.hull.box([2.4, 2, 2.4], SHADE["light"], Placement(q, a))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the roof rotor (BOSS-58): an octagonal steel cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], 0)
    cap = [
        [
            5.6 * math.cos(math.pi / 8 + k * math.pi / 4),
            5.6 * math.sin(math.pi / 8 + k * math.pi / 4),
        ]
        for k in range(8)
    ]
    top = TOWER_WALL
    p.hull.bevel_slab(
        cap, [top - 0.2, top + 0.8, top + 1.5], [0, 0.6], SHADE["panel"], Placement(at)
    )
    p.hull.box([6, 0.5, 1.2], SHADE["dark"], Placement([at[0], top + 1.4, at[2]]))
    p.neon.ring(5.5, 0.3, 8, N, Placement([at[0], top + 0.9, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    p.neon.ring(5.3, 0.4, 12, N, Placement(pt(ROTOR_AT[0], ROTOR_AT[1], TOWER_WALL + 0.6)))


def build_rotor_bastion(scene: Any) -> Any:
    """MB-ROTOR-BASTION-01, MB-ROTOR-BASTION-04: the Rotor Bastion.

    A square armoured tower on four ducted rotors, 3.8 L across, with mint lights: its front rotors'
    gun pods, its crown turret, its balcony turret and its roof rotor (their mounts, drawn by
    `build_boss_model`, BOSS-58). Its front arms fold back at its transformation
    (MB-ROTOR-BASTION-05).
    """

    def core(p: Any) -> None:
        _draw_tower(p)
        _draw_balcony(p)
        _draw_prow_floor(p)
        draw_rear_rotors(p)

    armour = rotor_arms()
    armour["prow"] = {"whole": _draw_prow}
    armour["roof-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return build_boss_model(
        ROTOR_BASTION,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "rotor-left": _rotor_pod,
                "rotor-right": _rotor_pod,
                "crown": _crown,
            },
            "armour": armour,
            "rig": {"build": build_blade_rig, "triangles": blade_triangles},
        },
    )
