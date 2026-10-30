"""Player shots of one ship (P03-R01..R03)

Fires the selected weapon at the selected level from the muzzle, moves the projectiles, applies
damage to the targets and reports impacts. Pure and deterministic: everything depends on the `dt`
given to `step`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.shot_target import damage_target, is_alive
from core.entities.weapon import BeamWeaponDefinition, ProjectileWeaponDefinition
from core.systems.beam import BeamSegment, trace_beam
from core.systems.projectile_motion import Projectile, advance_projectile

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import TypeVar  # noqa: E402

T = TypeVar("T")

from core.entities.shot_target import ShotTarget  # noqa: E402
from core.entities.weapon import WeaponDefinition  # noqa: E402

__pragma__("noskip")

DEG = math.pi / 180


class ShotImpact:
    """Where a projectile hit, for effects. `blast_radius` is 0 for a direct hit. `blocked` is true
    when the hit did no damage, e.g. on a shielded core (a sound of its own, P12-R09).
    """

    def __init__(
        self, weapon_id: str, x: float, y: float, blast_radius: float, blocked: bool
    ) -> None:
        self.weapon_id = weapon_id
        self.x = x
        self.y = y
        self.blast_radius = blast_radius
        self.blocked = blocked


class ShotWorldOptions:
    """The playfield (X in [0, width], Y in [0, height]) and what shots are culled by: shots
    `cull_margin` outside it are removed.
    """

    def __init__(self, width: float, height: float, cull_margin: float) -> None:
        self.width = width
        self.height = height
        self.cull_margin = cull_margin


def _at_or_none(values: Sequence[T], index: int) -> T | None:  # noqa: UP047 (no PEP 695)
    """`values[index]`, or None past its ends (Transcrypt gives undefined there)."""
    return values[index] if 0 <= index < len(values) else None


class ShotWorld:
    """Player shots of one ship. Its `projectiles` are a pool: entries with `alive` false are free
    for reuse.
    """

    def __init__(self, options: ShotWorldOptions, weapon: WeaponDefinition) -> None:
        self.options = options
        self.projectiles: list[Projectile] = []
        self.targets: list[ShotTarget] = []
        # Where shots launched from the muzzle start (the ship's nose); beams always start here.
        self.muzzle_x = 0.0
        self.muzzle_y = 0.0
        # Where shots launched from the centre start.
        self.center_x = 0.0
        self.center_y = 0.0
        # Beam segments of the last step (empty unless the weapon is a beam).
        self.beam: list[BeamSegment] = []
        # Impacts of the last step.
        self.impacts: list[ShotImpact] = []
        # Total damage dealt since the world was created.
        self.total_damage = 0.0
        # Whether the weapon fires; shots already in flight keep flying either way.
        self.firing = True
        # Volleys started since the world was created (a volley: every stream of the level once).
        self.volleys = 0
        self._weapon = weapon
        self._level = 1
        # Seconds until the next shot.
        self._cooldown = 0.0
        # The stream that fires next.
        self._next = 0

    @property
    def weapon(self) -> WeaponDefinition:
        return self._weapon

    @property
    def level(self) -> int:
        return self._level

    def select(self, weapon: WeaponDefinition, level: float) -> None:
        """Selects the weapon and its level (clamped to the weapon's levels). Shots in flight
        stay."""
        self._weapon = weapon
        self._level = min(max(1, math.floor(level + 0.5)), len(weapon.levels))
        self._cooldown = 0.0
        self._next = 0

    @property
    def active_count(self) -> int:
        """Number of projectiles in flight."""
        count = 0
        for p in self.projectiles:
            if p.alive:
                count += 1
        return count

    def step(self, dt: float) -> None:
        """Advances the simulation by `dt` seconds."""
        self.impacts = []
        for shot in self.projectiles:
            if shot.alive:
                self._move(shot, dt)
        weapon = self._weapon
        if not self.firing:
            self.beam = []
            self._cooldown = 0.0
            self._next = 0
        elif isinstance(weapon, ProjectileWeaponDefinition):
            self.beam = []
            self._fire(weapon, dt)
        else:
            self._fire_beam(weapon, dt)

    def _move(self, shot: Projectile, dt: float) -> None:
        advance_projectile(shot, self.targets, dt)
        self._collide(shot)
        if shot.alive and self._is_out(shot):
            shot.alive = False

    def _fire(self, weapon: ProjectileWeaponDefinition, dt: float) -> None:
        """Fires the level's streams one after the other, in their listed order, evenly spaced over
        the volley (reviewer, 2026-10-26): each stream still fires `shots_per_second` times a
        second.
        """
        self._cooldown -= dt
        streams_at = _at_or_none(weapon.levels, self._level - 1)
        streams = streams_at if streams_at is not None else []
        count = max(1, len(streams))
        while self._cooldown <= 0:
            # A shot due during this step has been flying for the rest of the step.
            flown = -self._cooldown
            index = self._next % count
            stream = _at_or_none(streams, index)
            if self._next % count == 0:
                self.volleys += 1
            if stream:
                self._move(
                    self._spawn(weapon, stream.offset_x, stream.angle_deg * DEG),
                    flown,
                )
            self._next = (self._next + 1) % count
            self._cooldown += 1 / (weapon.shots_per_second * count)

    def _spawn(
        self, weapon: ProjectileWeaponDefinition, offset_x: float, heading: float
    ) -> Projectile:
        shot = _first_free_projectile(self.projectiles)
        if shot is None:
            shot = Projectile(True, weapon, 0, 0, 0, 0, 0)
            self.projectiles.append(shot)
        shot.alive = True
        shot.weapon = weapon
        from_center = weapon.launch_point == "center"
        shot.x = (self.center_x if from_center else self.muzzle_x) + offset_x
        shot.y = (self.center_y if from_center else self.muzzle_y) - weapon.launch_back
        shot.heading = heading
        shot.speed = weapon.launch_speed
        shot.age = 0
        return shot

    def _fire_beam(self, weapon: BeamWeaponDefinition, dt: float) -> None:
        trace = trace_beam(
            weapon.levels,
            self._level,
            self.muzzle_x,
            self.muzzle_y,
            self.options.height + self.options.cull_margin,
            self.targets,
        )
        self.beam = trace.segments
        for hit in trace.hits:
            level = _at_or_none(weapon.levels, hit.level - 1)
            dps = level.damage_per_second if level else 0
            self.total_damage += damage_target(hit.target, dps * dt)

    def _collide(self, shot: Projectile) -> None:
        hit = None
        for t in self.targets:
            if (
                is_alive(t)
                and (t.x - shot.x) ** 2 + (t.y - shot.y) ** 2
                <= (t.radius + shot.weapon.radius) ** 2
            ):
                hit = t
                break
        if hit is None:
            return
        weapon = shot.weapon
        shot.alive = False
        dealt = self._damage(shot, hit)
        self.total_damage += dealt
        self.impacts.append(ShotImpact(weapon.id, shot.x, shot.y, weapon.blast_radius, dealt <= 0))

    def _damage(self, shot: Projectile, hit: ShotTarget) -> float:
        """Deals the shot's damage to `hit`, or to everything in its blast. Returns the damage
        dealt.
        """
        weapon = shot.weapon
        if weapon.blast_radius <= 0:
            return damage_target(hit, weapon.damage)
        dealt = 0.0
        for target in self.targets:
            reach = weapon.blast_radius + target.radius
            if is_alive(target) and (target.x - shot.x) ** 2 + (target.y - shot.y) ** 2 <= reach**2:
                dealt += damage_target(target, weapon.damage)
        return dealt

    def _is_out(self, shot: Projectile) -> bool:
        m = self.options.cull_margin
        return (
            shot.x < -m
            or shot.x > self.options.width + m
            or shot.y < -m
            or shot.y > self.options.height + m
        )


def _first_free_projectile(pool: list[Projectile]) -> Projectile | None:
    for shot in pool:
        if not shot.alive:
            return shot
    return None
