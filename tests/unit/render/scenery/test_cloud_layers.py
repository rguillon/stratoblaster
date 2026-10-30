"""Unit tests of `src/render/scenery/cloud_layers.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon
from helpers.render_looks import BLACK, GREY, WHITE, cloud
from helpers.sample_level import sample_atmosphere

from core.scenery.atmosphere import CloudCover
from render.scenery import cloud_layers
from render.scenery.cloud_layers import (
    ABOVE_CLOUDS_GROUP,
    BELOW_CLOUDS_GROUP,
    CloudLayer,
    CloudLayerState,
    build_cloud_layer,
    update_cloud_layer,
)


class _Material:
    """A cloud material: its mesh material, and the last frame it was driven with."""

    def __init__(self) -> None:
        self.material = "cloud-material"
        self.state: Any = None

    def set(self, state: Any) -> None:
        self.state = state


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, cloud_layers)
    monkeypatch.setattr(cloud_layers, "create_ground", _ground)


def _ground(label: str, width: float, height: float, subdivisions: int, scene: Any) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.size = (width, height)
    return node


def _seen(half_width: float = 10, z_near: float = 20, z_far: float = 120) -> Any:
    return SimpleNamespace(half_width=half_width, z_near=z_near, z_far=z_far)


def _layer(altitude: float = 100, margin: float = 5, index: int = 0, **look: Any) -> CloudLayer:
    return build_cloud_layer(
        FakeScene(),
        cloud(altitude=altitude, **look),
        _Material(),
        index,
        (_seen(), altitude, margin),
    )


def test_a_cloud_layer_is_a_plane_at_its_altitude_covering_the_view_and_a_margin() -> None:
    layer = _layer(altitude=100, margin=5)
    assert layer.mesh.size == (2 * (10 + 5), (120 - 20) + 2 * 5)
    assert layer.mesh.position.y == 100


def test_a_cloud_layer_is_drawn_after_the_ground_and_lower_layers_first() -> None:
    layer = _layer(index=2)
    assert layer.mesh.renderingGroupId == BELOW_CLOUDS_GROUP + 1
    assert layer.mesh.alphaIndex == 3
    assert layer.mesh.isPickable is False
    assert layer.mesh.material == "cloud-material"


def test_the_clouds_group_is_one_group_above_the_ground_group() -> None:
    assert BELOW_CLOUDS_GROUP == 0
    assert ABOVE_CLOUDS_GROUP == 2


def test_a_cloud_layer_starts_enabled_with_the_coverage_and_opacity_of_its_look() -> None:
    layer = _layer(coverage=0.7, opacity=0.4)
    assert layer.state.enabled is True
    assert layer.state.coverage == pytest.approx(0.7)
    assert layer.state.opacity == pytest.approx(0.4)


def test_the_middle_of_a_cloud_layer_is_the_middle_of_what_the_camera_sees() -> None:
    layer = _layer()
    assert layer.middle == pytest.approx((20 + 120) / 2)


def test_the_layer_follows_the_camera_at_its_middle() -> None:
    layer = _layer()
    update_cloud_layer(layer, (300, 0), (sample_atmosphere(), None, False))
    assert layer.mesh.position.z == pytest.approx(300 + layer.middle)


def test_the_drift_of_the_pattern_moves_with_the_time() -> None:
    layer = _layer(drift=(2, -3))
    update_cloud_layer(layer, (0, 10), (sample_atmosphere(), None, False))
    state = layer.material.state
    assert state.offset_x == pytest.approx(20)
    assert state.offset_z == pytest.approx(-30)


def test_a_layer_with_no_coverage_is_hidden() -> None:
    layer = _layer(coverage=0)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, False))
    assert layer.mesh.enabled is False


def test_a_layer_with_no_opacity_is_hidden() -> None:
    layer = _layer(opacity=0)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, False))
    assert layer.mesh.enabled is False


def test_a_layer_that_is_switched_off_by_code_is_hidden_even_with_coverage() -> None:
    layer = _layer()
    layer.state.enabled = False
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, False))
    assert layer.mesh.enabled is False


def test_a_visible_layer_is_shown() -> None:
    layer = _layer()
    layer.mesh.enabled = False
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, False))
    assert layer.mesh.enabled is True


def test_with_a_cover_the_cover_colours_are_drawn() -> None:
    layer = _layer(color=WHITE, shade=GREY)
    cover = CloudCover(0.9, 0.8, (0.2, 0.3, 0.4), (0.1, 0.1, 0.1))
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), cover, False))
    assert layer.material.state.color == (0.2, 0.3, 0.4)
    assert layer.material.state.shade == (0.1, 0.1, 0.1)


def test_without_a_cover_the_look_colours_are_drawn() -> None:
    layer = _layer(color=WHITE, shade=BLACK)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, False))
    assert layer.material.state.color == WHITE
    assert layer.material.state.shade == BLACK


def test_a_following_layer_takes_the_coverage_and_opacity_of_the_cover() -> None:
    layer = _layer(coverage=0.1, opacity=0.1)
    cover = CloudCover(0.9, 0.6, GREY, BLACK)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), cover, True))
    assert layer.state.coverage == pytest.approx(0.9)
    assert layer.state.opacity == pytest.approx(0.6)


def test_a_layer_that_does_not_follow_keeps_the_coverage_set_on_its_state() -> None:
    layer = _layer(coverage=0.1)
    layer.state.coverage = 0.3
    cover = CloudCover(0.9, 0.6, GREY, BLACK)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), cover, False))
    assert layer.state.coverage == pytest.approx(0.3)


def test_a_missing_cover_does_not_change_a_following_layer() -> None:
    layer = _layer(coverage=0.4)
    update_cloud_layer(layer, (0, 0), (sample_atmosphere(), None, True))
    assert layer.state.coverage == pytest.approx(0.4)


def test_the_cloud_state_fades_into_the_haze_and_fog_of_the_atmosphere() -> None:
    layer = _layer()
    atmosphere = sample_atmosphere()
    update_cloud_layer(layer, (0, 0), (atmosphere, None, False))
    fog = layer.material.state.fog
    assert fog.color == atmosphere.sky.haze
    assert (fog.start, fog.end) == (atmosphere.fog.start, atmosphere.fog.end)


def test_a_state_built_by_hand_is_kept_on_the_layer() -> None:
    state = CloudLayerState(False, 0.2, 0.3)
    assert (state.enabled, state.coverage, state.opacity) == (False, 0.2, 0.3)
