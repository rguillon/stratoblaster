# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/ship_select_stage.py` (UI-SHIP-01)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeVector, FakeWeakMap, patch_babylon

from render import model_animation, model_showcase, ship_select_stage
from render.ship_select_stage import (
    ShipSelectStage,
    ShipSelectStageOptions,
    StageCameraLook,
    StageLightsLook,
    StageRingLook,
)


def _pivot(x: float, scale: float = 1.0) -> FakeNode:
    pivot = FakeNode("pivot")
    pivot.position = FakeVector(x, 0, 0)
    pivot.scaling = FakeVector(scale, scale, scale)
    pivot.scaling.setAll = lambda value: pivot.scaling.set(value, value, value)  # type: ignore[attr-defined]
    return pivot


def _stage(pivots: list[FakeNode]) -> ShipSelectStage:
    """Return a stage built by hand.

    The constructor makes Babylon objects, which the tests replace.
    """
    stage = ShipSelectStage.__new__(ShipSelectStage)
    stage._options = SimpleNamespace(
        highlight_scale=1.2,
        dim_scale=0.8,
        scale_ease_per_sec=2.0,
        lights=SimpleNamespace(spot_intensity=3.0),
    )
    stage._selected = 0
    stage.showcase = SimpleNamespace(
        pivots=pivots,
        update=lambda _dt: None,
    )
    stage._spots = [SimpleNamespace(intensity=0.0) for _ in pivots]
    stage.ring = SimpleNamespace(position=FakeVector())
    return stage


def test_selecting_a_ship_lights_its_spot_only_and_moves_the_ring() -> None:
    """UI-SHIP-03; PERF-07: one light per ship, only turned on and off."""
    pivots = [_pivot(-5), _pivot(0), _pivot(5)]
    stage = _stage(pivots)
    stage.select(1)
    assert stage.selected == 1
    assert [spot.intensity for spot in stage._spots] == [0, 3.0, 0]
    assert stage.ring.position.x == 0
    assert stage.spot is stage._spots[1]


def test_a_selection_past_the_last_ship_is_clamped_to_it() -> None:
    pivots = [_pivot(-5), _pivot(0), _pivot(5)]
    stage = _stage(pivots)
    stage.select(9)
    assert stage.selected == 2
    assert stage.ring.position.x == 5


def test_a_negative_selection_is_clamped_to_the_first_ship() -> None:
    stage = _stage([_pivot(-5), _pivot(5)])
    stage.select(-3)
    assert stage.selected == 0


def test_a_stage_with_no_ship_can_select_without_error() -> None:
    stage = _stage([])
    stage.select(0)
    assert stage.selected == 0


def test_the_spot_of_an_empty_stage_is_an_error() -> None:
    stage = _stage([_pivot(0)])
    stage._spots = []
    with pytest.raises(ValueError, match="no ship"):
        _ = stage.spot


def test_the_highlighted_ship_grows_and_the_others_shrink_towards_their_target() -> None:
    pivots = [_pivot(-5, scale=1.0), _pivot(5, scale=1.0)]
    stage = _stage(pivots)
    stage.select(0)
    stage.update(0.5)
    ease = 1 - math.exp(-2.0 * 0.5)
    assert pivots[0].scaling.x == pytest.approx(1 + (1.2 - 1) * ease)
    assert pivots[1].scaling.x == pytest.approx(1 + (0.8 - 1) * ease)


def test_the_showcase_is_turned_on_each_update() -> None:
    calls: list[float] = []
    stage = _stage([_pivot(0)])
    stage.showcase.update = calls.append  # type: ignore[attr-defined]
    stage.update(0.25)
    assert calls == [0.25]


def test_each_ship_starts_at_its_target_scale_when_the_stage_is_built() -> None:
    stage = _stage([_pivot(0), _pivot(5)])
    stage.select(0)
    target: Any = stage._target_scale
    assert target(stage.showcase.pivots[0]) == 1.2
    assert target(stage.showcase.pivots[1]) == 0.8


# -- The stage built on Babylon fakes --------------------------------------------------------------

CAMERA = StageCameraLook(-math.pi / 2, 1.2, 0.8, 1.1, 1.5)
LIGHTS = StageLightsLook(0.4, 2.5, [0, -1, 1], 0.7, [1, -0.5, -1])
RING = StageRingLook(5.0, 0.2, -1.5, [0.2, 0.9, 1.0])
OPTIONS = ShipSelectStageOptions(6.0, 0.5, 1.25, 0.75, 4.0, CAMERA, LIGHTS, RING)


class _Scaling(FakeVector):
    """A node's scaling: `setAll(v)` sets all three axes."""

    def setAll(self, value: float) -> None:
        self.set(value, value, value)


@pytest.fixture
def babylon_fakes(monkeypatch: pytest.MonkeyPatch) -> dict[str, list[Any]]:
    """Fake the Babylon objects the stage and its showcase make; return them by kind."""
    patch_babylon(monkeypatch, ship_select_stage)
    patch_babylon(monkeypatch, model_showcase)
    patch_babylon(monkeypatch, model_animation)
    monkeypatch.setattr(model_animation, "ANIMATIONS", FakeWeakMap())
    made: dict[str, list[Any]] = {"cameras": [], "rings": []}

    def pivot(label: str, scene: FakeScene) -> FakeNode:
        node = scene.add_node(label)
        node.scaling = _Scaling(1, 1, 1)  # type: ignore[attr-defined]
        return node

    def camera(*args: Any) -> SimpleNamespace:
        made["cameras"].append(args)
        return SimpleNamespace()

    def torus(*args: Any) -> FakeNode:
        made["rings"].append(args)
        return FakeNode("ring", is_mesh=True)

    monkeypatch.setattr(model_showcase, "new_transform_node", pivot)
    monkeypatch.setattr(ship_select_stage, "new_arc_rotate_camera", camera)
    monkeypatch.setattr(ship_select_stage, "camera_fov_mode_horizontal_fixed", lambda: "HFIXED")
    monkeypatch.setattr(ship_select_stage, "create_torus", torus)
    monkeypatch.setattr(
        ship_select_stage, "new_standard_material", lambda label, _s: SimpleNamespace(name=label)
    )
    return made


def _ship(scene: FakeScene) -> FakeNode:
    root = scene.add_node("ship")
    hull = scene.add_node("hull", is_mesh=True)
    hull.parent = root
    return root


def test_ui_ship_01_the_camera_frames_every_ship_with_a_fixed_horizontal_view(
    babylon_fakes: dict[str, list[Any]],
) -> None:
    scene = FakeScene()
    stage = ShipSelectStage(scene, [_ship, _ship, _ship], OPTIONS)
    ((label, alpha, beta, radius, target, on),) = babylon_fakes["cameras"]
    assert (label, alpha, beta, on) == ("ship-select-camera", CAMERA.alpha, CAMERA.beta, scene)
    # Three ships 6 apart are 18 wide: half of it, with the margin, fills half the view.
    assert radius == pytest.approx(9 * 1.1 / math.tan(0.4))
    assert (target.x, target.y, target.z) == (0, 1.5, 0)
    assert stage.camera.fovMode == "HFIXED"
    assert stage.camera.fov == 0.8


@pytest.mark.usefixtures("babylon_fakes")
def test_ui_ship_03_only_the_highlighted_ship_s_key_light_is_on_and_it_lights_that_ship_only() -> (
    None
):
    """PERF-07: one light per ship."""
    stage = ShipSelectStage(FakeScene(), [_ship, _ship], OPTIONS)
    assert stage.selected == 0
    assert [spot.intensity for spot in stage._spots] == [2.5, 0]
    assert [spot.name for spot in stage._spots] == ["ship-select-spot-0", "ship-select-spot-1"]
    for i, spot in enumerate(stage._spots):
        assert (spot.direction.x, spot.direction.y, spot.direction.z) == (0, -1, 1)
        hull = stage.showcase.pivots[i].children[0].children[0]
        assert spot.includedOnlyMeshes == [hull]
    stage.select(1)
    assert stage.spot is stage._spots[1]
    assert [spot.intensity for spot in stage._spots] == [0, 2.5]


@pytest.mark.usefixtures("babylon_fakes")
def test_ui_ship_03_the_highlighted_ship_starts_scaled_up_and_the_others_down() -> None:
    stage = ShipSelectStage(FakeScene(), [_ship, _ship, _ship], OPTIONS)
    assert [pivot.scaling.x for pivot in stage.showcase.pivots] == [1.25, 0.75, 0.75]


def test_ui_ship_03_the_neon_ring_lies_under_the_highlighted_ship_self_lit(
    babylon_fakes: dict[str, list[Any]],
) -> None:
    scene = FakeScene()
    stage = ShipSelectStage(scene, [_ship, _ship], OPTIONS)
    assert babylon_fakes["rings"] == [("ship-select-ring", 5.0, 0.2, 48, scene)]
    ring = stage.ring
    assert (ring.position.x, ring.position.y) == (-3, -1.5)
    material = ring.material
    assert material.name == "ship-select-ring"
    assert material.emissiveColor.values == (0.2, 0.9, 1.0)
    assert material.diffuseColor.values == (0, 0, 0)
    assert material.specularColor.values == (0, 0, 0)
    assert material.disableLighting is True
    stage.select(1)
    assert ring.position.x == 3


@pytest.mark.usefixtures("babylon_fakes")
def test_ui_ship_03_the_ambient_and_rim_lights_light_every_ship(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lights: list[Any] = []

    def light(label: str, direction: Any, _scene: Any) -> SimpleNamespace:
        made = SimpleNamespace(name=label, direction=direction, intensity=1.0)
        lights.append(made)
        return made

    monkeypatch.setattr(ship_select_stage, "new_hemispheric_light", light)
    monkeypatch.setattr(ship_select_stage, "new_directional_light", light)
    ShipSelectStage(FakeScene(), [_ship], OPTIONS)
    ambient, rim, spot = lights
    assert spot.name == "ship-select-spot-0"
    assert ambient.name == "ship-select-ambient"
    assert (ambient.direction.x, ambient.direction.y, ambient.direction.z) == (0, 1, 0)
    assert ambient.intensity == 0.4
    assert rim.name == "ship-select-rim"
    assert (rim.direction.x, rim.direction.y, rim.direction.z) == (1, -0.5, -1)
    assert rim.intensity == 0.7
