"""Puts what some code creates into a layer (ported from `render/node-adopter.ts`)."""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    number_max_value,
    scene_meshes,
    scene_transform_nodes,
    scene_unique_id,
    unique_id,
)

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, TypeVar  # noqa: E402

T = TypeVar("T")
__pragma__("noskip")

# Draw order from which a layer's see-through meshes are drawn over all those that set none
# (P14-R05: the enemy shots). Babylon draws a mesh left at its default order
# (`Number.MAX_VALUE`) after every other, so a layer gives such meshes the one just below.
ON_TOP_ALPHA_INDEX = 1000000


def newer(items: list[Any], after: float) -> list[Any]:
    """Nodes of `items` created after the node numbered `after` (lists are in creation order)."""
    i = len(items)
    while i > 0 and unique_id(items[i - 1]) > after:
        i -= 1
    return items[i:]


class NodeAdopter:
    """Every mesh or node created while `run` runs, and left without a parent, is parented to
    `root`, and every new mesh is drawn in `rendering_group_id`, under `ON_TOP_ALPHA_INDEX` if
    it sets no draw order.

    It lets drawing code written for a flat playfield (shot renderers draw in the XY plane) be
    shown in another space, e.g. the tilted level view, without knowing about it. Clones of an
    adopted template keep its parent, group and draw order by themselves.
    """

    def __init__(
        self,
        scene: Any,
        root: Any,
        rendering_group_id: int,
        on_mesh: Callable[[Any], None] | None = None,
    ) -> None:
        self._scene = scene
        self.root = root
        self.rendering_group_id = rendering_group_id
        # Called with each mesh adopted (e.g. to add it to a glow layer).
        self._on_mesh = on_mesh

    def run(self, create: Callable[[], T]) -> T:
        """Runs `create`, then adopts what it created. Returns what `create` returned."""
        # Babylon numbers every node from one counter: what `create` builds gets higher numbers.
        before = scene_unique_id(self._scene)
        try:
            return create()
        finally:
            for node in newer(scene_transform_nodes(self._scene), before):
                self._parent(node)
            for mesh in newer(scene_meshes(self._scene), before):
                self._parent(mesh)
                mesh.renderingGroupId = self.rendering_group_id
                if mesh.alphaIndex == number_max_value():
                    mesh.alphaIndex = ON_TOP_ALPHA_INDEX - 1
                if self._on_mesh is not None:
                    self._on_mesh(mesh)

    def _parent(self, node: Any) -> None:
        if node.parent is None and node is not self.root:
            node.parent = self.root
