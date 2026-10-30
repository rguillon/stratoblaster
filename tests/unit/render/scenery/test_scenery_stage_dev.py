"""Unit tests of the dev viewer's parts of `src/render/scenery/scenery_stage.py` (D-199), on a
stage made without Babylon (its fields set by hand)."""

from types import SimpleNamespace
from typing import Any

from core.scenery.ground_boxes import PropPlacement
from render.scenery import prop_field
from render.scenery.scenery_stage import SOLO_CHUNK, SceneryStage


class FakeProps:
    def __init__(self) -> None:
        self.chunks: dict[int, list[Any]] = {}
        self.cleared = 0

    def clear(self) -> None:
        self.cleared += 1
        self.chunks = {}

    def set_chunk(self, index: int, placements: list[Any]) -> None:
        self.chunks[index] = placements


class FakePlacer:
    def __init__(self, by_chunk: dict[float, list[PropPlacement]]) -> None:
        self.by_chunk = by_chunk
        self.asked: list[float] = []

    def place(self, area: Any) -> list[PropPlacement]:
        self.asked.append(area.z_min)
        return self.by_chunk.get(area.z_min, [])


def stage(placer: FakePlacer | None = None) -> SceneryStage:
    s = SceneryStage.__new__(SceneryStage)
    s._solo = False
    s._props = FakeProps()
    s._placer = placer or FakePlacer({})
    s._ground = SimpleNamespace(half_width=50)
    s._ground_root = SimpleNamespace(scale=2.0, node=SimpleNamespace(position=SimpleNamespace(x=0)))
    s.options = SimpleNamespace(config=SimpleNamespace(chunk_length=100))
    return s


def hut(x: float, z: float) -> PropPlacement:
    return PropPlacement("hut", x, 1, z, 0, 1)


def test_d199_solo_props_replace_the_level_s_own() -> None:
    s = stage()
    s._props.chunks[3] = [hut(0, 0)]
    shown = [hut(1, 2)]
    s.solo_props(shown)
    assert s._solo
    assert s._props.chunks == {SOLO_CHUNK: shown}


def test_d199_the_first_chunk_with_the_kind_gives_its_prop_nearest_the_middle() -> None:
    tree = PropPlacement("tree", 0, 0, 210, 0, 1)
    placer = FakePlacer({200: [tree, hut(-30, 220), hut(10, 250)], 300: [hut(0, 310)]})
    s = stage(placer)
    found = s.find_prop("hut", 1000)
    assert (found.x, found.z) == (10, 250)
    assert placer.asked == [0, 100, 200]
    assert s.find_prop("tower", 1000) is None


def test_d199_the_ground_shifts_so_a_point_is_under_the_middle() -> None:
    s = stage()
    s.shift_ground(12)
    assert s.ground_root.node.position.x == -24


def test_d199_a_prop_extent_is_its_largest_side() -> None:
    positions = [0, 0, 0, 4, 1, -2, -1, 9, 3]
    geometry = SimpleNamespace(structure=SimpleNamespace(positions=positions))
    assert prop_field.prop_extent(lambda: geometry) == 9
    empty = SimpleNamespace(structure=SimpleNamespace(positions=[]))
    assert prop_field.prop_extent(lambda: empty) == 0
