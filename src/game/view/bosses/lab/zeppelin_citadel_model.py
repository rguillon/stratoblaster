# Copyright (c) 2026 Renaud Guillon
"""FB-ZEPPELIN-CITADEL-01 to -05: the Zeppelin Citadel, the Lab's L-13 final boss.

Logical pixels, nose +Z, Y up (towards the camera). A fortified town gondola slung under three gas
envelopes: a walled deck of hipped rooftops, streets and lanterns, two round bow towers and a keep
on its prow, two missile silos on its stern, cradle struts holding the middle envelope. Its
envelopes are in `zeppelin_citadel_envelopes`, its propellers, cables and gas cell in
`zeppelin_citadel_rig`.
"""

import math

from game.config.bosses.lab.zeppelin_citadel import (
    BOOM_H,
    BOOM_X,
    BOOM_YS,
    BOW_GUN_HEIGHT,
    BOW_RADIUS,
    BOW_TOP,
    BOW_TOWER,
    DECK,
    DORSAL_HEIGHT,
    KEEP_GUN_AT,
    KEEP_TOP,
    MIDDLE,
    ROTOR_AT,
    ROTOR_TOP,
    SILO_HEIGHT,
    STERN_HALF,
    STERN_SILO,
    STERN_TOP,
    TOWN,
    ZEPPELIN_CITADEL,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import SHADE, plate, rect, rod
from game.view.bosses.final_boss_shapes import edge_strips
from game.view.bosses.lab.zeppelin_citadel_envelopes import (
    Envelope,
    N,
    envelope_armour,
    model_outline,
    pt,
)
from game.view.bosses.lab.zeppelin_citadel_rig import CABLES, build_zeppelin_rig, rig_triangles
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The town's houses (config): `[x, y, half width, half depth, wall top, roof top]` each, right side
# and middle (the right ones mirrored on the left). Under the envelopes they stay below their keels.
HOUSES: list[Any] = [
    [0, -42, 7, 3.5, 11, 14],
    [11, -40, 3.5, 3, 10, 12.5],
    [27, -31, 4.5, 4, 9.5, 12],
    [40, -30, 3.5, 4.5, 9.5, 12],
    [28, -11, 4.5, 5, 10, 12.5],
    [40, -12, 3.5, 4, 9.5, 11.5],
    [27, 38, 4.5, 4, 9.5, 12],
    [40, 38, 3.5, 3.5, 9.5, 11.5],
    [12, 50, 5, 4, 10, 13],
]
# The cradle struts holding the middle envelope: their y.
CRADLE_YS = [-38, -8, 22]


def _m(x: float, y: float) -> list[Any]:
    """Return the config point `(x, y)` as a model `[x, z]`."""
    return [-x, -y]


def _loop(outline: list[Any], inset: float = 0) -> list[Any]:
    """Return a config outline (pulled in by `inset` towards the centre) as a closed polyline."""
    points: list[Any] = []
    for q in outline:
        d = math.hypot(q[0], q[1]) or 1
        k = (d - inset) / d
        points.append(_m(q[0] * k, q[1] * k))
    points.append(points[0])
    return points


def _draw_gondola(p: Any) -> None:
    """Draw the gondola's hull (FB-ZEPPELIN-CITADEL-02): a walled deck on a tapering keel.

    A lit line round its deck's edge, the slots its booms slide out of, mooring bollards.
    """
    p.hull.bevel_slab(
        model_outline(TOWN), [-4, DECK - 2, DECK], [7, 1], SHADE["base"], None, SHADE["mid"]
    )
    edge_strips(p.neon, _loop(TOWN, 1.4), 0.55, [DECK + 0.02, DECK + 0.14], N)
    # The boom slots on its flanks, lit inside.
    for s in [-1, 1]:
        for y in BOOM_YS:
            p.hull.box(
                [BOOM_X[1] - 34, 0.4, 4], SHADE["dark"], Placement(pt(s * 41, y, DECK - 0.2))
            )
            p.neon.box([BOOM_X[1] - 35, 0.2, 0.6], N, Placement(pt(s * 41, y, DECK + 0.1)))
            # The rail the boom slides on, out of the slot.
            p.hull.box(
                [4, BOOM_H[1] - BOOM_H[0] + 0.6, 3.6],
                SHADE["dark"],
                Placement(pt(s * 45.5, y, BOOM_H[0] - 0.3)),
            )
        for cable in CABLES:
            bollard = cable[0]
            p.hull.cylinder(
                1.2, 1.6, 6, SHADE["panel"], Placement(pt(s * bollard[0], bollard[1], DECK))
            )
    # Streets: dark lanes along the gaps between the envelopes, lanterns along them.
    for s in [-1, 1]:
        lane = [[s * 16.5, -40], [s * 20.5, -40], [s * 20.5, 46], [s * 16.5, 46]]
        p.hull.slab(model_outline(lane), [DECK - 0.1, DECK + 0.25], SHADE["dark"])
        for k in range(6):
            y = -34 + k * 14
            at = pt(s * 18.5, y, DECK + 0.2)
            p.hull.cylinder(0.35, 3, 4, SHADE["dark"], Placement(at))
            p.neon.box([0.9, 0.9, 0.9], N, Placement([at[0], DECK + 3.2, at[2]]))


def _draw_walls(p: Any) -> None:
    """Draw the bow's battlements: merlons along its walls, from the flanks round to its tip."""
    bow = [[-46, -36], [-40, -46], [-22, -60], [-6, -66], [6, -66], [22, -60], [40, -46], [46, -36]]
    for i in range(len(bow) - 1):
        a = bow[i]
        b = bow[i + 1]
        n = max(2, math.floor(math.hypot(b[0] - a[0], b[1] - a[1]) / 5))
        for k in range(n):
            t = (k + 0.5) / n
            x = a[0] + (b[0] - a[0]) * t
            y = a[1] + (b[1] - a[1]) * t
            yaw = math.atan2(-(b[0] - a[0]), -(b[1] - a[1]))
            p.hull.box(
                [1.8, 2.2, 2.6],
                SHADE["mid"],
                Placement(pt(x * 0.97, y * 0.97 + 0.6, DECK - 0.2), yaw),
                SHADE["light"],
            )


def _house(p: Any, spec: list[Any], side: float) -> None:
    """Add a house (FB-ZEPPELIN-CITADEL-02): plated walls under a hipped roof, a lit window."""
    x = spec[0] * side
    y = spec[1]
    w = spec[2]
    d = spec[3]
    wall = spec[4]
    roof = spec[5]
    p.hull.box([w * 2, wall - DECK, d * 2], SHADE["base"], Placement(pt(x, y, DECK)))
    outline = model_outline([
        [x - w - 0.6, y - d - 0.6],
        [x + w + 0.6, y - d - 0.6],
        [x + w + 0.6, y + d + 0.6],
        [x - w - 0.6, y + d + 0.6],
    ])
    p.hull.bevel_slab(
        outline,
        [wall - 0.3, wall, roof],
        [0, min(w, d) * 0.9],
        SHADE["panel"],
        None,
        SHADE["light"],
    )
    p.neon.box([min(2.2, w), 1.4, 0.3], N, Placement(pt(x, y - d - 0.05, wall - 2.6)))


def _draw_town(p: Any) -> None:
    """Draw the town's houses, mirrored but for the middle ones."""
    for spec in HOUSES:
        if spec[0] == 0:
            _house(p, spec, 1)
            continue
        for s in [-1, 1]:
            _house(p, spec, s)


def _draw_bow(p: Any) -> None:
    """Draw the bow towers' drums and the keep on the prow's tip (the core's turret's seat)."""
    for s in [-1, 1]:
        at = pt(s * BOW_TOWER[0], BOW_TOWER[1], 0)
        p.hull.lathe(
            [
                [BOW_RADIUS + 1.6, DECK - 0.5],
                [BOW_RADIUS, DECK + 2],
                [BOW_RADIUS, BOW_TOP],
                [0, BOW_TOP],
            ],
            8,
            SHADE["base"],
            Placement(at, math.pi / 8),
        )
        p.neon.ring(
            BOW_RADIUS + 0.1, 0.6, 8, N, Placement([at[0], BOW_TOP - 4, at[2]], math.pi / 8)
        )
        # A pennant on a mast at its back.
        mast = pt(s * (BOW_TOWER[0] + 3), BOW_TOWER[1] + 6, BOW_TOP - 1)
        p.hull.cylinder(0.35, 7, 4, SHADE["dark"], Placement(mast))
        p.neon.box([0.3, 1.6, 4], N, Placement([mast[0], mast[1] + 5, mast[2] - 2]))
    keep = [[-7, -51], [7, -51], [9, -57], [5, -63], [-5, -63], [-9, -57]]
    p.hull.bevel_slab(
        model_outline(keep),
        [DECK - 1, KEEP_TOP - 1, KEEP_TOP],
        [0, 1],
        SHADE["panel"],
        None,
        SHADE["mid"],
    )
    edge_strips(p.neon, _loop(keep, 0.5), 0.45, [KEEP_TOP - 3, KEEP_TOP - 2.4], N)
    seat = pt(KEEP_GUN_AT[0], KEEP_GUN_AT[1], KEEP_TOP - 0.4)
    p.hull.cylinder(6.4, 0.6, 8, SHADE["dark"], Placement(seat, math.pi / 8))


def _draw_stern(p: Any) -> None:
    """Draw the stern silos' blocks and the stern deck's rotor collar (its hatch is drawn apart)."""
    for s in [-1, 1]:
        x = s * STERN_SILO[0]
        y = STERN_SILO[1]
        h = STERN_HALF
        block = [[x - h, y - h], [x + h, y - h], [x + h, y + h], [x - h, y + h]]
        p.hull.bevel_slab(
            model_outline(block),
            [DECK - 1, STERN_TOP - 1, STERN_TOP],
            [0, 0.8],
            SHADE["base"],
            None,
            SHADE["mid"],
        )
        edge_strips(p.neon, _loop(block, 0), 0.4, [STERN_TOP - 3, STERN_TOP - 2.5], N)
    plate(p.hull, rect(_m(0, ROTOR_AT[1]), [14, 11]), DECK, SHADE["panel"], 1.2)
    p.hull.ring(
        5.6,
        ROTOR_TOP - DECK - 0.2,
        12,
        SHADE["dark"],
        Placement(pt(ROTOR_AT[0], ROTOR_AT[1], DECK)),
    )


def _draw_cradle(p: Any) -> None:
    """Draw the cradle struts holding the middle envelope off the plaza (left once it is gone)."""
    e = Envelope(MIDDLE, 1)
    for y in CRADLE_YS:
        t = (e.tail - y) / (e.tail - e.nose)
        for s in [-1, 1]:
            top = e.bottom_at(t, 9) + 1.4
            rod(p.hull, pt(s * 13.5, y, DECK - 0.5), pt(s * 9, y, top), 0.9, SHADE["mid"])
            p.hull.box([3.2, 1.4, 3.2], SHADE["dark"], Placement(pt(s * 13.5, y, DECK - 0.4)))
        p.neon.box([0.8, 0.8, 0.8], N, Placement(pt(13.5, y, DECK + 1)))
        p.neon.box([0.8, 0.8, 0.8], N, Placement(pt(-13.5, y, DECK + 1)))


def _dorsal(p: Any, at: Vec3) -> None:
    """Add a dorsal turret's ring (FB-ZEPPELIN-CITADEL-03): an armoured collar on its saddle."""
    x = at[0]
    z = at[2]
    p.hull.lathe(
        [
            [6.4, DORSAL_HEIGHT - 2],
            [6.4, DORSAL_HEIGHT - 0.6],
            [5.6, DORSAL_HEIGHT],
            [0, DORSAL_HEIGHT],
        ],
        8,
        SHADE["panel"],
        Placement([x, 0, z], math.pi / 8),
    )
    p.neon.ring(6.5, 0.5, 8, N, Placement([x, DORSAL_HEIGHT - 1.6, z], math.pi / 8))


def _bow_crown(p: Any, at: Vec3) -> None:
    """Add a bow tower's crown: a battlemented cupola on its drum, its turret's seat."""
    x = at[0]
    z = at[2]
    top = BOW_GUN_HEIGHT
    p.hull.lathe(
        [[BOW_RADIUS + 1, BOW_TOP - 0.4], [BOW_RADIUS + 1, top - 1], [BOW_RADIUS, top], [0, top]],
        8,
        SHADE["panel"],
        Placement([x, 0, z], math.pi / 8),
    )
    p.neon.ring(BOW_RADIUS + 1.1, 0.5, 8, N, Placement([x, top - 2, z], math.pi / 8))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [x + math.cos(a) * (BOW_RADIUS + 0.2), top - 0.4, z + math.sin(a) * (BOW_RADIUS + 0.2)]
        p.hull.box([2.2, 1.8, 2.2], SHADE["light"], Placement(q, a))


def _silo(p: Any, at: Vec3) -> None:
    """Add a stern silo's head: an armoured launcher housing, lit, its missile block on top."""
    x = at[0]
    z = at[2]
    h = STERN_HALF - 0.6
    p.hull.bevel_slab(
        [[x - h, z - h], [x + h, z - h], [x + h, z + h], [x - h, z + h]],
        [STERN_TOP - 0.4, SILO_HEIGHT - 0.6, SILO_HEIGHT],
        [0, 0.6],
        SHADE["panel"],
    )
    for s in [-1, 1]:
        p.neon.box([0.5, 0.3, h * 1.6], N, Placement([x + s * (h - 0.6), SILO_HEIGHT, z]))


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the stern rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = pt(ROTOR_AT[0], ROTOR_AT[1], 0)
    cap = [
        [6 * math.cos(math.pi / 8 + k * math.pi / 4), 6 * math.sin(math.pi / 8 + k * math.pi / 4)]
        for k in range(8)
    ]
    p.hull.bevel_slab(
        cap, [ROTOR_TOP - 1, ROTOR_TOP, ROTOR_TOP + 0.8], [0, 0.6], SHADE["mid"], Placement(at)
    )
    p.hull.box([6.6, 0.5, 1.2], SHADE["dark"], Placement([at[0], ROTOR_TOP + 0.7, at[2]]))
    p.neon.ring(5.9, 0.3, 8, N, Placement([at[0], ROTOR_TOP + 0.2, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a lit collar round the opening the rotor rises from."""
    p.neon.ring(5.7, 0.4, 12, N, Placement(pt(ROTOR_AT[0], ROTOR_AT[1], ROTOR_TOP - 0.2)))


def build_zeppelin_citadel(scene: Any) -> Any:
    """FB-ZEPPELIN-CITADEL-01, FB-ZEPPELIN-CITADEL-04: the Zeppelin Citadel.

    A fortified town slung under three gas envelopes, 5 L long, violet lights (shown green): its
    dorsal turrets, bow towers, stern silos, keep turret and stern rotor (their mounts, drawn by
    `build_boss_model`, BOSS-58). Its outer envelopes drift off at its first transformation, its
    middle one bursts at its second (FB-ZEPPELIN-CITADEL-05).
    """

    def core(p: Any) -> None:
        _draw_gondola(p)
        _draw_walls(p)
        _draw_town(p)
        _draw_bow(p)
        _draw_stern(p)
        _draw_cradle(p)

    armour = envelope_armour()
    armour["rotor-hatch"] = {"whole": _draw_hatch, "frame": _draw_hatch_frame}
    return build_boss_model(
        ZEPPELIN_CITADEL,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "dorsal-left": _dorsal,
                "dorsal-right": _dorsal,
                "bow-left": _bow_crown,
                "bow-right": _bow_crown,
                "stern-left": _silo,
                "stern-right": _silo,
            },
            "armour": armour,
            "rig": {"build": build_zeppelin_rig, "triangles": rig_triangles},
        },
    )
