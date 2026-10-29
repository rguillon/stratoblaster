"""The ground of a scrolling level seen by the tilted playfield camera (P04), ported from
`render/scenery/scenery-stage.ts`: sculpted terrain in chunks, an optional sea, cloud layers and
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
from render.scenery.level_ground import level_ground
from render.scenery.playfield_framing import (
    GroundWindow,
    PlayfieldFraming,
    frame_playfield,
    visible_ground,
)
from render.scenery.plume_layer import plume_light
from render.scenery.prop_field import PropField, level_prop_models, prop_drifts
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

# Infinity, as the TypeScript's `Infinity`.
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


class SceneryStage:
    """The ground of a scrolling level seen by the tilted playfield camera (P04): sculpted terrain
    in chunks, an optional sea, cloud layers and props, lit by a low sun. `update` moves everything
    to a distance along the level."""

    def __init__(self, scene: Any, options: SceneryStageOptions) -> None:
        self.scene = scene
        self.options = options
        self._time = 0.0
        self._with_runout = False
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
        self.camera = stage_camera(scene, self.framing.half_fov, config.far_clip)
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
        self._chunks = self._ground_root.adopt(self._build_chunks)
        self._roads = RoadLayers(scene, self.kit.roads)
        if options.atmosphere is not None and options.atmosphere.tile_grid:
            self._roads.show_tile_grid()
        self._props = self._ground_root.adopt(lambda: self._build_props(models))
        prop_models = options.prop_models
        self._traffic = self._ground_root.adopt(
            lambda: TrafficLayer(scene, prop_models, _props_of(self.kit), level.props.cars),
        )
        water = self._ground_root.adopt(
            lambda: sea_parts(scene, level, [self._x_half * 2, sea_length], self.kit),
        )
        self._sea = water.sea if water is not None else None
        self._rings: RainRings | None = water.rings if water is not None else None
        self._sea_enabled = self._sea is not None
        self._terrain = TerrainWatch()
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

        def rebuild() -> None:
            self._chunks.rebuild(self._field)
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
        ground.adopt(lambda: self._cover(z_min, z_max))
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
        z_high = min(z_max, z_far)
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
        for span in changes.added:
            self._place_chunk(span.index)

    def _take_runout(self) -> None:
        """Once the runout's streets and buildings come (generated after the rest, reviewer
        2026-10-28), places again the chunks they show in."""
        placed = self._placer.runout_placed
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
        self._roads.set_chunk(index, roads, self._field, span, self.options.look.roads, tiles)
        area = GroundArea(-self._x_half, self._x_half, span.z_min, span.z_max)
        self._props.set_chunk(index, self._placer.place(area))

    def _build_props(self, models: Any) -> PropField:
        """The props of the level, of `models`, casting shadows."""
        kit = self.kit

        def shadow(mesh: Any) -> None:
            kit.add_shadow_caster(mesh)

        return PropField(self.scene, models, _props_of(kit), shadow, kit.plume)

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


def _concat(first: Any, second: Any) -> list[Any]:
    """`[...first, ...second]` (a new list; `+` on JavaScript arrays would concatenate strings)."""
    out: list[Any] = []
    for item in first:
        out.append(item)
    for item in second:
        out.append(item)
    return out
