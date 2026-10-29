"""The props viewer page (`props/`, reviewer 2026-10-28), ported from `app/start-prop-viewer.ts`.

The prop models of one group laid out on the grid of tiles of a plain ground (with road tiles
around the models made for the grid), a turning camera, and a panel to pick the group and a prop,
which the camera then centres on."""

import math

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.prop_viewer_ground import ViewerTiles, build_viewer_ground  # noqa: E402
from app.prop_viewer_layout import tile_layout  # noqa: E402
from app.prop_viewer_roads import ViewerRoads  # noqa: E402
from config.prop_viewer import PROP_VIEWER_CONFIG as CFG  # noqa: E402
from render.babylon import (  # noqa: E402
    color3,
    color3_black,
    color4,
    new_arc_rotate_camera,
    new_directional_light,
    new_hemispheric_light,
    new_scene,
    new_standard_material,
    new_transform_node,
    vector3,
    vector3_up,
    vector3_zero,
)
from render.environment.showcase_environment_visual import (  # noqa: E402
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
)
from render.game_view import PropGroup  # noqa: E402
from render.scenery.prop_field import mesh_of  # noqa: E402
from ui.prop_viewer_panel import (  # noqa: E402
    PropViewerPanel,
    PropViewerPanelOptions,
    PropViewerSelection,
)

# Steps to the prop beside the picked one, by arrow key.
_STEP_KEYS = {"ArrowRight": 1, "ArrowLeft": -1}


class PropViewerOptions:
    """Options of `start_prop_viewer`.

    `environment`: procedural image-based lighting and glow (needs a real WebGL engine). `doc` and
    `panel_parent`: where the controls go. `keyboard_target`: where the arrow keys are listened to
    (None: none). `render_loop`: runs the engine's render loop (off in e2e tests, which render on
    demand)."""

    def __init__(
        self,
        environment: bool,
        doc: Any,
        panel_parent: Any,
        keyboard_target: Any,
        render_loop: bool,
    ) -> None:
        self.environment = environment
        self.doc = doc
        self.panel_parent = panel_parent
        self.keyboard_target = keyboard_target
        self.render_loop = render_loop


class ShownProp:
    """One prop laid out on the grid: its `id`, its `root` node, its `triangles`, and its `size`
    ([width X, depth Z, height])."""

    def __init__(self, id: str, root: Any, triangles: float, size: list[float]) -> None:
        self.id = id
        self.root = root
        self.triangles = triangles
        self.size = size


def _extent(geo: Any) -> list[float]:
    """Extent of `geo` along each axis: [min x, max x, max y, min z, max z]."""
    e = [0.0, 0.0, 0.0, 0.0, 0.0]
    positions = geo.positions
    for i in range(0, len(positions), 3):
        x = positions[i] if i < len(positions) else 0
        y = positions[i + 1] if i + 1 < len(positions) else 0
        z = positions[i + 2] if i + 2 < len(positions) else 0
        e[0] = window.Math.min(e[0], x)
        e[1] = window.Math.max(e[1], x)
        e[2] = window.Math.max(e[2], y)
        e[3] = window.Math.min(e[3], z)
        e[4] = window.Math.max(e[4], z)
    return e


def _materials(scene: Any) -> list[Any]:
    """The structure's and the lights' materials, as [structure, lights]."""
    structure = new_standard_material("prop-structure", scene)
    structure.diffuseColor = color3(1, 1, 1)
    structure.specularColor = color3(0.1, 0.1, 0.1)
    lights = new_standard_material("prop-lights", scene)
    intensity = CFG.light_intensity
    lights.emissiveColor = color3(intensity, intensity, intensity)
    lights.diffuseColor = color3_black()
    lights.specularColor = color3_black()
    lights.disableLighting = True
    return [structure, lights]


def _add_lights(scene: Any) -> None:
    lights = CFG.lights
    ambient = new_hemispheric_light("props-ambient", vector3_up(), scene)
    ambient.intensity = lights.ambient_intensity
    key_d = lights.key_direction
    key = new_directional_light("props-key", vector3(key_d[0], key_d[1], key_d[2]), scene)
    key.intensity = lights.key_intensity
    fill_d = lights.fill_direction
    fill = new_directional_light("props-fill", vector3(fill_d[0], fill_d[1], fill_d[2]), scene)
    fill.intensity = lights.fill_intensity


def _max_of(values: list[float]) -> float:
    best = float("-Infinity")
    for value in values:
        best = max(best, value)
    return best


def _min_of(values: list[float]) -> float:
    best = float("Infinity")
    for value in values:
        best = min(best, value)
    return best


class PropGrid:
    """The props of one group, each on whole tiles of the grid of the ground (phase 15)."""

    def __init__(self, scene: Any, models: Any, tiles: Any) -> None:
        self.scene = scene
        self._models = models
        self._tiles = tiles
        self.props: list[ShownProp] = []
        # Index of the group shown; -1 before the first.
        self.group = -1
        self._materials = _materials(scene)
        self._roads: Any = None
        if tiles.look:
            self._roads = ViewerRoads(scene, tiles.tile, tiles.look)
        self._ground: Any = None

    def show(self, group: Any, index: int) -> None:
        """Shows the props of `group` (index `index`) in place of the ones shown."""
        for p in self.props:
            p.root.dispose()
        if self._ground:
            self._ground.dispose()
        ids = group.ids if group else []
        built: list[list[Any]] = []
        for prop_id in ids:
            built.extend(self._build(prop_id))
        t = self._tiles.tile.size

        def tiles_of(v: float) -> Any:
            return max(1, math.ceil(v / t - 1e-6))

        streets = bool(group) and bool(group.streets) and bool(self._tiles.look)
        footprints = [[tiles_of(b[0].size[0]), tiles_of(b[0].size[1])] for b in built]
        gap = 1 if streets else math.ceil(CFG.gap / t)
        layout = tile_layout(footprints, gap, streets)
        for i in range(len(built)):
            prop = built[i][0]
            mid = built[i][1]
            centre = layout.centres[i] if i < len(layout.centres) else [0, 0]
            prop.root.position.set(centre[0] * t - mid[0], 0, centre[1] * t - mid[1])
        self.props = [b[0] for b in built]
        self._ground = build_viewer_ground(self.scene, layout, self._tiles, self._roads)
        self.group = index

    def _build(self, prop_id: str) -> list[list[Any]]:
        """The prop `prop_id`, as [prop, middle of its footprint in its own frame] (none when it has
        no model)."""
        pieces = self._tiles.pieces.get(prop_id) if self._tiles.pieces else None
        if pieces and self._roads:
            return self._build_road(prop_id, pieces, self._roads)
        factory = self._models.get(prop_id)
        if not factory:
            return []
        geometry = factory()
        root = new_transform_node("prop-" + prop_id, self.scene)
        parts = [
            [geometry.structure, self._materials[0]],
            [geometry.lights, self._materials[1]],
        ]
        for part in parts:
            geo = part[0]
            if not geo or len(geo.indices) == 0:
                continue
            mesh = mesh_of(prop_id, geo, part[1], self.scene)
            mesh.parent = root
            mesh.isPickable = True
            mesh.setEnabled(True)
        extent = _extent(geometry.structure)
        x0, x1, height, z0, z1 = extent[0], extent[1], extent[2], extent[3], extent[4]
        light_indices = len(geometry.lights.indices) if geometry.lights else 0
        triangles = (len(geometry.structure.indices) + light_indices) / 3
        prop = ShownProp(prop_id, root, triangles, [x1 - x0, z1 - z0, height])
        return [[prop, [(x0 + x1) / 2, (z0 + z1) / 2]]]

    def _build_road(self, prop_id: str, pieces: list[Any], roads: Any) -> list[list[Any]]:
        """A model of the road kit, drawn as the levels draw their roads: textured pieces."""
        root = new_transform_node("prop-" + prop_id, self.scene)
        mesh = roads.mesh(prop_id, pieces)
        if mesh:
            mesh.parent = root
            mesh.isPickable = True
        t = self._tiles.tile.size
        x0 = _min_of([p.x for p in pieces]) * t
        x1 = _max_of([p.x + p.size for p in pieces]) * t
        z0 = _min_of([p.z for p in pieces]) * t
        z1 = _max_of([p.z + p.size for p in pieces]) * t
        triangles = (mesh.getTotalIndices() if mesh else 0) / 3
        prop = ShownProp(prop_id, root, triangles, [x1 - x0, z1 - z0, 0])
        return [[prop, [(x0 + x1) / 2, (z0 + z1) / 2]]]


def _create_camera(scene: Any) -> Any:
    alpha, beta, fov = CFG.camera.alpha, CFG.camera.beta, CFG.camera.fov
    camera = new_arc_rotate_camera("props-camera", alpha, beta, 100, vector3_zero(), scene)
    camera.fov = fov
    camera.minZ = 0.5
    camera.maxZ = 5000
    camera.wheelDeltaPercentage = 0.01
    if scene.getEngine().getRenderingCanvas():
        camera.attachControl(True)
    return camera


def describe(prop: ShownProp) -> str:
    """The readout of `prop`: its id, size and triangle count."""
    w = str(math.floor(prop.size[0] + 0.5))
    d = str(math.floor(prop.size[1] + 0.5))
    h = str(math.floor(prop.size[2] + 0.5))
    return prop.id + " — " + w + " × " + d + " × " + h + " — " + str(prop.triangles) + " triangles"


def _frame(camera: Any, prop: ShownProp) -> str:
    """Centres `camera` on `prop` and returns its readout."""
    w = prop.size[0]
    d = prop.size[1]
    h = prop.size[2]
    camera.setTarget(prop.root.position.add(vector3(0, h / 2, 0)))
    largest = window.Math.max(w, d, h, 1)
    camera.radius = (largest * CFG.camera.framing_margin) / math.tan(camera.fov / 2)
    return describe(prop)


def _listen_picks(scene: Any, grid: PropGrid, panel: Any, select: Any, keys: Any) -> None:
    """Picks a prop on a click on the scene, or the next or previous one with the arrow keys."""

    def on_pointer_down(_event: Any, pick: Any) -> None:
        picked = pick.pickedMesh.parent if pick.pickedMesh else None
        index = -1
        for i in range(len(grid.props)):
            if grid.props[i].root is picked and index < 0:
                index = i
        if index >= 0:
            select(PropViewerSelection(grid.group, index))

    scene.onPointerDown = on_pointer_down

    def on_key(event: Any) -> None:
        step = _STEP_KEYS.get(event.key, 0)
        count = len(grid.props)
        if step == 0 or count == 0:
            return
        select(PropViewerSelection(grid.group, (panel.selection.prop + step + count) % count))

    if keys:
        keys.addEventListener("keydown", on_key)


class RunningPropViewer:
    """Handle on a running props viewer: `scene`, `camera`, `panel`, `groups`, the shown `props`,
    `select(selection)` and `dispose()`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        scene: Any,
        camera: Any,
        panel: Any,
        groups: list[Any],
        grid: PropGrid,
        select: Any,
    ) -> None:
        self._engine = engine
        self.scene = scene
        self.camera = camera
        self.panel = panel
        self.groups = groups
        self._grid = grid
        self._select = select

    @property
    def props(self) -> list[ShownProp]:
        """The props of the shown group."""
        return self._grid.props

    def select(self, selection: PropViewerSelection) -> None:
        self._select(selection)

    def dispose(self) -> None:
        self._engine.stopRenderLoop()
        self.panel.root.remove()
        self.scene.dispose()


def start_prop_viewer(engine: Any, game: Any, options: PropViewerOptions) -> RunningPropViewer:
    """Starts the props viewer page: the prop models of one group, laid out on the grid of tiles, a
    turning camera, and a panel to pick the group and a prop."""
    prop_models = game.view.scenery.prop_models
    groups = game.view.scenery.prop_groups or [PropGroup("Props", list(prop_models.keys()))]
    scene = new_scene(engine)
    clear = CFG.clear_color
    scene.clearColor = color4(clear[0], clear[1], clear[2], clear[3])
    _add_lights(scene)
    if options.environment:
        env: Any = CFG.environment
        glow: Any = CFG.glow
        apply_showcase_environment(
            scene,
            ShowcaseEnvironmentOptions(
                env.cube_size,
                env.intensity,
                env.stops,
                ShowcaseGlow(glow.intensity, glow.blur_kernel_size),
            ),
        )
    camera = _create_camera(scene)
    tiles = game.view.scenery.prop_tiles
    if not tiles:
        tiles = ViewerTiles(CFG.tile, None, None)
    grid = PropGrid(scene, prop_models, tiles)

    def select(selection: PropViewerSelection) -> None:
        if selection.group != grid.group and 0 <= selection.group < len(groups):
            grid.show(groups[selection.group], selection.group)
        panel.update(selection)
        if 0 <= selection.prop < len(grid.props):
            panel.set_readout(_frame(camera, grid.props[selection.prop]))

    def on_wireframe(wireframe: bool) -> None:
        scene.forceWireframe = wireframe

    panel = PropViewerPanel(
        PropViewerPanelOptions(
            options.doc,
            options.panel_parent,
            groups,
            PropViewerSelection(0, 0),
            select,
            on_wireframe,
        )
    )
    select(panel.selection)
    _listen_picks(scene, grid, panel, select, options.keyboard_target)
    if options.render_loop:

        def render_frame() -> None:
            scene.render()

        engine.runRenderLoop(render_frame)
    return RunningPropViewer(engine, scene, camera, panel, groups, grid, select)
