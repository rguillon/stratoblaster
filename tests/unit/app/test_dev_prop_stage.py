# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_prop_stage.py`: the props viewer's stage (D-205, DEV-MENU-16).

The prop alone on a floor ruled in blocks, and the camera turning round it.
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import FakeLight, FakeNode, FakeScene, FakeVector, patch_babylon

from app import dev_prop_stage
from app.dev_catalog import DevItem
from app.dev_prop_stage import (
    DEFAULT_BLOCK,
    DevPropStage,
    block_centre,
    blocks_of,
    close_up_distance,
    game_distance,
)
from config.dev_viewer import DEV_VIEWER_CONFIG
from config.game_play import GAME_PLAY_CONFIG


def test_d205_a_footprint_covers_whole_blocks_at_least_one() -> None:
    """DEV-MENU-16."""
    assert blocks_of(0, 10) == 1
    assert blocks_of(10, 10) == 1
    assert blocks_of(10.000000001, 10) == 1
    assert blocks_of(10.5, 10) == 2
    assert blocks_of(30, 10) == 3


def test_d205_an_even_footprint_is_centred_on_a_line_an_odd_one_in_a_square() -> None:
    assert block_centre(2, 10) == 0
    assert block_centre(1, 10) == 5
    assert block_centre(3, 10) == 5


def test_d205_the_game_distance_is_the_cameras_down_its_view_in_ground_units() -> None:
    """DEV-MENU-17."""
    camera = SimpleNamespace(tiltDeg=0.0, fovDeg=60.0, flightAltitude=100.0, groundScale=2.0)
    game = SimpleNamespace(
        screen=SimpleNamespace(width=480, height=720),
        view=SimpleNamespace(scenery=SimpleNamespace(camera=camera)),
    )
    # Straight down: the playfield fills the view, from 720 / (2 tan 30°) above the flight plane.
    height = 100 + 720 / (2 * math.tan(math.pi / 6))
    assert game_distance(game) == pytest.approx(height / 2)


def test_d205_a_close_up_fills_its_share_of_the_screen() -> None:
    """DEV-MENU-09."""
    fov = math.pi / 2
    distance = close_up_distance(10, fov, 0.5)
    assert 10 / (2 * distance * math.tan(fov / 2)) == pytest.approx(0.5)


# The stage itself: Babylon is the `render_fakes` helpers, with the stage's camera, floor, grid and
# meshes recorded here; the props' geometry, materials and looks are fakes too.


class FakeScaling:
    def __init__(self) -> None:
        self.all: float | None = None

    def setAll(self, value: float) -> None:
        self.all = value


class PropNode(FakeNode):
    """A node of the stage: the fields `render_fakes` nodes have, and the scaling."""

    def __init__(self, name: str, unique_id: float, is_mesh: bool) -> None:
        super().__init__(name, unique_id, is_mesh)
        self.scaling = FakeScaling()
        self.isPickable = True
        self.size: tuple[float, float] | None = None
        self.geometry: Any = None
        self.lines: list[Any] = []
        self.colors: list[Any] = []


class StageScene(FakeScene):
    """The stage's scene: its nodes are `PropNode`s; its engine gives the view's aspect ratio."""

    def __init__(self) -> None:
        super().__init__()
        self.clearColor: Any = None
        self.disposed = False
        self.aspect = 1.5

    def add_node(self, name: str = "", is_mesh: bool = False) -> FakeNode:
        node = PropNode(name, self.next_id(), is_mesh)
        node.scene = self
        (self.meshes if is_mesh else self.transformNodes).append(node)
        return node

    def getEngine(self) -> Any:
        return SimpleNamespace(getAspectRatio=lambda _camera: self.aspect)

    def dispose(self) -> None:
        self.disposed = True


class ArcCamera:
    def __init__(
        self, label: str, alpha: float, beta: float, radius: float, target: Any, scene: Any
    ) -> None:
        self.label = label
        self.alpha = alpha
        self.beta = beta
        self.radius = radius
        self.target = target
        self.scene = scene
        self.targetScreenOffset = FakeVector()

    def setTarget(self, target: Any) -> None:
        self.target = target


class GlowLayer:
    def __init__(self) -> None:
        self.own_material: list[Any] = []

    def referenceMeshToUseItsOwnMaterial(self, mesh: Any) -> None:
        self.own_material.append(mesh)


class Render:
    """What the stage asks of the render layer and of the game, recorded."""

    def __init__(self) -> None:
        self.scenes: list[StageScene] = []
        self.lights: list[FakeLight] = []
        self.environments: list[Any] = []
        self.glows: list[GlowLayer] = []
        self.materials: list[tuple[Any, Any]] = []
        self.window_materials = True
        self.levels: list[str] = []

    def new_scene(self, engine: str) -> StageScene:
        assert engine == "engine"
        scene = StageScene()
        self.scenes.append(scene)
        return scene

    def light(self, label: str, direction: Any, _scene: Any) -> FakeLight:
        light = FakeLight(label, direction)
        self.lights.append(light)
        return light

    def apply_showcase_environment(self, _scene: Any, options: Any) -> GlowLayer:
        self.environments.append(options)
        glow = GlowLayer()
        self.glows.append(glow)
        return glow

    def level_of(self, _game: Any, level_id: str) -> Any:
        self.levels.append(level_id)
        return SimpleNamespace(scenery=SimpleNamespace(id=level_id))

    def create_prop_materials(self, scene: Any, look: Any) -> Any:
        self.materials.append((scene, look))
        return SimpleNamespace(
            structure="structure-material", lights="lights-material", windows=None
        )

    def add_window_material(self, materials: Any, _scene: Any, _look: Any) -> None:
        # Only a look with a window atlas has windows (D-210).
        if self.window_materials:
            materials.windows = "windows-material"


def _ground(label: str, width: float, depth: float, scene: StageScene) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.size = (width, depth)
    return node


def _lines(label: str, lines: list[Any], colors: list[Any], scene: StageScene) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.lines = lines
    node.colors = colors
    return node


def _mesh_of(label: str, geometry: Any, material: Any, scene: StageScene) -> FakeNode:
    node = scene.add_node(label, is_mesh=True)
    node.geometry = geometry
    node.material = material
    node.enabled = False
    return node


@pytest.fixture
def render(monkeypatch: pytest.MonkeyPatch) -> Render:
    patch_babylon(monkeypatch, dev_prop_stage)
    fake = Render()
    for name, value in {
        "new_scene": fake.new_scene,
        "new_hemispheric_light": fake.light,
        "new_directional_light": fake.light,
        "apply_showcase_environment": fake.apply_showcase_environment,
        "new_arc_rotate_camera": ArcCamera,
        "new_standard_material": lambda label, _scene: SimpleNamespace(label=label),
        "create_ground_sized": _ground,
        "create_colored_line_system": _lines,
        "mesh_of": _mesh_of,
        "prop_bounds": lambda factory: factory.bounds,
        "prop_geometry": lambda factory: factory.geometry,
        "level_of": fake.level_of,
        "scenery_look": lambda _game, scenery: "look-of-" + scenery.id,
        "create_prop_materials": fake.create_prop_materials,
        "add_window_material": fake.add_window_material,
    }.items():
        monkeypatch.setattr(dev_prop_stage, name, value)
    return fake


class FakeScenery:
    """`game.view.scenery`: its camera by attribute, its prop models and tiles by key."""

    def __init__(self, fields: dict[str, Any]) -> None:
        self.camera = SimpleNamespace(
            tiltDeg=0.0, fovDeg=60.0, flightAltitude=100.0, groundScale=2.0
        )
        self._fields = fields

    def __contains__(self, key: str) -> bool:
        return key in self._fields

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]


def _geometry(indices: list[int]) -> SimpleNamespace:
    return SimpleNamespace(indices=indices)


TOWER = SimpleNamespace(
    # 12 across, 30 high, 8 along.
    bounds=[-6, 0, -4, 6, 30, 4],
    geometry=SimpleNamespace(
        structure=_geometry([0, 1, 2]), lights=_geometry([]), windows=_geometry([3, 4, 5])
    ),
)
CAR = SimpleNamespace(
    bounds=[-6, 0, -4, 6, 4, 4],
    geometry=SimpleNamespace(structure=_geometry([0, 1, 2]), lights=None, windows=None),
)


def make_stage_game(tiles: Any = "8") -> SimpleNamespace:
    fields: dict[str, Any] = {"propModels": {"tower": TOWER, "car": CAR}}
    if tiles == "8":
        fields["propTiles"] = {"tile": SimpleNamespace(size=8)}
    elif tiles is None:
        fields["propTiles"] = None
    return SimpleNamespace(
        screen=SimpleNamespace(width=480, height=720),
        view=SimpleNamespace(scenery=FakeScenery(fields)),
    )


PROPS = DEV_VIEWER_CONFIG.props
FOV = math.pi / 3
DISTANCE = (100 + 720 / (2 * math.tan(math.pi / 6))) / 2


def test_d205_the_stage_has_studio_lights_and_the_game_s_camera(render: Render) -> None:
    """DEV-MENU-16, DEV-MENU-17 (the game's distance and field of view)."""
    stage = DevPropStage("engine", make_stage_game(), False)
    (scene,) = render.scenes
    assert stage.scene is scene
    assert scene.clearColor.values == tuple(PROPS.clear_color)
    ambient, key, fill = render.lights
    assert (ambient.direction.y, ambient.intensity) == (1, PROPS.ambient_intensity)
    assert ambient.specular.values == (0, 0, 0)
    assert (key.direction.x, key.intensity) == (PROPS.key_direction[0], PROPS.key_intensity)
    assert (fill.direction.z, fill.intensity) == (PROPS.fill_direction[2], PROPS.fill_intensity)
    assert render.environments == []
    camera = stage.camera
    assert (camera.alpha, camera.beta) == (-math.pi / 2, PROPS.pitch)
    assert camera.radius == pytest.approx(DISTANCE)
    assert camera.fov == pytest.approx(FOV)
    assert (camera.minZ, camera.maxZ) == (0.5, pytest.approx(DISTANCE * 20))
    assert (stage.size, stage.target) == (0.0, [0.0, 0.0, 0.0])


@pytest.mark.parametrize(("tiles", "block"), [("8", 8), (None, DEFAULT_BLOCK), ("", DEFAULT_BLOCK)])
def test_d205_a_block_is_the_game_s_tile_or_the_default_without_one(
    render: Render, tiles: Any, block: float
) -> None:
    del render
    assert DevPropStage("engine", make_stage_game(tiles), False).block == block


def test_d210_with_the_environment_the_stage_has_its_lighting_and_glow(render: Render) -> None:
    DevPropStage("engine", make_stage_game(), True)
    (options,) = render.environments
    assert options.cube_size == int(GAME_PLAY_CONFIG.environment_cube_size)
    assert options.intensity == PROPS.environment_intensity
    stops = [(stop.at, stop.color) for stop in options.stops]
    assert stops == [(s[0], [s[1], s[2], s[3]]) for s in PROPS.environment_stops]
    glow = options.glow
    assert (glow.intensity, glow.blur_kernel_size) == (PROPS.glow[0], PROPS.glow[1])


def _named(scene: StageScene, prefix: str) -> list[Any]:
    return [mesh for mesh in scene.meshes if mesh.name.startswith(prefix)]


def test_d205_a_prop_stands_on_whole_squares_of_a_floor_ruled_round_it(render: Render) -> None:
    """DEV-MENU-16; D-210 (the windows, without glow here)."""
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("tower", "Tower", "1-2"))
    scene = render.scenes[0]
    # 12 across: 2 blocks of 8, centred on a line; 8 along: 1 block, centred in its square.
    (root,) = [node for node in scene.transformNodes if node.name == "dev-prop-tower"]
    assert _xyz(root.position) == (0, 0, 4)
    assert root.scaling.all == 1
    # No lights in this prop: its structure and its windows.
    meshes = _named(scene, "dev-prop-tower")
    assert [(m.material, m.parent, m.enabled) for m in meshes] == [
        ("structure-material", root, True),
        ("windows-material", root, True),
    ]
    assert (stage.size, stage.target) == (30, [0, 15, 4])
    # 2 blocks across: 1 + 1 + the grid's reach each way.
    half = 1 + 1 + PROPS.grid_reach
    (ground,) = _named(scene, "dev-props-ground")
    assert ground.size == (2 * half * 8, 2 * half * 8)
    assert ground.isPickable is False
    assert ground.material.label == "dev-props-ground"
    (grid,) = _named(scene, "dev-props-grid")
    assert len(grid.lines) == len(grid.colors) == 2 * (2 * half + 1)
    first = grid.lines[0]
    assert [_xyz(p) for p in first] == [
        (-half * 8, PROPS.grid_lift, -half * 8),
        (-half * 8, PROPS.grid_lift, half * 8),
    ]
    assert grid.colors[0][0].values == (*PROPS.grid_color, 1)
    assert ground.parent is grid.parent
    assert grid.isPickable is False


def test_d209_a_prop_is_drawn_at_its_scale_in_game(render: Render) -> None:
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("car", "Car", "1-1", "cars", 0.5))
    scene = render.scenes[0]
    (root,) = [node for node in scene.transformNodes if node.name == "dev-prop-car"]
    # Half size: 6 across and 4 along, one block each, centred in its square.
    assert _xyz(root.position) == (4, 0, 4)
    assert root.scaling.all == 0.5
    assert [m.material for m in _named(scene, "dev-prop-car")] == ["structure-material"]
    assert (stage.size, stage.target) == (6, [4, 1, 4])


@pytest.mark.parametrize(("environment", "glowing"), [(True, 1), (False, 0)])
def test_d210_only_the_windows_glow_with_their_own_material(
    render: Render, environment: bool, glowing: int
) -> None:
    stage = DevPropStage("engine", make_stage_game(), environment)
    stage.show(DevItem("tower", "Tower", "1-2"))
    windows = _named(render.scenes[0], "dev-prop-tower")[1]
    assert [g.own_material for g in render.glows] == [[windows]] * glowing


def test_d210_a_look_without_window_atlas_draws_no_windows(render: Render) -> None:
    render.window_materials = False
    stage = DevPropStage("engine", make_stage_game(), True)
    stage.show(DevItem("tower", "Tower", "1-2"))
    meshes = _named(render.scenes[0], "dev-prop-tower")
    assert [m.material for m in meshes] == ["structure-material"]
    assert render.glows[0].own_material == []


def test_d205_the_materials_of_a_level_s_look_are_made_once(render: Render) -> None:
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("tower", "Tower", "1-2"))
    stage.show(DevItem("car", "Car", "1-2"))
    stage.show(DevItem("tower", "Tower", "2-1"))
    scene = render.scenes[0]
    assert render.materials == [(scene, "look-of-1-2"), (scene, "look-of-2-1")]
    assert render.levels == ["1-2", "2-1"]


def test_d205_showing_another_prop_drops_the_last_one_and_its_floor(render: Render) -> None:
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("tower", "Tower", "1-2"))
    scene = render.scenes[0]
    (tower,) = [node for node in scene.transformNodes if node.name == "dev-prop-tower"]
    (floor,) = [node for node in scene.transformNodes if node.name == "dev-props-floor"]
    stage.show(DevItem("missing", "Missing", "1-2"))
    assert (tower.disposed, floor.disposed) == (True, True)
    # A prop without a model shows nothing.
    assert stage.size == 0
    assert [node.name for node in scene.transformNodes if not node.disposed] == []


def test_d205_disposing_the_stage_releases_the_prop_its_floor_and_the_scene(
    render: Render,
) -> None:
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("tower", "Tower", "1-2"))
    stage.dispose()
    scene = render.scenes[0]
    assert all(node.disposed for node in scene.transformNodes)
    assert scene.disposed is True
    assert stage.size == 0


def test_dev_menu_17_the_camera_turns_round_the_prop_at_the_game_s_distance(
    render: Render,
) -> None:
    """Also DEV-MENU-11 and D-208 (the wheel's zoom), D-206 (drawn right of the middle)."""
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.show(DevItem("tower", "Tower", "1-2"))
    stage.update([0.3, 0.2], False, 2)
    camera = stage.camera
    assert camera.alpha == pytest.approx(-math.pi / 2 - 0.3)
    assert camera.beta == pytest.approx(PROPS.pitch - 0.2)
    assert camera.radius == pytest.approx(DISTANCE / 2)
    assert _xyz(camera.target) == (0, 15, 4)
    shift = PROPS.view_shift * (DISTANCE / 2) * math.tan(FOV / 2) * render.scenes[0].aspect
    assert camera.targetScreenOffset.x == pytest.approx(shift)


@pytest.mark.parametrize(("up", "pitch"), [(5, PROPS.pitch_range[0]), (-5, PROPS.pitch_range[1])])
def test_dev_menu_17_the_camera_s_pitch_stays_in_its_range(
    render: Render, up: float, pitch: float
) -> None:
    del render
    stage = DevPropStage("engine", make_stage_game(), False)
    stage.update([0, up], False, 1)
    assert stage.camera.beta == pitch


def test_dev_menu_09_the_close_up_fills_its_share_of_the_screen_with_the_prop(
    render: Render,
) -> None:
    del render
    stage = DevPropStage("engine", make_stage_game(), False)
    # Nothing shown: the close-up keeps the game's distance.
    stage.update([0, 0], True, 1)
    assert stage.camera.radius == pytest.approx(DISTANCE)
    stage.show(DevItem("tower", "Tower", "1-2"))
    stage.update([0, 0], True, 1)
    assert stage.camera.radius == pytest.approx(
        close_up_distance(30, FOV, DEV_VIEWER_CONFIG.close_up_fill)
    )


def _xyz(vector: Any) -> tuple[float, float, float]:
    return (vector.x, vector.y, vector.z)
