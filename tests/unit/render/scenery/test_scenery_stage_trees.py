"""Unit tests of the chunks' trees and street sources in `src/render/scenery/scenery_stage.py`
(D-212, D-217), on a stage made without Babylon (its fields set by hand) and the game's stage
settings."""

import math
from types import SimpleNamespace
from typing import Any

import pytest

from config.scenery_stage import SCENERY_STAGE_CONFIG
from render.scenery import scenery_stage
from render.scenery.scenery_stage import SceneryStage, row_end, tree_sight
from render.scenery.terrain_chunks import ChunkChanges, ChunkSpan

CELL = 50


class FakeChunks:
    """Terrain chunks: `cover` keeps those over a Z range, as `TerrainChunks` does."""

    def __init__(self, length: float) -> None:
        self.length = length
        self.meshes: dict[int, str] = {}

    def span(self, index: int) -> ChunkSpan:
        return ChunkSpan(index, index * self.length, (index + 1) * self.length)

    def cover(self, z_min: float, z_max: float) -> ChunkChanges:
        first = math.floor(z_min / self.length)
        last = math.floor(z_max / self.length)
        removed = [i for i in list(self.meshes) if i < first or i > last]
        for i in removed:
            del self.meshes[i]
        added: list[ChunkSpan] = []
        for i in range(first, last + 1):
            if i not in self.meshes:
                self.meshes[i] = "mesh"
                added.append(self.span(i))
        return ChunkChanges(added, removed)

    def rebuild(self, field: Any) -> None:
        pass


class FakePlacer:
    """A placer: a building per chunk, and a tree per cell corner (as `trees_in` takes them)."""

    def __init__(self, tiles: Any = None) -> None:
        self.rules = SimpleNamespace(cell_size=CELL)
        self.roads = SimpleNamespace(roads=[], tiles=tiles, runout_from=None)
        self.runout_laid = False

    def want_placed(self, z: float) -> None:
        pass

    def place_without_trees(self, area: Any) -> list[Any]:
        return [("building", area.z_min)]

    def trees_in(self, area: Any) -> list[Any]:
        rows = range(math.ceil(area.z_min / CELL), math.ceil(area.z_max / CELL))
        return [("tree", j * CELL) for j in rows]

    def place(self, area: Any) -> list[Any]:
        return self.place_without_trees(area) + self.trees_in(area)


class FakeProps:
    """The prop field: the placements of each chunk, and each call that added trees."""

    def __init__(self) -> None:
        self.chunks: dict[int, list[Any]] = {}
        self.added: list[tuple[int, list[Any]]] = []

    def set_chunk(self, index: int, placements: list[Any]) -> None:
        self.chunks[index] = list(placements)

    def add_to_chunk(self, index: int, placements: list[Any]) -> None:
        self.added.append((index, placements))
        self.chunks[index].extend(placements)

    def remove_chunk(self, index: int) -> None:
        self.chunks.pop(index, None)

    def clear(self) -> None:
        self.chunks = {}


class FakeRoads:
    def set_chunk(self, *args: Any) -> None:
        pass

    def remove_chunk(self, index: int) -> None:
        pass

    def clear(self) -> None:
        pass

    def set_tile_chunk(self, index: int, chunk: Any) -> None:
        pass


class FakeSource:
    """A road source: the chunks asked for, none ready."""

    def __init__(self) -> None:
        self.asked: list[int] = []

    def request(self, spans: list[Any], look: Any, grid: bool) -> None:
        self.asked.extend(span[0] for span in spans)

    def take(self, index: int) -> Any:
        return None


# The ground in view, from the camera's Z: about what the playfield camera sees.
GROUND = SimpleNamespace(z_near=100, z_far=700, half_width=300)


def stage(placer: FakePlacer | None = None, tile_look: Any = None) -> SceneryStage:
    s = SceneryStage.__new__(SceneryStage)
    config = SCENERY_STAGE_CONFIG
    s.options = SimpleNamespace(
        config=config, look=SimpleNamespace(roads=SimpleNamespace(tiles=tile_look))
    )
    s._ground = GROUND
    s._ground_root = SimpleNamespace(adopt=lambda make: make())
    s._ahead = 1200
    s._chunks = FakeChunks(config.chunk_length)
    s._placer = placer or FakePlacer()
    s._field = "field"
    s._props = FakeProps()
    s._roads = FakeRoads()
    s._road_source = FakeSource()
    s._road_grid = False
    s._road_pending = []
    s._x_half = 400
    s._solo = False
    s._with_runout = False
    s._tree_jobs = []
    s._trees_later = False
    s._sight = []
    return s


def frame(s: SceneryStage, camera_z: float) -> None:
    """What `update` does for the ground with the camera at ground Z `camera_z`."""
    margin = SCENERY_STAGE_CONFIG.margin
    s._follow_ground(camera_z, camera_z + GROUND.z_near - margin, camera_z + GROUND.z_far + margin)


def trees_of(s: SceneryStage, index: int) -> list[Any]:
    return [p for p in s._props.chunks[index] if p[0] == "tree"]


def test_d212_the_first_chunks_get_their_trees_at_once() -> None:
    s = stage()
    frame(s, 0)
    assert sorted(s._props.chunks) == [0, 1, 2]
    assert len(trees_of(s, 1)) == 320 // CELL
    assert s._tree_jobs == []


def test_d212_a_chunk_coming_in_as_the_view_moves_grows_its_trees_a_row_per_frame() -> None:
    s = stage()
    frame(s, 0)
    camera_z = 0.0
    while 3 not in s._props.chunks:
        camera_z += 2
        frame(s, camera_z)
    # Chunk 3 came in out of sight, with its building only (its first row grew the same frame).
    assert camera_z + GROUND.z_far + SCENERY_STAGE_CONFIG.tree_reach < 960
    while s._tree_jobs:
        camera_z += 2
        frame(s, camera_z)
    rows = [placements for index, placements in s._props.added if index == 3]
    # Each frame a row of cells, never an empty one, each row once: corners 1000 to 1250.
    assert [len(row) for row in rows] == [1] * 6
    assert [row[0][1] for row in rows] == [1000, 1050, 1100, 1150, 1200, 1250]
    # All grown before the view could see them.
    assert camera_z + GROUND.z_far + SCENERY_STAGE_CONFIG.tree_reach < 960


def test_d212_a_waiting_chunk_coming_into_sight_gets_the_rest_of_its_trees_at_once() -> None:
    s = stage()
    frame(s, 0)
    frame(s, 180)
    assert [job[0] for job in s._tree_jobs] == [3]
    # A jump ahead (x4, a long frame): the rest of chunk 3 is in sight now.
    frame(s, 400)
    assert s._tree_jobs == []
    assert [p[1] for p in trees_of(s, 3)] == [1000, 1050, 1100, 1150, 1200, 1250]


def test_d212_a_chunk_placed_in_sight_gets_its_trees_with_its_buildings() -> None:
    s = stage()
    frame(s, 0)
    # A jump far ahead: the chunks in sight come whole, the one past them grows its trees.
    frame(s, 5000)
    sight = tree_sight(5000, GROUND, SCENERY_STAGE_CONFIG.tree_reach)
    for index in s._props.chunks:
        span = s._chunks.span(index)
        if span.z_max > sight[0] and span.z_min < sight[1]:
            assert len(trees_of(s, index)) > 0
    assert [job[0] for job in s._tree_jobs] == [18]


def test_d212_the_next_row_holds_one_row_of_cell_corners() -> None:
    # A chunk starting off the cells' grid: its first row is the corner after its start.
    assert row_end(320, 640, CELL) == 400
    assert row_end(400, 640, CELL) == 450
    # The last row ends with the chunk.
    assert row_end(600, 640, CELL) == 640
    assert row_end(0, 320, CELL) == 50


def test_d212_trees_are_seen_a_little_past_the_ground_in_view() -> None:
    assert tree_sight(1000, GROUND, 40) == [1060, 1740]


def test_d217_a_new_seed_takes_its_street_surfaces_from_its_own_ground(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    s = stage(FakePlacer(tiles="tiles"), tile_look="tile look")
    frame(s, 0)
    old = s._road_source
    s._road_pending.append(99)
    new_source = FakeSource()
    new_ground = SimpleNamespace(field="new field", placer=FakePlacer(tiles="tiles"))
    monkeypatch.setattr(scenery_stage, "level_ground", lambda level, seed: new_ground)
    monkeypatch.setattr(scenery_stage, "road_source_of", lambda ground: new_source)
    monkeypatch.setattr(scenery_stage, "_map_keys", list)
    s.options.level = "level"
    asked_before = list(old.asked)
    s.set_seed(7)
    assert s._road_source is new_source
    assert old.asked == asked_before
    assert sorted(new_source.asked) == [0, 1, 2]
    # The old seed's chunks still waiting are not taken.
    assert sorted(s._road_pending) == [0, 1, 2]
