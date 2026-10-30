"""Unit tests of `src/render/scenery/lightning_layer.py`."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, patch_babylon
from helpers.sample_level import sample_atmosphere

from core.scenery.lightning import Bolt, LightningSchedule, Strike
from render.scenery import lightning_layer
from render.scenery.lightning_layer import (
    BOLT_LOOK,
    LightningLayer,
    _hypot,
    _ribbons,
    _zigzag,
    bolt_lines,
)
from render.scenery.playfield_framing import GroundWindow

WINDOW = GroundWindow(10.0, 110.0, 50.0)


class _Schedule:
    """A storm's schedule with the same flash and strike at every time."""

    def __init__(self, flash: float, strike: Strike | None) -> None:
        self.flash = flash
        self.strike = strike

    def flash_at(self, time: float) -> float:
        return self.flash

    def strike_at(self, time: float) -> Strike | None:
        return self.strike


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, lightning_layer)
    monkeypatch.setattr(lightning_layer, "new_standard_material", _material)
    monkeypatch.setattr(lightning_layer, "is_enabled", lambda node: node.enabled)
    monkeypatch.setattr(lightning_layer, "dispose_node", lambda node: node.dispose())
    monkeypatch.setattr(lightning_layer, "new_mesh", _new_mesh)
    monkeypatch.setattr(
        lightning_layer, "vertex_data_of", lambda positions, indices: (positions, indices)
    )
    monkeypatch.setattr(lightning_layer, "apply_vertex_data", _apply)


def _material(label: str, scene: Any) -> SimpleNamespace:
    return SimpleNamespace(name=label, alpha=0.0)


def _new_mesh(label: str, scene: FakeScene) -> FakeNode:
    return scene.add_node(label, is_mesh=True)


def _apply(data: Any, mesh: FakeNode) -> None:
    mesh.data = data


def _layer(schedule: Any = None) -> LightningLayer:
    layer = LightningLayer(FakeScene(), 3, (WINDOW, 100.0))
    if schedule is not None:
        layer.schedule = schedule
    return layer


def _storm(lightning: float) -> Any:
    atmosphere = sample_atmosphere()
    atmosphere.lightning = lightning
    return atmosphere


def _bolt(x: float = 0.5, z: float = 0.25, seed: float = 9) -> Bolt:
    return Bolt(x, z, seed)


def test_the_bolt_constants_are_a_pale_violet_white_drawn_before_the_weather() -> None:
    assert BOLT_LOOK.color == (0.86, 0.86, 1)
    assert BOLT_LOOK.alpha_index == 3
    assert BOLT_LOOK.forks == 2


def test_the_bolt_material_is_additive_unlit_and_does_not_write_depth() -> None:
    layer = _layer()
    material = layer._material
    assert material.disableLighting is True
    assert material.alphaMode == "ALPHA_ADD"
    assert material.backFaceCulling is False
    assert material.disableDepthWrite is True
    assert material.emissiveColor.values == BOLT_LOOK.color


def test_a_new_layer_has_a_schedule_of_its_seed_and_shows_no_bolt() -> None:
    layer = _layer()
    assert isinstance(layer.schedule, LightningSchedule)
    assert layer.flash == 0
    assert layer.bolt_shown is False


def test_hypot_is_the_length_of_a_segment() -> None:
    assert _hypot(3, 4) == pytest.approx(5)


def test_a_zigzag_has_its_pieces_plus_one_points_from_its_start() -> None:
    random = lambda: 0.5  # noqa: E731 (a jag of none)
    points = _zigzag(random, (1.0, 2.0), 10.0, 0.0, 4)
    assert len(points) == 5
    assert points[0] == (1.0, 2.0)
    assert points[-1] == pytest.approx((11.0, 2.0))


def test_the_bolt_lines_are_a_main_line_and_its_forks() -> None:
    lines = bolt_lines(42, 100.0)
    assert len(lines) == 1 + BOLT_LOOK.forks
    main = lines[0]
    assert len(main) == BOLT_LOOK.pieces + 1
    assert main[0] == (0, 0)


def test_the_main_line_of_a_bolt_runs_its_share_of_the_view_from_the_centre() -> None:
    main = bolt_lines(42, 100.0)[0]
    end_x, end_z = main[-1]
    distance = math.hypot(end_x, end_z)
    assert distance == pytest.approx(100.0 * BOLT_LOOK.length_, abs=0.3)


def test_each_fork_starts_on_the_main_line_and_is_shorter() -> None:
    lines = bolt_lines(42, 100.0)
    main, forks = lines[0], lines[1:]
    for fork in forks:
        assert len(fork) == BOLT_LOOK.pieces // 2 + 1
        assert fork[0] in main[1:-1]
        end = math.hypot(fork[-1][0] - fork[0][0], fork[-1][1] - fork[0][1])
        assert end < 100.0 * BOLT_LOOK.length_


def test_a_bolt_drawn_from_the_same_seed_is_the_same_and_another_seed_differs() -> None:
    assert bolt_lines(42, 100.0) == bolt_lines(42, 100.0)
    assert bolt_lines(42, 100.0) != bolt_lines(43, 100.0)


def test_the_ribbons_are_two_triangles_per_segment_flat_in_the_ground_plane() -> None:
    positions, indices = _ribbons([[(0, 0), (1, 0), (2, 1)]], 0.5)
    assert len(positions) == 2 * 4 * 3
    assert len(indices) == 2 * 6
    assert all(positions[i] == 0 for i in range(1, len(positions), 3))


def test_a_ribbon_of_a_zero_length_segment_is_still_a_finite_shape() -> None:
    positions, _ = _ribbons([[(3, 3), (3, 3)]], 0.5)
    assert all(math.isfinite(value) for value in positions)


def test_a_flash_with_no_lightning_in_the_storm_is_no_flash() -> None:
    layer = _layer(_Schedule(0.9, Strike([0.0], _bolt())))
    assert layer.update(_storm(0), 1.0, 0) == 0
    assert layer.bolt_shown is False


def test_between_flashes_there_is_no_flash_and_no_bolt() -> None:
    layer = _layer(_Schedule(0.0, Strike([0.0], _bolt())))
    assert layer.update(_storm(1), 1.0, 0) == 0
    assert layer.bolt_shown is False


def test_a_flash_draws_the_bolt_near_the_camera_in_the_clouds() -> None:
    layer = _layer(_Schedule(0.8, Strike([0.0], _bolt(x=0.5, z=0.25, seed=9))))
    flash = layer.update(_storm(1), 1.0, 40.0)
    assert flash == pytest.approx(0.8)
    assert layer.bolt_shown is True
    mesh = layer._bolt
    assert mesh.position.x == pytest.approx(0)
    assert mesh.position.y == 100.0
    assert mesh.position.z == pytest.approx(40.0 + 10.0 + 0.25 * 100.0)
    assert mesh.renderingGroupId == 1
    assert mesh.alphaIndex == BOLT_LOOK.alpha_index
    assert mesh.isPickable is False


def test_the_bolt_material_fades_with_the_flash_and_the_storm() -> None:
    layer = _layer(_Schedule(0.5, Strike([0.0], _bolt())))
    layer.update(_storm(0.8), 1.0, 0)
    assert layer._material.alpha == pytest.approx(0.4)


def test_the_bolt_material_alpha_is_at_most_one() -> None:
    layer = _layer(_Schedule(1.0, Strike([0.0], _bolt())))
    layer.update(_storm(2.0), 1.0, 0)
    assert layer._material.alpha == 1


def test_the_bolt_of_a_strike_is_built_once_and_kept_while_the_strike_goes_on() -> None:
    strike = Strike([0.0], _bolt())
    layer = _layer(_Schedule(0.8, strike))
    layer.update(_storm(1), 1.0, 0)
    first = layer._bolt
    layer.update(_storm(1), 1.1, 0)
    assert layer._bolt is first


def test_a_new_strike_replaces_and_disposes_the_old_bolt() -> None:
    schedule = _Schedule(0.8, Strike([0.0], _bolt(seed=1)))
    layer = _layer(schedule)
    layer.update(_storm(1), 1.0, 0)
    old = layer._bolt
    schedule.strike = Strike([5.0], _bolt(seed=2))
    layer.update(_storm(1), 6.0, 0)
    assert old.disposed is True
    assert layer._bolt is not old
    assert layer.bolt_shown is True


def test_a_strike_without_a_bolt_draws_none_and_hides_the_last_one() -> None:
    schedule = _Schedule(0.8, Strike([0.0], _bolt()))
    layer = _layer(schedule)
    layer.update(_storm(1), 1.0, 0)
    schedule.strike = Strike([5.0], None)
    layer.update(_storm(1), 6.0, 0)
    assert layer._bolt.enabled is False
    assert layer.bolt_shown is False


def test_the_bolt_is_hidden_once_the_flash_is_over() -> None:
    schedule = _Schedule(0.8, Strike([0.0], _bolt()))
    layer = _layer(schedule)
    layer.update(_storm(1), 1.0, 0)
    schedule.flash = 0
    schedule.strike = None
    layer.update(_storm(1), 2.0, 0)
    assert layer.bolt_shown is False
    assert layer.flash == 0
