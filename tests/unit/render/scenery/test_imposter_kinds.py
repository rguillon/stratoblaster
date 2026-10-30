"""Unit tests of `src/render/scenery/imposter_kinds.py` (D-211, D-212)."""

from types import SimpleNamespace

import pytest

from render.geometry.gradient_shapes import ColoredGeometry
from render.scenery import imposter_kinds as module
from render.scenery.imposter_kinds import imposter_kinds
from render.scenery.scenery_look import PropGeometry


class _Field:
    def __init__(self, scene, kinds, look, tilt, material) -> None:  # noqa: PLR0917
        self.kinds = kinds
        self.meshes = ["quad-" + k for k in kinds]
        self.placed: list = []

    def place(self, placements) -> None:
        self.placed = placements


def _model(lit: bool):
    def make() -> PropGeometry:
        body = ColoredGeometry()
        body.positions.extend([0, 0, 0, 1, 0, 0, 0, 1, 0])
        body.indices.extend([0, 1, 2])
        lights = ColoredGeometry()
        if lit:
            lights.positions.extend([0, 0, 0, 1, 0, 0, 0, 1, 0])
            lights.indices.extend([0, 1, 2])
        shadow = ColoredGeometry()
        shadow.indices.extend([0, 1, 2])
        return PropGeometry(body, lights, None, None, shadow)

    return make


class _Atlas:
    def __init__(self) -> None:
        self.look = SimpleNamespace()
        self.material = "material"
        self.baked: list = []

    def bake(self, bodies, tilt) -> None:
        self.baked.append((bodies, tilt))


@pytest.fixture(autouse=True)
def _fake_field(monkeypatch) -> None:
    monkeypatch.setattr(module, "ImposterField", _Field)


def test_d212_no_kind_or_no_atlas_means_no_imposters() -> None:
    models = {"tree": _model(False)}
    assert imposter_kinds(None, models, ["rock"], lambda n: _Atlas(), 0.6) is None
    assert imposter_kinds(None, models, ["tree"], None, 0.6) is None
    assert imposter_kinds(None, models, ["tree"], lambda n: None, 0.6) is None


def test_d212_imposter_kinds_keep_only_their_lights_and_bake_once() -> None:
    atlas = _Atlas()
    asked: list = []

    def atlas_of(n: int) -> _Atlas:
        asked.append(n)
        return atlas

    models = {"tree": _model(True), "house": _model(False)}
    kinds = imposter_kinds(None, models, ["tree", "rock"], atlas_of, 0.6)
    assert kinds is not None
    assert asked == [1]
    assert kinds.kinds == ["tree"]
    assert kinds.meshes == ["quad-tree"]
    tree = kinds.models["tree"]()
    assert tree.structure.indices == []
    assert tree.lights.indices == [0, 1, 2]
    # D-212: and its shadow's stand-in.
    assert tree.shadow.indices == [0, 1, 2]
    assert kinds.models["house"] is models["house"]
    kinds.bake_once()
    kinds.bake_once()
    assert len(atlas.baked) == 1
    assert atlas.baked[0][1] == 0.6
    kinds.place(["p"])
    assert kinds.field.placed == ["p"]
