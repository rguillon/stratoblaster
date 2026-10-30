"""Builds the core types of the bosses (P07) from their config records: the one place where the
config layer meets `core/`.

The config (`game/config/`) keeps the TypeScript's camelCase shape verbatim; `core/` is snake_case
and tests `is None` for an omitted optional field. Under Transcrypt an omitted field is `undefined`,
not `None`, so every optional field is mapped here (`opt`), and every field is copied under its
core name. Nothing else in `game/sim/` builds core boss types from config.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss import BossDeath, BossPartSpec, BossStats
from core.entities.boss_joint import BossJointSpec, JointSwing
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

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

# A config record (`game/config/record.py`), typed as Any there.
ConfigRecord = Any
__pragma__("noskip")


def opt(value: Any) -> Any:
    """The config's optional field `value`, or None when the config leaves it out."""
    if value == None:  # noqa: E711 (undefined or null: Transcrypt has both)
        return None
    return value


def _maybe(value: Any, convert: Callable[[Any], Any]) -> Any:
    """`convert(value)`, or None when the config leaves the field out."""
    if value == None:  # noqa: E711
        return None
    return convert(value)


def bullet_spec(bullet: ConfigRecord) -> EnemyBulletSpec:
    """An enemy bullet of the config, with its burst when it has one."""
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
    """The core shape of a config volley's shape (its `kind` says which)."""
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
    """A volley of the design's stages, fired from the muzzles and turret of its gun (the TS
    `#armed`).
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
    result: list[BossVolley] = []
    for volley in volleys:
        result.append(armed_volley(design, volley))
    return result


def launch_volley(launch: ConfigRecord, side: int) -> BossVolley:
    """The volley of a part's launch (P07-R05: hangars, drone bays). `side` is which side of the
    boss the part is on (-1 left, 1 right), for the Gnats' way out.
    """
    fire = launch_fire(launch.kind, launch.count, side)
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


def _keys(record: ConfigRecord) -> list[str]:
    """The keys of a config record, in their order. A record is a plain JavaScript object, which
    has no `keys()` method under Transcrypt.
    """
    result: list[str] = []
    __pragma__(
        "js",
        "{}",
        """
    result = Object.keys(record);
    """,
    )
    return result


def break_ring_ids(design: ConfigRecord) -> list[str]:
    """The ids of the parts that burst into a ring of bullets when destroyed, in their order."""
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
    )


def _joint_specs(joints: ConfigRecord) -> Any:
    """The joints of a boss, by id."""
    result: Any = {}
    for joint_id in _keys(joints):
        joint = joints[joint_id]
        swing = joint.swing
        phase = swing.phase
        if phase == None:  # noqa: E711
            phase = 0
        result[joint_id] = BossJointSpec(
            joint.x,
            joint.y,
            JointSwing(swing.amplitudeDeg, swing.period, phase),
            opt(joint.parent),
        )
    return result


def _turret_specs(design: ConfigRecord) -> Any:
    """The turrets of the design's pieces, by piece (`BossStats.turrets`): a piece has one when its
    guns name a turret pivot.
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
    """The stats of a boss of `design` (its turrets, and its angry time when it has a rage)."""
    stats = design.stats
    rage_seconds = BOSS_TIMING.rageSeconds if design.rage else opt(stats.rageSeconds)
    parts: list[BossPartSpec] = []
    for part in stats.parts:
        parts.append(_part_spec(part))
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
        _maybe(stats.joints, _joint_specs),
    )
