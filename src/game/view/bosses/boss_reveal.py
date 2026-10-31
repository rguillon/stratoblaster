"""How a boss's hidden weapon parts come out as it transforms (docs/superpowers/specs/2026-10-31-
boss-armour-shedding-design.md, D-224): folded flat into the frame its shed armour leaves, each
swings up on its hinge, rising, then slides its barrel out (overshooting and settling). Nothing
grows from nothing.

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_limbs import boss_point
from render.babylon import set_enabled

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Vec3 = list[float]
__pragma__("noskip")

HIDDEN = "hidden"
REVEALING = "revealing"
SHOWN = "shown"


def reveal_phase(reveal: int | None, form: int, transforming_into: int) -> str:
    """Whether something revealed (or shed) by transformation `reveal` is still hidden, coming
    out, or shown, for a boss that has done `form` transformations and is doing
    `transforming_into` (0: none)."""
    if reveal is None or form >= reveal:
        return SHOWN
    if transforming_into == reveal:
        return REVEALING
    return HIDDEN


def ease(t: float) -> float:
    """Smooth step from 0 to 1 (slow start, slow end)."""
    k = min(1, max(0, t))
    return k * k * (3 - 2 * k)


def back_out(t: float, overshoot: float) -> float:
    """From 0 to 1, past 1 by a little (`overshoot`: the back-out ease's constant) then back."""
    k = min(1, max(0, t)) - 1
    return 1 + (overshoot + 1) * k * k * k + overshoot * k * k


def share(t: float, span: list[float]) -> float:
    """How far `t` is through `span` [start, end], from 0 to 1."""
    return min(1, max(0, (t - span[0]) / (span[1] - span[0])))


class Pose:
    """Where a node goes: its `position` and its turn about Y (`yaw`, radians)."""

    def __init__(self, position: Vec3, yaw: float) -> None:
        self.position = position
        self.yaw = yaw


def hinge_pose(base: Vec3, hinge: Vec3, fold: float, sink: float, t: float) -> Pose:
    """The pose of a part's root (at `base` on its frame) swinging up about `hinge` (model space),
    `t` of the way: turned by `fold` and `sink` px down at first, as it rests at the end."""
    e = ease(t)
    yaw = (1 - e) * fold
    c = math.cos(yaw)
    s = math.sin(yaw)
    # Babylon's turn about Y: x' = x cos + z sin, z' = -x sin + z cos.
    rx = hinge[0] * c + hinge[2] * s
    rz = -hinge[0] * s + hinge[2] * c
    return Pose([base[0] + hinge[0] - rx, base[1] - (1 - e) * sink, base[2] + hinge[2] - rz], yaw)


def slide_offset(axis: Vec3, distance: float, t: float) -> Vec3:
    """Where a sliding barrel is from its rest, `t` of the way out: `distance` back along `axis`
    at first, overshooting its rest a little before it settles."""
    back = (1 - back_out(t, BOSS_LOOK.reveal.overshoot)) * distance
    return [-axis[0] * back, -axis[1] * back, -axis[2] * back]


def weapon_hinge(at: Vec3, radius: float, mount: Any) -> list[Any]:
    """`[hinge, fold]` of a hidden weapon drawn round `at` (model space): from its `mount`
    `[dx, dy, fold]` (px, X right, Y up) if it has one, else on its inner side (towards the centre
    line, or its tail for one on it), folded back along the hull."""
    if mount != None:  # noqa: E711
        offset = boss_point(mount[0], mount[1])
        return [[at[0] + offset[0], 0, at[2] + offset[2]], mount[2]]
    if abs(at[0]) < 1:
        return [[at[0], 0, at[2] - radius * 0.9], math.pi * 0.9]
    side = 1 if at[0] > 0 else -1
    return [[at[0] - side * radius * 0.9, 0, at[2]], side * 2.4]


class Slide:
    """A piece of a weapon that slides out: its `node`, its `rest` position, along `axis` by
    `distance`."""

    def __init__(self, node: Any, rest: Vec3, axis: Vec3, distance: float) -> None:
        self.node = node
        self.rest = rest
        self.axis = axis
        self.distance = distance


class RevealView:
    """How one hidden part of a boss model comes out: its part's root (`root`, at `base` on its
    frame), its hinge and fold (`weapon_hinge`), how far it sinks, and what slides out."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        reveal: int,
        root: Any,
        base: Vec3,
        hinge: list[Any],
        sink: float,
        slides: list[Slide],
    ) -> None:
        self.reveal = reveal
        self.root = root
        self.base = base
        self.hinge = hinge
        self.sink = sink
        self.slides = slides

    def show(self, form: int, transforming_into: int, transform: float) -> str:
        """Poses the part for a boss that has done `form` transformations, doing
        `transforming_into` `transform` of the way. Returns its phase (see `reveal_phase`)."""
        phase = reveal_phase(self.reveal, form, transforming_into)
        look = BOSS_LOOK.reveal
        if phase == REVEALING and transform < look.swing[0]:
            # Folded away under the armour until it has burst.
            set_enabled(self.root, False)
            return phase
        if phase == HIDDEN:
            set_enabled(self.root, False)
            self._pose(Pose(self.base, 0), 1)
            return phase
        if phase == SHOWN:
            self._pose(Pose(self.base, 0), 1)
            return phase
        set_enabled(self.root, True)
        swing = share(transform, look.swing)
        pose = hinge_pose(self.base, self.hinge[0], self.hinge[1], self.sink, swing)
        self._pose(pose, share(transform, look.slide))
        return phase

    def _pose(self, pose: Pose, slide: float) -> None:
        root = self.root
        root.position.set(pose.position[0], pose.position[1], pose.position[2])
        root.rotation.y = pose.yaw
        for piece in self.slides:
            d = slide_offset(piece.axis, piece.distance, slide)
            r = piece.rest
            piece.node.position.set(r[0] + d[0], r[1] + d[1], r[2] + d[2])


def build_reveal(design: Any, spec: Any, model_root: Any, slides: list[Slide]) -> RevealView:
    """The reveal of the hidden part `spec` of a boss of `design`, its model under `model_root`,
    the pieces that slide out `slides`."""
    at = boss_point(spec.x, spec.y)
    weapons = design.weapons
    look = weapons[spec.id] if weapons != None and spec.id in weapons else None  # noqa: E711
    mount = look.mount if look != None and "mount" in look else None  # noqa: E711
    base = [model_root.position.x, model_root.position.y, model_root.position.z]
    hinge = weapon_hinge(at, spec.radius, mount)
    sink = spec.radius * BOSS_LOOK.reveal.sink
    if look != None and "rig" in look and look.rig:  # noqa: E711
        # At the end of a rig (D-228): it rises into place as the rig unfolds, no swing.
        hinge = [at, 0]
        sink = spec.radius * 0.5
    return RevealView(spec.reveal, model_root, base, hinge, sink, slides)
