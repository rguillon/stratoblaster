"""Unit tests of `src/render/scenery/stage_parts.py`."""

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeScene, FakeVector, patch_babylon

from core.scenery.scenery_level import SceneryLevel
from render.scenery import stage_parts
from render.scenery.stage_parts import (
    TerrainWatch,
    lowest_ground,
    sea_parts,
    sea_plane,
    stage_camera,
    terrain_last,
)


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, stage_parts)
    monkeypatch.setattr(
        stage_parts, "create_ground", lambda label, w, h, sub, scene: _ground(label, w, h, scene)
    )
    monkeypatch.setattr(
        stage_parts, "new_free_camera", lambda label, pos, scene: _camera(label, scene)
    )
    monkeypatch.setattr(stage_parts, "RainRings", lambda scene, rings, extent: ("rings", extent))


def _ground(label: str, width: float, height: float, scene: Any) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.size = (width, height)
    node.position = FakeVector()
    return node


def _camera(label: str, scene: Any) -> SimpleNamespace:
    return SimpleNamespace(name=label, fov=0.0, minZ=0.0, maxZ=0.0)


def _level(sea_level: float | None, sections: list[tuple[float, float]]) -> SceneryLevel:
    relief = [
        SimpleNamespace(relief=SimpleNamespace(base=base, amplitude=amp)) for base, amp in sections
    ]
    sea = None if sea_level is None else SimpleNamespace(level=sea_level)
    return SimpleNamespace(sections=relief, sea=sea)  # type: ignore[return-value]


def test_without_a_sea_the_lowest_ground_is_the_lowest_relief() -> None:
    level = _level(None, [(10, 4), (20, 2), (12, 9)])
    assert lowest_ground(level) == pytest.approx(3)


def test_with_a_sea_the_sea_level_is_the_lowest_ground() -> None:
    level = _level(2, [(10, 4), (20, 2)])
    assert lowest_ground(level) == 2


def test_the_stage_camera_sees_twice_the_half_field_of_view_up_to_the_far_clip() -> None:
    scene = FakeScene()
    camera = stage_camera(scene, half_fov=0.5, far_clip=800)
    assert camera.fov == pytest.approx(1.0)
    assert (camera.minZ, camera.maxZ) == (1, 800)
    assert scene.activeCamera is camera


class _Mesh:
    def __init__(self, material: object) -> None:
        self._material = material

    def getMaterial(self) -> object:  # noqa: N802
        return self._material


def test_the_terrain_is_drawn_after_the_other_meshes() -> None:
    terrain_material = object()
    compare = terrain_last(terrain_material)
    terrain = _Mesh(terrain_material)
    prop = _Mesh(object())
    assert compare(prop, terrain) < 0
    assert compare(terrain, prop) > 0


def test_meshes_on_the_same_side_of_the_terrain_are_ordered_by_the_painter_sort(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(stage_parts, "render_painter_sort_compare", lambda a, b: 7.0)
    compare = terrain_last(object())
    assert compare(_Mesh(1), _Mesh(2)) == 7.0


def test_the_sea_plane_is_a_pickable_free_ground_at_the_sea_level() -> None:
    scene = FakeScene()
    material = object()
    sea = sea_plane(scene, [100, 50, 3], material)
    assert sea.size == (100, 50)
    assert sea.position.y == 3
    assert sea.material is material
    assert sea.isPickable is False and sea.receiveShadows is True and sea.alphaIndex == 0


def test_a_level_without_a_sea_has_no_sea_parts() -> None:
    level = _level(None, [(0, 1)])
    assert sea_parts(FakeScene(), level, [10, 10], SimpleNamespace()) is None


def test_a_level_with_a_sea_has_its_plane_and_its_rain_rings() -> None:
    level = _level(5, [(0, 1)])
    kit = SimpleNamespace(sea="sea-material", rings="ring-material")
    parts = sea_parts(FakeScene(), level, [40, 30], kit)
    assert parts is not None
    assert parts.sea.size == (40, 30)
    assert parts.sea.position.y == 5
    assert parts.rings == ("rings", (5, 40, 30))


def test_a_terrain_watch_tells_its_watchers_about_each_mesh_now_and_later() -> None:
    watch = TerrainWatch()
    seen_before: list[str] = []
    watch.add("chunk-1")
    watch.watch(seen_before.append)
    watch.add("chunk-2")
    assert seen_before == ["chunk-1", "chunk-2"]

    seen_after: list[str] = []
    watch.watch(seen_after.append)
    assert seen_after == ["chunk-1", "chunk-2"]
