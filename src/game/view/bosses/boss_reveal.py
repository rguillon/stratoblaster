"""How a boss's hidden weapon parts come out as it transforms (docs/superpowers/specs/
2026-10-31-ship-glow-and-boss-transform-design.md, Part B).

Two styles, the design's `revealStyle`:

- `armour` (the default): an armour plate covers each hidden part; as the boss transforms it blows
  off (thrown out, spinning, falling) and the weapon beneath rises into place;
- `unfold`: the hidden part is folded into the hull and swings out, growing, about its spot.

Model space of a boss: logical pixels, +Y up (towards the camera), see `boss_limbs.boss_point`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_limbs import ORIGIN, boss_point, hang
from game.view.enemies.enemy_mesh import build_enemy_model
from render.babylon import get_hierarchy_bounding_vectors, new_transform_node, set_enabled
from render.edge_trim_mesh import clear_trim

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Vec3 = list[float]
__pragma__("noskip")

HIDDEN = "hidden"
REVEALING = "revealing"
SHOWN = "shown"


def reveal_phase(reveal: int | None, form: int, transforming_into: int) -> str:
    """Whether a part revealed by transformation `reveal` is hidden, coming out, or shown, for a
    boss that has done `form` transformations and is doing `transforming_into` (0: none)."""
    if reveal is None or form >= reveal:
        return SHOWN
    if transforming_into == reveal:
        return REVEALING
    return HIDDEN


def ease(t: float) -> float:
    """Smooth step from 0 to 1 (slow start, slow end)."""
    k = min(1, max(0, t))
    return k * k * (3 - 2 * k)


class Pose:
    """Where a node goes: its `position`, `scale` and turn about Y (`yaw`, radians)."""

    def __init__(self, position: Vec3, scale: float, yaw: float) -> None:
        self.position = position
        self.scale = scale
        self.yaw = yaw


def unfold_pose(base: Vec3, at: Vec3, t: float) -> Pose:
    """The pose of a part's root (at `base` on its frame, its model drawn round `at`) unfolding,
    `t` of the way: it grows from nothing about `at`, swinging out from folded along the hull."""
    e = ease(t)
    side = 1 if at[0] >= 0 else -1
    yaw = (1 - e) * BOSS_LOOK.reveal.unfoldTurn * side
    c = math.cos(yaw)
    s = math.sin(yaw)
    # Babylon's turn about Y: x' = x cos + z sin, z' = -x sin + z cos.
    tx = (at[0] * c + at[2] * s) * e
    tz = (-at[0] * s + at[2] * c) * e
    ty = at[1] * e
    return Pose([base[0] + at[0] - tx, base[1] + at[1] - ty, base[2] + at[2] - tz], e, yaw)


def rise_pose(base: Vec3, radius: float, t: float) -> Pose:
    """The pose of a part's root rising out of the hull from under its armour, `t` of the way."""
    e = ease(t)
    sunk = (1 - e) * radius * BOSS_LOOK.reveal.sink
    return Pose([base[0], base[1] - sunk, base[2]], 1, 0)


def plate_pose(at: Vec3, radius: float, t: float) -> Pose:
    """The pose of an armour plate (drawn round `at`) blown off, `t` of the way: thrown out from
    the boss's centre and up, spinning, falling back down as it goes."""
    look = BOSS_LOOK.reveal
    horizontal = math.hypot(at[0], at[2])
    dx = at[0] / horizontal if horizontal > 0 else 0
    dz = at[2] / horizontal if horizontal > 0 else 1
    out = t * radius * look.throw
    up = 4 * t * (1 - t) * radius * look.lift - t * t * radius * look.fall
    return Pose([dx * out, up, dz * out], max(0, 1 - t * t), t * look.spin)


def _plate_outline(cx: float, cz: float, half: float) -> list[list[float]]:
    """An octagon of half-width `half` round (cx, cz)."""
    result: list[list[float]] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        result.append([cx + math.cos(a) * half, cz + math.sin(a) * half])
    return result


def build_plate(name: str, scene: Any, neon: Any, at: Vec3, half: float, top: float) -> Any:
    """An armour plate over a hidden part: a bevelled octagon of half-width `half` round `at`,
    from the boss's middle up to `top`, in the hull's metal, with a neon seam."""
    hull = ENEMY_LOOK.hull

    def draw(p: Any) -> None:
        outline = _plate_outline(at[0], at[2], half)
        height = max(top, half * 0.3)
        p.hull.bevel_slab(outline, [0, height * 0.7, height], [0, half * 0.2], hull.panel)
        seam = _plate_outline(at[0], at[2], half * 0.45)
        p.neon.bevel_slab(seam, [height, height + 0.4, height + 0.6], [0, 0.2], neon)

    model = build_enemy_model(name + "-plate", scene, neon, draw)
    # It blows off: it must not hide the edges of the weapon beneath from the trim.
    clear_trim(model.root)
    return model


class RevealView:
    """How one hidden part of a boss model comes out: its part's root (`root`, at `base` on its
    frame), and in the `armour` style its plate (`plate`, a node, its model drawn round `at`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        reveal: int,
        style: str,
        root: Any,
        base: Vec3,
        at: Vec3,
        radius: float,
        plate: Any,
        plate_base: Vec3,
    ) -> None:
        self.reveal = reveal
        self.style = style
        self.root = root
        self.base = base
        self.at = at
        self.radius = radius
        self.plate = plate
        self.plate_base = plate_base

    def show(self, form: int, transforming_into: int, transform: float) -> str:
        """Poses the part (and its plate) for a boss that has done `form` transformations, doing
        `transforming_into` `transform` of the way. Returns the part's phase (see
        `reveal_phase`): a hidden part's model is not shown."""
        phase = reveal_phase(self.reveal, form, transforming_into)
        if phase == HIDDEN:
            set_enabled(self.root, False)
            self._pose(Pose(self.base, 1, 0))
            self._plate(Pose([0, 0, 0], 1, 0), True)
            return phase
        if phase == SHOWN:
            self._pose(Pose(self.base, 1, 0))
            self._plate(Pose([0, 0, 0], 1, 0), False)
            return phase
        if self.style == "unfold":
            self._pose(unfold_pose(self.base, self.at, transform))
        else:
            self._pose(rise_pose(self.base, self.radius, transform))
            self._plate(plate_pose(self.at, self.radius, transform), True)
        return phase

    def _pose(self, pose: Pose) -> None:
        root = self.root
        root.position.set(pose.position[0], pose.position[1], pose.position[2])
        root.scaling.set(pose.scale, pose.scale, pose.scale)
        root.rotation.y = pose.yaw

    def _plate(self, pose: Pose, shown: bool) -> None:
        if self.plate is None:
            return
        set_enabled(self.plate, shown)
        if not shown:
            return
        # The plate turns and shrinks about its own centre `at`.
        at = self.at
        c = math.cos(pose.yaw)
        s = math.sin(pose.yaw)
        k = pose.scale
        rx = (at[0] * c + at[2] * s) * k
        rz = (-at[0] * s + at[2] * c) * k
        b = self.plate_base
        self.plate.position.set(
            b[0] + pose.position[0] + at[0] - rx,
            b[1] + pose.position[1],
            b[2] + pose.position[2] + at[2] - rz,
        )
        self.plate.scaling.set(k, k, k)
        self.plate.rotation.y = pose.yaw


def build_reveal(design: Any, spec: Any, model_root: Any, frame: Any, neon: Any) -> RevealView:
    """The reveal of the hidden part `spec` of a boss of `design`, its model under `model_root`
    (hung on `frame`)."""
    style = design.revealStyle if design.revealStyle else "armour"
    at = boss_point(spec.x, spec.y)
    base = [model_root.position.x, model_root.position.y, model_root.position.z]
    plate = None
    plate_base = [0.0, 0.0, 0.0]
    if style == "armour":
        scene = model_root.getScene()
        bounds = get_hierarchy_bounding_vectors(model_root)
        half = max(
            spec.radius,
            (bounds.max.x - bounds.min.x) / 2,
            (bounds.max.z - bounds.min.z) / 2,
        )
        node = new_transform_node(design.id + "-" + spec.id + "-armour", scene)
        hang(node, ORIGIN, frame)
        plate_base = [node.position.x, node.position.y, node.position.z]
        model = build_enemy_model_plate(design.id + "-" + spec.id, scene, neon, at, half, bounds)
        model.root.parent = node
        plate = node
    return RevealView(spec.reveal, style, model_root, base, at, spec.radius, plate, plate_base)


def build_enemy_model_plate(
    name: str, scene: Any, neon: Any, at: Vec3, half: float, bounds: Any
) -> Any:
    """The plate model over a part whose model spans `bounds` (its top is the plate's)."""
    top = max(0, bounds.max.y * BOSS_LOOK.reveal.plateTop)
    return build_plate(name, scene, neon, [at[0], 0, at[2]], half * BOSS_LOOK.reveal.plateSize, top)
