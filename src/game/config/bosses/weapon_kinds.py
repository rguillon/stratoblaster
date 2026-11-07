# Copyright (c) 2026 Renaud Guillon
"""The kinds of hidden weapon a boss reveals as it transforms (BOSS-40; D-221, D-229).

Design: docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-design.md. Their
sizes, muzzles and volleys.

- `gatling`: a three-barrelled turret that follows the player (bursts);
- `lance`: a laser lance pointing down the screen (lasers);
- `rack`: a box of four missile cells (homing missiles);
- `orb`: a glowing emitter on top (rings);
- `beam`: the Scorpion's tail cannon (a giant laser, D-228);
- `cannon`: a big turret with one heavy barrel (aimed spreads of large, slow shells);
- `mortar`: a short, wide tube tilted up on a round base (flak shells that burst into rings);
- `battery`: a long, low gun deck, five barrels in a row (wide fans straight down);
- `sweeper`: a turret with a two-pronged emitter (a laser that sweeps after the player);
- `hangar`: a box bay whose doors slide open (it launches Hornets).

Muzzles are worked out here from a weapon's size; the boss view draws its model with the same
numbers (`game/view/bosses/hidden_weapon_shapes.py`). Offsets in px from the boss's centre, X right,
Y up (its nose points down, at -Y), and heights above the playfield.
"""

from game.config.bosses.boss_guns import gun_mount, laser_mount, missile_mount
from game.config.bosses.boss_kit import bullet, bursting, sweeping, volley
from game.config.record import record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


KINDS = [
    "gatling",
    "lance",
    "rack",
    "orb",
    "beam",
    "cannon",
    "mortar",
    "battery",
    "sweeper",
    "hangar",
]

# Shares of a weapon's radius `r`. The pod: an octagon of `pod` r, `height` r high (unless given).
# The gatling's turret: `turret` r across, three barrels `gap` of the turret apart, `bore` and
# `length` of it. The lance: `lance` r long, `lanceBore` r thick. The rack's cells: `cell` r round,
# `cellX` and `cellY` r off its centre, `cellTop` r above the pod. The orb: `orb` r round, its
# centre `orbTop` r above the pod.
# The cannon's turret: `cannonTurret` r round on a square base `cannonBase` r across, one barrel
# `cannonBore` of the turret thick and `cannonLength` of it long. The mortar: a round base
# `mortarBase` r across, its tube `mortarBore` r round and `mortarLength` r long, its foot
# `mortarBack` r behind the centre and `mortarFoot` r over the pod, tilted `mortarDeg` up from the
# hull towards the nose.
# The battery: a deck `deckWidth` r across and `deckDepth` r deep, `barrels` barrels `barrelGap` r
# apart, `barrelBore` r round and `barrelLength` r long out of its front, `barrelLift` of the deck's
# height up. The sweeper: its turret `sweeperTurret` r round, two prongs `prongGap` r apart and
# `prongLength` r long, the lens between their tips `lensLift` of the turret over the pod. The
# hangar: a box `bayWidth` r across and `bayDepth` r deep.
WEAPON_SHAPE = record({
    "pod": 0.9,
    "height": 0.5,
    "turret": 0.62,
    "gap": 0.32,
    "bore": 0.12,
    "length": 0.9,
    "lance": 1.9,
    "lanceBore": 0.2,
    "cell": 0.16,
    "cellX": 0.32,
    "cellY": 0.28,
    "cellTop": 0.3,
    "orb": 0.38,
    "orbTop": 0.42,
    "cannonTurret": 0.72,
    "cannonBase": 0.8,
    "cannonBore": 0.24,
    "cannonLength": 1.5,
    "mortarBase": 0.95,
    "mortarBore": 0.32,
    "mortarLength": 0.95,
    "mortarBack": 0.2,
    "mortarFoot": 0.15,
    "mortarDeg": 55,
    "deckWidth": 1.9,
    "deckDepth": 0.9,
    "barrels": 5,
    "barrelGap": 0.4,
    "barrelBore": 0.1,
    "barrelLength": 0.7,
    "barrelLift": 0.7,
    "sweeperTurret": 0.6,
    "prongGap": 0.36,
    "prongLength": 1.25,
    "lensLift": 0.3,
    "bayWidth": 1.8,
    "bayDepth": 1.5,
})

# The barrels round an orb's rotor: one for each bullet of its rings.
ORB_BARRELS = 10

# A giant laser (D-228): `width` px wide (four of the usual), firing `firing` seconds every
# `every` seconds.
BEAM = record({"width": 44, "firing": 2.4, "every": 7})

# What each kind fires (D-229): the cannon's shells and the battery's and mortar's bullets, and how
# many a hangar launches of which kind.
WEAPON_FIRE = record({
    "cannon": {"every": 2.4, "count": 3, "spacingDeg": 12, "speed": 150, "radius": 7},
    "mortar": {"every": 3.2, "speed": 110, "radius": 8, "after": 1.1, "count": 8, "small": 170},
    "battery": {"every": 2.0, "count": 7, "spacingDeg": 9, "speed": 180},
    "sweeper": {"every": 8, "firing": 2.0},
    "hangar": {"kind": "hornets", "count": 2, "every": 7},
})


def pod_height(radius: float, height: Any) -> float:
    """Return the height of a weapon's pod's top: `height` when given, else its share of the radius.

    `height` may be `[base, top]`: a pod standing on a surface above the playfield (see `pod_base`).
    """
    if height == None:
        value: float = radius * WEAPON_SHAPE.height
        return value
    if isinstance(height, list):
        top: float = height[1]
        return top
    given: float = height
    return given


def pod_base(height: Any) -> float:
    """Return the height a weapon's pod stands on: `height`'s base, `[base, top]`, else 0.

    A pod on a wing stands on its membrane, not through it from the playfield.
    """
    if isinstance(height, list):
        base: float = height[0]
        return base
    return 0.0


def _gun(part_id: str, at: list[Any], h: float, options: Any) -> list[Any]:
    return [gun_mount(part_id, part_id, at, h, options)]


def _gatling_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return three barrels side by side on a turret, taking turns (its bursts)."""
    size = r * WEAPON_SHAPE.turret
    return _gun(
        part_id,
        at,
        h,
        {
            "size": size,
            "barrels": 3,
            "gap": size * WEAPON_SHAPE.gap,
            "bore": size * WEAPON_SHAPE.bore,
            "length": size * WEAPON_SHAPE.length,
        },
    )


def _cannon_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return three heavy barrels side by side on a big turret, sweeping its spreads."""
    size = r * WEAPON_SHAPE.cannonTurret
    bore = size * WEAPON_SHAPE.cannonBore * 0.7
    return _gun(
        part_id,
        at,
        h,
        {
            "size": size,
            "barrels": WEAPON_FIRE.cannon.count,
            "gap": bore * 2.4,
            "bore": bore,
            "length": size * WEAPON_SHAPE.cannonLength,
        },
    )


def _mortar_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return one short, wide barrel on a squat turret: its flak shells."""
    return _gun(
        part_id,
        at,
        h,
        {
            "size": r * WEAPON_SHAPE.mortarBase * 0.7,
            "barrels": 1,
            "bore": r * WEAPON_SHAPE.mortarBore,
            "length": r * WEAPON_SHAPE.mortarLength,
        },
    )


def _battery_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return a row of barrels on a low turret, sweeping its fans across the screen."""
    return _gun(
        part_id,
        at,
        h,
        {
            "size": r * WEAPON_SHAPE.deckDepth * 0.6,
            "barrels": WEAPON_SHAPE.barrels,
            "gap": r * WEAPON_SHAPE.barrelGap * 0.6,
            "bore": r * WEAPON_SHAPE.barrelBore,
            "length": r * WEAPON_SHAPE.barrelLength,
        },
    )


def _orb_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return a rotor: barrels all round a spinning hub, one for each bullet of its rings."""
    return _gun(
        part_id,
        at,
        h,
        {
            "size": r * WEAPON_SHAPE.orb,
            "barrels": ORB_BARRELS,
            "layout": "ring",
            "bore": r * 0.07,
            "length": r * 0.42,
        },
    )


def _lance_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return a laser lance pointing down the screen, on a fixed base."""
    return [
        laser_mount(
            part_id,
            part_id,
            at,
            h,
            {
                "size": r * 0.45,
                "bore": r * WEAPON_SHAPE.lanceBore,
                "length": r * WEAPON_SHAPE.lance,
            },
        )
    ]


def _beam_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return a giant laser's emitter, pointing out behind the boss (D-228: the Scorpion's tail)."""
    return [
        laser_mount(
            part_id,
            part_id,
            at,
            h,
            {"size": r * 0.6, "bore": r * 0.32, "length": r * 1.1, "restDeg": 180},
        )
    ]


def _sweeper_mounts(part_id: str, at: list[Any], h: float, r: float) -> list[Any]:
    """Return a laser on a turret that follows the player (its beam sweeps)."""
    return [
        laser_mount(
            part_id,
            part_id,
            at,
            h,
            {
                "size": r * WEAPON_SHAPE.sweeperTurret,
                "bore": r * 0.16,
                "length": r * WEAPON_SHAPE.prongLength,
                "turret": True,
            },
        )
    ]


def _rack_mounts(part_id: str, at: list[Any], h: float, _r: float) -> list[Any]:
    """Return a block of four missile ports."""
    return [missile_mount(part_id, part_id, at, h, 4)]


def _hangar_mounts(_part_id: str, _at: list[Any], _h: float, _r: float) -> list[Any]:
    return []


# The mounts of each kind (BOSS-58): `(part id, at, pod height, radius) -> mounts`.
MOUNTS_OF = {
    "gatling": _gatling_mounts,
    "cannon": _cannon_mounts,
    "lance": _lance_mounts,
    "beam": _beam_mounts,
    "rack": _rack_mounts,
    "orb": _orb_mounts,
    "mortar": _mortar_mounts,
    "battery": _battery_mounts,
    "sweeper": _sweeper_mounts,
    "hangar": _hangar_mounts,
}


def _known(kind: str) -> None:
    if kind not in KINDS:
        raise ValueError('Unknown hidden weapon kind "' + kind + '"')


def weapon_mounts(kind: str, part_id: str, at: list[Any], radius: float, height: Any) -> Any:
    """Return the mounts of a weapon of `kind` centred on `at`, on its pod (BOSS-58).

    One mount each, named as its part: three gun models (a gatling's or a cannon's turret, a
    mortar's, a battery's fixed fan, an orb's rotor), lasers (a lance, a beam, a sweeper's turret),
    a missile block (a rack); none for a hangar.
    """
    _known(kind)
    mounts: list[Any] = MOUNTS_OF[kind](part_id, at, pod_height(radius, height), radius)
    return mounts


def _gatling_fire(part_id: str, style: str, first: float) -> list[Any]:
    return [volley.burst(part_id, 2.2, 4, 0.12, bullet(style, 190), first)]


def _lance_fire(part_id: str, _style: str, first: float) -> list[Any]:
    return [volley.laser(part_id, 7.5, 1.4, first)]


def _rack_fire(part_id: str, _style: str, first: float) -> list[Any]:
    return [volley.missiles(part_id, 6, 2, 30, first)]


def _orb_fire(part_id: str, style: str, first: float) -> list[Any]:
    return [volley.ring(part_id, 2.6, ORB_BARRELS, 13, bullet(style, 175), first)]


def _beam_fire(part_id: str, _style: str, first: float) -> list[Any]:
    return [volley.laser(part_id, BEAM.every, BEAM.firing, first, BEAM.width)]


def _cannon_fire(part_id: str, style: str, first: float) -> list[Any]:
    c = WEAPON_FIRE.cannon
    shell = bullet(style, c.speed, c.radius)
    return [volley.aimed(part_id, c.every, c.count, c.spacingDeg, shell, first)]


def _mortar_fire(part_id: str, style: str, first: float) -> list[Any]:
    m = WEAPON_FIRE.mortar
    flak = bursting(style, m.speed, m.radius, [m.after, m.count, bullet(style, m.small)])
    return [volley.aimed(part_id, m.every, 1, 0, flak, first)]


def _battery_fire(part_id: str, style: str, first: float) -> list[Any]:
    b = WEAPON_FIRE.battery
    return [volley.fan(part_id, b.every, b.count, b.spacingDeg, bullet(style, b.speed), first)]


def _sweeper_fire(part_id: str, _style: str, first: float) -> list[Any]:
    w = WEAPON_FIRE.sweeper
    return [sweeping(volley.laser(part_id, w.every, w.firing, first))]


def _hangar_fire(_part_id: str, _style: str, _first: float) -> list[Any]:
    return []


# What each kind fires: `(part id, bullet style, first) -> volleys`.
FIRE_OF = {
    "gatling": _gatling_fire,
    "lance": _lance_fire,
    "rack": _rack_fire,
    "orb": _orb_fire,
    "beam": _beam_fire,
    "cannon": _cannon_fire,
    "mortar": _mortar_fire,
    "battery": _battery_fire,
    "sweeper": _sweeper_fire,
    "hangar": _hangar_fire,
}


def weapon_volleys(kind: str, part_id: str, style: str, first: float) -> list[Any]:
    """Return what a weapon of `kind` fires, first `first` seconds into a stage.

    Its bullets are in `style`. The gatling bursts of 4, the lance its laser, the rack 2 homing
    missiles, the orb rings of 10, the cannon spreads of 3 large shells, the mortar flak, the
    battery fans of 7, the sweeper a sweeping laser; a hangar launches instead (`weapon_launches`).
    """
    _known(kind)
    volleys: list[Any] = FIRE_OF[kind](part_id, style, first)
    return volleys


def weapon_launches(kind: str, part_id: str, first: float) -> list[Any]:
    """Return what a weapon of `kind` launches (see `BossDesign.launches`): a hangar's Hornets."""
    if kind != "hangar":
        return []
    h = WEAPON_FIRE.hangar
    return [{"from": part_id, "kind": h.kind, "count": h.count, "every": h.every, "first": first}]
