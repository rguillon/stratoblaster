"""P09-R09, 3-4: the Dam Breaker's parts (sluice cannons, chemical tanks, armour plate, drone
hangar) and its swamp growth. Ported from `view/bosses/world-3/dam-breaker-parts.ts`. Logical
pixels, nose +Z, Y up (towards the camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.boss_kit import mirror
from game.config.bosses.world_3.dam_breaker import DAM_SPOUT
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.final_boss_greebles import rod
from game.view.bosses.mini_boss_greebles import (
    hazard,
    lamps,
    rect,
    vent,
)
from game.view.bosses.mini_boss_mechanism import cog
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
)
from game.view.bosses.world_3.jungle_flesh import F, gland, sign_of, table, vein_to
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The Dam Breaker's toxic green neon.
TOXIC = BOSS_LOOK.neon["dam-breaker"]
# Swamp moss on its ledges, the vines hanging over its sides, and rust (World 3 growth).
MOSS = [0.13, 0.2, 0.07]
VINE = [0.08, 0.14, 0.05]
RUST = [0.2, 0.1, 0.05]
# Height of the barge's deck.
DECK_Y = 4


def moss(hull: SolidBuilder, points: list[Vec3], size: float = 3) -> None:
    """Moss cushions at each point (`[x, y, z]`)."""
    for i in range(len(points)):
        r = size * (0.75 + (i % 3) * 0.2)
        hull.cylinder(r, r * 0.45, 5, MOSS, Placement(points[i], i * 0.9), r * 0.4)


def vines(hull: SolidBuilder, points: list[Vec3], drop: float = 7) -> None:
    """Vines hanging over an edge from each point (`[x, y, z]`), drooping by `drop`."""
    for i in range(len(points)):
        x = points[i][0]
        y = points[i][1]
        z = points[i][2]
        out = sign_of(x) * 1.5
        low: Vec3 = [x + out, y - drop * (0.7 + (i % 2) * 0.4), z + (i % 3) - 1]
        rod(hull, [x, y, z], low, 0.45, VINE)


def sluice(p: EnemyParts, at: Vec3) -> None:
    """A sluice cannon around its centre `at` (P09-R09): a gate house on the deck, its sluice gate
    raised over a chute whose lip lets out the sludge, a hand wheel on top, a green glow inside."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # The left sluice (screen left) is on the model's +X side.
    spouts = DAM_SPOUT if at[0] > 0 else mirror(DAM_SPOUT)
    if len(spouts) == 0:
        return
    lip = boss_point(spouts[0][0], spouts[0][1], spouts[0][2])
    # P16-R06: a gland swelling out of the beast's back, a metal sluice gate grafted in its mouth.
    p.flesh.box([22, 12, 14], F.crimson, Placement(offset(at, 0, DECK_Y, -2)), F.sinew)
    gland(p, offset(at, 0, DECK_Y + 12, -5), 3, TOXIC)
    # The gate, raised in its frame, and the dark culvert under it.
    hull.box([16, 6, 1.6], SHADE["edge"], Placement(offset(at, 0, DECK_Y + 8, 5.6)))
    hull.box([15, 6, 0.6], H.dark, Placement(offset(at, 0, DECK_Y + 0.5, 5.4)))
    for s in SIDES:
        hull.box([2, 16, 2.4], H.panel, Placement(offset(at, s * 9, DECK_Y, 5.4)))
        neon.box([0.6, 14, 0.5], TOXIC, Placement(offset(at, s * 7.7, DECK_Y + 1, 6.7)))
    # The chute out to its lip.
    hull.box(
        [14, 1.2, 11],
        H.panel,
        Placement([lip[0], lip[1] - 1.6, lip[2] - 5.5], 0, -0.12),
    )
    charge.box(
        [11, 0.4, 9],
        WHITE,
        Placement([lip[0], lip[1] - 1, lip[2] - 5.5], 0, -0.12),
    )
    neon.box([14, 0.6, 0.6], TOXIC, Placement([lip[0], lip[1] - 0.6, lip[2] - 0.3]))
    muzzle(lip)
    cog(hull, offset(at, 0, DECK_Y + 14.4, -3), 4.2, 8)
    hull.cylinder(0.8, 2.4, 4, H.dark, Placement(offset(at, 0, DECK_Y + 12, -3)))
    moss(
        hull,
        [offset(at, 7, DECK_Y + 12, -7), offset(at, -8, DECK_Y + 12, -6)],
        2.2,
    )


# A chemical tank's body: a capsule lying along Z (a lathe profile, its axis along +Y).
TANK = table(
    [
        [0, -17],
        [7, -16],
        [11, -13],
        [12, -9],
        [12, 9],
        [11, 13],
        [7, 16],
        [0, 17],
    ]
)


def tank(p: EnemyParts, at: Vec3) -> None:
    """A chemical tank around its centre `at` (P09-R09): a fat capsule on cradles at the barge's
    side, glowing green through bands of glass, hooped with rusty straps, vines hanging off it."""
    hull = p.hull
    neon = p.neon
    s = sign_of(at[0])
    axis = offset(at, 0, 12, 0)
    # P16-R06: a bloated toxin bladder of teal flesh, hooped by rusty grafted straps.
    p.flesh.lathe(TANK, 7, F.teal, Placement(axis, math.pi / 8, QUARTER))
    for dz in [-9, 0, 9]:
        neon.ring(12.2, 3, 8, TOXIC, Placement(offset(axis, 0, 0, dz - 1.5), 0, QUARTER))
    for ring_z in [-13, -4.5, 4.5, 13]:
        hull.ring(12.4, 1.6, 8, RUST, Placement(offset(axis, 0, 0, ring_z - 0.8), 0, QUARTER))
    # The cradles and the outrigger beams back to the hull.
    for dz in [-8, 8]:
        hull.box([18, 4, 3], H.dark, Placement(offset(at, 0, 0, dz)))
        hull.box([16, 3, 3], H.panel, Placement(offset(at, -s * 16, 1, dz)), SHADE["edge"])
    hull.box([5, 3, 4], H.panel, Placement(offset(axis, 0, 11, 14)))
    lamps(neon, [offset(axis, 0, 14.4, 14)], 1.3, TOXIC)
    vines(
        hull,
        [
            offset(at, s * 9, 18, -6),
            offset(at, s * 10, 16, 5),
            offset(at, s * 8, 19, 12),
        ],
    )
    moss(hull, [offset(axis, -s * 3, 11.6, -6)], 2.4)


# The armour plate seen from above: a wide, chamfered slab over the bow (around its centre).
PLATE = table([[-22, -6], [-18, 9], [18, 9], [22, -6], [14, -12], [-14, -12]])


def plate(p: EnemyParts, at: Vec3) -> None:
    """The armour plate around its centre `at` (P09-R09): a thick, sloped slab bolted over the
    bow, no weapon, hazard stripes along its front edge, green slits, moss in its seams."""
    hull = p.hull
    neon = p.neon
    top = DECK_Y + 9
    hull.bevel_slab(
        PLATE,
        [DECK_Y, top - 3, top],
        [0, 2.4],
        H.base,
        Placement(at),
        SHADE["edge"],
    )
    hazard(hull, offset(at, 0, top, -7.5), [24, 3], 8, 0)
    for s in SIDES:
        neon.box([0.8, 0.4, 9], TOXIC, Placement(offset(at, s * 12, top + 0.05, 1.5), s * 0.25))
        for dz in [-4, 4]:
            hull.cylinder(0.9, 0.6, 5, SHADE["edge"], Placement(offset(at, s * 17, top - 1.4, dz)))
    hull.box([10, 1, 6], H.panel, Placement(offset(at, 0, top, 3)), SHADE["edge"])
    moss(hull, [offset(at, -15, top - 1.5, 6), offset(at, 9, top, -2)], 2)


def hangar(p: EnemyParts, at: Vec3) -> None:
    """The drone hangar around its centre `at` (P09-R09): a bay at the bow, its open door framed
    in green, where its Hornets leave from."""
    hull = p.hull
    neon = p.neon
    # P16-R06: a brood pouch of flesh on the bow, its drone hatch a grafted metal door.
    p.flesh.bevel_slab(
        rect(26, 20),
        [DECK_Y - 4, DECK_Y, DECK_Y + 7],
        [1, 1.5],
        F.purple,
        Placement(at),
        F.crimson,
    )
    vein_to(
        p,
        [offset(at, -11, DECK_Y + 7.2, -8), offset(at, 11, DECK_Y + 7.2, -8)],
        [0, 1, 4],
        TOXIC,
    )
    hull.box([18, 6, 0.8], H.dark, Placement(offset(at, 0, DECK_Y - 1.5, 9.8)))
    neon.box([20, 0.8, 0.6], TOXIC, Placement(offset(at, 0, DECK_Y + 4.8, 10.2)))
    for s in SIDES:
        neon.box([0.8, 6, 0.6], TOXIC, Placement(offset(at, s * 9.8, DECK_Y - 1.4, 10.2)))
        lamps(neon, [offset(at, s * 11, DECK_Y + 7, 7)], 1.2, TOXIC)
    vent(hull, offset(at, 0, DECK_Y + 7, -3), [12, 8], 4)
    vines(hull, [offset(at, 12, DECK_Y + 6, 9), offset(at, -4, DECK_Y + 6, 10)], 6)
