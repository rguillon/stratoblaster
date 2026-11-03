# Copyright (c) 2026 Renaud Guillon
"""FB-DAM-BREAKER-01 to FB-DAM-BREAKER-05, 3-4: the Dam Breaker.

Logical pixels, nose +Z, Y up (towards the camera). A giant armoured barge: a long, flat hull, the
pump house amidships with its stack, two sluice gate houses either side of the bow, the armour
plate and the drone hangar on the bow, the chemical tanks on outriggers at its sides, rust, moss
and vines all over. The plating over its flank decks and its bow's wing decks is the armour it sheds
(FB-DAM-BREAKER-11, FB-DAM-BREAKER-12, D-254): drawn apart (`dam_breaker_armour`).
"""

import math

from game.config.bosses.world_3.dam_breaker import DAM_BREAKER, DAM_CORE_GUNS, DAM_STACK
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.final_boss_shapes import (
    barrels,
    edge_strips,
    mirrored,
)
from game.view.bosses.mini_boss_greebles import (
    hazard,
    lamps,
    seam,
    vent,
)
from game.view.bosses.mini_boss_mechanism import conduit
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.dam_breaker_armour import flank_plating, wing_plating
from game.view.bosses.world_3.dam_breaker_parts import (
    DECK_Y,
    RUST,
    TOXIC,
    hangar,
    moss,
    plate,
    sluice,
    tank,
    vines,
)
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, table, vein_to
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION, RibSpec, ribs
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The hull seen from above (right half, bow to stern).
HULL = mirrored([
    [0, 74],
    [22, 72],
    [40, 64],
    [54, 48],
    [58, 30],
    [58, -52],
    [52, -66],
    [36, -72],
    [0, -72],
])
# Heights of the hull: its keel, its rim, its deck.
HULL_Y = [-8, -1, DECK_Y]
# The pump house amidships (loft stations along Z: z, half width, bottom, top).
PUMP_HOUSE = table([
    [-22, 16, DECK_Y, 14],
    [-6, 20, DECK_Y, 18],
    [10, 18, DECK_Y, 17],
    [18, 13, DECK_Y, 12],
])
# Where the stack stands on the pump house's back.
STACK_FOOT = [0, 17, -8]


def draw_hull(p: EnemyParts) -> None:
    """Draw the hull, its green-lit rim and the deck seams between its plating.

    And the swamp growing over it (FB-DAM-BREAKER-04). The flank and wing decks' plating, with the
    seams, rust and moss on it, is drawn apart (`dam_breaker_armour`).
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # FB-DAM-BREAKER-02: a giant, bloated swamp beast wallowing like a barge: a broad back of
    # moss-skinned flesh, its rusty plates, sluices and tanks grafted on, veins of toxin pulsing
    # through it.
    flesh.bevel_slab(HULL, HULL_Y, [4, 2], F.sinew, None, JUNGLE_FLESH)
    for s in SIDES:
        vein_to(
            p,
            [[s * 8, DECK_Y + 0.3, 40], [s * 30, DECK_Y + 0.3, -60]],
            [s * 14, 0, 0],
            TOXIC,
            1.6,
        )
    for s in SIDES:
        edge_strips(
            neon,
            [[s * 57.4, 28], [s * 57.4, -50]],
            0.8,
            [DECK_Y - 3, DECK_Y - 2],
            TOXIC,
        )
        for z in [-40, -20]:
            seam(hull, [s * 6, z], [s * 29, z], [DECK_Y, 0.8, 0.4], H.dark)
        seam(hull, [s * 6, 34], [s * 13, 34], [DECK_Y, 0.8, 0.4], H.dark)
        seam(hull, [s * 28.8, 20], [s * 28.8, -62], [DECK_Y, 0.8, 0.4], H.dark)
        vines(
            hull,
            [
                [s * 58, DECK_Y, 20],
                [s * 58, DECK_Y, -4],
                [s * 58, DECK_Y, -36],
                [s * 56, DECK_Y, -58],
            ],
        )
    moss(hull, [[12, DECK_Y, -64]])
    hazard(hull, [0, DECK_Y, 46], [28, 3], 7, 0)


def draw_pump_house(p: EnemyParts) -> None:
    """Draw the pump house.

    A lofted block, its windows lit as it charges, the stack and its pipes.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    # FB-DAM-BREAKER-02: the pump house a swollen hump of flesh over bone ribs, its stack grafted
    # on.
    flesh.loft(ROUND_SECTION, PUMP_HOUSE, F.slate)
    ribs(flesh, [-14, -2, 8], RibSpec(19, DECK_Y, 13.4, 0.9), F.bone)
    hull.box([30, 2.4, 1], H.dark, Placement([0, 13.6, 16.8], 0, 0.5))
    charge.box([26, 1, 0.6], WHITE, Placement([0, 14.1, 17.4], 0, 0.5))
    vent(hull, [10, 18, -12], [8, 7], 3)
    for s in SIDES:
        # Lit strips along the hump's flanks, following its swell (BOSS-52).
        seam(neon, [s * 15.2, -15], [s * 19.5, -5], [12, 0.6, 0.4], TOXIC)
        seam(neon, [s * 19.5, -5], [s * 17.7, 5], [12, 0.6, 0.4], TOXIC)
        conduit(hull, [s * 18, 10, -16], [s * 44, DECK_Y + 6, -10], 1.2, 3)
        conduit(hull, [s * 15, 8, 14], [s * 38, DECK_Y + 8, 20], 1, 2)
        lamps(neon, [[s * 9, 14.5, -16]], 1.4, TOXIC)
    moss(hull, [[-8, 18, -16], [12, 17.4, 4]])
    rod(hull, [-12, 18, -16], [-12, 30, -16], 0.4)
    lamps(neon, [[-12, 30, -16]], 1, TOXIC)


def draw_stack(p: EnemyParts) -> None:
    """Draw the stack on the pump house's back, its top where the core's rings leave from."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(DAM_STACK) == 0:
        return
    top = boss_point(DAM_STACK[0][0], DAM_STACK[0][1], DAM_STACK[0][2])
    height = top[1] - STACK_FOOT[1]
    hull.cylinder(6, height - 1, 8, H.base, Placement(table(STACK_FOOT)), 4.6)
    hull.ring(6.2, 1.6, 8, RUST, Placement(offset(STACK_FOOT, 0, 3, 0)))
    neon.ring(4.8, 1, 8, TOXIC, Placement(offset(top, 0, -2.4, 0)))
    charge.cylinder(3.6, 1, 8, WHITE, Placement(offset(top, 0, -1, 0)))
    muzzle(top, "ring")


def draw_guns(p: EnemyParts) -> None:
    """Draw the pump house's twin guns at its front (the core's aimed shots, bursts and fans)."""
    for m in DAM_CORE_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        length = 7
        base: Vec3 = offset(tip, 0, 0, -length - 1.4)
        p.hull.box([5, 4, 6], H.base, Placement(offset(base, 0, -2.4, -1)), SHADE["edge"])
        barrels(p, base, [1, 0], [1, length])


def draw_stern(p: EnemyParts) -> None:
    """Draw the stern: three reactors, a rudder housing and the dam-breaking ram's pistons."""
    for s in SIDES:
        reactor_sac(p, table([s * 20, 0, -72]), 4.5, TOXIC, F.sinew, None)
        p.hull.box([1.6, 8, 10], H.panel, Placement([s * 40, -8, -64]))
    reactor_sac(p, table([0, 0, -72]), 4, TOXIC, F.sinew, None)
    p.hull.box([30, 6, 8], H.base, Placement([0, DECK_Y, -64]), SHADE["edge"])
    p.neon.box([26, 0.5, 0.6], TOXIC, Placement([0, DECK_Y + 6, -59.8]))


def draw_mounts(p: EnemyParts) -> None:
    """Draw a socket for each sluice and tank mount on the deck (left once the part is gone).

    FB-DAM-BREAKER-03.
    """
    hull = p.hull
    for s in SIDES:
        hull.cylinder(9, 0.8, 8, H.dark, Placement([s * 46, DECK_Y, 20], math.pi / 8))
        hull.box([4, 2, 26], SHADE["edge"], Placement([s * 56, DECK_Y - 4, -14], 0, 0))
    hull.cylinder(1.2, 1, 4, H.dark, Placement([0, DECK_Y, 68], 0, QUARTER))


def dam_breaker_core(p: EnemyParts) -> None:
    """Add the core of the Dam Breaker: its hull, pump house, stack, guns, stern and mounts."""
    draw_hull(p)
    draw_pump_house(p)
    draw_stack(p)
    draw_guns(p)
    draw_stern(p)
    draw_mounts(p)


def build_dam_breaker(scene: Any) -> Any:
    """FB-DAM-BREAKER-01, FB-DAM-BREAKER-05: the Dam Breaker, a giant armoured barge.

    With toxic green neon: sluice gate houses letting out sludge, glowing chemical tanks at its
    sides, an armour plate and a drone hangar on its bow, a pump house and its stack amidships,
    swamp growth over its rusty decks. The plating of its flank decks (`flanks`) and of its bow's
    wing decks (`wings`) is the armour it sheds.
    """
    parts: dict[str, Any] = {
        "sluice-left": sluice,
        "sluice-right": sluice,
        "plate": plate,
        "tank-left": tank,
        "tank-right": tank,
        "hangar": hangar,
    }
    return build_boss_model(
        DAM_BREAKER,
        scene,
        TOXIC,
        {
            "core": dam_breaker_core,
            "parts": parts,
            "armour": {"flanks": {"whole": flank_plating}, "wings": {"whole": wing_plating}},
        },
    )
