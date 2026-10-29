"""One-line weapon description for the shots viewer, ported from `ui/weapon-summary.ts`."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")

from typing import Any  # noqa: E402

from core.entities.weapon import WeaponDefinition  # noqa: E402

__pragma__("noskip")

from core.entities.weapon import BeamWeaponDefinition  # noqa: E402


def _signed_angle(deg: float) -> str:
    if deg == 0:
        return "0°"
    sign = "+" if deg > 0 else "−"
    return sign + str(abs(deg)) + "°"


def _plural(n: int, word: str) -> str:
    return str(n) + " " + word + ("" if n == 1 else "s")


def _has_level(weapon: WeaponDefinition, level: int) -> bool:
    """True when `weapon.levels[level - 1]` exists (JavaScript's `undefined` is out of range)."""
    return level >= 1 and level <= len(weapon.levels)


def weapon_summary(weapon: WeaponDefinition, level: int) -> str:
    """One-line description of a weapon at a level, for the shots viewer (P03-R10), e.g.
    "Bullet L3 · 3 streams (0°, −10°, +10°) · 8 shots/s per stream · 10 damage".
    """
    head: str = weapon.name + " L" + str(level)
    if isinstance(weapon, BeamWeaponDefinition):
        if not _has_level(weapon, level):
            return head
        beam: Any = weapon.levels[level - 1]
        pierce = (
            "goes through " + _plural(level - 1, "ship") if level > 1 else "stops at the first ship"
        )
        return (
            head
            + " · "
            + str(beam.damage_per_second)
            + " damage/s · "
            + str(beam.width)
            + " px wide · "
            + pierce
        )
    streams: Any = weapon.levels[level - 1] if _has_level(weapon, level) else []
    angles = ", ".join([_signed_angle(s.angle_deg) for s in streams])
    area = " within " + str(weapon.blast_radius) + " px" if weapon.blast_radius > 0 else ""
    return " · ".join(
        [
            head,
            _plural(len(streams), "stream") + " (" + angles + ")",
            str(weapon.shots_per_second) + " shots/s per stream",
            str(weapon.damage) + " damage" + area,
        ]
    )
