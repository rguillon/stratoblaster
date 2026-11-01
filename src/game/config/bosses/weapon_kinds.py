"""The kinds of hidden weapon a boss reveals as it transforms (D-221, D-229; docs/superpowers/specs/
2026-11-01-boss-weapon-variety-and-shape-shifts-design.md): their sizes, muzzles and volleys.

- `gatling`: a three-barrelled turret that follows the player (bursts);
- `lance`: a laser lance pointing down the screen (lasers);
- `rack`: a box of four missile cells (homing missiles);
- `orb`: a glowing emitter on top (rings);
- `beam`: the Scorpion's tail cannon (a giant laser, D-228);
- `cannon`: a big turret with one heavy barrel (aimed spreads of large, slow shells);
- `mortar`: a short, wide tube tilted up on a round base (flak shells that burst into rings);
- `battery`: a long, low gun deck, five barrels in a row (wide fans straight down);
- `sweeper`: a turret with a two-pronged emitter (a laser that sweeps after the player);
- `hangar`: a box bay whose doors slide open (it launches Gnats).

Muzzles are worked out here from a weapon's size; the boss view draws its model with the same
numbers (`game/view/bosses/hidden_weapon_shapes.py`). Offsets in px from the boss's centre, X right,
Y up (its nose points down, at -Y), and heights above the playfield.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, bursting, sweeping, volley
from game.config.record import record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

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
WEAPON_SHAPE = record(
    {
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
    }
)

# A giant laser (D-228): `width` px wide (four of the usual), firing `firing` seconds every
# `every` seconds.
BEAM = record({"width": 44, "firing": 2.4, "every": 7})

# What each kind fires (D-229): the cannon's shells and the battery's and mortar's bullets, and how
# many a hangar launches of which kind.
WEAPON_FIRE = record(
    {
        "cannon": {"every": 2.4, "count": 3, "spacingDeg": 12, "speed": 150, "radius": 7},
        "mortar": {"every": 3.2, "speed": 110, "radius": 8, "after": 1.1, "count": 8, "small": 170},
        "battery": {"every": 2.0, "count": 7, "spacingDeg": 9, "speed": 180},
        "sweeper": {"every": 8, "firing": 2.0},
        "hangar": {"kind": "gnats", "count": 2, "every": 7},
    }
)


def pod_height(radius: float, height: Any) -> float:
    """The height of a weapon's pod: `height` when given, else its share of the radius."""
    if height == None:  # noqa: E711
        value: float = radius * WEAPON_SHAPE.height
        return value
    given: float = height
    return given


def gatling_turret(radius: float) -> Any:
    """The gatling turret's sizes (its radius, barrel gap, bore and length)."""
    rt = radius * WEAPON_SHAPE.turret
    return record(
        {
            "radius": rt,
            "gap": rt * WEAPON_SHAPE.gap,
            "bore": rt * WEAPON_SHAPE.bore,
            "length": rt * WEAPON_SHAPE.length,
        }
    )


def cannon_turret(radius: float) -> Any:
    """The cannon's turret's sizes (as `gatling_turret`: one heavy barrel)."""
    rt = radius * WEAPON_SHAPE.cannonTurret
    return record(
        {
            "radius": rt,
            "gap": 0,
            "bore": rt * WEAPON_SHAPE.cannonBore,
            "length": rt * WEAPON_SHAPE.cannonLength,
        }
    )


def turret_tip(t: Any) -> list[float]:
    """`[reach, lift]` of the tips of the barrels of a turret of sizes `t` (`mini_boss_shapes.
    turret`, aimed down the screen) from its pivot on top of its pod: how far ahead, how high."""
    return [0.3 * t.radius + t.length + 0.5 * t.radius + 0.6 * t.bore, 0.28 * t.radius]


def mortar_mouth(radius: float) -> list[float]:
    """Where the mortar's tube ends from its pod's top centre: `[ahead, up]` (px towards the nose
    and above the pod)."""
    e = WEAPON_SHAPE.mortarDeg * math.pi / 180
    length = radius * WEAPON_SHAPE.mortarLength
    return [
        length * math.cos(e) - radius * WEAPON_SHAPE.mortarBack,
        radius * WEAPON_SHAPE.mortarFoot + length * math.sin(e),
    ]


def battery_offsets(radius: float) -> list[float]:
    """The offsets across (X) of the battery's barrels from its centre, left to right."""
    n = WEAPON_SHAPE.barrels
    gap = radius * WEAPON_SHAPE.barrelGap
    return [(i - (n - 1) / 2) * gap for i in range(n)]


def _gatling_guns(x: float, y: float, h: float, radius: float) -> Any:
    t = gatling_turret(radius)
    tip = turret_tip(t)
    muzzles = [[x - (i - 1) * t.gap, y - tip[0], h + tip[1]] for i in range(3)]
    return record({"gun": muzzles, "turret": [x, y]})


def _cannon_guns(x: float, y: float, h: float, radius: float) -> Any:
    tip = turret_tip(cannon_turret(radius))
    return record({"gun": [[x, y - tip[0], h + tip[1]]], "turret": [x, y]})


def _lance_guns(x: float, y: float, h: float, radius: float) -> Any:
    return record({"laser": [[x, y - radius * WEAPON_SHAPE.lance, h * 0.9]]})


def _rack_guns(x: float, y: float, h: float, radius: float) -> Any:
    dx = radius * WEAPON_SHAPE.cellX
    dy = radius * WEAPON_SHAPE.cellY
    top = h + radius * WEAPON_SHAPE.cellTop
    return record(
        {"missile": [[x + sx * dx, y + sy * dy, top] for sx in [-1, 1] for sy in [-1, 1]]}
    )


def _orb_guns(x: float, y: float, h: float, radius: float) -> Any:
    emitter = [[x, y, h + radius * WEAPON_SHAPE.orbTop]]
    return record({"gun": emitter, "ring": emitter})


def _mortar_guns(x: float, y: float, h: float, radius: float) -> Any:
    mouth = mortar_mouth(radius)
    return record({"gun": [[x, y - mouth[0], h + mouth[1]]]})


def _battery_guns(x: float, y: float, h: float, radius: float) -> Any:
    ahead = radius * (WEAPON_SHAPE.deckDepth / 2 + WEAPON_SHAPE.barrelLength)
    lift = h * WEAPON_SHAPE.barrelLift
    return record({"gun": [[x + dx, y - ahead, lift] for dx in battery_offsets(radius)]})


def _sweeper_guns(x: float, y: float, h: float, radius: float) -> Any:
    lift = h + radius * WEAPON_SHAPE.sweeperTurret * WEAPON_SHAPE.lensLift
    lens = [[x, y - radius * WEAPON_SHAPE.prongLength, lift]]
    return record({"laser": lens, "turret": [x, y], "turretLaser": True})


def _hangar_guns(_x: float, _y: float, _h: float, _radius: float) -> Any:
    return record({})


# The guns of each kind: `(x, y, pod height, radius) -> guns`.
GUNS_OF = {
    "gatling": _gatling_guns,
    "cannon": _cannon_guns,
    "lance": _lance_guns,
    "beam": _lance_guns,
    "rack": _rack_guns,
    "orb": _orb_guns,
    "mortar": _mortar_guns,
    "battery": _battery_guns,
    "sweeper": _sweeper_guns,
    "hangar": _hangar_guns,
}


def _known(kind: str) -> None:
    if kind not in KINDS:
        raise ValueError('Unknown hidden weapon kind "' + kind + '"')


def weapon_guns(kind: str, at: list[Any], radius: float, height: Any) -> Any:
    """The guns of a weapon of `kind` centred on `at` (see `BossDesign.guns`)."""
    _known(kind)
    return GUNS_OF[kind](at[0], at[1], pod_height(radius, height), radius)


def _gatling_fire(part_id: str, style: str, first: float) -> list[Any]:
    return [volley.burst(part_id, 2.2, 4, 0.12, bullet(style, 190), first)]


def _lance_fire(part_id: str, _style: str, first: float) -> list[Any]:
    return [volley.laser(part_id, 7.5, 1.4, first)]


def _rack_fire(part_id: str, _style: str, first: float) -> list[Any]:
    return [volley.missiles(part_id, 6, 2, 30, first)]


def _orb_fire(part_id: str, style: str, first: float) -> list[Any]:
    return [volley.ring(part_id, 2.6, 10, 13, bullet(style, 175), first)]


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
    """What a weapon of `kind` fires, first `first` seconds into a stage (bullets in `style`): the
    gatling bursts of 4, the lance its laser, the rack 2 homing missiles, the orb rings of 10, the
    cannon spreads of 3 large shells, the mortar flak, the battery fans of 7, the sweeper a sweeping
    laser; a hangar launches instead (`weapon_launches`)."""
    _known(kind)
    volleys: list[Any] = FIRE_OF[kind](part_id, style, first)
    return volleys


def weapon_launches(kind: str, part_id: str, first: float) -> list[Any]:
    """What a weapon of `kind` launches (see `BossDesign.launches`): a hangar's Gnats."""
    if kind != "hangar":
        return []
    h = WEAPON_FIRE.hangar
    return [{"from": part_id, "kind": h.kind, "count": h.count, "every": h.every, "first": first}]
