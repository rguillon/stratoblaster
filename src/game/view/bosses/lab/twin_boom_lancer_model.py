# Copyright (c) 2026 Renaud Guillon
"""MB-TWIN-BOOM-LANCER-01 to MB-TWIN-BOOM-LANCER-05: the Twin-Boom Lancer, the Lab's L-18 mini boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A gigantic
twin-boom fighter: a central pod with a smoked canopy on a straight wing, two long engine booms
either side (an engine cowling at the front of each, a tail fin at the back), a tailplane joining
them. The booms are moving pieces (they slide in and lock together as it transforms); the cowlings'
upper petals, the tailplane's halves, the inner wings' sleeves, the radiator blades and the latches
are its rig (`twin_boom_lancer_rig`). A machine, not a creature: the Lab's fourth round builds
gigantic airplanes (user request, 2026-11-06). Its gun mounts are drawn by `build_boss_model`
(BOSS-58).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.twin_boom_lancer import (
    BOOM_ENDS,
    BOOM_GUN_AT,
    BOOM_GUN_H,
    BOOM_H,
    BOOM_R,
    BOOM_X,
    CANNON_POD,
    COWL,
    COWL_R,
    DORSAL_AT,
    DORSAL_H,
    FIN,
    FIN_TOP,
    NOSE_AT,
    NOSE_H,
    POD,
    ROTOR_AT,
    ROTOR_H,
    TWIN_BOOM_LANCER,
    WING_ROOT,
    WING_SPAN,
    WING_TIP,
    WING_Y,
    pod_top,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.twin_boom_lancer_rig import build_lancer_rig, lancer_triangles
from game.view.bosses.world_1_organic_kit import M, polygon
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, POD_SECTION, canopy_paint
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


N = BOSS_LOOK.neon["twin-boom-lancer"]
QUARTER = math.pi / 2
# Its smoked canopy glass and its darkest metal.
GLASS = [0.05, 0.065, 0.08]
SOOT = [0.035, 0.035, 0.042]
# A boom's stations behind its cowling, `[y, radius]`, from the cowling's back to its tail.
BOOM = [[COWL[1], 6.2], [-10, BOOM_R], [30, 5.5], [48, 4.6], [BOOM_ENDS[1], 2.4]]


def flat(x: float, y: float) -> list[Any]:
    """Return the playfield point `(x, y)` as a model outline point `[x, z]`."""
    return [-x, -y]


def _stations(spec: list[Any], axis: float) -> list[Any]:
    """Return loft stations (tail to nose) from `[y, radius]` (nose to tail) round `axis`."""
    result: list[Any] = []
    for k in range(len(spec)):
        q = spec[len(spec) - 1 - k]
        result.append([-q[0], q[1], axis - q[1], axis + q[1]])
    return result


def _boom_loft(p: Any, s: float) -> None:
    """Draw a boom behind its cowling (MB-TWIN-BOOM-LANCER-02): a long hexagonal tube."""
    x = -s * BOOM_X
    p.hull.loft(POD_SECTION, _stations(BOOM, BOOM_H), M.base, Placement([x, 0, 0]))
    # A plated saddle along its back, lit along both edges, from the gun pack to the fin.
    p.hull.box([4.4, 0.8, 50], M.panel, Placement([x, BOOM_H + BOOM_R - 0.4, -11]))
    for d in [-1, 1]:
        p.neon.box([0.4, 0.5, 46], N, Placement([x + d * 2.4, BOOM_H + BOOM_R - 0.2, -13]))


def _cowl(p: Any, s: float) -> None:
    """Draw a cowling's fixed lower half, its engine core and its intake fan (rig: the petals).

    The lower half and the inner upper facet of a hexagonal shell (open: the petals close it), a
    bulkhead at its back, the engine core along its axis (the cannon's pod stands on it) and the
    intake fan's face at its front, behind a lit lip.
    """
    x = -s * BOOM_X
    lower = [[-1, 0.5], [-0.5, 0], [0.5, 0], [1, 0.5]]
    # The inner upper facet stays: towards the centre line (+X in the model for the right boom).
    if s > 0:
        lower.append([0.5, 1])
    else:
        lower.insert(0, [-0.5, 1])
    r = COWL_R
    shell = [[-COWL[1], r, BOOM_H - r, BOOM_H + r], [-COWL[0], r, BOOM_H - r, BOOM_H + r]]
    p.hull.loft(lower, shell, M.panel, Placement([x, 0, 0]), LoftOptions(True))
    p.hull.loft(
        POD_SECTION,
        [[-COWL[1] - 0.6, r, BOOM_H - r, BOOM_H + r], [-COWL[1], r, BOOM_H - r, BOOM_H + r]],
        M.base,
        Placement([x, 0, 0]),
    )
    core = CANNON_POD[0] - BOOM_H
    p.hull.cylinder(
        core, COWL[1] - COWL[0] - 2, 8, SOOT, Placement([x, BOOM_H, -COWL[1]], 0, QUARTER)
    )
    # The intake fan's face: a dark disc, a lit ring and a hub cone at the front.
    front = -COWL[0] - 2.4
    p.bare.cylinder(r - 1.2, 0.5, 10, M.dark, Placement([x, BOOM_H, front], 0, QUARTER))
    p.neon.ring(r - 1.6, 0.4, 10, N, Placement([x, BOOM_H, front + 0.5], 0, QUARTER))
    p.hull.cylinder(2, 2.2, 8, M.panel, Placement([x, BOOM_H, front + 0.5], 0, QUARTER), 0.4)
    # The lit lip of its lower half.
    for k in range(3):
        a = math.pi * (1.0 + (k + 0.5) / 3)
        p.neon.box(
            [r * 0.95, 0.5, 0.6],
            N,
            Placement(
                [x + math.cos(a) * r * 0.86, BOOM_H + math.sin(a) * r * 0.86, -COWL[0] - 0.3],
                0,
                0,
                a + QUARTER,
            ),
        )


def _outer_wing(p: Any, s: float) -> None:
    """Draw a boom's outer wing panel: a tapered slab out to its tip, a lit leading edge."""
    xb = BOOM_X + BOOM_R - 0.5
    root = WING_ROOT
    tip = WING_TIP
    outline = [
        flat(s * xb, root[0]),
        flat(s * WING_SPAN, tip[0]),
        flat(s * WING_SPAN, tip[1]),
        flat(s * xb, root[1]),
    ]
    p.hull.bevel_slab(
        outline, [WING_Y[0], WING_Y[1] - 0.7, WING_Y[1]], [0, 0.7], M.base, None, M.panel
    )
    lead = [flat(s * (xb + 1), root[0] + 0.3), flat(s * (WING_SPAN - 1), tip[0] + 0.3)]
    _strip(p.neon, lead, 0.6, [WING_Y[1] - 0.5, WING_Y[1] + 0.1])
    # Two dark panel lines and a lamp at the tip.
    for k in range(2):
        xa = xb + 8 + k * 9
        p.bare.box(
            [0.4, 0.3, 12], M.dark, Placement([-s * xa, WING_Y[1], (root[0] + root[1]) / 2 * -1])
        )
    p.neon.box(
        [1.4, 1, 3], N, Placement([-s * (WING_SPAN - 0.6), WING_Y[1] - 0.6, -(tip[0] + tip[1]) / 2])
    )


def _strip(builder: Any, ends: list[Any], width: float, heights: list[float]) -> None:
    """Add a light strip `width` wide between two model outline points."""
    a = ends[0]
    b = ends[1]
    length = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    nx = (a[1] - b[1]) / length * width / 2
    nz = (b[0] - a[0]) / length * width / 2
    outline = [
        [a[0] + nx, a[1] + nz],
        [b[0] + nx, b[1] + nz],
        [b[0] - nx, b[1] - nz],
        [a[0] - nx, a[1] - nz],
    ]
    builder.slab(outline, heights, N)


def _fin(p: Any, s: float) -> None:
    """Draw a boom's tail fin: a swept plate standing on its tail, lit along its leading edge."""
    x = -s * BOOM_X
    base = BOOM_H + 4.5
    outline = [
        [base, -FIN[1]],
        [base, -FIN[0]],
        [FIN_TOP, -(FIN[0] + 10)],
        [FIN_TOP, -(FIN[1] + 1)],
    ]
    p.hull.slab(outline, [-0.7, 0.7], M.panel, Placement([x, 0, 0], 0, 0, QUARTER), M.base)
    p.neon.box([0.6, 0.6, 7], N, Placement([x, FIN_TOP, -(FIN[0] + 14)]))
    p.neon.box(
        [0.5, FIN_TOP - base - 2, 0.6], N, Placement([x, base + 1, -(FIN[0] + 1.5)], 0, -0.6)
    )


def _boom_details(p: Any, s: float) -> None:
    """Draw a boom's gun pylon, its exhausts, its tail light and the outer sleeve of its inner wing.

    The pylon stands under its gun pack (the stump of a destroyed gun stands on it); the outer
    sleeve rides with the boom (the rig's middle sleeve slides under it).
    """
    x = -s * BOOM_X
    gun = boss_point(s * BOOM_GUN_AT[0], BOOM_GUN_AT[1], BOOM_H + 1)
    p.hull.box([5, BOOM_GUN_H - BOOM_H - 1.2, 6], M.panel, Placement(gun), M.base)
    # The exhaust: a nozzle at its tail, glowing.
    p.reactor([x, BOOM_H, -BOOM_ENDS[1] - 0.2], 2)
    for k in range(3):
        z = -6 - k * 5
        p.neon.box([0.4, 1.4, 2.4], N, Placement([x + s * (BOOM_R - 0.1), BOOM_H - 1, z]))
    # The outer sleeve of the inner wing, on the boom's inner side.
    inner = BOOM_X - BOOM_R + 0.5
    sleeve = [
        flat(s * inner, WING_ROOT[0]),
        flat(s * (inner - 7.5), WING_ROOT[0]),
        flat(s * (inner - 7.5), WING_ROOT[1]),
        flat(s * inner, WING_ROOT[1]),
    ]
    p.hull.bevel_slab(
        sleeve, [WING_Y[0], WING_Y[1] - 0.6, WING_Y[1]], [0, 0.6], M.base, None, M.panel
    )
    p.neon.box(
        [0.5, 0.4, 13],
        N,
        Placement([-s * (inner - 7.2), WING_Y[1], -(WING_ROOT[0] + WING_ROOT[1]) / 2]),
    )


def draw_boom(s: float) -> Any:
    """Return the drawing of the boom on side `s` (1: right) as it rests: its moving piece."""

    def draw(p: Any) -> None:
        _boom_loft(p, s)
        _cowl(p, s)
        _outer_wing(p, s)
        _fin(p, s)
        _boom_details(p, s)

    return draw


def _pod(p: Any) -> None:
    """Draw the central pod (MB-TWIN-BOOM-LANCER-02): a fighter's fuselage, a smoked canopy.

    Its stations from its nose to its tail, the canopy painted on its back over the wing's leading
    edge; lights down its shoulders; the seats of the nose gun, the dorsal turret and the tail rotor
    on its back; its exhaust at its tail.
    """
    stations = [[-q[0], q[1], q[2], q[3]] for q in reversed(POD)]
    p.hull.loft(
        FIGHTER_SECTION, stations, M.base, None, LoftOptions(False, canopy_paint([4], GLASS))
    )
    for d in [-1, 1]:
        p.neon.box([0.4, 0.5, 22], N, Placement([d * 3.3, 30.1, 1]))
    nose = boss_point(NOSE_AT[0], NOSE_AT[1], NOSE_H - 2)
    p.hull.cylinder(4.6, 2, 8, M.panel, Placement(nose, math.pi / 8))
    dorsal = boss_point(DORSAL_AT[0], DORSAL_AT[1], DORSAL_H - 2.4)
    p.hull.cylinder(4.6, 2.4, 8, M.panel, Placement(dorsal, math.pi / 8))
    rotor = boss_point(ROTOR_AT[0], ROTOR_AT[1], ROTOR_H - 2)
    p.hull.cylinder(6.2, 2, 8, M.panel, Placement(rotor, math.pi / 8))
    p.reactor([0, 22.5, -POD[len(POD) - 1][0] + 1.2], 2.6)
    # Its canopy's frame bars and a lamp on its nose.
    for z in [23, 28.5]:
        p.bare.box([5.6, 0.6, 0.6], SOOT, Placement([0, pod_top(-z) - 0.4, z]))
    p.neon.box([1, 0.8, 1.6], N, Placement([0, 22.4, 45.4]))


def _hatch(p: Any) -> None:
    """Draw the hatch over the tail rotor (BOSS-58): an octagonal cap, a lit seam round it."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.bevel_slab(
        polygon(8, 5.8),
        [ROTOR_H - 0.3, ROTOR_H + 0.6, ROTOR_H + 1.6],
        [0, 0.8],
        M.panel,
        Placement(at),
    )
    p.neon.ring(5.4, 0.25, 8, N, Placement([at[0], ROTOR_H + 0.7, at[2]], math.pi / 8))


def _hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at = boss_point(ROTOR_AT[0], ROTOR_AT[1], 0)
    p.hull.ring(6, 1.2, 12, M.base, Placement([at[0], ROTOR_H - 0.6, at[2]]))
    p.neon.ring(6, 0.3, 12, N, Placement([at[0], ROTOR_H + 0.4, at[2]]))


def boom_gun(p: Any, at: Vec3) -> None:
    """Add a boom's gun pack (MB-TWIN-BOOM-LANCER-03): an armoured fairing on its pylon, lit."""
    top = BOOM_GUN_H
    outline = [
        [at[0] - 4, at[2] - 5.5],
        [at[0] + 4, at[2] - 5.5],
        [at[0] + 3.4, at[2] + 5.5],
        [at[0] - 3.4, at[2] + 5.5],
    ]
    p.hull.bevel_slab(outline, [BOOM_H + 3, top - 0.8, top], [0, 0.8], M.panel, None, M.base)
    for d in [-1, 1]:
        p.neon.box([0.4, 0.6, 9], N, Placement([at[0] + d * 3.9, top - 1.6, at[2]]))
    p.bare.box([6, 0.4, 1], SOOT, Placement([at[0], top - 0.2, at[2] - 3.5]))


def dorsal_turret(p: Any, at: Vec3) -> None:
    """Add the dorsal turret's armoured collar (MB-TWIN-BOOM-LANCER-03) on the pod's back."""
    top = DORSAL_H
    p.hull.cylinder(6.6, 3.4, 10, M.panel, Placement([at[0], top - 3.2, at[2]], math.pi / 10), 6)
    p.neon.ring(6.3, 0.4, 10, N, Placement([at[0], top - 0.6, at[2]], math.pi / 10))
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        q = [at[0] + math.sin(a) * 6.8, top - 3, at[2] + math.cos(a) * 6.8]
        p.hull.box([1.4, 2.6, 1.4], M.base, Placement(q, a))


def cannon_breech(p: Any, at: Vec3) -> None:
    """Add a cannon's pod (MB-TWIN-BOOM-LANCER-10): the heavy breech block risen from the engine.

    A long armoured block on the engine core in the opened cowling, lit down its sides, cooling
    ribs across its back; its turret rises out of it (BOSS-58).
    """
    base = CANNON_POD[0]
    top = CANNON_POD[1]
    outline = [
        [at[0] - 4.2, at[2] - 5.5],
        [at[0] + 4.2, at[2] - 5.5],
        [at[0] + 4.2, at[2] + 4.5],
        [at[0] - 4.2, at[2] + 4.5],
    ]
    p.hull.bevel_slab(outline, [base, top - 0.8, top], [0, 0.9], M.panel, None, M.base)
    for d in [-1, 1]:
        p.neon.box([0.4, 0.7, 8], N, Placement([at[0] + d * 4.25, top - 1.8, at[2] - 0.5]))
    for k in range(3):
        p.bare.box([7, 0.6, 0.6], SOOT, Placement([at[0], top - 0.1, at[2] - 2.4 - k * 1.4]))


def lancer_armour() -> Any:
    """Return the Twin-Boom Lancer's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "boom-right": {"whole": draw_boom(1)},
        "boom-left": {"whole": draw_boom(-1)},
        "rotor-hatch": {"whole": _hatch, "frame": _hatch_frame},
    }


def build_twin_boom_lancer(scene: Any) -> Any:
    """MB-TWIN-BOOM-LANCER-01, MB-TWIN-BOOM-LANCER-04: the Twin-Boom Lancer.

    A gigantic twin-boom fighter about 3.6 L across: a central pod on a straight wing between two
    long engine booms, a tailplane joining their tails; gold light lines (shown yellow).
    """

    def core(p: Any) -> None:
        _pod(p)

    return build_boss_model(
        TWIN_BOOM_LANCER,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "boom-left": boom_gun,
                "boom-right": boom_gun,
                "dorsal": dorsal_turret,
                "cannon-left": cannon_breech,
                "cannon-right": cannon_breech,
            },
            # MB-TWIN-BOOM-LANCER-10: the petals, tailplane, sleeves, radiator blades and latches.
            "rig": {"build": build_lancer_rig, "triangles": lancer_triangles},
            "armour": lancer_armour(),
        },
    )
