# Copyright (c) 2026 Renaud Guillon
"""FB-CATHEDRAL-ENGINE-01 to FB-CATHEDRAL-ENGINE-05: the Cathedral Engine, the Lab's L-8 final boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera; a playfield point
`(x, y)` is model `(-x, -y)`. A gothic machine-church seen from above: a cross of dark stone-grey
metal on a plinth, its west front and two towers at the front, the nave behind with its aisles and
flying buttresses, the transept across with an organ-pipe bank in each arm, the crossing tower
under the rose window, the choir and the round apse with its chapels and its exhausts at the back.
A machine, not a creature (the Lab's second set, 2026-11-06). Its parts and its armour are in
`cathedral_engine_parts`; its gun mounts are drawn by `build_boss_model` (BOSS-58).
"""

import math

from game.config.bosses.lab.cathedral_engine import (
    AISLE,
    APSE_AT,
    CATHEDRAL_ENGINE,
    CHOIR_AISLE,
    CHOIR_VESSEL,
    PORTAL_AT,
    SPIRE_AT,
    TRANSEPT,
    VAULT_HEIGHTS,
    VESSEL,
    VESSEL_TOP,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import mirrored, strip
from game.view.bosses.lab.cathedral_engine_parts import (
    CROSSING_TOP,
    SLATE,
    TOWER_TOP,
    TRANSEPT_DECK,
    V,
    draw_aisles,
    draw_choir_aisles,
    draw_hatch,
    draw_hatch_frame,
    draw_vault,
    model_zs,
    organ,
    prism,
    rose,
    spire,
)
from game.view.bosses.mini_boss_greebles import vent
from game.view.bosses.mini_boss_shapes import offset
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


# The plinth's top, every block stands on; the aisles' vaults' top under their roofs.
PLINTH = 3
AISLE_VAULT = 8


def _footprint() -> list[Any]:
    """Return the cross's footprint in model space: west front, nave, transept, choir and apse."""
    right: list[Any] = [
        [0, -74],
        [28, -74],
        [28, -56],
        [AISLE, -56],
        [AISLE, -TRANSEPT[1]],
        [TRANSEPT[0], -TRANSEPT[1]],
        [TRANSEPT[0], TRANSEPT[1]],
        [CHOIR_AISLE, TRANSEPT[1]],
        [CHOIR_AISLE, 48],
    ]
    for k in range(1, 6):
        a = k * math.pi / 12
        right.append([CHOIR_AISLE * math.cos(a), 48 + CHOIR_AISLE * math.sin(a)])
    right.append([0, 48 + CHOIR_AISLE])
    return [[-q[0], -q[1]] for q in mirrored(right)]


def _block(p: Any, xy: list[Any], size: list[Any], heights: list[Any], color: Any) -> None:
    """Add a box centred on the playfield point `xy`, `size` [across, along], between `heights`."""
    p.hull.box(
        [size[0], heights[1] - heights[0], size[1]],
        color,
        Placement(boss_point(xy[0], xy[1], heights[0])),
    )


def _pinnacle(p: Any, at: Vec3, tall: float) -> None:
    """Add a pinnacle standing at `at`: a slim four-sided cone, a violet light on its tip."""
    p.hull.cylinder(1.6, tall, 4, SLATE, Placement(at, math.pi / 4), 0.1)
    p.neon.box([0.7, 0.7, 0.7], V, Placement(offset(at, 0, tall * 0.55, 0)))


def _flyer(p: Any, s: float, y: float, inner: list[Any], pier: float) -> None:
    """Add a flying buttress on side `s` at playfield `y`: a pier at `pier` across, its arch.

    The arch leans from the pier's top up against the high wall at `inner` ([x, height]); a footing
    ties the pier to the plinth.
    """
    z = -y
    top = 11
    p.hull.box([3.4, top, 3.4], M.panel, Placement([s * pier, 0, z]))
    p.hull.box([pier - AISLE + 1, PLINTH, 2.6], M.base, Placement([s * (pier + AISLE) / 2, 0, z]))
    _pinnacle(p, [s * pier, top, z], 5)
    run = pier - 1.7 - inner[0]
    rise = inner[1] - top
    mid = [s * (pier - 1.7 + inner[0]) / 2, (top + inner[1]) / 2 - 0.5, z]
    p.hull.box(
        [math.hypot(run, rise) + 1, 1, 1.4],
        M.base,
        Placement(mid, 0, 0, -s * math.atan2(rise, run)),
    )


def _draw_west_front(p: Any) -> None:
    """Draw the west front (FB-CATHEDRAL-ENGINE-02): two towers, the terrace and the portal.

    The towers carry the spires (parts); the portal gun stands on the terrace between them (the
    core's mount, BOSS-58), over a pointed arch of light, the nave's gable rising behind.
    """
    for s in SIDES:
        _block(p, [s * SPIRE_AT[0], SPIRE_AT[1]], [14, 18], [PLINTH, TOWER_TOP], M.panel)
        tower = boss_point(s * SPIRE_AT[0], SPIRE_AT[1], PLINTH)
        for dx in [-3, 3]:
            p.neon.box([0.7, 5.5, 0.4], V, Placement(offset(tower, dx, 2, 9.1)))
        strip(p.neon, [s * 13.4, 72], [s * 26.6, 72], 0.5, [TOWER_TOP - 0.6, TOWER_TOP + 0.1], V)
    _block(p, [0, -65], [26, 18], [PLINTH, 10], M.base)
    prism(
        p.hull, [[-11, 10], [11, 10], [11, 13], [0, 17.5], [-11, 13]], model_zs([-58, -55]), SLATE
    )
    door = boss_point(0, -74, PLINTH)
    for s in SIDES:
        p.neon.box([0.6, 4, 0.5], V, Placement(offset(door, s * 3, 0, 0)))
        p.neon.box([0.6, 3.6, 0.5], V, Placement(offset(door, s * 1.6, 3.6, 0), 0, 0, s * 0.6))
    strip(p.neon, [-12.6, 73.4], [12.6, 73.4], 0.5, [9.4, 10.1], V)
    seat = boss_point(PORTAL_AT[0], PORTAL_AT[1], 9.9)
    p.hull.cylinder(5.2, 0.4, 8, M.dark, Placement(seat, math.pi / 8))


def _draw_nave(p: Any) -> None:
    """Draw the nave (FB-CATHEDRAL-ENGINE-02): its aisles' vaults, the high walls and buttresses.

    Its roofs are its armour (`cathedral_engine_parts`); the high vessel's deck lies under its
    vault, a violet line along each aisle's outer wall.
    """
    _block(p, [0, -36], [AISLE * 2, 44], [PLINTH, AISLE_VAULT], M.base)
    _block(p, [0, -37], [VESSEL * 2, 40], [AISLE_VAULT, VAULT_HEIGHTS[0]], M.panel)
    for s in SIDES:
        strip(p.neon, [s * (AISLE - 0.3), 56], [s * (AISLE - 0.3), 16], 0.5, [7.4, 8.1], V)
        for y in [-50, -26]:
            _flyer(p, s, y, [VESSEL, 15], 31)


def _draw_crossing(p: Any) -> None:
    """Draw the crossing tower and the transept arms (FB-CATHEDRAL-ENGINE-02).

    The tower under the rose window, a pinnacle on each corner; each transept arm a flat deck the
    organ bank stands on, a parapet of light along its sides, conduits from the crossing to the
    organ and pinnacles at its end.
    """
    _block(p, [0, 0], [32, 32], [PLINTH, CROSSING_TOP], M.panel)
    for dx in [-15, 15]:
        for dz in [-15, 15]:
            _pinnacle(p, [dx, CROSSING_TOP, dz], 8)
    reach = TRANSEPT[0]
    half = TRANSEPT[1]
    for s in SIDES:
        arm = [[s * 15, -half], [s * reach, -half], [s * reach, half], [s * 15, half]]
        p.hull.bevel_slab(
            arm, [PLINTH, TRANSEPT_DECK - 0.8, TRANSEPT_DECK], [0, 0.8], M.base, None, M.panel
        )
        edges: list[float] = [-half + 0.4, half - 0.4]
        for edge in edges:
            strip(
                p.neon,
                [s * 17, edge],
                [s * (reach - 1), edge],
                0.5,
                [TRANSEPT_DECK - 0.7, TRANSEPT_DECK + 0.05],
                V,
            )
            _pinnacle(p, [s * (reach - 1.5), TRANSEPT_DECK, edge], 6)
        # A short gabled roof from the crossing to the organ's console, ribbed across, a violet
        # line along its ridge.
        xs = [16, 34] if s > 0 else [-34, -16]
        prism(
            p.hull,
            [[-10, TRANSEPT_DECK - 0.5], [10, TRANSEPT_DECK - 0.5], [10, 13], [0, 16], [-10, 13]],
            xs,
            SLATE,
            math.pi / 2,
        )
        strip(p.neon, [s * 17, 0], [s * 33, 0], 0.6, [15.6, 16.2], V)
        for x in [20, 25, 30]:
            for side in SIDES:
                p.hull.box([1, 0.6, 9.4], M.base, Placement([s * x, 13.9, side * 5], 0, side * 0.3))
        p.hull.box([3, 1.5, 22], SLATE, Placement([s * (reach - 2), TRANSEPT_DECK, 0]))
        # Panel seams and two vents on the deck round the organ.
        for edge in [-11.5, 11.5]:
            p.hull.box([26, 0.3, 0.6], M.dark, Placement([s * 47, TRANSEPT_DECK, edge]))
        for dz in [-6, 6]:
            vent(p.hull, [s * 58, TRANSEPT_DECK, dz], [4, 5], 3)


def _draw_choir(p: Any) -> None:
    """Draw the choir and the apse (FB-CATHEDRAL-ENGINE-02).

    The choir's aisles' vaults (their roofs are armour), its high vessel with the lantern rotor's
    hatch on its flat top, its buttresses; the round apse with its ribs of light and the apse rotor
    on its crown (the core's mounts, BOSS-58), its chapels round it and the engine's exhausts at
    its back.
    """
    _block(p, [0, 31], [CHOIR_AISLE * 2, 34], [PLINTH, AISLE_VAULT], M.base)
    w = CHOIR_VESSEL
    prism(
        p.hull,
        [[-w, AISLE_VAULT], [w, AISLE_VAULT], [w, 14], [6, VESSEL_TOP], [-6, VESSEL_TOP], [-w, 14]],
        model_zs([14, 48]),
        M.panel,
    )
    for s in SIDES:
        strip(p.neon, [s * 5.8, -16], [s * 5.8, -46], 0.5, [VESSEL_TOP - 0.4, VESSEL_TOP + 0.1], V)
        strip(
            p.neon,
            [s * (CHOIR_AISLE - 0.3), -16],
            [s * (CHOIR_AISLE - 0.3), -46],
            0.5,
            [7.4, 8.1],
            V,
        )
        for y in [22, 42]:
            _flyer(p, s, y, [w, 14.5], 30)
    apse = boss_point(0, 48, 0)
    p.hull.lathe(
        [[22, PLINTH], [22, 11], [18, 13], [7, VESSEL_TOP], [0, VESSEL_TOP]],
        16,
        SLATE,
        Placement(apse, math.pi / 16),
    )
    p.neon.ring(22.05, 0.6, 16, V, Placement(offset(apse, 0, 10, 0), math.pi / 16))
    for k in range(7):
        a = math.pi / 2 + k * math.pi / 6
        rib = offset(apse, 12.5 * math.sin(a), 14.6, 12.5 * math.cos(a))
        p.neon.box([0.5, 0.4, 11.4], V, Placement(rib, a, 0.27))
    seat = boss_point(APSE_AT[0], APSE_AT[1], VESSEL_TOP - 0.1)
    p.hull.cylinder(6, 0.5, 10, M.dark, Placement(seat))
    for deg in [-80, -40, 40, 80]:
        a = deg * math.pi / 180
        chapel = boss_point(25 * math.sin(a), 48 + 25 * math.cos(a), 0.5)
        p.hull.cylinder(5, 8, 8, M.panel, Placement(chapel, math.pi / 8))
        p.hull.cylinder(5.3, 3, 8, SLATE, Placement(offset(chapel, 0, 8, 0), math.pi / 8), 0.4)
        p.neon.box([0.7, 0.7, 0.7], V, Placement(offset(chapel, 0, 10.6, 0)))
    # The engine's exhausts behind the apse.
    p.hull.box([14, 6, 8], M.base, Placement(boss_point(0, 69, 0.5)))
    for s in SIDES:
        nozzle = boss_point(s * 3.6, 74, 3.5)
        p.hull.cylinder(
            2.8, 3.2, 8, M.dark, Placement(offset(nozzle, 0, 0, 3), 0, -math.pi / 2), 2.4
        )
        p.reactor(nozzle, 2.2)


def _draw_core(p: Any) -> None:
    """Draw the core: its plinth, west front, nave, crossing, transept, choir and apse."""
    p.hull.bevel_slab(_footprint(), [0, 1.6, PLINTH], [1, 0.6], M.dark, None, M.base)
    _draw_west_front(p)
    _draw_nave(p)
    _draw_crossing(p)
    _draw_choir(p)


def build_cathedral_engine(scene: Any) -> Any:
    """FB-CATHEDRAL-ENGINE-01, FB-CATHEDRAL-ENGINE-04: the Cathedral Engine.

    A gothic machine-church 4.5 L long with violet lights: its two spires, its two organ-pipe banks
    and its rose window are its parts; its aisles' roofs, its choir aisles' roofs and its high vault
    its armour; the portal gun, the apse rotor and the lantern rotor under its hatch the core's
    guns.
    """
    return build_boss_model(
        CATHEDRAL_ENGINE,
        scene,
        V,
        {
            "core": _draw_core,
            "parts": {
                "spire-left": spire,
                "spire-right": spire,
                "organ-left": organ,
                "organ-right": organ,
                "rose": rose,
            },
            "armour": {
                "aisles": {"whole": draw_aisles},
                "choir-aisles": {"whole": draw_choir_aisles},
                "vault": {"whole": draw_vault},
                "lantern-hatch": {"whole": draw_hatch, "frame": draw_hatch_frame},
            },
        },
    )
