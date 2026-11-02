# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/scenery_stage.py`.

Its small pure helpers, then the chunks' trees and street sources (D-212, GFX-PROP-14; D-217), on a
stage made without Babylon (its fields set by hand) and the game's stage settings. Last, a stage
built whole and updated, its ground, kit, sky and Babylon parts replaced by stand-ins that record
what it asks of them (ENG-47).
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeNode, FakeVector
from helpers.render_looks import make_look
from helpers.sample_level import sample_level

from config.scenery_stage import SCENERY_STAGE_CONFIG
from core.content.game_definition import LogicalScreen
from core.scenery.ground_boxes import GroundArea, PropPlacement
from render.scenery import scenery_stage
from render.scenery.atmosphere_of import AtmosphereOptions
from render.scenery.cloud_layers import ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP
from render.scenery.ground_root import GroundRoot, ground_window_of
from render.scenery.level_ground import LevelGround
from render.scenery.playfield_framing import frame_playfield, visible_ground
from render.scenery.scenery_kit import SceneryKitContext, SceneryKitFrame, SeaSize
from render.scenery.scenery_look import PlayfieldCameraLook
from render.scenery.scenery_stage import (
    SceneryStage,
    _concat,
    _kit_context,
    _map_keys,
    _plume_frame,
    _props_of,
    _sky_placement,
    row_end,
    tree_sight,
)
from render.scenery.scenery_stage_options import SceneryStageConfig, SceneryStageOptions
from render.scenery.sky_layers import SkyPlacement
from render.scenery.terrain_chunks import ChunkChanges, ChunkSpan

# The JavaScript-only helpers as the module defines them (the `world` fixture replaces them in it).
JS_PLUME_FRAME = _plume_frame
JS_MAP_KEYS = _map_keys


def test_concat_joins_two_sequences_into_a_new_list() -> None:
    first = [1, 2]
    second = (3,)
    joined = _concat(first, second)
    assert joined == [1, 2, 3]
    assert joined is not first


def test_concat_of_nothing_is_empty() -> None:
    assert _concat([], []) == []


def test_the_kit_context_carries_the_sea_size() -> None:
    context = _kit_context("look", "sun", 3.0, 400, 300, 9)
    assert isinstance(context, SceneryKitContext)
    assert context.look == "look"
    assert context.sea_level == 3.0
    assert context.sun == "sun"
    assert isinstance(context.sea_size, SeaSize)
    assert (context.sea_size.width, context.sea_size.length_) == (400, 300)
    assert context.seed == 9


def test_the_sky_placement_keeps_its_callbacks_and_margin() -> None:
    placement = _sky_placement(len, abs, 100, 20)
    assert isinstance(placement, SkyPlacement)
    assert placement.flight_altitude == 100


def test_the_props_materials_are_the_kit_props() -> None:
    kit = SimpleNamespace(props="materials")
    assert _props_of(kit) == "materials"


# The chunks' trees and street sources (D-212, D-217).

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


class FakeRoads:
    def set_chunk(self, *args: Any) -> None:
        pass

    def remove_chunk(self, index: int) -> None:
        pass

    def set_tile_chunk(self, index: int, chunk: Any) -> None:
        pass


class FakeSource:
    """A road source: the chunks asked for, none ready."""

    def __init__(self) -> None:
        self.asked: list[int] = []

    def request(self, spans: list[Any], _look: Any, _grid: bool) -> None:
        self.asked.extend(span[0] for span in spans)

    def take(self, _index: int) -> Any:
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
    s._with_runout = False
    s._tree_jobs = []
    s._trees_later = False
    s._sight = []
    return s


def frame(s: SceneryStage, camera_z: float) -> None:
    """Do what `update` does for the ground with the camera at ground Z `camera_z`."""
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


def test_the_plume_frame_and_the_map_keys_are_javascript_only() -> None:
    """JavaScript-only: a plain object and `Array.from(map.keys())`; CPython runs placeholders."""
    assert JS_PLUME_FRAME(1.0, "camera", "right", "up", "light", "haze", "fog") is None
    assert JS_MAP_KEYS({3: "mesh"}) == []


# A stage built whole: its ground, kit, sky and Babylon parts are stand-ins recording what the stage
# asks of them (ENG-47).

STAGE_CONFIG = SceneryStageConfig(320, 8, 80, 15, 2500, 4000, (40, 120), 40, 200, 40)
SCREEN = LogicalScreen(600, 800)


class _Scene:
    """A Babylon scene: the rendering groups' settings."""

    def __init__(self) -> None:
        self.auto_clear: list[tuple[int, bool, bool]] = []
        self.orders: list[tuple[int, Any]] = []

    def setRenderingAutoClearDepthStencil(self, group: int, depth: bool, stencil: bool) -> None:
        self.auto_clear.append((group, depth, stencil))

    def setRenderingOrder(self, group: int, compare: Any) -> None:
        self.orders.append((group, compare))


class _Camera:
    """The stage's camera: where it is, where it looks, and its axes."""

    def __init__(self, half_fov: float, clips: tuple[float, float], viewport: object) -> None:
        self.half_fov = half_fov
        self.clips = clips
        self.viewport = viewport
        self.position = FakeVector()
        self.targets: list[FakeVector] = []

    def setTarget(self, target: FakeVector) -> None:
        self.targets.append(target)

    def getDirection(self, axis: FakeVector) -> tuple[str, float, float, float]:
        return ("direction", axis.x, axis.y, axis.z)


class _Sky:
    """The sky layers: what they were made with, attached to and updated with."""

    def __init__(self, scene: Any, look: Any, setup: tuple[Any, ...]) -> None:
        self.scene = scene
        self.look = look
        self.setup = setup
        self.sun = SimpleNamespace(direction=FakeVector(0, -1, 1), position=None)
        self.attached: tuple[Any, SkyPlacement] | None = None
        self.clouds = ["cloud-state"]
        self.atmosphere = "atmosphere-here"
        self.weather_particles = 12
        self.flash = 0.25
        self.updates: list[tuple[float, Any]] = []
        self.lit = SimpleNamespace(
            sky=SimpleNamespace(haze="haze"), fog=SimpleNamespace(start=10, end=900)
        )

    def attach(self, kit: Any, placement: SkyPlacement) -> None:
        self.attached = (kit, placement)

    def update(self, distance: float, frame: Any) -> Any:
        self.updates.append((distance, frame))
        return self.lit


class _Kit:
    """A scenery kit: its materials, and what the stage gave it."""

    def __init__(self, scene: Any, context: SceneryKitContext) -> None:
        self.scene = scene
        self.context = context
        self.roads = "road-material"
        self.terrain = "terrain-material"
        self.props = "prop-materials"
        self.plume = "plume-factory"
        self.casters: list[Any] = []
        self.atlases: list[tuple[Any, Any]] = []
        self.frames: list[SceneryKitFrame] = []

    def imposter_atlas(self, look: Any, kinds: Any) -> str:
        self.atlases.append((look, kinds))
        return "atlas"

    def add_shadow_caster(self, mesh: Any) -> None:
        self.casters.append(mesh)

    def update(self, frame: SceneryKitFrame) -> None:
        self.frames.append(frame)


class _GroundRoot(GroundRoot):
    """The ground's node, without Babylon: what the stage made under it."""

    def __init__(self, scene: Any, scale: float) -> None:
        self.scene = scene
        self.scale = scale
        self.node = FakeNode("ground-root")
        self.adopted = 0

    def adopt(self, create: Any) -> Any:
        self.adopted += 1
        return create()


class _Chunks(FakeChunks):
    """The terrain chunks, made as `TerrainChunks` is."""

    def __init__(self, scene: Any, terrain: Any, options: Any, field: Any, on_mesh: Any) -> None:
        super().__init__(options.length_)
        self.made = (scene, terrain, options, field)
        self.on_mesh = on_mesh

    @property
    def count(self) -> int:
        return len(self.meshes)


class _Props(FakeProps):
    """The prop field, made as `PropField` is: the window, syncs, drifts and plume frames."""

    def __init__(self, *args: Any) -> None:
        super().__init__()
        self.args = args
        self.windows: list[tuple[float, float, float]] = []
        self.calls: list[str] = []
        self.drifts: list[tuple[Any, float]] = []
        self.plume_frames: list[Any] = []
        self.light_meshes = ["prop-light"]
        self.window_meshes = ["prop-window"]
        self.structure_meshes = ["prop-structure"]
        self.plume_count = 2

    @property
    def count(self) -> int:
        return sum(len(p) for p in self.chunks.values())

    def set_window(self, z_min: float, z_max: float, step: float) -> None:
        self.windows.append((z_min, z_max, step))

    def bake_imposters(self) -> None:
        self.calls.append("bake")

    def sync(self) -> None:
        self.calls.append("sync")

    def drift(self, drifts: Any, time: float) -> None:
        self.drifts.append((drifts, time))

    def update_plumes(self, frame: Any) -> None:
        self.plume_frames.append(frame)


class _Roads(FakeRoads):
    """The road layers: the chunks they were given and whether the tile grid is shown."""

    def __init__(self, _scene: Any, material: Any) -> None:
        self.material = material
        self.grid = False
        self.chunks: list[int] = []
        self.tile_chunks: list[tuple[int, Any]] = []

    @property
    def count(self) -> int:
        return len(self.chunks)

    def set_chunk(self, index: int, *_args: Any) -> None:
        self.chunks.append(index)

    def show_tile_grid(self) -> None:
        self.grid = True

    def set_tile_chunk(self, index: int, chunk: Any) -> None:
        self.tile_chunks.append((index, chunk))


class _Traffic:
    """The cars: what they were made with and each update."""

    def __init__(self, *args: Any) -> None:
        self.args = args
        self.updates: list[tuple[float, GroundArea, Any]] = []
        self.light_meshes = ["car-light"]
        self.structure_meshes = ["car-body"]

    def update(self, time: float, area: GroundArea, source: Any) -> None:
        self.updates.append((time, area, source))


class _Placer(FakePlacer):
    """The level's placer: also how far it was asked to place its buildings."""

    def __init__(self, tiles: Any = None) -> None:
        super().__init__(tiles)
        self.ensured: list[float] = []
        self.wanted: list[float] = []

    def ensure_placed(self, z: float) -> None:
        self.ensured.append(z)

    def want_placed(self, z: float) -> None:
        self.wanted.append(z)


class _Field:
    """The level's height field: flat at 3, its highest ground 50."""

    ceiling = 50

    def height(self, x: float, z: float) -> float:
        return 3 + 0 * (x + z)


class _ReadySource(FakeSource):
    """A road source whose chunks in `ready` are made."""

    def __init__(self) -> None:
        super().__init__()
        self.ready: dict[int, Any] = {}

    def take(self, index: int) -> Any:
        return self.ready.pop(index, None)


class _World:
    """What the stage was made of, as the fakes recorded it."""

    def __init__(self) -> None:
        self.grounds: list[LevelGround] = []
        self.tiles: Any = None
        self.imposters: list[tuple[Any, ...]] = []
        self.seas: list[tuple[Any, ...]] = []
        self.suns: list[tuple[Any, ...]] = []
        self.plume_frames: list[tuple[Any, ...]] = []

    def level_ground(self, level: Any, seed: int) -> LevelGround:
        ground = LevelGround(level, seed, _Field(), _Placer(self.tiles))  # type: ignore[arg-type]
        ground.roads_source = _ReadySource()
        self.grounds.append(ground)
        return ground

    def imposter_kinds(self, *args: Any) -> str:
        self.imposters.append(args)
        atlas_of = args[3]
        atlas_of(len(args[2]))
        return "tree-imposters"

    def sea_parts(self, scene: Any, level: Any, size: Any, kit: Any) -> Any:
        self.seas.append((scene, level, size, kit))
        if level.sea is None:
            return None
        sea = FakeNode("sea", is_mesh=True)
        rings = SimpleNamespace(shown=0.4, updates=[])
        rings.update = lambda atmosphere, frame: rings.updates.append((atmosphere, frame))
        return SimpleNamespace(sea=sea, rings=rings)

    def snapped_light_position(self, *args: Any) -> str:
        self.suns.append(args)
        return "sun-position"

    def plume_frame(self, *args: Any) -> tuple[Any, ...]:
        self.plume_frames.append(args)
        return args


@pytest.fixture
def world(monkeypatch: pytest.MonkeyPatch) -> _World:
    w = _World()
    for name, fake in {
        "level_ground": w.level_ground,
        "GroundRoot": _GroundRoot,
        "stage_camera": lambda _scene, fov, clips, viewport: _Camera(fov, clips, viewport),
        "SkyLayers": _Sky,
        "RoadLayers": _Roads,
        "PropField": _Props,
        "imposter_kinds": w.imposter_kinds,
        "TrafficLayer": _Traffic,
        "sea_parts": w.sea_parts,
        "TerrainChunks": _Chunks,
        "terrain_last": lambda terrain: ("terrain last", terrain),
        "plume_light": lambda atmosphere: ("plume light", atmosphere),
        "snapped_light_position": w.snapped_light_position,
        "_plume_frame": w.plume_frame,
        "js_object": dict,
        "js_set": lambda o, k, v: o.__setitem__(k, v),
        "vector3": FakeVector,
        "vector3_right": lambda: FakeVector(1, 0, 0),
        "vector3_up": lambda: FakeVector(0, 1, 0),
        "_map_keys": list,
    }.items():
        monkeypatch.setattr(scenery_stage, name, fake)
    return w


def _stage_options(
    level: Any = None, ground_scale: float | None = 2, atmosphere: Any = None
) -> SceneryStageOptions:
    models = {"block": "block-model", "stick": "stick-model", "sedan": "sedan-model"}
    return SceneryStageOptions(
        SCREEN,
        PlayfieldCameraLook(30, 50, 120, ground_scale),
        level if level is not None else sample_level(),
        make_look(),
        models,
        _Kit,
        STAGE_CONFIG,
        atmosphere,
    )


def _built(options: SceneryStageOptions | None = None) -> SceneryStage:
    return SceneryStage(_Scene(), options if options is not None else _stage_options())


def hut(x: float, z: float) -> PropPlacement:
    return PropPlacement("hut", x, 1, z, 0, 1)


def test_gfx_cam_05_a_stage_is_built_over_its_level_s_ground_seen_by_its_camera(
    world: _World,
) -> None:
    options = _stage_options()
    s = _built(options)
    level = options.level
    [ground] = world.grounds
    assert (ground.level, ground.seed) == (level, level.seed)
    assert (s._seed, s.field) == (level.seed, ground.field)
    # GFX-CAM-04: the ground drawn twice as big, seen over what the camera sees of it.
    assert s._ground_root.scale == 2
    framing = frame_playfield(SCREEN, options.camera)
    window = ground_window_of(options, framing, 2)
    assert (s._ground.z_near, s._ground.z_far) == (window.z_near, window.z_far)
    x_half = math.ceil((window.half_width + 80) / 8) * 8
    assert s._x_half == x_half
    # The buildings of the screens the level starts with, and two more ahead, placed now.
    ahead = 2 * (window.z_far - window.z_near)
    assert ground.placer.ensured == [window.z_far + ahead]
    # D-216: the camera's clipping planes.
    assert (s.camera.half_fov, s.camera.clips) == (framing.half_fov, (200, 4000))
    assert s.camera.viewport is None  # D-252: the whole canvas unless a window is given
    sky = s._sky
    assert sky.setup == (level.scroll_speed, None, level.seed)
    assert s.sun is sky.sun


def test_the_kit_gets_the_look_the_sun_and_a_sea_one_wave_tile_longer_than_the_ground(
    world: _World,
) -> None:
    s = _built()
    context = s.kit.context
    assert context.look is s.options.look
    assert context.sun is s.sun
    assert (context.sea_level, context.seed) == (0, s._seed)
    length = s._ground.z_far - s._ground.z_near + 2 * 80 + s.options.look.sea.tileSize
    assert (context.sea_size.width, context.sea_size.length_) == (2 * s._x_half, length)
    [(_scene, level, size, kit)] = world.seas
    assert (level, size, kit) == (s.options.level, [2 * s._x_half, length], s.kit)
    assert s._sea is not None
    assert s._sea_enabled


@pytest.mark.usefixtures("world")
def test_gfx_cam_07_the_sky_is_attached_over_the_ground_s_depth() -> None:
    s = _built()
    groups = [group for group, _depth, _stencil in s.scene.auto_clear]
    assert groups == [BELOW_CLOUDS_GROUP + 1, ABOVE_CLOUDS_GROUP]
    assert all(not depth and not stencil for _g, depth, stencil in s.scene.auto_clear)
    kit, placement = s._sky.attached
    assert kit is s.kit
    assert (placement.flight_altitude, placement.margin) == (120, 80)
    assert s.clouds == ["cloud-state"]


@pytest.mark.usefixtures("world")
def test_perf_28_the_terrain_chunks_span_the_ground_and_are_drawn_last() -> None:
    s = _built()
    assert s.scene.orders == [(BELOW_CLOUDS_GROUP, ("terrain last", "terrain-material"))]
    _scene, terrain, chunk_options, field = s._chunks.made
    assert (terrain, field) == ("terrain-material", s.field)
    assert (chunk_options.length_, chunk_options.cell) == (320, 8)
    assert (chunk_options.x_min, chunk_options.columns) == (-s._x_half, 2 * s._x_half // 8)


@pytest.mark.usefixtures("world")
def test_gfx_terrain_13_each_terrain_chunk_casts_shadows_unless_the_look_says_not() -> None:
    s = _built()
    seen: list[Any] = []
    s._chunks.on_mesh("chunk-0")
    s.watch_terrain(seen.append)
    s._chunks.on_mesh("chunk-1")
    assert seen == ["chunk-0", "chunk-1"]
    assert s.kit.casters == ["chunk-0", "chunk-1"]
    s.options.look.terrain.castsShadows = False
    s._chunks.on_mesh("chunk-2")
    assert s.kit.casters == ["chunk-0", "chunk-1"]
    assert seen[-1] == "chunk-2"


def test_d212_the_props_are_the_level_s_models_with_its_trees_as_imposters(world: _World) -> None:
    """GFX-PROP-12: the props cast shadows through the kit."""
    s = _built()
    scene, models, materials, shadow, plumes, imposters = s._props.args
    assert scene is s.scene
    # The sedan is a car, not a prop standing on the ground.
    assert models == {"block": "block-model", "stick": "stick-model"}
    assert (materials, plumes, imposters) == ("prop-materials", "plume-factory", "tree-imposters")
    [(_scene, imposter_models, kinds, _atlas_of, tilt)] = world.imposters
    assert (imposter_models, kinds, tilt) == (models, ["stick"], s.framing.tilt)
    assert s.kit.atlases[0] == (s.options.look.props.treeImposters, 1)
    shadow("tree-mesh")
    assert s.kit.casters == ["tree-mesh"]


@pytest.mark.usefixtures("world")
def test_gfx_car_08_the_cars_are_made_from_every_model_with_the_kit_s_imposters() -> None:
    """D-211."""
    s = _built()
    scene, models, materials, cars, atlas_of, tilt = s._traffic.args
    assert (scene, models, materials) == (s.scene, s.options.prop_models, "prop-materials")
    assert cars is s.options.level.props.cars
    assert tilt == s.framing.tilt
    assert atlas_of(3) == "atlas"
    assert s.kit.atlases[-1] == (s.options.look.props.imposters, 3)


@pytest.mark.usefixtures("world")
def test_without_a_ground_scale_or_a_sea_the_ground_is_drawn_as_it_is_and_dry() -> None:
    """GFX-WATER-02."""
    level = sample_level()
    level.sea = None
    s = _built(_stage_options(level, ground_scale=None))
    assert s._ground_root.scale == 1
    assert s.kit.context.sea_level == 0
    assert s._sea is None
    assert not s._sea_enabled
    assert s.rain_rings == 0
    assert s.lava is None


@pytest.mark.usefixtures("world")
def test_dev_opt_06_the_tile_grid_is_drawn_only_when_the_debug_options_ask() -> None:
    assert not _built()._roads.grid
    assert not _built(_stage_options(atmosphere=AtmosphereOptions(tile_grid=False)))._roads.grid
    assert _built(_stage_options(atmosphere=AtmosphereOptions(tile_grid=True)))._roads.grid


@pytest.mark.usefixtures("world")
def test_the_stage_reports_its_sky_its_rain_rings_and_its_counts() -> None:
    """GFX-SKY-04, GFX-WEATHER-03, GFX-WEATHER-09, GFX-WEATHER-11."""
    s = _built()
    assert s.atmosphere == "atmosphere-here"
    assert s.weather_particles == 12
    assert s.lightning_flash == 0.25
    assert s.rain_rings == 0.4
    s._props.set_chunk(0, [hut(0, 0), hut(1, 1)])
    s._chunks.meshes[0] = "mesh"
    s._roads.chunks = [0, 1, 2]
    assert s.stats == {"props": 2, "chunks": 1, "roads": 3}
    assert s.plumes == 2


@pytest.mark.usefixtures("world")
def test_gfx_terrain_15_the_glowing_meshes_are_the_props_and_cars_lights() -> None:
    """GFX-CAR-09, D-210."""
    s = _built()
    assert s.glowing_meshes == ["prop-light", "car-light"]
    assert s.window_meshes == ["prop-window"]
    assert s.glow_occluders == ["prop-structure", "car-body"]


@pytest.mark.usefixtures("world")
def test_gfx_terrain_18_the_sea_is_the_lava_when_the_look_s_liquid_is_lava() -> None:
    s = _built()
    assert s.lava is None
    s.options.look.sea.lava = "lava look"
    assert s.lava is s._sea


@pytest.mark.usefixtures("world")
def test_a_playfield_point_is_over_the_flight_plane_from_the_screen_s_middle() -> None:
    point = _built().playfield_point(400, 50, 1000)
    assert (point.x, point.y, point.z) == (100, 120, 1050)


@pytest.mark.usefixtures("world")
def test_gfx_sky_12_a_cloud_layer_stays_clear_of_the_highest_ground() -> None:
    s = _built()
    # The highest ground, 50, drawn twice as big: 100, and 15 above it.
    assert s.cloud_altitude(SimpleNamespace(altitude=90)) == 115
    assert s.cloud_altitude(SimpleNamespace(altitude=300)) == 300


@pytest.mark.usefixtures("world")
def test_the_sky_s_window_at_an_altitude_is_what_the_camera_sees_of_that_plane() -> None:
    s = _built()
    seen = s._window_at(60)
    expected = visible_ground(s.framing, 600 / 800, 120 + s.framing.height, 60, 60)
    assert (seen.z_near, seen.z_far, seen.half_width) == (
        expected.z_near,
        expected.z_far,
        expected.half_width,
    )
    assert s._sky.attached[1].window_at(60).z_far == expected.z_far


@pytest.mark.usefixtures("world")
def test_gfx_cam_02_an_update_moves_the_camera_and_the_ground_to_the_distance() -> None:
    s = _built()
    s.update(100, 0.5)
    framing = s.framing
    camera = s.camera.position
    assert (camera.x, camera.y, camera.z) == (0, 120 + framing.height, 100 + framing.back)
    [target] = s.camera.targets
    expected = (0, camera.y + framing.direction[0], camera.z + framing.direction[1])
    assert (target.x, target.y, target.z) == pytest.approx(expected)
    # GFX-CAM-04: the ground twice as big passes twice as fast under the view.
    assert s._ground_root.node.position.z == -100
    camera_z = (camera.z + 100) / 2
    ahead = 2 * (s._ground.z_far - s._ground.z_near)
    assert s._placer.wanted == [camera_z + s._ground.z_far + ahead]
    assert s._sight == tree_sight(camera_z, s._ground, 40)
    first = math.floor((camera_z + s._ground.z_near - 80) / 320)
    last = math.floor((camera_z + s._ground.z_far + 80) / 320)
    assert sorted(s._chunks.meshes) == list(range(first, last + 1))


@pytest.mark.usefixtures("world")
def test_perf_25_an_update_draws_the_props_near_the_ground_in_view_and_their_drift() -> None:
    """GFX-PROP-05, GFX-PROP-15."""
    s = _built()
    s.update(100, 0.5)
    s.update(110, 0.25)
    camera_z = s._ground_root.to_ground(s.camera.position.z)
    props = s._props
    z_near = camera_z + s._ground.z_near - 40
    z_far = camera_z + s._ground.z_far + 120
    assert props.windows[-1] == pytest.approx((z_near, z_far, 40))
    assert props.calls == ["bake", "sync", "bake", "sync"]
    assert props.drifts[-1] == (s._drifts, 0.75)


@pytest.mark.usefixtures("world")
def test_gfx_car_08_the_cars_are_placed_near_the_ground_in_view_on_the_level_s_roads() -> None:
    """PERF-27."""
    s = _built()
    s.update(100, 0.5)
    camera_z = s._ground_root.to_ground(s.camera.position.z)
    [(time, area, source)] = s._traffic.updates
    assert time == 0.5
    x_half = min(s._x_half, s._ground.half_width + 40)
    assert (area.x_min, area.x_max) == (-x_half, x_half)
    z_low = max(camera_z + s._ground.z_near - 80, camera_z + s._ground.z_near - 40)
    z_high = min(camera_z + s._ground.z_far + 80, camera_z + s._ground.z_far + 120)
    assert (area.z_min, area.z_max) == pytest.approx((z_low, z_high))
    assert source["roads"] is s._placer.roads.roads
    assert source["seed"] == s._seed
    # The cars stand on the stage's ground.
    assert source["height"](4, 9) == 3


@pytest.mark.usefixtures("world")
def test_gfx_water_03_the_sea_follows_the_view_by_whole_wave_tiles() -> None:
    """GFX-WEATHER-09: the rain rings follow the middle of the view."""
    s = _built()
    s.update(100, 0.5)
    camera_z = s._ground_root.to_ground(s.camera.position.z)
    middle = camera_z + (s._ground.z_near + s._ground.z_far) / 2
    assert s._sea.position.z == math.floor(middle / 16 + 0.5) * 16
    assert s._sea.position.z % 16 == 0
    [(atmosphere, frame)] = s._rings.updates
    assert atmosphere is s._sky.lit
    assert frame == pytest.approx((0.5, middle, True))


def test_gfx_sky_04_an_update_moves_the_sky_and_lights_the_plumes_with_its_atmosphere(
    world: _World,
) -> None:
    """GFX-PROP-18."""
    s = _built()
    s.update(100, 0.5)
    camera_z = s._ground_root.to_ground(s.camera.position.z)
    [(distance, (time, camera, z_from))] = s._sky.updates
    assert (distance, time, camera) == (100, 0.5, s.camera)
    assert z_from == s._ground_root.to_world(camera_z + s._ground.z_near - 80)
    lit = s._sky.lit
    frame = (
        0.5,
        s.camera.position,
        ("direction", 1, 0, 0),
        ("direction", 0, 1, 0),
        ("plume light", lit),
        "haze",
        lit.fog,
    )
    assert world.plume_frames == [frame]
    assert s._props.plume_frames == [frame]


def test_gfx_sky_02_the_sun_is_placed_by_whole_shadow_texels_over_the_view(
    world: _World,
) -> None:
    s = _built()
    s.update(100, 0.5)
    camera_z = s._ground_root.to_ground(s.camera.position.z)
    middle = camera_z + (s._ground.z_near + s._ground.z_far) / 2
    [(direction, target, distance, texel)] = world.suns
    assert direction is s.sun.direction
    assert (target.x, target.y, target.z) == (0, 0, s._ground_root.to_world(middle))
    shadow = s.options.look.sun.shadow
    assert (distance, texel) == (2500, shadow.frustum / shadow.mapSize)
    assert s.sun.position == "sun-position"


@pytest.mark.usefixtures("world")
def test_the_kit_is_updated_with_the_time_camera_sea_atmosphere_and_ground() -> None:
    s = _built()
    s.update(100, 0.5)
    [frame] = s.kit.frames
    assert (frame.time, frame.sea_enabled, frame.atmosphere) == (0.5, True, s._sky.lit)
    assert frame.camera_position is s.camera.position
    assert (frame.ground.scale, frame.ground.offset_z) == (2, -100)


@pytest.mark.usefixtures("world")
def test_a_dry_level_updates_without_a_sea_or_rain_rings() -> None:
    level = sample_level()
    level.sea = None
    s = _built(_stage_options(level))
    s.update(100, 0.5)
    assert s._sea is None
    assert s.kit.frames[0].sea_enabled is False


@pytest.mark.usefixtures("world")
def test_the_chunks_the_runout_reaches_are_placed_again_once_it_is_laid() -> None:
    """Reviewer, 2026-10-28: its streets and buildings come after the rest."""
    s = _built()
    s.update(0, 0.5)
    placed = list(s._roads.chunks)
    runout_from = 700.0
    s._placer.roads.runout_from = runout_from
    s._placer.runout_laid = True
    s.update(0, 0.5)
    again = s._roads.chunks[len(placed) :]
    expected = [i for i in s._chunks.meshes if (i + 1) * 320 > runout_from - 64]
    assert sorted(again) == sorted(expected)
    assert 0 not in again
    # Only once.
    s.update(0, 0.5)
    assert len(s._roads.chunks) == len(placed) + len(again)


@pytest.mark.usefixtures("world")
def test_a_runout_with_no_streets_places_no_chunk_again() -> None:
    s = _built()
    s.update(0, 0.5)
    placed = list(s._roads.chunks)
    s._placer.runout_laid = True
    s.update(0, 0.5)
    assert s._roads.chunks == placed
    assert s._with_runout is True


def test_d217_the_street_surfaces_ready_are_given_to_their_chunks_the_others_wait(
    world: _World,
) -> None:
    """GFX-ROAD-21; a chunk placed again while its streets are on their way waits once."""
    world.tiles = "tiles"
    options = _stage_options()
    options.look.roads.tiles = "tile look"
    s = _built(options)
    source = s._road_source
    source.ready[1] = "streets of 1"
    s.update(0, 0.5)
    assert s._roads.tile_chunks == [(1, "streets of 1")]
    waiting = sorted(i for i in s._chunks.meshes if i != 1)
    assert sorted(s._road_pending) == waiting
    # The runout places chunks again: they are asked for again, and still wait once each.
    s._placer.roads.runout_from = 0
    s._placer.runout_laid = True
    s.update(0, 0.5)
    assert sorted(s._road_pending) == sorted(s._chunks.meshes)
    assert len(set(s._road_pending)) == len(s._road_pending)
