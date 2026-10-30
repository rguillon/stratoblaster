"""Unit tests of `src/render/enemy_layer.py`."""

import math
from typing import Any

import pytest
from helpers.render_fakes import FakeScene, patch_babylon

from render import enemy_layer
from render.enemy_layer import EnemyLayer


class FakeModel:
    def __init__(self, scene: FakeScene) -> None:
        self.root = scene.add_node("body", is_mesh=True)
        self.synced: list[tuple[Any, float]] = []

    def sync(self, enemy: Any, dt_seconds: float) -> None:
        self.synced.append((enemy, dt_seconds))


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, enemy_layer)


class FakeEnemy:
    """An enemy is an object: two enemies are the same only when they are the same object."""

    def __init__(self, model: str, x: float = 0, y: float = 0, heading: float = 0) -> None:
        self.model = model
        self.x = x
        self.y = y
        self.heading = heading


def _enemy(model: str, x: float = 0, y: float = 0, heading: float = 0) -> FakeEnemy:
    return FakeEnemy(model, x, y, heading)


def _layer(made: list[FakeModel]) -> tuple[EnemyLayer, FakeScene]:
    scene = FakeScene()

    def factory(s: FakeScene) -> FakeModel:
        model = FakeModel(s)
        made.append(model)
        return model

    return EnemyLayer(scene, {"drone": factory, "tank": factory}), scene


def test_an_enemy_is_drawn_at_its_position_with_its_nose_along_its_heading() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    enemy = _enemy("drone", x=10, y=20, heading=math.pi / 2)

    layer.sync([enemy], 0.1)

    assert layer.count == 1 and layer.model_count == 1
    slot_pivot = made[0].root.parent.parent
    assert (slot_pivot.position.x, slot_pivot.position.y, slot_pivot.position.z) == (10, 20, 0)
    assert slot_pivot.rotation.z == pytest.approx(-math.pi / 2)
    assert made[0].synced == [(enemy, 0.1)]


def test_the_model_stands_on_a_holder_that_turns_its_nose_up() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    layer.sync([_enemy("drone")], 0)
    holder = made[0].root.parent
    assert holder.rotation.x == pytest.approx(-math.pi / 2)


def test_a_model_that_leaves_is_hidden_and_reused_by_its_kind() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    first = _enemy("drone")
    layer.sync([first], 0)
    pivot = made[0].root.parent.parent

    layer.sync([], 0)
    assert layer.count == 0
    assert pivot.enabled is False

    layer.sync([_enemy("drone", x=5)], 0)
    assert layer.model_count == 1
    assert pivot.enabled is True


def test_a_new_kind_gets_a_new_model() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    layer.sync([_enemy("drone")], 0)
    layer.sync([_enemy("drone"), _enemy("tank")], 0)
    assert layer.model_count == 2
    assert layer.count == 2


def test_an_enemy_of_an_unknown_kind_is_an_error() -> None:
    layer, _ = _layer([])
    with pytest.raises(ValueError, match="No model for enemy boss"):
        layer.sync([_enemy("boss")], 0)


def test_prepare_next_builds_one_hidden_model_per_kind_until_all_are_built() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)

    first = layer.prepare_next()
    assert len(first) == 1  # The model's meshes, to compile their shaders.
    assert layer.model_count == 1
    assert made[0].root.parent.parent.enabled is False

    assert len(layer.prepare_next()) == 1
    assert layer.prepare_next() == []
    assert layer.model_count == 2


def test_a_prepared_model_is_reused_for_the_first_enemy_of_its_kind() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    layer.prepare_next()
    layer.sync([_enemy("drone")], 0)
    assert layer.model_count == 1


def test_clear_hides_every_drawn_enemy() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    layer.sync([_enemy("drone"), _enemy("tank")], 0)
    layer.clear()
    assert layer.count == 0
    assert all(model.root.parent.parent.enabled is False for model in made)


def test_dispose_disposes_every_model_and_forgets_them() -> None:
    made: list[FakeModel] = []
    layer, _ = _layer(made)
    layer.sync([_enemy("drone")], 0)
    layer.sync([], 0)
    layer.dispose()
    assert made[0].root.parent.parent.disposed is True
    assert layer.count == 0
