"""Reusable nodes for things drawn in varying numbers (ported from `render/node-pool.ts`).

Nodes are created on demand, then shown or hidden instead of being created and disposed every
frame (ENG-19): shots, particles, flashes.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import dispose_node, set_enabled

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


class NodePool:
    """A pool of nodes made by `create(index)`."""

    def __init__(self, create: Callable[[int], Any]) -> None:
        self.nodes: list[Any] = []
        self._create = create

    def show(self, count: int) -> list[Any]:
        """Enables the first `count` nodes, creating missing ones, and disables the others."""
        while len(self.nodes) < count:
            self.nodes.append(self._create(len(self.nodes)))
        for i in range(len(self.nodes)):
            set_enabled(self.nodes[i], i < count)
        return self.nodes[0:count]

    def dispose(self) -> None:
        for node in self.nodes:
            dispose_node(node)
        while len(self.nodes) > 0:
            self.nodes.pop()
