"""Building blocks of the World 1 bosses (P07-R05)

Logical pixels with X right and Y up, from the boss's centre; the boss faces down the screen, so
its nose is at -Y and its tail at +Y. Times in seconds, angles in degrees, speeds in px/s.

A boss's design (`BossDesign` in the TS) is a record with: `id` (kind id and model key),
`stats`, `stopFraction` (height where it stops coming down, as a fraction of the playfield's
height), `sway` and `bob` (`amplitude` and `period`; once in place it sways left and right by up
to `amplitude`, less when its parts would leave the ship's reach, P07-R05, and bobs up and down),
`spinRate` (radians a second its orbiting parts turn, optional), `stages` (one pattern per stage:
`stages[k]` once `k` parts are destroyed, P07-R04), `rage` (its angry pattern, optional, see
`boss_rage.py`: a bullet hell it fires for `BOSS_TIMING.rageSeconds` after the pause that follows
each destroyed part), `launches` (optional: enemies some parts launch in every stage while they
stand, a hangar's Gnats, a bay's Hornets: `count` of `kind` every `every` seconds),
`breakRings` (optional: a ring of bullets some parts burst into when destroyed, the Refinery
Titan's tanks) and `guns` (the muzzles of the guns of its core and parts, by piece: a part id or
`core`; where their shots leave from, phase 7 review; its model draws its barrels' tips there).

The guns of a piece (`Guns` in the TS) are: `turret` (the pivot, from the boss's centre, X right,
Y up; the guns turn around it the way they fire next, phase 7 review, D-060), `turretLaser`
(its lasers are on that turret too: they aim at the player during the warning line and hold
still while the beam fires), `gun` (bullets), `ring` (a ring of bullets; the `gun` ones when
omitted), `missile` and `laser`, each a list of muzzles `[x, y, height]`.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies import ENEMY_UNIT
from game.config.record import concat, merge, record
from game.config.scoring import boss_part_points

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# `L`, the length of the medium player ship (as for the enemies).
L = ENEMY_UNIT


def _unset(value: Any) -> bool:
    """Whether a field is missing or null: `=== undefined` or `=== null` in the TS."""
    return bool(value == None)  # noqa: E711


# Which of a piece's guns fire each kind of volley (`FIRED_BY` in the TS).
FIRED_BY = record(
    {
        "aimed": lambda guns: guns.gun,
        "fan": lambda guns: guns.gun,
        "burst": lambda guns: guns.gun,
        "ring": lambda guns: guns.gun if _unset(guns.ring) else guns.ring,
        "missiles": lambda guns: guns.missile,
        "laser": lambda guns: guns.laser,
        "launch": lambda guns: [],
    }
)


def volley_muzzles(design: Any, shot: Any) -> Any:
    """The muzzles `volley` fires from, among its piece's guns (none for launches)."""
    guns = design.guns[shot["from"]]
    if _unset(guns):
        guns = {}
    fired = FIRED_BY[shot["shape"]["kind"]](guns)
    return [] if _unset(fired) else fired


def volley_on_turret(design: Any, shot: Any) -> bool:
    """Whether `volley` fires from its piece's turret: its `gun`s (or `laser`s) when on one."""
    guns = design.guns[shot["from"]]
    if _unset(guns) or _unset(guns.turret):
        return False
    muzzles = volley_muzzles(design, shot)
    return bool(muzzles is guns.gun or (guns.turretLaser is True and muzzles is guns.laser))


def mirror(muzzles: list[list[Any]]) -> list[list[Any]]:
    """`muzzles` mirrored left to right, for the gun on the other side."""
    return [[-m[0], m[1], m[2]] for m in muzzles]


def twin(x: float, y: float, height: float, gap: float | None = None) -> list[list[Any]]:
    """Two muzzles side by side at `x ± gap` (or `±x`, a pair either side of the centre line)."""
    if gap is None:
        return [[x, y, height], [-x, y, height]]
    return [[x - gap, y, height], [x + gap, y, height]]


def cells(xs: list[Any], ys: list[Any], height: float) -> list[list[Any]]:
    """Missile cells in rows and columns, at the `xs` and `ys` given, all `height` high."""
    return [[x, y, height] for x in xs for y in ys]


# Phase 5 enemies a boss's part launches (see `BossDesign.launches`): a record with `from`,
# `kind` ('gnats' or 'hornets'), `count`, `every` and `first` (optional).

# Shared timings of every boss (tunable values of P07).
BOSS_TIMING = record(
    {
        # No fire for this long after a part is destroyed (P07-R04, `stage_change_pause`).
        "stagePause": 1,
        # Blasts over the hull for about 2 s, then the big one (P07-R06).
        "death": {"seconds": 2, "every": 0.16},
        # How far above the top edge a boss appears, and how fast it comes in (about 3 s).
        "spawnMargin": 30,
        "entrySpeed": 75,
        # Speed it eases into its place at, and the distance over which it brakes.
        "brakeDistance": 60,
        # It rolls into its sideways moves (phase 7 review): up to `maxDeg` at `fullSpeed` px/s
        # across (about its fastest sway), easing towards it `easePerSec` of the way a second.
        "roll": {"maxDeg": 12, "fullSpeed": 60, "easePerSec": 4},
        # Degrees a second a turret turns at, following the player (phase 7 review).
        "turretTurnDeg": 150,
        # Degrees a second a laser turret follows the player at during the warning line (phase 8
        # review): about half as fast as the ship crosses its aim from 300 px away, so it can be
        # outrun.
        "laserTurnDeg": 20,
        # Seconds a boss is angry after the pause that follows each destroyed part (phase 7).
        "rageSeconds": 3,
    }
)


def bullet(style: str, speed: float, radius: float = 4) -> Any:
    """Enemy bullets in a style of the enemy look."""
    return record({"speed": speed, "radius": radius, "style": style})


# Boss missiles: like the Rocketeer's, and shot down the same way (GD-43).
MISSILE = record(
    {
        "speed": 140,
        "turnRateDeg": 80,
        "homingSeconds": 3,
        "radius": 5,
        "health": 10,
        "style": "rocketeer",
    }
)


def laser_of(firing_seconds: float, width: float = 12) -> Any:
    """Boss lasers: the Lancer's, with its 1 s warning line (GD-43)."""
    return record(
        {
            "warningSeconds": 1,
            "firingSeconds": firing_seconds,
            "width": width,
            "style": "lancer",
        }
    )


def bursting(style: str, speed: float, radius: float, spec: list[Any]) -> Any:
    """A slow, big bullet of `style` that bursts into a ring of `count` small ones `after` seconds
    from its firing (phase 8: the Aurora Station's cryo cannons).

    `spec` is `[after, count, small]`, with `small` the bullet of the ring.
    """
    after, count, small = spec
    return record(
        {
            "speed": speed,
            "radius": radius,
            "style": style,
            "burst": {"after": after, "count": count, "bullet": small},
        }
    )


def part(
    part_id: str,
    position: list[Any],
    radius: float,
    health: float,
    options: Any = None,
) -> Any:
    """A part: `options` holds `shields`, `drop`, `orbits` and `joint` (all optional)."""
    opts: Any = record({}) if _unset(options) else record(options)
    result = record(
        {
            "id": part_id,
            "x": position[0],
            "y": position[1],
            "radius": radius,
            "health": health,
            "shieldsCore": True if _unset(opts.shields) else opts.shields,
            "dropChance": 0.5 if _unset(opts.drop) else opts.drop,
        }
    )
    if opts.orbits:
        result["orbits"] = True
    if not _unset(opts.joint):
        result["joint"] = opts.joint
    return result


def stats(options: Any) -> Any:
    """The numbers of a boss of `size` L across.

    `options`: `id`, `name`, `size`, `coreRadius`, `coreHealth`, `points`, `groundSpeed`,
    `parts`, and optionally `coreDrop` and `joints` (its moving limbs, phase 7 review: see
    `BossStats.joints`).
    """
    options = record(options)
    result = record(
        {
            "model": options.id,
            "name": options["name"],
            "radius": (options.size * L) / 2,
            "coreRadius": options.coreRadius,
            "health": options.coreHealth,
            "points": options.points,
            "partPoints": boss_part_points(options.points),
            "groundSpeed": options.groundSpeed,
            "parts": options.parts,
            "stagePause": BOSS_TIMING.stagePause,
            "death": BOSS_TIMING.death,
            "roll": BOSS_TIMING.roll,
        }
    )
    if not _unset(options.coreDrop):
        result["coreDropChance"] = options.coreDrop
    if not _unset(options.joints):
        result["joints"] = options.joints
    return result


def stages(parts: list[Any], core: list[list[Any]]) -> list[Any]:
    """The stages of a boss: the parts' volleys in every stage (each stops with its part), and
    the core's own volleys, one list per stage. The core's volleys differ from a stage to the
    next, so every stage fires another pattern (P07-R04).
    """
    return [concat(parts, own) for own in core]


def only_while(shot: Any, part_id: str) -> Any:
    """`volley` fired only while the part `part` stands (`needs`): phase 8, the Fjord Lynx's
    radar mast.
    """
    return merge(shot, {"needs": part_id})


def only_after(shot: Any, part_id: str) -> Any:
    """`volley` fired only once the part `part` is destroyed (`after`)."""
    return merge(shot, {"after": part_id})


def _shot(source: str, every: float, first: Any, shape: Any) -> Any:
    shot = record({"from": source, "every": every, "shape": shape})
    if not _unset(first):
        shot["first"] = first
    return shot


def _volley_aimed(
    source: str, every: float, count: float, spacing_deg: float, b: Any, first: Any = None
) -> Any:
    shape = record({"kind": "aimed", "count": count, "spacingDeg": spacing_deg, "bullet": b})
    return _shot(source, every, first, shape)


def _volley_fan(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    source: str,
    every: float,
    count: float,
    spacing_deg: float,
    b: Any,
    first: Any = None,
    heading_deg: float = 0,
) -> Any:
    shape = record(
        {
            "kind": "fan",
            "headingDeg": heading_deg,
            "count": count,
            "spacingDeg": spacing_deg,
            "bullet": b,
        }
    )
    return _shot(source, every, first, shape)


def _volley_ring(
    source: str, every: float, count: float, turn_deg: float, b: Any, first: Any = None
) -> Any:
    shape = record({"kind": "ring", "count": count, "turnDeg": turn_deg, "bullet": b})
    return _shot(source, every, first, shape)


def _volley_burst(
    source: str, every: float, count: float, gap: float, b: Any, first: Any = None
) -> Any:
    shape = record({"kind": "burst", "count": count, "gap": gap, "bullet": b})
    return _shot(source, every, first, shape)


def _volley_missiles(
    source: str, every: float, count: float, spacing_deg: float, first: Any = None
) -> Any:
    shape = record(
        {"kind": "missiles", "count": count, "spacingDeg": spacing_deg, "missile": MISSILE}
    )
    return _shot(source, every, first, shape)


def _volley_laser(source: str, every: float, firing_seconds: float, first: Any = None) -> Any:
    shape = record({"kind": "laser", "laser": laser_of(firing_seconds)})
    return _shot(source, every, first, shape)


# Volleys, `from` a part id or `core`. `first` defaults to `every`.
volley = record(
    {
        "aimed": _volley_aimed,
        "fan": _volley_fan,
        "ring": _volley_ring,
        "burst": _volley_burst,
        "missiles": _volley_missiles,
        "laser": _volley_laser,
    }
)


def with_own_lasers(design: Any) -> Any:
    """`design` with its lasers drawn in its own colour (phase 8 review): their style is its kind
    id, which the laser renderer colours with the boss's neon.
    """

    def own(pattern: list[Any]) -> list[Any]:
        return [
            merge(
                v,
                {
                    "shape": merge(
                        v.shape,
                        {"laser": merge(v.shape.laser, {"style": design.id})},
                    )
                },
            )
            if v.shape.kind == "laser"
            else v
            for v in pattern
        ]

    result = merge(design, {"stages": [own(p) for p in design.stages]})
    if not _unset(design.rage):
        result["rage"] = own(design.rage)
    return result
