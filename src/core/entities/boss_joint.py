"""Moving limbs of a boss, ported from `core/entities/boss-joint.ts` (phase 7 review).

A joint turns what hangs on it (parts, their hit circles and muzzles, other joints) around its
pivot, swinging to and fro. Joints hang on other joints, so an arm can bend at the shoulder, the
elbow and the wrist.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Protocol  # noqa: E402


class JointedPart(Protocol):
    """What a part says about the joint it hangs on (see `BossPartSpec`)."""

    @property
    def id(self) -> str: ...

    @property
    def joint(self) -> str | None: ...

    @property
    def orbits(self) -> bool: ...


__pragma__("noskip")


class JointSwing:
    """How a joint swings: up to `amplitude_deg` either way and back every `period` seconds."""

    def __init__(self, amplitude_deg: float, period: float, phase: float = 0) -> None:
        """`phase` (0..1) is how far into a period it starts (0 when omitted)."""
        self.amplitude_deg = amplitude_deg
        self.period = period
        self.phase = phase


class BossJointSpec:
    """A joint: its pivot, the joint it hangs on, and how it swings."""

    def __init__(
        self,
        x: float,
        y: float,
        swing: JointSwing,
        parent: str | None = None,
    ) -> None:
        """`x` and `y` are its pivot, from the boss's centre (X right, Y up), as the boss is drawn
        at rest. `parent` is the joint it hangs on, if any: it moves with that one.
        """
        self.x = x
        self.y = y
        self.swing = swing
        self.parent = parent


def _check_joints(specs: dict[str, BossJointSpec], parts: Sequence[JointedPart]) -> None:
    """Raises when a joint or a part hangs on no joint or a joint on itself, or a part also
    orbits.
    """
    for part in parts:
        joint = part.joint
        if joint is None:
            continue
        if joint not in specs:
            raise ValueError('Part "' + part.id + '" hangs on no joint "' + joint + '"')
        if part.orbits:
            raise ValueError('Part "' + part.id + '" both orbits and hangs on a joint')
    # Transcrypt cannot iterate a dict directly: the keys are listed.
    for joint_id in specs.keys():  # noqa: SIM118
        seen: list[str] = []
        j: str | None = joint_id
        while j is not None:
            if j not in specs:
                raise ValueError('Boss joint "' + joint_id + '" hangs on no joint "' + j + '"')
            if j in seen:
                raise ValueError('Boss joint "' + joint_id + '" hangs on itself')
            seen.append(j)
            j = specs[j].parent


class BossJoints:
    """The joints of a boss, by id, and how far each is turned now."""

    def __init__(
        self,
        specs: dict[str, BossJointSpec] | None = None,
        parts: Sequence[JointedPart] | None = None,
    ) -> None:
        """Raises when a joint or one of `parts` hangs on no joint, or a part also orbits."""
        self._specs: dict[str, BossJointSpec] = dict(specs) if specs is not None else {}
        self._angles: dict[str, float] = {}
        self._time = 0.0
        _check_joints(self._specs, parts if parts is not None else [])
        self.step(0)

    def step(self, dt: float) -> None:
        """Swings them on by `dt` seconds."""
        self._time += dt
        for joint_id in self._specs.keys():  # noqa: SIM118
            swing = self._specs[joint_id].swing
            turns = self._time / swing.period + swing.phase
            self._angles[joint_id] = ((swing.amplitude_deg * math.pi) / 180) * math.sin(
                2 * math.pi * turns
            )

    def angle(self, joint_id: str) -> float:
        """How far joint `joint_id` is turned on the one it hangs on: radians, clockwise on
        screen.
        """
        return self._angles.get(joint_id, 0)

    def move(self, joint_id: str | None, x: float, y: float) -> tuple[float, float]:
        """Where the point `(x, y)` (from the boss's centre, as drawn at rest) of something hanging
        on joint `joint_id` is now, turned by that joint and those it hangs on. Unmoved without a
        joint.
        """
        px, py = x, y
        j = joint_id
        while j is not None:
            spec = self._specs.get(j)
            if spec is None:
                break
            a = self.angle(j)
            c, s = math.cos(a), math.sin(a)
            dx, dy = px - spec.x, py - spec.y
            px, py = spec.x + dx * c + dy * s, spec.y - dx * s + dy * c
            j = spec.parent
        return px, py
