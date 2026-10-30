"""Data-only description of player weapons

Positions and distances are in logical pixels, with X to the right and Y up (forward); angles are
in degrees from forward, positive to the right.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
__pragma__("noskip")


class ShotStream:
    """One stream of shots at a weapon level: where they leave the ship and which way they go."""

    def __init__(self, offset_x: float, angle_deg: float) -> None:
        """`offset_x` is the sideways offset from the ship's muzzle."""
        self.offset_x = offset_x
        self.angle_deg = angle_deg


class ProjectileWeaponDefinition:
    """A weapon that fires projectiles (bullets, missiles...) in streams."""

    kind = "projectile"

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        id: str,
        name: str,
        launch_point: str,
        shots_per_second: float,
        launch_speed: float,
        acceleration: float,
        max_speed: float,
        homing_turn_rate_deg: float,
        homing_range: float,
        radius: float,
        damage: float,
        blast_radius: float,
        levels: list[list[ShotStream]],
        launch_back: float = 0,
    ) -> None:
        """Fields, with the optional `launch_back` last.

        - `launch_point`: `"muzzle"` (the ship's nose) or `"center"`, where the streams start.
        - `shots_per_second`: shots per second in each stream.
        - `acceleration`: constant acceleration along the heading, px/s² (0: constant velocity).
        - `max_speed`: speed cap, px/s; ignored when `acceleration` is 0.
        - `homing_turn_rate_deg`: turn rate towards the closest target, degrees a second (0: flies
          straight).
        - `homing_range`: a homing shot only sees targets within this distance of it, px (phase 5
          review).
        - `blast_radius`: 0 damages the target hit only; above 0, every target within this
          distance of the impact.
        - `levels[i]` lists the streams fired at level `i + 1`.
        - `launch_back`: shots start this far behind the launch point (px, towards the ship's
          tail), so they leave from inside the ship; 0 when omitted.
        """
        self.id = id
        self.name = name
        self.launch_point = launch_point
        self.shots_per_second = shots_per_second
        self.launch_speed = launch_speed
        self.acceleration = acceleration
        self.max_speed = max_speed
        self.homing_turn_rate_deg = homing_turn_rate_deg
        self.homing_range = homing_range
        self.radius = radius
        self.damage = damage
        self.blast_radius = blast_radius
        self.levels = levels
        self.launch_back = launch_back


class BeamLevel:
    """One level of a beam weapon."""

    def __init__(self, damage_per_second: float, width: float) -> None:
        self.damage_per_second = damage_per_second
        self.width = width


class BeamWeaponDefinition:
    """A continuous beam fired straight ahead. At level 1 it stops at the first target it hits;
    above, it goes through the target and continues one level lower.
    """

    kind = "beam"

    def __init__(self, id: str, name: str, levels: list[BeamLevel]) -> None:
        """`levels[i]` is level `i + 1`."""
        self.id = id
        self.name = name
        self.levels = levels


__pragma__("skip")
type WeaponDefinition = ProjectileWeaponDefinition | BeamWeaponDefinition
__pragma__("noskip")


def _validate_projectile(weapon: ProjectileWeaponDefinition) -> None:
    positive = [
        ("shots_per_second", weapon.shots_per_second),
        ("launch_speed", weapon.launch_speed),
        ("radius", weapon.radius),
        ("damage", weapon.damage),
    ]
    for key, value in positive:
        if not (value > 0):  # noqa: SIM201
            raise ValueError('Weapon "' + weapon.id + '": ' + key + " must be positive")
    non_negative = [
        ("acceleration", weapon.acceleration),
        ("homing_turn_rate_deg", weapon.homing_turn_rate_deg),
        ("homing_range", weapon.homing_range),
        ("blast_radius", weapon.blast_radius),
    ]
    for key, value in non_negative:
        if not (value >= 0):
            raise ValueError('Weapon "' + weapon.id + '": ' + key + " must be >= 0")
    if not (weapon.launch_back >= 0):
        raise ValueError('Weapon "' + weapon.id + '": launch_back must be >= 0')
    if weapon.acceleration > 0 and not (weapon.max_speed >= weapon.launch_speed):
        raise ValueError('Weapon "' + weapon.id + '": max_speed must be >= launch_speed')
    for streams in weapon.levels:
        if len(streams) == 0:
            raise ValueError('Weapon "' + weapon.id + '": every level needs at least one stream')


def _validate_beam(weapon: BeamWeaponDefinition) -> None:
    for level in weapon.levels:
        if not (level.damage_per_second > 0) or not (level.width > 0):
            raise ValueError('Weapon "' + weapon.id + '": damage and width must be positive')


def validate_weapons(weapons: list[WeaponDefinition]) -> None:
    """Raises a descriptive error if the weapons have duplicate ids, no levels or invalid values."""
    ids: list[str] = []
    for weapon in weapons:
        if weapon.id in ids:
            raise ValueError('Duplicate weapon id "' + weapon.id + '"')
        ids.append(weapon.id)
        if len(weapon.levels) == 0:
            raise ValueError('Weapon "' + weapon.id + '" has no level')
        if isinstance(weapon, ProjectileWeaponDefinition):
            _validate_projectile(weapon)
        else:
            _validate_beam(weapon)


def weapon_level_count(weapon: WeaponDefinition) -> int:
    """Number of levels of a weapon."""
    return len(weapon.levels)


def find_weapon(weapons: list[WeaponDefinition], id: str) -> WeaponDefinition:
    """Returns the weapon with the given id, or raises if there is none."""
    for weapon in weapons:
        if weapon.id == id:
            return weapon
    raise ValueError('Unknown weapon "' + id + '"')
