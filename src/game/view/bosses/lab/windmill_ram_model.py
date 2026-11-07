# Copyright (c) 2026 Renaud Guillon
"""MB-WINDMILL-RAM-01 to MB-WINDMILL-RAM-05: the Windmill Ram, the Lab's L-14 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A wedge-shaped flying siege engine: a
timber-and-iron hull (plank decking, iron bands, a gunwale round it), the iron-headed battering ram
housed in its bow, a windmill tower on its stern carrying the sails (`windmill_ram_sails`, a rig of
their own). Its two prow halves are moving pieces that swing apart like doors; its cheek guns and
its belfry are its parts. A machine, not a creature: the Lab's third round builds flying fortresses
(user request, 2026-11-06).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.windmill_ram import (
    BELFRY_AT,
    BELFRY_TOP,
    CHEEK,
    CHEEK_HEIGHT,
    DECK,
    HUB,
    HULL_BACK,
    HULL_FRONT,
    HULL_HALF,
    PROW,
    PROW_HINGE,
    PROW_Y,
    RAM_GUN_AT,
    ROTOR_AT,
    TOWER_AT,
    TOWER_TOP,
    WINDMILL_RAM,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.lab.windmill_ram_sails import build_sail_rig, sail_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["windmill-ram"]
# Timber shades (greyed as the boss's body shades are, BOSS-50): planks and beams.
WOOD = [0.11, 0.105, 0.1]
WOOD_DARK = [0.07, 0.066, 0.062]
# The ram inside the bow (bared once the prow opens): its log's radius and height, from the hull's
# front back to its iron head.
RAM = {"radius": 4, "y": 6.5, "from": -22, "head": -56, "tip": -64}


def _xz(x: float, y: float) -> list[float]:
    """Return a config point `[x, y]` as a model outline point (XZ)."""
    return [-x, -y]


def _hull_outline() -> list[list[float]]:
    a = HULL_HALF[0]
    b = HULL_HALF[1]
    return [
        _xz(-a, HULL_FRONT),
        _xz(a, HULL_FRONT),
        _xz(b, HULL_BACK - 6),
        _xz(b - 6, HULL_BACK),
        _xz(6 - b, HULL_BACK),
        _xz(-b, HULL_BACK - 6),
    ]


def _half_at(y: float) -> float:
    """Return the hull's half width at `y` (config), along its straight flanks."""
    t = (y - HULL_FRONT) / (HULL_BACK - 6 - HULL_FRONT)
    return HULL_HALF[0] + (HULL_HALF[1] - HULL_HALF[0]) * t


def _draw_hull(p: Any) -> None:
    """Draw the hull (MB-WINDMILL-RAM-02): an iron-skinned wedge, plank decking, a gunwale.

    Iron bands across the deck, plank seams along it, a lit strake down each flank, buttress ribs
    on its sides and a keel under the bow where the ram is housed.
    """
    p.hull.bevel_slab(_hull_outline(), [0, 6, DECK - 0.6], [4, 0.6], M.base, None, M.panel)
    p.hull.slab(
        [[x * 0.93, z * 0.97 + 0.6] for x, z in _hull_outline()], [DECK - 0.6, DECK], WOOD, None
    )
    # Plank seams along the deck.
    for k in range(-3, 4):
        x = k * 5.4
        p.bare.box(
            [0.4, 0.2, HULL_BACK - HULL_FRONT - 6],
            WOOD_DARK,
            Placement([x, DECK, -(HULL_FRONT + HULL_BACK - 6) / 2]),
        )
    # Iron bands across it, riveted.
    for y in [-20, -4, 16, 34]:
        h = _half_at(y) - 1.5
        p.hull.box([h * 2, 0.6, 1.6], M.panel, Placement(boss_point(0, y, DECK - 0.1)))
        for s in [-1, 1]:
            p.bare.box([0.8, 0.3, 0.8], M.base, Placement(boss_point(s * (h - 1.5), y, DECK + 0.5)))
    # The gunwale along each flank, a lit strake under it, buttress ribs down the side.
    for s in [-1, 1]:
        a = [s * (HULL_HALF[0] - 0.8), HULL_FRONT]
        b = [s * (HULL_HALF[1] - 0.8), HULL_BACK - 6]
        rod(p.hull, boss_point(a[0], a[1], DECK), boss_point(b[0], b[1], DECK), 1.1, M.panel)
        rod(
            p.neon,
            boss_point(a[0] + s * 1.6, a[1], 6.6),
            boss_point(b[0] + s * 1.9, b[1], 6.6),
            0.35,
            N,
        )
        for y in [-14, 0, 14, 28, 42]:
            x = s * (_half_at(y) + 0.6)
            p.hull.box([2.2, 6, 2.2], M.panel, Placement(boss_point(x, y, 1.6)))
    # The stern's transom: a raised iron rail, lit.
    rail = HULL_HALF[1] - 7
    p.hull.box([rail * 2, 2.2, 1.6], M.panel, Placement(boss_point(0, HULL_BACK - 0.8, DECK - 0.5)))
    p.neon.box([rail * 1.6, 0.4, 0.4], N, Placement(boss_point(0, HULL_BACK - 0.2, DECK + 1)))


def _draw_ram(p: Any) -> None:
    """Draw the bow's keel and the battering ram housed in it (bared as the prow opens).

    A dark keel floor in the prow's outline, the iron-banded ram log on cradles along the centre
    line, its iron head with a lit seam, and the hinge posts the prow halves swing on.
    """
    floor = [_xz(q[0], q[1]) for q in PROW if q[0] > 0]
    for k in range(len(PROW)):
        q = PROW[len(PROW) - 1 - k]
        if q[0] > 0:
            floor.append(_xz(-q[0], q[1]))
    p.hull.slab(floor, [0, PROW_Y[0] + 0.4], M.dark)
    r = RAM["radius"]
    y = RAM["y"]
    log_len = RAM["from"] - RAM["head"]
    p.hull.cylinder(r, log_len, 8, WOOD, Placement(boss_point(0, RAM["from"], y), 0, math.pi / 2))
    for k in range(4):
        z = -RAM["from"] + 6 + k * 8
        p.hull.cylinder(r + 0.5, 1.4, 8, M.panel, Placement([0, y, z], 0, math.pi / 2))
    for z in [28, 44]:
        p.hull.box([2 * r + 2, y - r + 1, 2.4], M.base, Placement([0, 0, z]))
    # The iron head: a tapering block to a blunt point, a lit seam round its collar.
    p.hull.cylinder(
        r + 1.4,
        RAM["head"] - RAM["tip"],
        8,
        M.panel,
        Placement(boss_point(0, RAM["head"], y), 0, math.pi / 2),
        1.2,
    )
    p.neon.ring(r + 1.5, 0.5, 8, N, Placement(boss_point(0, RAM["head"] + 0.6, y), 0, math.pi / 2))
    for s in [-1, 1]:
        hinge = boss_point(s * PROW_HINGE[0], PROW_HINGE[1], 0)
        p.hull.cylinder(2.4, PROW_Y[1] + 1.2, 8, M.panel, Placement(hinge))
        p.neon.ring(2.45, 0.4, 8, N, Placement([hinge[0], PROW_Y[1] - 1.5, hinge[2]]))


def _draw_decks(p: Any) -> None:
    """Draw what stands on the deck: the ram gun's seat, the rotor's well, gratings, winches."""
    seat = boss_point(RAM_GUN_AT[0], RAM_GUN_AT[1], 0)
    p.hull.cylinder(6.2, 1.2, 10, M.panel, Placement([seat[0], DECK - 0.2, seat[2]]))
    p.neon.ring(6.25, 0.35, 10, N, Placement([seat[0], DECK + 0.4, seat[2]]))
    well = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.bare.cylinder(6.6, 0.6, 8, M.dark, Placement([well[0], DECK - 0.1, well[2]]))
    for s in [-1, 1]:
        # Gratings and winch drums either side of the belfry.
        at = boss_point(s * 15, 12, DECK)
        p.bare.box([6, 0.4, 10], M.dark, Placement(at))
        for k in range(4):
            p.bare.box([5.4, 0.7, 0.6], M.panel, Placement([at[0], DECK, at[2] - 3.6 + 2.4 * k]))
        drum = boss_point(s * 17, -10, DECK + 2.4)
        p.hull.cylinder(
            2, 6, 8, WOOD, Placement([drum[0] - 3, drum[1], drum[2]], math.pi / 2, math.pi / 2)
        )
        p.hull.box([1.2, 3.4, 4], M.panel, Placement(boss_point(s * 13.6, -10, DECK)))
        p.hull.box([1.2, 3.4, 4], M.panel, Placement(boss_point(s * 20.4, -10, DECK)))


def _draw_tower(p: Any) -> None:
    """Draw the windmill tower on the stern (MB-WINDMILL-RAM-04) and the axle up to the hub.

    An octagonal tapering tower of iron-banded timber, a gallery round its top, its cap tilted
    with the sails, the axle out of it to the hub.
    """
    at = boss_point(TOWER_AT[0], TOWER_AT[1], 0)
    p.hull.lathe(
        [[9, DECK - 1], [8.6, DECK + 4], [6.6, TOWER_TOP]], 8, WOOD, Placement(at, math.pi / 8)
    )
    for h in [DECK + 4, TOWER_TOP - 5]:
        r = 8.6 - (h - DECK - 4) * 2 / (TOWER_TOP - DECK - 4)
        p.hull.ring(r + 0.3, 1.2, 8, M.panel, Placement([at[0], h, at[2]], math.pi / 8))
    p.neon.ring(7.6, 0.5, 8, N, Placement([at[0], TOWER_TOP - 8, at[2]], math.pi / 8))
    # The gallery round its top, and its cap.
    p.hull.bevel_slab(
        polygon(8, 9),
        [TOWER_TOP - 1.2, TOWER_TOP - 0.4, TOWER_TOP],
        [1, 0.3],
        M.panel,
        Placement([at[0], 0, at[2]], math.pi / 8),
        M.base,
    )
    hub = boss_point(HUB[0], HUB[1], HUB[2])
    # The cap's block, and the axle out of it up to the hub.
    p.hull.cylinder(5.2, 3, 8, M.base, Placement([at[0], TOWER_TOP - 0.5, at[2]]), 4.2)
    rod(p.hull, [at[0], TOWER_TOP + 1, at[2]], hub, 2.4, M.panel)


def _cheek(p: Any, at: Vec3) -> None:
    """Add a cheek gun's cowl (MB-WINDMILL-RAM-03): an armoured ring on the shut prow, lit."""
    x = at[0]
    z = at[2]
    p.hull.bevel_slab(
        polygon(8, 6.2),
        [PROW_Y[1] - 0.4, PROW_Y[1] + 0.4, CHEEK_HEIGHT],
        [0, 0.6],
        M.panel,
        Placement([x, 0, z], math.pi / 8),
        M.base,
    )
    p.neon.ring(6.25, 0.35, 8, N, Placement([x, CHEEK_HEIGHT - 0.6, z], math.pi / 8))
    for dz in [-4.4, 4.4]:
        p.hull.box([3.2, 1.2, 1.2], M.base, Placement([x, CHEEK_HEIGHT - 0.4, z + dz]))


def _draw_belfry_tower(p: Any) -> None:
    """Draw the belfry's tower amidships (MB-WINDMILL-RAM-02): its fighting top is the part.

    A square timber tower on an iron plinth, iron corner posts, planked faces with lit arrow slits;
    what its fighting top leaves once destroyed stands on its roof.
    """
    at = boss_point(BELFRY_AT[0], BELFRY_AT[1], 0)
    x = at[0]
    z = at[2]
    half = 8
    roof = BELFRY_TOP - 2
    p.hull.bevel_slab(
        polygon(4, 12.5), [DECK - 0.5, DECK + 1, DECK + 2], [0, 1], M.panel, Placement([x, 0, z])
    )
    p.hull.box([half * 2, roof - DECK - 2, half * 2], WOOD, Placement([x, DECK + 2, z]), WOOD_DARK)
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            p.hull.box(
                [2, roof - DECK - 1.5, 2],
                M.panel,
                Placement([x + sx * half, DECK + 2, z + sz * half]),
            )
    for k in range(4):
        yaw = k * math.pi / 2
        c = math.cos(yaw)
        s = math.sin(yaw)
        q = [x + s * (half + 0.05), 0, z + c * (half + 0.05)]
        p.neon.box([4, 3, 0.4], N, Placement([q[0], 15, q[2]], yaw))
        p.hull.box([half * 2 + 1, 1, 0.6], M.panel, Placement([q[0], 12, q[2]], yaw))
    # The gun's pedestal on its roof (what its gun leaves once destroyed stands on it).
    p.hull.cylinder(4.6, BELFRY_TOP + 1.2 - roof, 8, M.panel, Placement([x, roof, z]))


def _belfry(p: Any, at: Vec3) -> None:
    """Add the belfry's fighting top (MB-WINDMILL-RAM-03): a crenellated platform, its gun's ring.

    It crowns the belfry's tower; its gun stands on it.
    """
    x = at[0]
    z = at[2]
    top = BELFRY_TOP
    p.hull.bevel_slab(
        polygon(4, 13), [top - 2.2, top - 1, top], [1.2, 0.4], M.panel, Placement([x, 0, z]), M.base
    )
    for k in range(8):
        a = k * math.pi / 4
        p.hull.box(
            [2.4, 1.8, 1.4],
            M.base,
            Placement([x + math.sin(a) * 8.2, top, z + math.cos(a) * 8.2], a),
        )
    p.neon.ring(6, 0.4, 10, N, Placement([x, top + 0.2, z]))
    p.neon.ring(9.25, 0.4, 4, N, Placement([x, top - 1.6, z], math.pi / 4))


def _draw_pavises(p: Any) -> None:
    """Hang a row of pavise shields along each gunwale, and a lantern on each stern corner."""
    for s in [-1, 1]:
        for k in range(6):
            y = -18 + k * 10
            x = s * (_half_at(y) + 0.9)
            yaw = s * 0.08
            p.bare.box(
                [0.8, 4.2, 6.4], M.panel, Placement(boss_point(x, y, DECK - 2.6), yaw), M.base
            )
            p.neon.box([0.9, 0.5, 2.4], N, Placement(boss_point(x, y, DECK + 0.6), yaw))
        corner = boss_point(s * (HULL_HALF[1] - 4), HULL_BACK - 2, DECK)
        p.hull.cylinder(0.6, 6, 4, M.panel, Placement(corner))
        p.neon.box([1.6, 1.8, 1.6], N, Placement([corner[0], DECK + 6, corner[2]]))


def _prow(s: float) -> Any:
    """Return the drawing of the prow half on side `s` (model X sign), shut as drawn."""

    def outline(points: list[Any]) -> list[list[float]]:
        return [[s * abs(q[0]), -q[1]] for q in points]

    def draw(p: Any) -> None:
        y0 = PROW_Y[0]
        y1 = PROW_Y[1]
        p.hull.bevel_slab(outline(PROW), [y0, y1 - 3, y1], [2, 1.4], M.base, None, M.panel)
        # The cheek gun's seat (what its gun leaves once destroyed stands on it).
        p.hull.cylinder(
            4.6, CHEEK_HEIGHT - y1 + 0.4, 8, M.panel, Placement([s * CHEEK[0], y1 - 0.2, -CHEEK[1]])
        )
        # Riveted armour plates over its top, a lit seam between them.
        for plate in [
            [[1, -60], [6, -60], [13, -44], [1, -44]],
            [[1, -42], [14, -42], [19, -28], [1, -28]],
        ]:
            p.hull.bevel_slab(outline(plate), [y1 - 0.2, y1 - 0.2, y1 + 0.7], [0, 0.5], M.panel)
        rod(p.neon, [s * 9.5, y1 + 0.1, 43], [s * 2, y1 + 0.1, 43], 0.3, N)
        # The lit edge where the two halves meet, and its inner face's dark recess (seen open).
        p.neon.box([0.4, 0.5, 40], N, Placement([s * 0.35, y1 - 0.6, 46]))
        p.bare.box([0.4, y1 - y0 - 4, 38], M.dark, Placement([s * 0.2, y0 + 1.5, 45]))
        # Its iron cap at the tip, and the hinge knuckle on its back outer corner.
        p.hull.bevel_slab(
            outline([[0, -68], [5, -66], [8, -59], [0, -59]]),
            [y0, y1 - 2, y1 + 1],
            [1.5, 1],
            M.panel,
        )
        hinge = boss_point(s * -PROW_HINGE[0], PROW_HINGE[1], 0)
        p.hull.box(
            [4, y1 - y0 - 2, 5], M.panel, Placement([hinge[0] - s * 1.6, y0 + 1, hinge[2] + 3])
        )

    return draw


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over its deck rotor (BOSS-58): an armoured cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 6.2), [DECK - 0.2, DECK - 0.2, DECK + 1.2], [0, 0.8], M.panel, Placement(at)
    )
    p.hull.bevel_slab(
        polygon(8, 4.2), [DECK + 1.2, DECK + 1.2, DECK + 2.2], [0, 0.6], M.base, Placement(at)
    )
    p.neon.ring(6, 0.25, 8, N, Placement([at[0], DECK + 0.8, at[2]], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(5.8, 1.2, 16, M.base, Placement([at[0], DECK - 0.2, at[2]]))
    p.neon.ring(5.8, 0.3, 16, N, Placement([at[0], DECK + 0.8, at[2]]))


def build_windmill_ram(scene: Any) -> Any:
    """MB-WINDMILL-RAM-01, MB-WINDMILL-RAM-04: the Windmill Ram.

    A wedge-shaped siege engine with amber light lines (shown yellow), its ram prow shut, a belfry
    amidships and the windmill's sails turning on its stern.
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_ram(p)
        _draw_decks(p)
        _draw_tower(p)
        _draw_belfry_tower(p)
        _draw_pavises(p)

    return build_boss_model(
        WINDMILL_RAM,
        scene,
        N,
        {
            "core": core,
            "parts": {"cheek-left": _cheek, "cheek-right": _cheek, "belfry": _belfry},
            "armour": {
                # The config's right is the model's -X.
                "prow-right": {"whole": _prow(-1)},
                "prow-left": {"whole": _prow(1)},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
            "rig": {"build": build_sail_rig, "triangles": sail_triangles},
        },
    )
