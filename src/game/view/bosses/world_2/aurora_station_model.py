"""P08-R10, 2-3: the Aurora Station

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_2.aurora_station import (
    AURORA_COLLAR,
    AURORA_HUB_GUNS,
    AURORA_STATION,
)
from game.view.enemies.enemy_shapes import POD_SECTION, SIDES  # noqa: E402
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import curve, organ, tendril  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402

__pragma__("noskip")

from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, plate, rect, seam  # noqa: E402
from game.view.bosses.mini_boss_shapes import (  # noqa: E402
    QUARTER,
    SHADE,
    WHITE,
    H,
    socket,
)
from game.view.bosses.world_2.aurora_station_parts import (  # noqa: E402
    AURORA_GREEN,
    AURORA_VIOLET,
    cryo_cannon,
    cryo_turret,
    dish,
    emitter,
    emitter_turret,
    hangar,
    iced,
    icicles,
)
from game.view.bosses.world_2.w2_organic import (  # noqa: E402
    ICE_FLESH,
    crystals,
    glow_vein,
    sinew,
)

# The hub: a wide octagonal drum (a lathe profile).
HUB = [  # type: list[list[float]]
    [0.0, -6.0],
    [20.0, -6.0],
    [25.0, -2.0],
    [25.0, 3.0],
    [21.0, 7.0],
    [0.0, 7.0],
]
# An eighth of a turn: the octagons' flat faces to the front.
EIGHTH = math.pi / 8
# A habitat module behind the hub (loft stations; one either side of the centre line).
HABITAT = [  # type: list[list[float]]
    [-56.0, 4.0, -2.0, 6.0],
    [-50.0, 7.0, -3.0, 9.0],
    [-26.0, 7.0, -3.0, 9.0],
    [-20.0, 5.0, -1.0, 7.0],
]
# A radiator wing behind the truss (the right one; mirrored for the left).
RADIATOR = [  # type: list[list[float]]
    [20.0, -24.0],
    [76.0, -26.0],
    [84.0, -32.0],
    [84.0, -46.0],
    [20.0, -48.0],
]
# Where the radiators' icicles hang (one radiator; mirrored for the other).
RADIATOR_ICICLES = [  # type: list[list[float]]
    [30.0, -0.6, -47.0],
    [46.0, -0.6, -46.5],
    [62.0, -0.6, -46.0],
    [78.0, -0.6, -45.0],
]


def draw_hub(p: EnemyParts) -> None:
    """The hub, its module and the mast the turning dish stands on; the collar its spirals leave."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    # P16-R06: the bell of a great ice jellyfish, a metal collar grafted round its crown.
    flesh.lathe(HUB, 8, ICE_FLESH.purple, Placement(None, EIGHTH))
    flesh.cylinder(20.5, 0.3, 8, ICE_FLESH.rime, Placement([0.0, 7.0, 0.0], EIGHTH))
    neon.ring(25.1, 1.0, 8, AURORA_GREEN, Placement([0.0, -0.5, 0.0], EIGHTH))
    hull.cylinder(11.0, 6.0, 8, H.panel, Placement([0.0, 7.0, 0.0], EIGHTH), 10.0)
    for a in [0, 1, 2, 3, 4, 5]:
        yaw = a * math.pi / 3 + 0.3
        glow_vein(
            p,
            [math.sin(yaw) * 11.0, 7.4, math.cos(yaw) * 11.0],
            [math.sin(yaw) * 23.0, 3.0, math.cos(yaw) * 23.0],
            1.0,
            AURORA_GREEN,
        )
    neon.ring(10.9, 0.8, 8, AURORA_VIOLET, Placement([0.0, 9.5, 0.0], EIGHTH))
    for m in AURORA_COLLAR:
        collar = boss_point(m[0], m[1], m[2])
        charge.cylinder(
            4.2,
            1.0,
            8,
            WHITE,
            Placement([collar[0], collar[1] - 1.0, collar[2]]),
        )
        muzzle(collar, "ring")
        hull.cylinder(1.8, 5.0, 6, H.dark, Placement(collar))
    for s in SIDES:
        crystals(flesh, [s * 16.0, 6.5, -8.0], 3.5)
        socket(hull, [s * 36.0, 1.0, 40.0], 7.5, 0.8)


def draw_truss(p: EnemyParts) -> None:
    """The truss: a girder across to the cryo cannons, struts to the emitters, the spine."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R06: a spine of bone across to the cryo bladders, arms of sinew out to the emitters.
    flesh.box([10.0, 5.0, 26.0], ICE_FLESH.sinew, Placement([0.0, -1.0, 33.0]), ICE_FLESH.rime)
    for s in SIDES:
        tendril(
            flesh,
            curve([s * 20.0, 0.0, -4.0], [s * 58.0, 0.0, -4.0], [0.0, 2.0, 1.0], 3),
            [3.0, 2.2],
            5,
            ICE_FLESH.bone,
        )
        sinew(flesh, [s * 15.0, 0.0, 14.0], [s * 33.0, 0.0, 36.0], 2.2, ICE_FLESH.sinew)
        for x in [30, 42]:
            organ(
                flesh,
                2.6,
                5,
                ICE_FLESH.bone,
                Placement([s * x, -2.5, -4.0]),
                0.9,
            )
        hull.ring(3.2, 1.2, 6, H.panel, Placement([s * 50.0, 0.0, -4.0], 0, 0, QUARTER))
        neon.box(
            [30.0, 0.5, 0.6],
            AURORA_GREEN if s > 0 else AURORA_VIOLET,
            Placement([s * 38.0, 0.6, -0.4]),
        )


def draw_habitats(p: EnemyParts) -> None:
    """The habitat modules behind the hub (violet windows) and their reactors."""
    hull = p.hull
    neon = p.neon
    for s in SIDES:
        p.flesh.loft(
            POD_SECTION,
            HABITAT,
            ICE_FLESH.membrane,
            Placement([s * 12.0, 0.0, 0.0]),
            LoftOptions(False, lambda side, band: iced(side)),
        )
        lamps(
            neon,
            [[s * 19.0, 4.0, z] for z in [-28.0, -34.0, -40.0, -46.0]],
            1.2,
            AURORA_VIOLET,
        )
        reactor_sac(p, [s * 12.0, 2.5, -56.0], 3.4, AURORA_GREEN, ICE_FLESH.purple)
    tendril(
        p.flesh,
        curve([0.0, 0.0, -20.0], [0.0, 0.0, -52.0], [0.0, 2.0, 0.0], 3),
        [2.6, 1.0],
        5,
        ICE_FLESH.sinew,
    )
    plate(hull, rect(5.0, 8.0), [2.8, 0.5], H.panel, Placement([0.0, 0.0, -30.0]))


def draw_radiators(p: EnemyParts) -> None:
    """The radiator wings behind the truss: iced panels, dark ribs, a green edge light."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        # P16-R06: frilled membrane fins on bone rays, where the radiators were.
        outline: list[OutlinePoint] = [[s * p0[0], p0[1]] for p0 in RADIATOR]
        flesh.bevel_slab(
            outline,
            [-0.6, 0.0, 1.0],
            [0.4, 0.6],
            ICE_FLESH.membrane,
            None,
            ICE_FLESH.teal,
        )
        for x in [30.0, 42.0, 54.0, 66.0, 78.0]:
            sinew(
                flesh,
                [s * (x - 4.0), 1.0, -25.0],
                [s * x, 1.0, -46.5],
                0.6,
                ICE_FLESH.bone,
                [0.0, 0.4, 0.0],
            )
        seam(neon, [s * 84.2, -32.0], [s * 84.2, -46.0], [0.2, 0.5, 0.6], AURORA_GREEN)
        seam(hull, [s * 18.0, -30.0], [s * 21.0, -30.0], [0.0, 3.0, 3.0], H.panel)
        icicles(flesh, RADIATOR_ICICLES, s)


def draw_guns(p: EnemyParts) -> None:
    """The hub guns either side of the hangar's spine (the core's aimed shots, bursts and fans)."""
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    for m in AURORA_HUB_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([4.0, 4.5, 6.0], H.panel, Placement([x, y - 3.0, z - 7.0]), SHADE["edge"])
        hull.cylinder(1.3, 6.4, 6, H.dark, Placement([x, y, z - 7.0], 0, QUARTER))
        charge.cylinder(1.35, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


def draw_core(p: EnemyParts) -> None:
    """The core: the hub, the truss, the habitats, the radiators and the guns."""
    draw_hub(p)
    draw_truss(p)
    draw_habitats(p)
    draw_radiators(p)
    draw_guns(p)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """What `build_boss_model` draws a boss from: a plain
    object, with `ring` and `limbs` None when absent."""
    drawing: Any = None
    __pragma__(
        "js",
        "{}",
        """
    drawing = {core: core, parts: parts, turrets: turrets, limbs: limbs, ring: ring};
    """,
    )
    return drawing


def build_aurora_station(scene: Any) -> BuiltEnemyModel:
    """P08-R10: the Aurora Station, a flying research station in green and violet neon: a hub under
    a slowly turning dish, two dish emitters and a drone hangar at its nose, two cryo cannons at
    the ends of its truss, habitat modules and iced radiator wings behind.
    P16-R06: now a living ice jellyfish, a bell of cold flesh under a frilled crown, a bone spine
    out to its cryo bladders, egg sacs and membrane fins behind, metal grafts on its guns."""
    model: BuiltEnemyModel = build_boss_model(
        AURORA_STATION,
        scene,
        AURORA_GREEN,
        boss_drawing(
            draw_core,
            {
                "emitter-left": emitter,
                "emitter-right": emitter,
                "cryo-left": cryo_cannon,
                "cryo-right": cryo_cannon,
                "hangar": hangar,
            },
            {
                "cryo-left": cryo_turret,
                "cryo-right": cryo_turret,
                "emitter-left": emitter_turret,
                "emitter-right": emitter_turret,
            },
            None,
            dish,
        ),
    )
    return model
