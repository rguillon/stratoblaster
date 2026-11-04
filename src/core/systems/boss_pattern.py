# Copyright (c) 2026 Renaud Guillon
"""Boss volleys (BOSS-23).

What volleys fire, from which piece, on which timer. Angles in degrees in the data; a preset heading
of 0 is straight down, positive towards the right of the screen. Pure and deterministic.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.systems.enemy_motion import fan_headings
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Protocol

from core.entities.boss_turret import BossTurret
from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyContext,
    EnemyLaserSpec,
    EnemyMissileSpec,
    LaserOwner,
)
from core.entities.muzzle import Muzzle, PlanePoint, RaisedPoint
from core.systems.gun_muzzles import MuzzleSource

# __pragma__ ("noskip")


DEG = math.pi / 180
# How far (radians) a turret may be from where its next aimed volley goes for it to fire (BOSS-29):
# about 6 degrees, so the shots leave the way the barrels point.
AIM_TOLERANCE = 0.105
# Straight down the screen.
DOWN = math.pi
INFINITY = float("Infinity")

# The core fires the volleys whose `from` is this.
CORE = "core"


class BossAimedShape:
    """`count` bullets in a fan `spacing_deg` apart, the middle one at the player."""

    def __init__(self, count: int, spacing_deg: float, bullet: EnemyBulletSpec) -> None:
        self.kind = "aimed"
        self.count = count
        self.spacing_deg = spacing_deg
        self.bullet = bullet


class BossFanShape:
    """`count` bullets in a fan around a preset heading (`heading_deg`)."""

    def __init__(
        self, heading_deg: float, count: int, spacing_deg: float, bullet: EnemyBulletSpec
    ) -> None:
        self.kind = "fan"
        self.heading_deg = heading_deg
        self.count = count
        self.spacing_deg = spacing_deg
        self.bullet = bullet


class BossRingShape:
    """`count` bullets all around, the ring turned by `turn_deg` more at each volley (a spiral)."""

    def __init__(self, count: int, turn_deg: float, bullet: EnemyBulletSpec) -> None:
        self.kind = "ring"
        self.count = count
        self.turn_deg = turn_deg
        self.bullet = bullet


class BossBurstShape:
    """`count` single bullets at the player, `gap` seconds apart."""

    def __init__(self, count: int, gap: float, bullet: EnemyBulletSpec) -> None:
        self.kind = "burst"
        self.count = count
        self.gap = gap
        self.bullet = bullet


class BossMissilesShape:
    """`count` homing missiles in a fan `spacing_deg` apart around the player's direction."""

    def __init__(self, count: int, spacing_deg: float, missile: EnemyMissileSpec) -> None:
        self.kind = "missiles"
        self.count = count
        self.spacing_deg = spacing_deg
        self.missile = missile


class BossLaserShape:
    """A laser straight down from the piece: warning line first (BOSS-30)."""

    def __init__(self, laser: EnemyLaserSpec) -> None:
        self.kind = "laser"
        self.laser = laser


class BossLaunchShape:
    """Enemies launched from the piece (e.g. a hangar's drones): `launch(x, y)` gives them."""

    def __init__(self, launch: Callable[[float, float], list[Enemy]]) -> None:
        self.kind = "launch"
        self.launch = launch


class BossVolley:
    """One weapon of a stage's pattern (BOSS-21).

    `from_`: what fires it: the id of a part (it stops for good once that part is destroyed) or
    `core`. `muzzles`: the muzzles of that piece's gun its shots leave from (see
    `MuzzleSource.place`), the one furthest along each shot's way; the piece's centre when None.
    `turret`: whether those muzzles are on the piece's turret (phase 7 review): they turn with it,
    and it turns the way its next volley goes (see `BossPattern.turn_turrets`). `needs`: fires only
    while the part with this id stands (e.g. a radar that aims the guns); `after`: only once that
    part is destroyed; always when None. `every`: seconds between two volleys. `first`: seconds
    before the first one, from the start of the stage; `every` when None.
    """

    def __init__(
        self,
        from_: str,
        every: float,
        shape: "BossVolleyShape",
        muzzles: Sequence[Muzzle] | None = None,
        turret: bool | None = None,
        needs: str | None = None,
        after: str | None = None,
        first: float | None = None,
    ) -> None:
        self.from_ = from_
        self.every = every
        self.shape = shape
        self.muzzles = muzzles
        self.turret = turret
        self.needs = needs
        self.after = after
        self.first = first


# Typing names only: Transcrypt skips this block, CPython needs the classes above first.
__pragma__("skip")
BossVolleyShape = (
    BossAimedShape
    | BossFanShape
    | BossRingShape
    | BossBurstShape
    | BossMissilesShape
    | BossLaserShape
    | BossLaunchShape
)
# The volleys of one stage.
BossPatternSpec = Sequence[BossVolley]


class VolleySource(MuzzleSource, Protocol):
    """What volleys fire from: the playfield position of a piece, its muzzles.

    The laser owner it is, and the turret its guns are on, if any.
    """

    turret: BossTurret | None


# The piece a volley fires from, or None once it is destroyed.
VolleySources = Callable[[str], VolleySource | None]
__pragma__("noskip")


class _VolleyState:
    """What a volley is doing: its timers, its turns and its guns."""

    def __init__(self, left: float, guns: GunMuzzles) -> None:
        # Seconds until the next volley.
        self.left = left
        # Turns of a ring so far.
        self.turns = 0
        # Bullets of a burst still to fire, and seconds until the next one.
        self.burst = 0
        self.burst_left = 0.0
        # Seconds since its last laser was fired (Infinity before the first).
        self.laser_age = INFINITY
        self.guns = guns


class _TurretGroup:
    """The indices of the volleys that fire from one piece's turret."""

    def __init__(self, from_: str, volleys: list[int]) -> None:
        self.from_ = from_
        self.volleys = volleys


def _live(volley: BossVolley, intact: Callable[[str], bool]) -> bool:
    """Whether `volley` fires when only the pieces for which `intact` is true remain (BOSS-24)."""
    return (
        intact(volley.from_)
        and (volley.needs is None or intact(volley.needs))
        and (volley.after is None or not intact(volley.after))
    )


class BossPattern:
    """Fires one stage's pattern (BOSS-21).

    Each volley on its own timer, from its piece, as long as that piece is there. Timers run
    `ctx.fire_rate` times faster (a level's difficulty, BOSS-26). Pure and deterministic.
    """

    def __init__(self, volleys: BossPatternSpec) -> None:
        self.volleys = volleys
        self._states: list[_VolleyState] = []
        for volley in volleys:
            left = volley.first if volley.first is not None else volley.every
            self._states.append(_VolleyState(left, GunMuzzles(volley.muzzles, volley.turret)))
        # The pieces whose turrets its volleys fire from, and the indices of those volleys.
        self._turrets: list[_TurretGroup] = []
        for i in range(len(volleys)):
            volley = volleys[i]
            if not volley.turret:
                continue
            group = _find_turret_group(self._turrets, volley.from_)
            if group is None:
                self._turrets.append(_TurretGroup(volley.from_, [i]))
            else:
                group.volleys.append(i)

    @property
    def charge(self) -> float:
        """How ready the next volley is, 0..1 (for charging lights)."""
        best = 0.0
        for i in range(len(self.volleys)):
            volley = self.volleys[i]
            left = self._states[i].left
            best = max(best, 1 - min(1, left / volley.every))
        return best

    def step(self, ctx: EnemyContext, dt: float, sources: VolleySources) -> None:
        """Advances the volleys by `dt` seconds, scaled by the fire rate.

        Fires those that are due from their sources and steps their bursts. A volley without a live
        source waits.
        """
        time = dt * ctx.fire_rate
        for i in range(len(self.volleys)):
            volley = self.volleys[i]
            state = self._states[i]
            source = sources(volley.from_)
            if not source or not _live(volley, lambda f: bool(sources(f))):
                continue
            state.left -= time
            while state.left <= 0:
                if not _on_aim(ctx, volley, state, source):
                    # Held until its turret points the way the shots go.
                    state.left = 0
                    break
                state.left += volley.every
                self._fire(ctx, volley, state, source)
            self._step_burst(ctx, volley, state, source, time)

    def turn_turrets(self, ctx: EnemyContext, dt: float, sources: VolleySources) -> None:
        """Turn the turrets its volleys fire from for `dt` seconds (BOSS-29).

        The way their next volley goes (a burst under way first): at the player for aimed shots and
        bursts, along a fan's heading, and with a ring's turn, so a turret firing a spiral spins.
        Pauses included. A laser's turret aims at the player until its beam fires (slowly while its
        warning line shows, `laser_turn_rate_deg`), then holds still (BOSS-31).
        """
        for group in self._turrets:
            source = sources(group.from_)
            if not source:
                continue
            turret = source.turret if hasattr(source, "turret") else None
            if not turret:
                continue
            for i in group.volleys:
                self._states[i].laser_age += dt
            laser = self._laser_aim(ctx, group.volleys, source, turret)
            aim = (
                laser
                if laser is not None
                else self._aim_of(ctx, group.volleys, source, turret, sources)
            )
            spec = turret.spec
            laser_rate = (
                spec.laser_turn_rate_deg
                if spec.laser_turn_rate_deg is not None
                else spec.turn_rate_deg
            )
            rate = spec.turn_rate_deg if laser is None else laser_rate
            # Entities start `aim` at the int 0; it is a float from here on.
            turret.aim = turn_towards(turret.aim, aim, rate * DEG * dt)

    def _laser_aim(
        self,
        ctx: EnemyContext,
        volleys: list[int],
        source: VolleySource,
        turret: BossTurret,
    ) -> float | None:
        """Where `turret` points while one of its `volleys`' lasers shows.

        At the player during its warning line, where it is while the beam fires (still at the player
        for a beam that `sweeps`). None when none shows.
        """
        for i in volleys:
            shape = self.volleys[i].shape
            age = self._states[i].laser_age
            if not isinstance(shape, BossLaserShape):
                continue
            warning = shape.laser.warning_seconds
            firing = shape.laser.firing_seconds
            if age < warning:
                return _aim_at_player(ctx, source, turret)
            if age < warning + firing:
                if shape.laser.sweeps is True:
                    return _aim_at_player(ctx, source, turret)
                return turret.aim
        return None

    def _aim_of(
        self,
        ctx: EnemyContext,
        volleys: list[int],
        source: VolleySource,
        turret: BossTurret,
        sources: VolleySources,
    ) -> float:
        """Where `turret` should point for the next of its `volleys` to fire (radians from rest)."""

        def on(i: int) -> bool:
            return _live(self.volleys[i], lambda f: bool(sources(f)))

        def left(i: int) -> float:
            return self._states[i].left if on(i) else INFINITY

        next_volley: int | None = None
        for i in volleys:
            if self._states[i].burst > 0:
                next_volley = i
                break
        if next_volley is None:
            best = volleys[0]
            for i in range(1, len(volleys)):
                if left(volleys[i]) < left(best):
                    best = volleys[i]
            next_volley = best
        return _turret_aim(
            ctx,
            self.volleys[next_volley],
            self._states[next_volley],
            source,
            turret,
        )

    def _fire(
        self, ctx: EnemyContext, volley: BossVolley, state: _VolleyState, source: VolleySource
    ) -> None:
        shape = volley.shape
        if isinstance(shape, BossBurstShape):
            state.burst = shape.count
            state.burst_left = 0
        elif isinstance(shape, BossMissilesShape):
            fire_aimed(
                ctx,
                state.guns,
                source,
                (shape.count, shape.spacing_deg),
                lambda x, y, h: ctx.fire_missile(x, y, h, shape.missile),
            )
        elif isinstance(shape, BossLaserShape):
            ctx.fire_laser(_laser_owner(volley, state, source), shape.laser)
            state.laser_age = 0
        elif isinstance(shape, BossLaunchShape):
            for enemy in shape.launch(source.x, source.y):
                ctx.spawn(enemy)
        elif isinstance(shape, BossAimedShape):
            fire_aimed(
                ctx,
                state.guns,
                source,
                (shape.count, shape.spacing_deg),
                lambda x, y, h: ctx.fire_bullet(x, y, h, shape.bullet),
            )
        else:
            for h in _preset_headings(shape, state):
                point = state.guns.along(ctx, source, h)
                ctx.fire_bullet(point.x, point.y, h, shape.bullet)

    def _step_burst(
        self,
        ctx: EnemyContext,
        volley: BossVolley,
        state: _VolleyState,
        source: VolleySource,
        time: float,
    ) -> None:
        """Fire the bullets of a burst, `gap` seconds apart.

        Each is aimed at the player when it leaves.
        """
        shape = volley.shape
        if not isinstance(shape, BossBurstShape):
            return
        state.burst_left -= time
        while state.burst > 0 and state.burst_left <= 0:
            if not _on_aim(ctx, volley, state, source):
                state.burst_left = 0
                break
            fire_aimed(
                ctx,
                state.guns,
                source,
                (1, 0),
                lambda x, y, h: ctx.fire_bullet(x, y, h, shape.bullet),
            )
            state.burst -= 1
            state.burst_left += shape.gap


def _find_turret_group(groups: list[_TurretGroup], from_: str) -> _TurretGroup | None:
    for group in groups:
        if group.from_ == from_:
            return group
    return None


def _preset_headings(shape: BossFanShape | BossRingShape, state: _VolleyState) -> list[float]:
    """Return the headings of one volley of bullets in a preset fan, or a ring that turns."""
    if isinstance(shape, BossFanShape):
        return fan_headings(DOWN - shape.heading_deg * DEG, shape.count, shape.spacing_deg * DEG)
    turn = state.turns * shape.turn_deg * DEG
    state.turns += 1
    return [DOWN + turn + (2 * math.pi * k) / shape.count for k in range(shape.count)]


def _turret_aim(
    ctx: EnemyContext,
    volley: BossVolley,
    state: _VolleyState,
    source: VolleySource,
    turret: BossTurret,
) -> float:
    """Where `turret` points for `volley` (radians from rest): see `BossPattern.turn_turrets`."""
    shape = volley.shape
    if isinstance(shape, (BossAimedShape, BossBurstShape, BossLaserShape)):
        return _aim_at_player(ctx, source, turret)
    if isinstance(shape, BossFanShape):
        return wrap_angle(-shape.heading_deg * DEG)
    if isinstance(shape, BossRingShape):
        # Spinning on from the last ring's turn to the next one's as the next one gets ready; its
        # bullets leave from the barrels pointing their way, so the closest of the ring's turns.
        ready = 1 - min(1, state.left / volley.every)
        turn = (state.turns - 1 + ready) * shape.turn_deg * DEG
        spacing = (2 * math.pi) / shape.count
        steps = math.floor(wrap_angle(turret.aim - turn) / spacing + 0.5)
        return wrap_angle(turn + spacing * steps)
    return 0


def _on_aim(
    ctx: EnemyContext, volley: BossVolley, state: _VolleyState, source: VolleySource
) -> bool:
    """Whether the turret of `volley`'s guns points the way its shots go, within `AIM_TOLERANCE`.

    Aimed shots, bursts, missiles and fans leave only once it does (BOSS-29), so they never come
    out of barrels pointing elsewhere. True for the others: a ring's bullets go all round, a laser
    has its warning line, and a volley not on a turret has none to wait for.
    """
    shape = volley.shape
    if not volley.turret or isinstance(shape, (BossRingShape, BossLaserShape, BossLaunchShape)):
        return True
    turret = source.turret if hasattr(source, "turret") else None
    if not turret:
        return True
    aim = _turret_aim(ctx, volley, state, source, turret)
    return abs(wrap_angle(aim - turret.aim)) <= AIM_TOLERANCE


class _TurnedLaserOwner:
    """A laser owner that follows its piece's turret: its heading turns with the turret."""

    def __init__(self, owner: LaserOwner, turret: BossTurret) -> None:
        self._owner = owner
        self._turret = turret

    @property
    def emitter(self) -> PlanePoint | RaisedPoint:
        return self._owner.emitter

    @property
    def heading(self) -> float:
        return self._owner.heading + self._turret.aim

    @property
    def gone(self) -> bool:
        return self._owner.gone

    @property
    def health(self) -> float:
        return self._owner.health


def _laser_owner(volley: BossVolley, state: _VolleyState, source: VolleySource) -> LaserOwner:
    """Return what a laser of `volley` leaves from and follows: its piece, from a muzzle.

    Turned with the piece's turret when the volley is on it (phase 8 review).
    """
    owner = state.guns.laser(source)
    turret = source.turret if volley.turret and hasattr(source, "turret") else None
    if not turret:
        return owner
    return _TurnedLaserOwner(owner, turret)


def _aim_at_player(ctx: EnemyContext, source: VolleySource, turret: BossTurret) -> float:
    """How far `turret` must turn from its rest (straight down) to point at the player."""
    if hasattr(source, "place"):
        pivot = source.place((turret.spec.x, turret.spec.y, 0))
        pivot_x, pivot_y = pivot.x, pivot.y
    else:
        pivot_x, pivot_y = source.x, source.y
    return wrap_angle(heading_to(pivot_x, pivot_y, ctx.player_x, ctx.player_y) - DOWN)
