"""Unit tests of `src/render/babylon.py`: the wrappers that take a Python value and do one thing
with it. The rest of the module is JavaScript, run only in the browser."""

from types import SimpleNamespace

import pytest

from render.babylon import dispose_node, is_enabled, scene_unique_id, set_enabled


class _Node:
    def __init__(self) -> None:
        self.enabled = True
        self.disposed = False

    def setEnabled(self, on: bool) -> None:  # noqa: N802 (Babylon's name)
        self.enabled = on

    def isEnabled(self) -> int:  # noqa: N802
        return 1 if self.enabled else 0

    def dispose(self) -> None:
        self.disposed = True


def test_a_node_is_enabled_or_disabled_through_babylon() -> None:
    node = _Node()
    set_enabled(node, False)
    assert node.enabled is False
    assert is_enabled(node) is False
    set_enabled(node, True)
    assert is_enabled(node) is True


def test_a_node_is_disposed_through_babylon() -> None:
    node = _Node()
    dispose_node(node)
    assert node.disposed is True


def test_the_scene_counter_is_a_number() -> None:
    scene = SimpleNamespace(getUniqueId=lambda: 7)
    assert scene_unique_id(scene) == pytest.approx(7)
    assert isinstance(scene_unique_id(scene), float)
