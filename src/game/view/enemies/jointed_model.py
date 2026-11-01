# Copyright (c) 2026 Renaud Guillon
"""How an enemy with moving parts is drawn (ENM-27).

Everything is in model space as at rest (logical pixels, nose +Z, Y up; a point `(x, y)` of the
design is at `boss_point`).
"""

from core.entities.jointed_enemy import JointedEnemy
from game.config.record import field
from game.view.bosses.boss_limbs import boss_point
from game.view.enemies.enemy_mesh import build_enemy_model
from game.view.enemies.living_motion import new_breath
from render.babylon import new_transform_node

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[float]
type Rgb = list[float]
# __pragma__ ("noskip")


ORIGIN = [0, 0, 0]  # type: list[float]


def sub(a: Vec3, b: Any) -> list[float]:
    """Return `a - b`, component by component."""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


class JointedModelError(Exception):
    """An enemy's joint or part does not match its model."""


class Frame:
    """A joint's node and its pivot in model space."""

    def __init__(self, node: Any, origin: Any) -> None:
        self.node = node
        self.origin = origin


def joint_frames(name: str, design: Any, root: Any) -> dict[str, Frame]:
    """Return a node per joint, hung on the joint it hangs on.

    Its pivot is where the design puts it.
    """
    specs = field(design, "joints", {})
    frames: dict[str, Frame] = {}

    def make(joint_id: str) -> Frame:
        if joint_id in frames:
            return frames[joint_id]
        spec = field(specs, joint_id, None)
        if spec == None:
            raise JointedModelError('Enemy "' + name + '" has no joint "' + joint_id + '"')
        parent = Frame(root, ORIGIN) if spec["parent"] == None else make(spec["parent"])
        origin = boss_point(spec["x"], spec["y"])
        node = new_transform_node(name + "-" + joint_id + "-joint", root.getScene())
        node.parent = parent.node
        d = sub(origin, parent.origin)
        node.position.set(d[0], d[1], d[2])
        frame = Frame(node, origin)
        frames[joint_id] = frame
        return frame

    for joint_id in list(specs.keys()):
        make(joint_id)
    return frames


def build_jointed_model(name: str, scene: Any, color: Rgb, design: Any, drawing: Any) -> Any:
    """Build the model of an enemy with moving parts.

    Its hull is on the root, its limbs and parts on their joints' nodes (or on a ring turning with
    the enemy's spin), each drawn by `build_enemy_model` with the enemy's neon `color`. The joints
    turn as the enemy's do, so a part is drawn where it is hit (ENM-28), and a destroyed part
    disappears (ENM-29).
    """
    # ENM-44: its hull, limbs and parts breathe as one creature.
    breath = new_breath()
    body = build_enemy_model(name, scene, color, drawing["body"], breath)
    root = body.root
    frames = joint_frames(name, design, root)
    ring = new_transform_node(name + "-ring", scene)
    ring.parent = root
    pieces: list[Any] = []

    def hang(piece: str, draw: Any, frame: Frame) -> Any:
        model = build_enemy_model(name + "-" + piece, scene, color, draw, breath)
        model.root.parent = frame.node
        d = sub(ORIGIN, frame.origin)
        model.root.position.set(d[0], d[1], d[2])
        pieces.append(model)
        return model

    def frame_of(joint: Any) -> Frame:
        if joint != None and joint in frames:
            return frames[joint]
        return Frame(root, ORIGIN)

    if "ring" in drawing:
        hang("ring", drawing["ring"], Frame(ring, ORIGIN))
    limbs = field(drawing, "limbs", {})
    for joint, draw in limbs.items():
        hang(joint, draw, frame_of(joint))
    parts: list[Any] = []
    for spec in design["parts"]:
        draw = drawing["parts"][spec["id"]]
        if draw == None:
            raise JointedModelError(
                'Enemy "' + name + '" does not draw its part "' + spec["id"] + '"'
            )
        frame = (
            Frame(ring, ORIGIN)
            if field(spec, "orbits", False)
            else frame_of(field(spec, "joint", None))
        )
        parts.append(hang(spec["id"], draw, frame))

    syncer = _JointedSync(body, pieces, frames, ring, parts)
    return _Built(root, lambda enemy, dt: syncer.sync(enemy, dt))


class _JointedSync:
    """What keeps a jointed model in step with its enemy: its pieces, joints, ring and parts."""

    def __init__(
        self, body: Any, pieces: list[Any], frames: dict[Any, Frame], ring: Any, parts: list[Any]
    ) -> None:
        self._body = body
        self._pieces = pieces
        self._frames = frames
        self._ring = ring
        self._parts = parts

    def sync(self, enemy: Any, dt: float) -> None:
        """Turn the joints and the ring as the enemy's do, and hide its destroyed parts."""
        self._body.sync(enemy, dt)
        for piece in self._pieces:
            piece.sync(enemy, dt)
        if not isinstance(enemy, JointedEnemy):
            return
        for joint_id, frame in self._frames.items():
            frame.node.rotation.y = enemy.joints.angle(joint_id)
        self._ring.rotation.y = enemy.spin
        for i, model in enumerate(self._parts):
            part = enemy.parts[i] if i < len(enemy.parts) else None
            model.root.setEnabled(not (part != None and part.destroyed is True))


class _Built:
    """The model built: its root node and per-frame sync."""

    def __init__(self, root: Any, sync: Any) -> None:
        self.root = root
        self.sync = sync
