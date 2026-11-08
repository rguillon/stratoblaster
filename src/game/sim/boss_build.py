# Copyright (c) 2026 Renaud Guillon
"""Builds the core types of the bosses from their config records.

Each boss is data the boss engine runs (BOSS-07): the one place where the config layer meets
`core/`.

The config (`game/config/`) keeps camelCase keys; `core/` is snake_case and tests `is None` for an
omitted optional field. Under Transcrypt an omitted field is `undefined`, not `None`, so every
optional field is mapped here (`opt`), and every field is copied under its core name. Nothing else
in `game/sim/` builds core boss types from config.
"""

import math

from core.entities.boss import BossDeath, BossPartSpec, BossStats
from core.entities.boss_roll import BossRoll
from core.entities.boss_turret import BossTurretSpec
from core.entities.enemy import EnemyBulletSpec, EnemyBurstSpec, EnemyLaserSpec, EnemyMissileSpec
from core.systems.boss_mounts import BossMount, BossMountSpec
from core.systems.boss_pattern import (
    BossAimedShape,
    BossBurstShape,
    BossFanShape,
    BossLaserShape,
    BossLaunchShape,
    BossMissilesShape,
    BossRingShape,
    BossVolley,
)
from game.config.bosses.boss_guns import mount_muzzles
from game.config.bosses.boss_kit import BOSS_TIMING, volley_muzzles, volley_on_turret
from game.sim.bosses.boss_launches import launch_fire
from game.sim.config_access import keys_of as _keys
from game.sim.config_access import opt
from game.sim.enemies.enemy_helpers import missile_spec
from game.sim.joints import joint_specs

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
# __pragma__ ("noskip")


def _maybe(value: Any, convert: Callable[[Any], Any]) -> Any:
    """`convert(value)`, or None when the config leaves the field out."""
    if value == None:
        return None
    return convert(value)


def bullet_spec(bullet: ConfigRecord) -> EnemyBulletSpec:
    """Return an enemy bullet of the config, with its burst when it has one (BOSS-23)."""
    burst = opt(bullet.burst)
    burst_spec = None
    if burst is not None:
        burst_spec = EnemyBurstSpec(burst["after"], burst["count"], bullet_spec(burst["bullet"]))
    return EnemyBulletSpec(bullet.speed, bullet.radius, bullet.style, burst_spec)


def _missile_spec(missile: ConfigRecord, up: bool) -> EnemyMissileSpec:
    return missile_spec(missile, up)


def _laser_spec(laser: ConfigRecord) -> EnemyLaserSpec:
    return EnemyLaserSpec(
        laser.warningSeconds,
        laser.firingSeconds,
        laser.width,
        laser.style,
        laser.sweeps is True,
    )


def _shape(shape: ConfigRecord) -> Any:
    """Return the core shape of a config volley's shape (its `kind` says which)."""
    kind = shape.kind
    if kind == "aimed":
        return BossAimedShape(shape.count, shape.spacingDeg, bullet_spec(shape.bullet))
    if kind == "fan":
        return BossFanShape(
            shape.headingDeg, shape.count, shape.spacingDeg, bullet_spec(shape.bullet)
        )
    if kind == "ring":
        return BossRingShape(shape.count, shape.turnDeg, bullet_spec(shape.bullet))
    if kind == "burst":
        return BossBurstShape(shape.count, shape.gap, bullet_spec(shape.bullet))
    if kind == "missiles":
        return BossMissilesShape(
            shape.count, shape.spacingDeg, _missile_spec(shape.missile, shape.up), shape.up
        )
    if kind == "laser":
        return BossLaserShape(_laser_spec(shape.laser))
    raise ValueError("Unknown boss volley shape " + kind)


# The kind of mount each kind of volley fires from (BOSS-58); a launch needs none.
MOUNT_KIND = {
    "aimed": "gun",
    "fan": "gun",
    "burst": "gun",
    "ring": "gun",
    "missiles": "missile",
    "laser": "laser",
}


def _fits(mount: ConfigRecord, volley: ConfigRecord) -> bool:
    """Whether a volley can fire from `mount`: its kind, and a rotor for a ring only."""
    kind = volley.shape.kind
    if kind not in MOUNT_KIND or MOUNT_KIND[kind] != mount.kind:
        return False
    if mount.kind != "gun":
        return True
    return bool((kind == "ring") == (mount.layout == "ring"))


def volley_mount(design: ConfigRecord, volley: ConfigRecord) -> ConfigRecord | None:
    """Return the mount a volley of the design fires from (BOSS-58), None for one it has none of.

    The one it names (`mount`), or the first of its piece's that fits it: a rotor for a ring,
    another gun mount for other bullets, a laser's, a missile mount's.
    """
    mounts = opt(design.mounts) or []
    named = opt(volley.mount)
    for mount in mounts:
        if named is not None:
            if mount.id == named:
                return mount
        elif mount.piece == volley["from"] and _fits(mount, volley):
            return mount
    if named is not None:
        raise ValueError('Unknown boss mount "' + named + '"')
    return None


def armed_volley(
    design: ConfigRecord, volley: ConfigRecord, mounts: dict[str, BossMount] | None = None
) -> BossVolley:
    """Return a volley of the design's stages, fired from its mount, or its gun's muzzles.

    This is the TS `#armed`. From the boss's mount it fires from (`mounts`, by id: BOSS-58) when it
    has one, else from the muzzles and turret of its piece's gun. The volley fires only while the
    part it `needs` stands or once the part it comes `after` is destroyed (BOSS-24). Each boss's own
    volleys are its boss file's stage patterns (`specs/bosses/`).
    """
    mount = volley_mount(design, volley)
    armed = mounts[mount.id] if mount is not None and mounts is not None else None
    return BossVolley(
        volley["from"],
        volley.every,
        _shape(volley.shape),
        None if armed is not None else volley_muzzles(design, volley),
        None if armed is not None else volley_on_turret(design, volley),
        opt(volley.needs),
        opt(volley.after),
        opt(volley.first),
        armed,
    )


def armed_pattern(
    design: ConfigRecord, volleys: list[ConfigRecord], mounts: dict[str, BossMount] | None = None
) -> list[BossVolley]:
    """`volleys` armed (see `armed_volley`), in the same order."""
    result: list[BossVolley] = [armed_volley(design, volley, mounts) for volley in volleys]
    return result


def mount_specs(design: ConfigRecord) -> list[BossMountSpec]:
    """Return the gun mounts of the design's pieces (BOSS-58), in its order.

    Each with its barrels' tips at rest (`boss_guns.mount_muzzles`) and its turret, turning at the
    bosses' rate (a laser's following the player at the laser rate, BOSS-31).
    """
    result: list[BossMountSpec] = []
    for mount in opt(design.mounts) or []:
        turret = None
        if mount.turret:
            # Any turret follows the player at the laser rate while a laser of it shows (BOSS-31,
            # D-284): a laser fired from a gun turret no longer turns at the guns' rate.
            turret = BossTurretSpec(
                mount.at[0], mount.at[1], BOSS_TIMING.turretTurnDeg, BOSS_TIMING.laserTurnDeg
            )
        result.append(
            BossMountSpec(mount.id, mount.piece, mount.kind, mount_muzzles(mount), turret)
        )
    return result


def launch_volley(launch: ConfigRecord) -> BossVolley:
    """Return the volley of a part's launch (BOSS-25: hangars, drone bays)."""
    fire = launch_fire(launch.count)
    return BossVolley(
        launch["from"],
        launch.every,
        BossLaunchShape(fire),
        None,
        None,
        None,
        None,
        opt(launch.first),
    )


def _angrier(volley: BossVolley, k: int) -> BossVolley:
    """Return `volley` fired in anger (BOSS-27): `rageRate` times as often, missiles in more.

    A laser keeps its warning, its beam and a gap between two (it cannot fire faster than that).
    """
    shape = volley.shape
    every = volley.every / BOSS_TIMING.rageRate
    if isinstance(shape, BossLaserShape):
        laser = shape.laser
        slowest = laser.warning_seconds + laser.firing_seconds + BOSS_TIMING.rageLaserGap
        every = max(every, slowest)
    if isinstance(shape, BossMissilesShape):
        shape = BossMissilesShape(
            shape.count * BOSS_TIMING.rageMissiles, shape.spacing_deg, shape.missile, shape.up
        )
    # It opens fire at once, its weapons one after the other.
    first = min(every, BOSS_TIMING.rageFirst + k * BOSS_TIMING.rageStagger)
    return BossVolley(
        volley.from_,
        every,
        shape,
        volley.muzzles,
        volley.turret,
        volley.needs,
        volley.after,
        first,
        volley.mount,
    )


def angry_pattern(
    design: ConfigRecord, form: int, mounts: dict[str, BossMount] | None = None
) -> list[BossVolley]:
    """Return what a boss of `design` fires when angry after transformation `form` (BOSS-27).

    Only the hidden weapons that transformation revealed, whatever their kind (bullets, missiles,
    lasers, a hangar's Hornets), each fired `rageRate` times as often (see `_angrier`), and those of
    the design's `rageAlso` (part ids) revealed before, still standing.
    """
    also = opt(design.rageAlso) or []
    revealed = [
        part.id
        for part in design.stats.parts
        if opt(part.reveal) == form
        or (part.id in also and opt(part.reveal) is not None and opt(part.reveal) < form)
    ]
    stages = design.stages
    volleys = [volley for volley in stages[len(stages) - 1] if volley["from"] in revealed]
    armed = [armed_volley(design, volley, mounts) for volley in volleys]
    launches = [launch for launch in opt(design.launches) or [] if launch["from"] in revealed]
    armed.extend([launch_volley(launch) for launch in launches])
    return [_angrier(volley, k) for k, volley in enumerate(armed)]


def break_ring_ids(design: ConfigRecord) -> list[str]:
    """Return the ids of the parts that burst into a ring of bullets when destroyed (BOSS-23).

    The ids come in the parts' order.
    """
    rings = opt(design.breakRings)
    if rings is None:
        return []
    return _keys(rings)


def _part_spec(part: ConfigRecord) -> BossPartSpec:
    return BossPartSpec(
        part.id,
        part.x,
        part.y,
        part.radius,
        part.health,
        part.shieldsCore is True,
        part.dropChance,
        part.orbits is True,
        opt(part.joint),
        opt(part.reveal),
        opt(part.retire),
    )


def default_transforms(design: ConfigRecord) -> list[int] | None:
    """When a boss of `design` transforms (BOSS-36): its design's `transforms`, or.

    For K transformations (its hidden parts' highest `reveal`) and n original parts, the k-th once
    ceil(k n / (K + 1)) of them are destroyed: half of them for a mini boss's one, a third and two
    thirds for a final boss's two (BOSS-35). None when it has no hidden part. Each boss's own
    transformations are in its boss file (`specs/bosses/`).
    """
    given = opt(design.transforms)
    if given is not None:
        result: list[int] = given
        return result
    forms = 0
    originals = 0
    for part in design.stats.parts:
        reveal = opt(part.reveal)
        if reveal is None:
            originals += 1
        else:
            forms = max(forms, reveal)
    if forms == 0:
        return None
    return [math.ceil((k * originals) / (forms + 1)) for k in range(1, forms + 1)]


def _turret_specs(design: ConfigRecord) -> Any:
    """Return the turrets of the design's pieces, by piece (`BossStats.turrets`).

    A piece has one when its guns name a turret pivot (BOSS-29), its lasers turning at the laser
    rate (BOSS-31).
    """
    result: Any = {}
    for piece in _keys(design.guns):
        guns = design.guns[piece]
        if opt(guns.turret) is None:
            continue
        # Its lasers, whichever turret they fire from, follow at the laser rate (D-284).
        result[piece] = BossTurretSpec(
            guns.turret[0],
            guns.turret[1],
            BOSS_TIMING.turretTurnDeg,
            BOSS_TIMING.laserTurnDeg,
        )
    return result


def _death(death: ConfigRecord) -> BossDeath:
    return BossDeath(death.seconds, death.every)


def _roll(rule: ConfigRecord) -> BossRoll:
    return BossRoll(rule.maxDeg, rule.fullSpeed, rule.easePerSec)


def boss_stats(design: ConfigRecord) -> BossStats:
    """Return the stats of a boss of `design` (its turrets, and its angry time when it has a rage).

    With the parts its design may name for each transformation (BOSS-36).
    """
    stats = design.stats
    transforms = default_transforms(design)
    rage_seconds = BOSS_TIMING.rageSeconds if transforms is not None else opt(stats.rageSeconds)
    parts: list[BossPartSpec] = [_part_spec(part) for part in stats.parts]
    return BossStats(
        stats.model,
        stats.radius,
        stats.health,
        stats.points,
        stats["name"],
        stats.coreRadius,
        parts,
        stats.groundSpeed,
        stats.stagePause,
        _death(stats.death),
        rage_seconds,
        opt(stats.coreDropChance),
        opt(stats.partPoints),
        _maybe(stats.roll, _roll),
        _turret_specs(design),
        _maybe(stats.joints, joint_specs),
        transforms,
        BOSS_TIMING.transformSeconds,
        opt(design.transformParts),
        opt(design.turns),
        mount_specs(design),
    )
