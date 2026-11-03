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
from game.config.bosses.boss_kit import BOSS_TIMING, volley_muzzles, volley_on_turret
from game.sim.bosses.boss_launches import launch_fire
from game.sim.config_access import keys_of as _keys
from game.sim.config_access import opt
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


def _missile_spec(missile: ConfigRecord) -> EnemyMissileSpec:
    return EnemyMissileSpec(
        missile.speed,
        missile.turnRateDeg,
        missile.homingSeconds,
        missile.radius,
        missile.health,
        missile.style,
    )


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
        return BossMissilesShape(shape.count, shape.spacingDeg, _missile_spec(shape.missile))
    if kind == "laser":
        return BossLaserShape(_laser_spec(shape.laser))
    raise ValueError("Unknown boss volley shape " + kind)


def armed_volley(design: ConfigRecord, volley: ConfigRecord) -> BossVolley:
    """Return a volley of the design's stages, fired from the muzzles and turret of its gun.

    This is the TS `#armed`. The volley fires only while the part it `needs` stands or once the part
    it comes `after` is destroyed (BOSS-24). Each boss's own volleys are its boss file's stage
    patterns (`specs/bosses/`).
    """
    return BossVolley(
        volley["from"],
        volley.every,
        _shape(volley.shape),
        volley_muzzles(design, volley),
        volley_on_turret(design, volley),
        opt(volley.needs),
        opt(volley.after),
        opt(volley.first),
    )


def armed_pattern(design: ConfigRecord, volleys: list[ConfigRecord]) -> list[BossVolley]:
    """`volleys` armed (see `armed_volley`), in the same order."""
    result: list[BossVolley] = [armed_volley(design, volley) for volley in volleys]
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
        laser_turn = BOSS_TIMING.laserTurnDeg if guns.turretLaser else None
        result[piece] = BossTurretSpec(
            guns.turret[0],
            guns.turret[1],
            BOSS_TIMING.turretTurnDeg,
            laser_turn,
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
    rage_seconds = BOSS_TIMING.rageSeconds if design.rage else opt(stats.rageSeconds)
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
        default_transforms(design),
        BOSS_TIMING.transformSeconds,
        opt(design.transformParts),
        opt(design.turns),
    )
