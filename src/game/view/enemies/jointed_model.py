"""How an enemy with moving parts is drawn (P05-R13)

Everything is in model space as at rest (logical pixels, nose +Z, Y up; a point `(x, y)` of the
design is at `boss_point`).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from core.entities.jointed_enemy import JointedEnemy  # noqa: E402
from game.config.record import field  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from game.view.enemies.living_motion import new_breath  # noqa: E402
from render.babylon import new_transform_node  # noqa: E402

ORIGIN = [0, 0, 0]  # type: list[float]


def sub(a: Vec3, b: Any) -> list[float]:
    """`a - b`, component by component."""
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


class Frame:
    """A joint's node and its pivot in model space."""

    def __init__(self, node: Any, origin: Any) -> None:
        self.node = node
        self.origin = origin


def joint_frames(name: str, design: Any, root: Any) -> dict[str, Frame]:
    """A node per joint, hung on the joint it hangs on, its pivot where the design puts it."""
    specs = field(design, "joints", {})
    frames: dict[str, Frame] = {}

    def make(joint_id: str) -> Frame:
        if joint_id in frames:
            return frames[joint_id]
        spec = field(specs, joint_id, None)
        if spec == None:  # noqa: E711
            raise Exception('Enemy "' + name + '" has no joint "' + joint_id + '"')
        parent = Frame(root, ORIGIN) if spec["parent"] == None else make(spec["parent"])  # noqa: E711
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


def build_jointed_model(  # noqa: C901
    name: str, scene: Any, color: Rgb, design: Any, drawing: Any
) -> Any:
    """Builds the model of an enemy with moving parts (P05-R13): its hull on the root, its limbs and
    parts on their joints' nodes (or on a ring turning with the enemy's spin), each drawn by
    `build_enemy_model` with the enemy's neon `color`. The joints turn as the enemy's do, and a
    destroyed part disappears."""
    # P16-R07: its hull, limbs and parts breathe as one creature.
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
        if joint != None and joint in frames:  # noqa: E711
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
        if draw == None:  # noqa: E711
            raise Exception('Enemy "' + name + '" does not draw its part "' + spec["id"] + '"')
        if "orbits" in spec and spec["orbits"]:
            frame = Frame(ring, ORIGIN)
        else:
            frame = frame_of(field(spec, "joint", None))
        parts.append(hang(spec["id"], draw, frame))

    def sync(enemy: Any, dt: float) -> None:
        body.sync(enemy, dt)
        for piece in pieces:
            piece.sync(enemy, dt)
        if not isinstance(enemy, JointedEnemy):
            return
        for joint_id, frame in frames.items():
            frame.node.rotation.y = enemy.joints.angle(joint_id)
        ring.rotation.y = enemy.spin
        for i, model in enumerate(parts):
            part = enemy.parts[i] if i < len(enemy.parts) else None
            model.root.setEnabled(not (part != None and part.destroyed is True))  # noqa: E711

    return _Built(root, sync)


class _Built:
    """The model built: its root node and per-frame sync."""

    def __init__(self, root: Any, sync: Any) -> None:
        self.root = root
        self.sync = sync
