"""P08-R10, 2-5: the Boreal Citadel's destroyable parts (aurora cannons, missile batteries, dome
generators) Each is drawn around its
centre (model space: logical pixels, nose +Z, Y up)."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_2.boreal_citadel import BOREAL_BATTERY, BOREAL_CANNON  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    QUARTER,
    WHITE,
)
from game.view.bosses.world_2.boreal_citadel_city import (  # noqa: E402
    AURORA,
    CITADEL_DECK,
    VIOLET,
    icicles,
    rect,
)
from game.view.bosses.world_2.w2_organic import ICE_FLESH  # noqa: E402
from game.view.enemies.enemy_shapes import POD_SECTION, around, decal, radial  # noqa: E402
from render.geometry.organic import RibSpec, ribs  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

H = ENEMY_LOOK.hull

# Height of the outriggers' top, where the aurora cannons sit.
OUTRIGGER_TOP = 3

# An aurora cannon's pod (loft stations around its centre), snowed over on its back.
CANNON_POD = [
    [-14.0, 6.0, 0.0, 7.0],
    [-4.0, 8.0, -0.5, 9.0],
    [12.0, 7.0, 0.0, 8.0],
    [21.0, 4.5, 1.5, 6.0],
]
POD_BACK = 2
# The lens at the front of its barrel (lathe profile, along the barrel).
LENS = [
    [0.0, 0.0],
    [3.4, 1.0],
    [2.4, 3.0],
    [0.0, 3.6],
]
# The aurora curtains on its back: thin lit fins, green below and violet along their tops.
CURTAINS = [-3.2, 0.0, 3.2]

# A missile battery's armoured block (around its centre), and the size of a cell's hatch.
BATTERY = rect(24, 26)
HATCH = [7.0, 5.6]

# A dome generator's pedestal and heated glass dome (lathe profiles, bottom to top).
PEDESTAL = [
    [12.0, 0.0],
    [12.5, 2.0],
    [10.5, 4.5],
    [0.0, 4.5],
]
DOME = [
    [9.0, 0.0],
    [8.0, 3.8],
    [5.0, 6.6],
    [0.0, 7.6],
]


def draw_cannon(p: EnemyParts, pos: Vec3) -> None:
    """P08-R10: an aurora cannon on an outrigger, turning on its turntable (its turret, phase 8
    review): a frosted pod, a long barrel with charge coils, a lens where its laser leaves, and
    lit aurora curtains rippling along its back."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = pos[0]
    z = pos[2]
    at: Vec3 = [x, OUTRIGGER_TOP, z]
    # P16-R06: a swollen gun organ, its barrel a metal graft, its curtains lit fins on its back.
    flesh.loft(
        POD_SECTION,
        CANNON_POD,
        ICE_FLESH.purple,
        Placement(at),
        LoftOptions(
            False,
            lambda side, band: ICE_FLESH.rime if side == POD_BACK else None,
        ),
    )
    m = BOREAL_CANNON[0]
    tip = boss_point(-x, m[1], m[2])

    def along(dz: float) -> Placement:
        return Placement([x, tip[1], dz], 0, QUARTER)

    lens_at = tip[2] - LENS[3][1]
    hull.cylinder(2.6, lens_at - (z + 20), 6, H.dark, along(z + 20))
    for dz in [z + 23, z + 27]:
        charge.ring(3.2, 1.3, 6, WHITE, along(dz))
    charge.lathe(LENS, 6, WHITE, along(lens_at))
    muzzle(tip, "laser")
    for i, dx in enumerate(CURTAINS):
        top = OUTRIGGER_TOP + 9 + (i % 2) * 1.5
        sway = (i - 1) * 0.12
        neon.box([0.35, 3.2, 14 - i * 2], AURORA, Placement([x + dx, top, z - 2], sway))
        neon.box([0.45, 0.8, 14 - i * 2], VIOLET, Placement([x + dx, top + 3.2, z - 2], sway))
    hull.box([12, 1.2, 5], H.panel, Placement([x, OUTRIGGER_TOP + 1, z - 13]), H.base)
    # Ribs along its flanks.
    ribs(
        flesh,
        [z - 6, z, z + 6],
        RibSpec(8.4, OUTRIGGER_TOP, 8.5, 0.6),
        ICE_FLESH.bone,
        Placement([x, 0, 0]),
    )


def draw_cannon_mount(p: EnemyParts, pos: Vec3) -> None:
    """The turntable an aurora cannon turns on (phase 8 review: its turret, drawn by
    `draw_cannon`, aims its laser): a low drum on the outrigger, ringed with violet neon."""
    x = pos[0]
    z = pos[2]
    # P16-R06: a shoulder of muscle on the fin.
    p.flesh.cylinder(10, OUTRIGGER_TOP, 8, ICE_FLESH.sinew, Placement([x, 0, z]), 9)
    p.neon.ring(10.3, 0.6, 8, VIOLET, Placement([x, OUTRIGGER_TOP - 0.4, z]))


def draw_battery(p: EnemyParts, pos: Vec3) -> None:
    """P08-R10: a missile battery on the deck: a snowed-over armoured block, six hatches lit as
    its missiles load, violet strips down its sides, icicles under its front."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    x = pos[0]
    z = pos[2]
    battery = BOREAL_BATTERY if x < 0 else mirror(BOREAL_BATTERY)
    cells = [boss_point(q[0], q[1], q[2]) for q in battery]
    height = cells[0][1] if len(cells) > 0 else 0
    top = height - 0.08
    base = CITADEL_DECK.top
    # P16-R06: an armoured growth, a mound of flesh under a metal hatch plate.
    flesh.bevel_slab(
        BATTERY,
        [base - 1, base, top - 1.2],
        [0, 3],
        ICE_FLESH.crimson,
        Placement([x, 0, z]),
        ICE_FLESH.purple,
    )
    hull.bevel_slab(
        rect(18, 20),
        [top - 1.4, top - 0.6, top],
        [0, 0.6],
        H.base,
        Placement([x, 0, z]),
        H.panel,
    )
    for c in cells:
        cx = c[0]
        cz = c[2]
        decal(hull, rect(HATCH[0], HATCH[1], [cx, cz]), top + 0.04, H.dark)
        decal(charge, rect(HATCH[0] - 2, HATCH[1] - 2, [cx, cz]), height, WHITE)
        muzzle([cx, height, cz], "missile")
    for s in [-1, 1]:
        neon.box([0.6, 1.4, 20], VIOLET, Placement([x + s * 12.2, base + 3.4, z]))
    neon.box([18, 1.2, 0.6], AURORA, Placement([x, base + 3.4, z + 13.2]))
    icicles(
        flesh,
        [[x - 10, z + 13.4], [x + 10, z + 13.4]],
        top,
        4,
    )


def draw_dome(p: EnemyParts, pos: Vec3) -> None:
    """P08-R10: a dome generator (no weapon; it shields the core): a heated glass dome glowing
    aurora green through its ring of ice, three pylons with violet lights."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    x = pos[0]
    z = pos[2]
    base = CITADEL_DECK.top
    # P16-R06: a glowing blister swelling from the flesh, held by bone spikes.
    flesh.lathe(PEDESTAL, 8, ICE_FLESH.purple, Placement([x, base, z], math.pi / 8))
    hull.ring(12.6, 1, 8, H.panel, Placement([x, base + 1.2, z], math.pi / 8))
    neon.ring(12.7, 0.6, 8, VIOLET, Placement([x, base + 0.4, z], math.pi / 8))
    neon.lathe(DOME, 8, AURORA, Placement([x, base + 4.5, z]))
    flesh.ring(9.4, 1, 8, ICE_FLESH.sinew, Placement([x, base + 4.4, z]))
    for a in around(3):
        spoke = radial(a + math.pi / 3, 11, 0)
        px = spoke[0]
        pz = spoke[2]
        pylon = rect(2.6, 2.6, [x + px, z + pz])
        flesh.bevel_slab(
            pylon,
            [base + 4, base + 4, base + 15],
            [0, 1.1],
            ICE_FLESH.bone,
            None,
            ICE_FLESH.rime,
        )
        decal(neon, rect(1.4, 1.4, [x + px, z + pz]), base + 15.05, VIOLET)
