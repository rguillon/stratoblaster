"""The moving limbs of boss models (phase 7 review): their
joints as nodes, and what is drawn on them. Model space as in `boss_model.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
__pragma__("noskip")

from render.babylon import (  # noqa: E402
    new_transform_node,
    set_enabled,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
# A limb drawn on a joint: its record of draw and part.
type LimbDrawing = dict[str, Any]
__pragma__("noskip")

from game.view.enemies.organic_parts import opt  # noqa: E402

ORIGIN = [0, 0, 0]


def _keys(value: Any) -> list[str]:
    """`Object.keys(value)`."""
    __pragma__("skip")
    return list(value.keys())
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.keys(value);")
    return []


def _entries(value: Any) -> list[Any]:
    """`Object.entries(value)`: a list of `[key, value]` pairs."""
    __pragma__("skip")
    return [[key, item] for key, item in value.items()]
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.entries(value);")
    return []


def boss_point(x: float, y: float, height: float = 0) -> list[Any]:
    """Model space of a boss: logical pixels, its nose at +Z, +Y up (towards the camera). A boss
    faces down the screen, so the point `(x, y)` of the playfield (X right, Y up, from its centre)
    is model `(-x, height, -y)`.
    """
    return [-x, height, -y]


class JointFrame:
    """Where things hanging on a joint are drawn: its node, and its pivot in model space."""

    def __init__(self, node: Any, origin: list[Any]) -> None:
        self.node = node
        self.origin = origin


def _sub(a: list[Any], b: list[Any]) -> list[Any]:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


class JointFrames:
    """The joints of a boss as nodes (phase 7 review), each at its pivot on the one it hangs on."""

    def __init__(self, design: Any, root: Any) -> None:
        self._design = design
        self._root = root
        self._frames: dict[str, JointFrame] = {}
        self._order: list[str] = []
        specs = opt(design.stats, "joints", {})
        for joint_id in _keys(specs):
            self._make(joint_id, specs)

    def _make(self, joint_id: str, specs: Any) -> JointFrame:
        made = self._frames.get(joint_id)
        if made != None:  # noqa: E711
            return made
        spec = specs[joint_id]
        if spec == None:  # noqa: E711
            raise ValueError('Boss "' + self._design.id + '" has no joint "' + joint_id + '"')
        parent_id = opt(spec, "parent", None)
        if parent_id == None:  # noqa: E711
            parent = JointFrame(self._root, ORIGIN)
        else:
            parent = self._make(parent_id, specs)
        origin = boss_point(spec.x, spec.y)
        node = new_transform_node(
            self._design.id + "-" + joint_id + "-joint", self._root.getScene()
        )
        node.parent = parent.node
        offset = _sub(origin, parent.origin)
        node.position.set(offset[0], offset[1], offset[2])
        frame = JointFrame(node, origin)
        self._frames[joint_id] = frame
        self._order.append(joint_id)
        return frame

    def frame(self, joint: Any, holder: Any) -> JointFrame:
        """The frame of `joint`, or `holder` at the model's origin without one."""
        found = None if joint == None else self._frames.get(joint)  # noqa: E711
        if joint != None and found == None:  # noqa: E711
            raise ValueError('No boss joint "' + joint + '"')
        if found != None:  # noqa: E711
            return found
        return JointFrame(holder, ORIGIN)

    def show(self, boss: Any) -> None:
        """Turns them as `boss`'s joints are now; at rest without one."""
        for joint_id in self._order:
            node = self._frames[joint_id].node
            node.rotation.y = 0 if boss == None else boss.joints.angle(joint_id)  # noqa: E711


def hang(node: Any, at: list[Any], frame: JointFrame) -> None:
    """Puts `node` (drawn in model space) at `at` on `frame`."""
    node.parent = frame.node
    offset = _sub(at, frame.origin)
    node.position.set(offset[0], offset[1], offset[2])


class BossLimbs:
    """The limbs of a boss model (see `BossDrawing.limbs`), each built by `build` and hung on its
    joint; one that belongs to a part goes and flashes with it, the others with the core."""

    def __init__(
        self,
        design: Any,
        limbs: Any,
        joints: JointFrames,
        build: Any,
    ) -> None:
        self._joints = joints
        self._limbs: list[Any] = []
        for entry in _entries({} if limbs == None else limbs):  # noqa: E711
            joint = entry[0]
            limb = entry[1]
            group = build(joint, limb.draw)
            hang(group.model.root, ORIGIN, joints.frame(joint, group.model.root))
            part = _index_of_part(design.stats.parts, opt(limb, "part", None))
            if opt(limb, "part", None) != None and part < 0:  # noqa: E711
                raise ValueError(
                    'Boss "'
                    + design.id
                    + '": limb "'
                    + joint
                    + '" belongs to no part "'
                    + limb.part
                    + '"'
                )
            self._limbs.append([group, part])

    def show(self, boss: Any, lit: Any, dt: float) -> None:
        """Shows them as `boss` is now (its joints turned); at rest for a stand-in."""
        self._joints.show(boss)
        for entry in self._limbs:
            group = entry[0]
            part = entry[1]
            group.model.sync(lit, dt)
            if boss == None:  # noqa: E711
                continue
            owner = boss.parts[part] if part >= 0 else None
            owned_destroyed = owner != None and owner.destroyed  # noqa: E711
            set_enabled(group.model.root, not owned_destroyed)
            group.show(owner.since_hit if owner != None else boss.core.since_hit)  # noqa: E711


def _index_of_part(parts: list[Any], part_id: Any) -> int:
    """The index of the part called `part_id` in `parts`, or -1 (as `findIndex`)."""
    for i in range(len(parts)):
        if parts[i].id == part_id:
            return i
    return -1
