"""Unit tests of `src/render/model_showcase.py`."""

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeWeakMap, patch_babylon

from render import model_animation, model_showcase
from render.model_animation import add_model_animation
from render.model_showcase import ModelShowcase, ShowcaseOptions


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, model_showcase)
    patch_babylon(monkeypatch, model_animation)
    monkeypatch.setattr(model_animation, "ANIMATIONS", FakeWeakMap())


def _factory(scene: FakeScene) -> FakeNode:
    return scene.add_node("model")


def test_models_are_spaced_along_x_and_centred_on_the_origin() -> None:
    scene = FakeScene()
    showcase = ModelShowcase(scene, [_factory] * 3, ShowcaseOptions(4, 0))
    assert [pivot.position.x for pivot in showcase.pivots] == [-4, 0, 4]
    assert showcase.width == pytest.approx(12)


def test_each_model_is_the_only_child_of_its_pivot() -> None:
    scene = FakeScene()
    showcase = ModelShowcase(scene, [_factory, _factory], ShowcaseOptions(2, 0))
    for pivot in showcase.pivots:
        assert len(pivot.children) == 1


def test_update_turns_each_pivot_and_steps_its_animations() -> None:
    scene = FakeScene()
    showcase = ModelShowcase(scene, [_factory, _factory], ShowcaseOptions(2, 0.5))
    seen: list[float] = []
    add_model_animation(showcase.pivots[1], seen.append)

    showcase.update(0.5)
    showcase.update(0.5)

    assert [pivot.rotation.y for pivot in showcase.pivots] == pytest.approx([0.5, 0.5])
    assert seen == [0.5, 0.5]


def test_dispose_disposes_every_pivot() -> None:
    scene = FakeScene()
    showcase = ModelShowcase(scene, [_factory], ShowcaseOptions(2, 0))
    showcase.dispose()
    assert all(pivot.disposed for pivot in showcase.pivots)
