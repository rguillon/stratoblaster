"""Unit tests of `src/render/model_animation.py`."""

import pytest
from helpers.render_fakes import FakeNode, FakeWeakMap, patch_babylon

from render import model_animation
from render.model_animation import add_model_animation, step_model_animations


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, model_animation)
    # `ANIMATIONS` is made at import time, when Babylon's WeakMap does not exist yet.
    monkeypatch.setattr(model_animation, "ANIMATIONS", FakeWeakMap())


def _tree() -> tuple[FakeNode, FakeNode, FakeNode]:
    root = FakeNode("root")
    child = FakeNode("child")
    grandchild = FakeNode("grandchild")
    root.children = [child]
    child.children = [grandchild]
    return root, child, grandchild


def test_a_step_runs_the_animations_of_the_root_and_all_its_descendants() -> None:
    root, child, grandchild = _tree()
    seen: list[tuple[str, float]] = []
    add_model_animation(root, lambda dt: seen.append(("root", dt)))
    add_model_animation(child, lambda dt: seen.append(("child", dt)))
    add_model_animation(grandchild, lambda dt: seen.append(("grandchild", dt)))

    step_model_animations(root, 0.25)

    assert seen == [("root", 0.25), ("child", 0.25), ("grandchild", 0.25)]


def test_several_animations_on_one_node_all_run_in_order() -> None:
    root, _, _ = _tree()
    seen: list[str] = []
    add_model_animation(root, lambda dt: seen.append("first"))
    add_model_animation(root, lambda dt: seen.append("second"))
    step_model_animations(root, 1)
    assert seen == ["first", "second"]


def test_a_node_without_animations_is_stepped_without_error() -> None:
    root, _, _ = _tree()
    step_model_animations(root, 1)


def test_animations_of_other_trees_are_not_run() -> None:
    root, _, _ = _tree()
    other = FakeNode("other")
    seen: list[str] = []
    add_model_animation(other, lambda dt: seen.append("other"))
    step_model_animations(root, 1)
    assert seen == []
