"""The ground of a scrolling level seen by the tilted playfield camera (P04): sculpted terrain in
chunks, an optional sea, cloud layers and
props, lit by a low sun. `update` moves everything to a distance along the level.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.scenery.ground_boxes import GroundArea
from core.scenery.height_field import HeightField
from render.babylon import (
    js_object,
    js_set,
    vector3,
    vector3_right,
    vector3_up,
)
from render.scenery.cloud_layers import ABOVE_CLOUDS_GROUP, BELOW_CLOUDS_GROUP
from render.scenery.ground_root import GroundRoot, ground_window_of
from render.scenery.imposter_kinds import imposter_kinds
from render.scenery.level_ground import level_ground, road_source_of
from render.scenery.playfield_framing import (
    GroundWindow,
    PlayfieldFraming,
    frame_playfield,
    visible_ground,
)
from render.scenery.plume_layer import plume_light
from render.scenery.prop_field import (
    PropField,
    level_prop_models,
    level_tree_kinds,
    prop_drifts,
)
from render.scenery.rain_rings import RainRings
from render.scenery.road_field import RoadLayers
from render.scenery.scenery_kit import SceneryKitContext, SceneryKitFrame, SeaSize
from render.scenery.scenery_lighting import snapped_light_position
from render.scenery.sky_layers import SkyLayers, SkyPlacement
from render.scenery.stage_parts import TerrainWatch, sea_parts, stage_camera, terrain_last
from render.scenery.terrain_chunks import TerrainChunkOptions, TerrainChunks
from render.scenery.traffic_layer import TrafficLayer

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from core.scenery.atmosphere import Atmosphere  # noqa: E402
from render.scenery.cloud_layers import CloudLayerState  # noqa: E402
from render.scenery.scenery_look import CloudLayerLook  # noqa: E402
from render.scenery.scenery_stage_options import SceneryStageOptions  # noqa: E402

__pragma__("noskip")

# How far before the runout its streets and buildings can change what a chunk shows: the trees
# keep clear of the buildings (reviewer, 2026-10-28).
RUNOUT_REACH = 64

# Infinity.
INFINITY = float("Infinity")


def _map_keys(cache: Any) -> list[Any]:
    """The keys of a JavaScript `Map`, as a list (a copy)."""
    __pragma__("js", "{}", "return Array.from(cache.keys());")
    return []


def _props_of(kit: Any) -> Any:
    """The props' materials of the kit (its `PropMaterials`, as the prop field and traffic take)."""
    return kit.props


def _plume_frame(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    time: float,
    camera_position: Any,
    right: Any,
    up: Any,
    light: Any,
    haze: Any,
    fog: Any,
) -> Any:
    """The frame of the props' plumes: `{ time, cameraPosition, right, up, light, fog }`, the fog
    as `{ color, start, end }`."""
    __pragma__(
        "js",
        "{}",
        "return {time: time, cameraPosition: camera_position, right: right, up: up, light: light, "
        "fog: {color: haze, start: fog.start, end: fog.end}};",
    )
    return None


# The chunk the props of `solo_props` are kept in: no terrain chunk has it.
SOLO_CHUNK = -1000000


class SceneryStage:
    """The ground of a scrolling level seen by the tilted playfield camera (P04): sculpted terrain
    in chunks, an optional sea, cloud layers and props, lit by a low sun. `update` moves everything
    to a distance along the level."""

    def __init__(self, scene: Any, options: SceneryStageOptions) -> None:
        self.scene = scene
        self.options = options
        self._time = 0.0
        self._with_runout = False
        # Dev viewer (D-199): only the props given to `solo_props` are drawn, no car.
        self._solo = False
        level = options.level
        look = options.look
        config = options.config
        models = level_prop_models(level, options.prop_models)
        self._seed = level.seed
        ground = level_ground(level, self._seed)
        self._field: HeightField = ground.field
        self._placer = ground.placer
        self._drifts = prop_drifts(level)
        self.framing: PlayfieldFraming = frame_playfield(options.screen, options.camera)
        scale = options.camera.groundScale if options.camera.groundScale is not None else 1
        self._ground_root = GroundRoot(scene, scale)
        self._ground: GroundWindow = ground_window_of(
            options, self.framing, self._ground_root.scale
        )
        self._x_half = (
            math.ceil((self._ground.half_width + config.margin) / config.cell) * config.cell
        )
        self.camera = stage_camera(
            scene, self.framing.half_fov, (config.near_clip, config.far_clip)
        )
        # P08-R04: the time of day, clouds and weather along the level.
        self._sky = SkyLayers(scene, look, (level.scroll_speed, options.atmosphere, level.seed))
        self.sun = self._sky.sun
        # One more wave tile: the sea plane moves by whole tiles (see `update`).
        sea_length = (
            self._ground.z_far - self._ground.z_near + 2 * config.margin + look.sea.tileSize
        )
        sea_level = level.sea.level if level.sea is not None else 0
        self.kit = options.kit(
            scene,
            _kit_context(look, self.sun, sea_level, self._x_half * 2, sea_length, level.seed),
        )
        # The screens the level starts with (and two more ahead of each, see `update`), placed now.
        self._ahead = 2 * (self._ground.z_far - self._ground.z_near)
        self._placer.ensure_placed(self._ground.z_far + self._ahead)
        self._chunks = self._ground_root.adopt(self._build_chunks)
        self._roads = RoadLayers(scene, self.kit.roads)
        # The street surfaces of the tile roads come from the ground (the worker's, or made here)
        # when their chunk is placed; the ones not made yet wait in `_road_pending`.
        self._road_source = road_source_of(ground)
        self._road_grid = bool(options.atmosphere is not None and options.atmosphere.tile_grid)
        self._road_pending: list[int] = []
        if self._road_grid:
            self._roads.show_tile_grid()
        self._props = self._ground_root.adopt(lambda: self._build_props(models))
        prop_models = options.prop_models
        self._traffic = self._ground_root.adopt(
            lambda: TrafficLayer(
                scene,
                prop_models,
                _props_of(self.kit),
                level.props.cars,
                lambda kinds: self.kit.imposter_atlas(look.props.imposters, kinds),
                self.framing.tilt,
            ),
        )
        water = self._ground_root.adopt(
            lambda: sea_parts(scene, level, [self._x_half * 2, sea_length], self.kit),
        )
        self._sea = water.sea if water is not None else None
        self._rings: RainRings | None = water.rings if water is not None else None
        self._sea_enabled = self._sea is not None
        self._terrain = TerrainWatch()
        # D-212: the chunks whose trees are still to come, a row of cells per frame, as
        # `[index, z from, z to]`; the chunks of the first cover get theirs at once (the level is
        # loading), and so do those in sight (`_sight`, the ground Z range where trees can be seen).
        self._tree_jobs: list[list[Any]] = []
        self._trees_later = False
        self._sight: list[float] = []
        self.clouds: list[CloudLayerState] = self._attach_sky()

    def _attach_sky(self) -> list[CloudLayerState]:
        """The clouds, weather and aurora above the ground, drawn keeping the ground's depth."""
        for group in [BELOW_CLOUDS_GROUP + 1, ABOVE_CLOUDS_GROUP]:
            self.scene.setRenderingAutoClearDepthStencil(group, False, False)
        options = self.options
        self._sky.attach(
            self.kit,
            _sky_placement(
                self._window_at,
                self.cloud_altitude,
                options.camera.flightAltitude,
                options.config.margin,
            ),
        )
        return self._sky.clouds

    @property
    def atmosphere(self) -> Atmosphere:
        """The level's look where the view is now (P08-R04)."""
        atmosphere: Atmosphere = self._sky.atmosphere
        return atmosphere

    @property
    def weather_particles(self) -> int:
        """Weather particles drawn on the last frame (P08-R05)."""
        count: int = self._sky.weather_particles
        return count

    @property
    def rain_rings(self) -> float:
        """Strength of the rain rings drawn on the water on the last frame (P09-R05; 0 = none)."""
        return self._rings.shown if self._rings is not None else 0

    @property
    def lightning_flash(self) -> float:
        """How bright the lightning was on the last frame (P09-R05; 0 = no flash)."""
        return self._sky.flash

    @property
    def field(self) -> HeightField:
        """The level's ground."""
        return self._field

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def has_sea(self) -> bool:
        return self._sea is not None

    @property
    def sea_enabled(self) -> bool:
        return self._sea_enabled

    @property
    def stats(self) -> Any:
        """Number of props, terrain chunks and roads in the scene."""
        stats = js_object()
        js_set(stats, "props", self._props.count)
        js_set(stats, "chunks", self._chunks.count)
        js_set(stats, "roads", self._roads.count)
        return stats

    @property
    def glowing_meshes(self) -> list[Any]:
        """Meshes of the props' self-lit accents (for a glow layer)."""
        return _concat(self._props.light_meshes, self._traffic.light_meshes)

    @property
    def window_meshes(self) -> list[Any]:
        """Meshes of the props' windows (D-210), among the glowing ones: a glow layer draws them
        with their own material."""
        meshes: list[Any] = self._props.window_meshes
        return meshes

    @property
    def glow_occluders(self) -> list[Any]:
        """Meshes that hide the glowing ones behind them (reviewer, 2026-10-28): the props and the
        cars. A glow layer draws them black; the terrain chunks come through `watch_terrain`."""
        return _concat(self._props.structure_meshes, self._traffic.structure_meshes)

    @property
    def lava(self) -> Any:
        """Phase 10: the lava (P10-R05), when the level's liquid is lava, else None."""
        return self._sea if self.options.look.sea.lava != None else None  # noqa: E711 (absent: undefined)

    @property
    def plumes(self) -> int:
        """Plume meshes drawn on the last frame (phase 10: smoke and steam)."""
        count: int = self._props.plume_count
        return count

    def watch_terrain(self, watch: Callable[[Any], None]) -> None:
        """Calls `watch` with every terrain chunk mesh, now and as new ones are made."""
        self._terrain.watch(watch)

    def set_seed(self, seed: int) -> None:
        """Regenerates the terrain and the props from another seed."""
        self._seed = seed
        ground = level_ground(self.options.level, seed)
        self._field = ground.field
        self._placer = ground.placer
        # The street surfaces of the new roads: the old seed's still on their way are not taken.
        self._road_source = road_source_of(ground)
        self._road_pending = []

        def rebuild() -> None:
            self._chunks.rebuild(self._field)
            self._tree_jobs = []
            self._props.clear()
            self._roads.clear()
            for index in _map_keys(self._chunks.meshes):
                self._place_chunk(index)

        self._ground_root.adopt(rebuild)

    def set_sea_enabled(self, enabled: bool) -> None:
        """Shows or hides the sea; a level without a sea stays without one (P04-R02)."""
        self._sea_enabled = enabled and self._sea is not None
        if self._sea is not None:
            self._sea.setEnabled(self._sea_enabled)

    def solo_props(self, placements: list[Any]) -> None:
        """Dev viewer (D-199): the level's own props and cars are no longer drawn, only
        `placements` (`PropPlacement`, in ground units: kinds of this level), standing on its
        ground as its own do."""
        self._solo = True
        self._tree_jobs = []
        self._props.clear()
        self._props.set_chunk(SOLO_CHUNK, placements)

    def find_prop(self, kind: str, z_end: float) -> Any:
        """Dev viewer (D-199): where the level first places a prop of `kind` (ground units, up to
        ground Z `z_end`), the one nearest the middle of its first chunk that has one; None if it
        places none there. Places the level's buildings up to it."""
        length = self.options.config.chunk_length
        half = self._ground.half_width
        z = 0.0
        while z < z_end:
            best: Any = None
            for p in self._placer.place(GroundArea(-half, half, z, z + length)):
                if p.kind == kind and (best is None or abs(p.x) < abs(best.x)):
                    best = p
            if best is not None:
                return best
            z += length
        return None

    def shift_ground(self, x: float) -> None:
        """Dev viewer (D-199): moves the ground so its X `x` (ground units) is under the middle of
        the view."""
        root = self._ground_root
        root.node.position.x = -x * root.scale

    @property
    def ground_root(self) -> GroundRoot:
        """The node the ground hangs from (its scale, and where ground Z is drawn)."""
        return self._ground_root

    def playfield_point(self, x: float, y: float, distance: float) -> Any:
        """World position of a playfield point (logical pixels, origin at its bottom left)."""
        screen = self.options.screen
        camera = self.options.camera
        return vector3(x - screen.width / 2, camera.flightAltitude, distance + y)

    def update(self, distance: float, dt: float) -> None:
        """Moves the camera, the terrain, the sea and the clouds to `distance` along the level."""
        self._time += dt
        margin = self.options.config.margin
        camera = self.camera.position
        camera.set(
            0,
            self.options.camera.flightAltitude + self.framing.height,
            distance + self.framing.back,
        )
        dy = self.framing.direction[0]
        dz = self.framing.direction[1]
        self.camera.setTarget(vector3(0, camera.y + dy, camera.z + dz))
        # The ground's Z under the camera, and the ground in view (ground units).
        ground = self._ground_root
        ground.move_to(distance)
        camera_z = ground.to_ground(camera.z)
        z_min = camera_z + self._ground.z_near - margin
        z_max = camera_z + self._ground.z_far + margin
        self._follow_ground(camera_z, z_min, z_max)
        self._update_props(camera_z, z_min, z_max)
        middle = camera_z + (self._ground.z_near + self._ground.z_far) / 2
        if self._sea is not None:
            tile = self.options.look.sea.tileSize
            # Whole tiles only, so the waves stay put on the ground while the plane follows the
            # camera.
            self._sea.position.z = math.floor(middle / tile + 0.5) * tile
        atmosphere = self._sky.update(distance, (self._time, self.camera, ground.to_world(z_min)))
        if self._rings is not None:
            self._rings.update(atmosphere, (self._time, middle, self._sea_enabled))
        self._update_plumes(atmosphere)
        shadow = self.options.look.sun.shadow
        self.sun.position = snapped_light_position(
            self.sun.direction,
            vector3(0, 0, ground.to_world(middle)),
            self.options.config.sun_distance,
            shadow.frustum / shadow.mapSize,
        )
        self.kit.update(
            SceneryKitFrame(
                self._time,
                camera,
                self._sea_enabled,
                atmosphere,
                ground.transform,
            ),
        )

    def _follow_ground(self, camera_z: float, z_min: float, z_max: float) -> None:
        """Keeps the chunks over ground Z [z_min, z_max], around the view of the camera at ground Z
        `camera_z`, with their roads and props; the trees still to come grow (D-212)."""
        # The buildings two screens ahead of the view are asked for as the view moves.
        self._placer.want_placed(camera_z + self._ground.z_far + self._ahead)
        self._sight = tree_sight(camera_z, self._ground, self.options.config.tree_reach)
        self._ground_root.adopt(lambda: self._cover(z_min, z_max))
        self._trees_later = True
        self._grow_trees()

    def _height(self, x: float, z: float) -> float:
        return self._field.height(x, z)

    def _update_props(self, camera_z: float, z_min: float, z_max: float) -> None:
        """The props in view near the camera at `camera_z`, drifting, and the cars on the ground."""
        config = self.options.config
        near = config.prop_reach[0]
        far = config.prop_reach[1]
        z_near = camera_z + self._ground.z_near - near
        z_far = camera_z + self._ground.z_far + far
        self._props.set_window(z_near, z_far, config.prop_step)
        self._props.bake_imposters()
        self._props.sync()
        self._props.drift(self._drifts, self._time)
        traffic = js_object()
        js_set(traffic, "roads", self._placer.roads.roads)
        js_set(traffic, "height", self._height)
        js_set(traffic, "seed", self._seed)
        # The cars, placed again every frame, only near the ground in view, as the props (reviewer,
        # 2026-10-28): not over the whole chunks.
        x_half = min(self._x_half, self._ground.half_width + near)
        z_low = max(z_min, z_near)
        # Dev viewer (D-199): no car, an empty area.
        z_high = z_low - 1 if self._solo else min(z_max, z_far)
        self._traffic.update(
            self._time,
            GroundArea(-x_half, x_half, z_low, z_high),
            traffic,
        )

    def _update_plumes(self, atmosphere: Atmosphere) -> None:
        """Phase 10: the props' smoke and steam, lit and fogged by `atmosphere`."""
        camera = self.camera
        self._props.update_plumes(
            _plume_frame(
                self._time,
                camera.position,
                camera.getDirection(vector3_right()),
                camera.getDirection(vector3_up()),
                plume_light(atmosphere),
                atmosphere.sky.haze,
                atmosphere.fog,
            ),
        )

    def _cover(self, z_min: float, z_max: float) -> None:
        """Keeps the chunks over [z_min, z_max], with their roads and props."""
        self._take_runout()
        changes = self._chunks.cover(z_min, z_max)
        for index in changes.removed:
            self._props.remove_chunk(index)
            self._roads.remove_chunk(index)
        self._tree_jobs = [job for job in self._tree_jobs if job[0] not in changes.removed]
        self._road_pending = [i for i in self._road_pending if i not in changes.removed]
        for span in changes.added:
            self._place_chunk(span.index)
        self._take_roads()

    def _take_runout(self) -> None:
        """Once the runout's streets and buildings come (generated after the rest, reviewer
        2026-10-28), places again the chunks they show in."""
        placed = self._placer.runout_laid
        if placed == self._with_runout:
            return
        self._with_runout = placed
        runout_from = self._placer.roads.runout_from
        from_ = (runout_from if runout_from is not None else INFINITY) - RUNOUT_REACH
        for index in _map_keys(self._chunks.meshes):
            if self._chunks.span(index).z_max > from_:
                self._place_chunk(index)

    def _place_chunk(self, index: int) -> None:
        span = self._chunks.span(index)
        roads = self._placer.roads.roads
        tiles = self._placer.roads.tiles
        look = self.options.look.roads
        # The bounds are passed as a pair: a `ChunkSpan` is not indexable (the street test would
        # then pass every street of the level into every chunk).
        self._roads.set_chunk(index, roads, self._field, (span.z_min, span.z_max), look, tiles)
        if tiles is not None and look.tiles is not None:
            self._road_source.request(
                [[index, span.z_min, span.z_max]], look.tiles, self._road_grid
            )
            if index not in self._road_pending:
                self._road_pending.append(index)
        area = GroundArea(-self._x_half, self._x_half, span.z_min, span.z_max)
        if self._solo:
            return
        self._tree_jobs = [job for job in self._tree_jobs if job[0] != index]
        # A chunk in sight (placed again by the runout or a new seed, or come after a jump) gets its
        # trees with its buildings: they would else blink out and grow back in sight. One that
        # comes in as the view moves on is out of sight (`tree_reach` is less than `margin`).
        if not self._trees_later or self._in_sight(span.z_min, span.z_max):
            self._props.set_chunk(index, self._placer.place(area))
            return
        # D-212: the buildings now, the trees over the next frames (see `_grow_trees`).
        self._props.set_chunk(index, self._placer.place_without_trees(area))
        self._tree_jobs.append([index, span.z_min, span.z_max])

    def _in_sight(self, z_min: float, z_max: float) -> bool:
        """Whether ground Z [z_min, z_max] reaches into the ground where trees can be seen."""
        sight = self._sight
        return len(sight) > 0 and z_max > sight[0] and z_min < sight[1]

    def _grow_trees(self) -> None:
        """D-212: the trees of one more row of cells of the first chunk still waiting for them (a
        wood's take tens of milliseconds a chunk: placed at once, they made the frame long). A chunk
        coming into sight gets the rest of its trees at once (after a jump, at x4 or a long frame,
        it would else be seen bare). The others grow unseen, though they may be drawn already: the
        props are drawn further out than trees can be seen."""
        waiting: list[list[Any]] = []
        for job in self._tree_jobs:
            if self._in_sight(job[1], job[2]):
                self._add_trees(job, job[2])
            else:
                waiting.append(job)
        self._tree_jobs = waiting
        if len(waiting) == 0:
            return
        job = waiting[0]
        z_to = row_end(job[1], job[2], self._placer.rules.cell_size)
        self._add_trees(job, z_to)
        if z_to >= job[2]:
            self._tree_jobs.pop(0)

    def _add_trees(self, job: list[Any], z_to: float) -> None:
        """Adds the trees of `job`'s chunk from its next row up to ground Z `z_to`."""
        area = GroundArea(-self._x_half, self._x_half, job[1], z_to)
        self._props.add_to_chunk(job[0], self._placer.trees_in(area))
        job[1] = z_to

    def _take_roads(self) -> None:
        """Gives the street surfaces that are ready to their chunks; the others keep waiting."""
        waiting: list[int] = []
        for index in self._road_pending:
            chunk = self._road_source.take(index)
            if chunk is None:
                waiting.append(index)
            else:
                self._roads.set_tile_chunk(index, chunk)
        self._road_pending = waiting

    def _build_props(self, models: Any) -> PropField:
        """The props of the level, of `models`, casting shadows."""
        kit = self.kit

        def shadow(mesh: Any) -> None:
            kit.add_shadow_caster(mesh)

        # D-212: the trees drawn as imposters, if the look has theirs.
        level = self.options.level
        trees = imposter_kinds(
            self.scene,
            models,
            level_tree_kinds(level),
            lambda kinds: kit.imposter_atlas(self.options.look.props.treeImposters, kinds),
            self.framing.tilt,
        )
        return PropField(self.scene, models, _props_of(kit), shadow, kit.plume, trees)

    def _build_chunks(self) -> TerrainChunks:
        config = self.options.config
        self.scene.setRenderingOrder(BELOW_CLOUDS_GROUP, terrain_last(self.kit.terrain))
        options = TerrainChunkOptions(
            config.chunk_length,
            config.cell,
            -self._x_half,
            int((2 * self._x_half) / config.cell),
        )

        def on_mesh(mesh: Any) -> None:
            if self.options.look.terrain.castsShadows is not False:
                self.kit.add_shadow_caster(mesh)
            self._terrain.add(mesh)

        return TerrainChunks(self.scene, self.kit.terrain, options, self._field, on_mesh)

    def cloud_altitude(self, look: CloudLayerLook) -> float:
        """Height of a cloud layer: its look's altitude, raised if needed to stay `cloud_clearance`
        above the highest ground, so clouds never pass through the terrain (phase 4 review)."""
        ceiling = self._field.ceiling * self._ground_root.scale
        return max(look.altitude, ceiling + self.options.config.cloud_clearance)

    def _window_at(self, altitude: float) -> GroundWindow:
        """What the camera sees of the plane at `altitude`."""
        screen = self.options.screen
        camera_y = self.options.camera.flightAltitude + self.framing.height
        return visible_ground(
            self.framing,
            screen.width / screen.height,
            camera_y,
            altitude,
            altitude,
        )


def _kit_context(
    look: Any,
    sun: Any,
    sea_level: float,
    width: float,
    length: float,
    seed: int,
) -> Any:
    """The `SceneryKitContext` the kit factory gets (its sea size: width and length)."""
    return SceneryKitContext(look, sun, sea_level, SeaSize(width, length), seed)


def _sky_placement(window_at: Any, altitude_of: Any, flight_altitude: float, margin: float) -> Any:
    """The `SkyPlacement` of the sky layers (their window and altitude callbacks)."""
    return SkyPlacement(window_at, altitude_of, flight_altitude, margin)


def tree_sight(camera_z: float, ground: GroundWindow, reach: float) -> list[float]:
    """D-212: the ground Z range where trees can be seen from the camera at ground Z `camera_z`:
    the ground in view, `reach` wider at both ends (a tree rises into the view from past them)."""
    return [camera_z + ground.z_near - reach, camera_z + ground.z_far + reach]


def row_end(z_from: float, z_end: float, cell: float) -> float:
    """D-212: where the next row of cells of a chunk ends, from ground Z `z_from`, at most `z_end`:
    the area [z_from, row_end) holds exactly one row of cell corners (`PropPlacer.trees_in`), the
    first at or after `z_from`."""
    return min(z_end, (math.ceil(z_from / cell) + 1) * cell)


def _concat(first: Any, second: Any) -> list[Any]:
    """`[...first, ...second]` (a new list; `+` on JavaScript arrays would concatenate strings)."""
    out: list[Any] = []
    for item in first:
        out.append(item)
    for item in second:
        out.append(item)
    return out
