"""The props viewer's stage (D-205): the prop picked alone on a plain floor ruled in blocks (one
square per tile of the game's grid), under studio lights, with no level's ground loaded. The
camera turns round the prop as dragged; it is either at the game's distance with the game's field
of view (the prop as big as in game) or close enough for the prop to fill the close-up's share of
the screen. The prop's materials are those of the first level that has it (its world's tone).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from app.level_prepare import level_of
from app.level_scene import scenery_look
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG
from config.game_play import GAME_PLAY_CONFIG
from render.babylon import (
    color3,
    color3_black,
    color4,
    create_colored_line_system,
    create_ground_sized,
    dispose_node,
    new_arc_rotate_camera,
    new_directional_light,
    new_hemispheric_light,
    new_scene,
    new_standard_material,
    new_transform_node,
    set_enabled,
    vector3,
    vector3_up,
    vector3_zero,
)
from render.environment.gradient_cube import GradientStop
from render.environment.showcase_environment_visual import (
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
)
from render.scenery.playfield_framing import frame_playfield
from render.scenery.prop_field import mesh_of, prop_bounds, prop_geometry
from render.scenery.scenery_kit import create_prop_materials

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from app.dev_catalog import DevItem  # noqa: E402

__pragma__("noskip")

# The size of a block when the game names no grid of tiles (ground units).
DEFAULT_BLOCK = 10.0
# What a footprint may pass a whole number of blocks by and still count as that number.
BLOCK_SLACK = 1e-6


def blocks_of(length: float, block: float) -> int:
    """How many blocks a footprint `length` long covers (at least one)."""
    return max(1, int(math.ceil(length / block - BLOCK_SLACK)))


def block_centre(blocks: int, block: float) -> float:
    """Where a footprint of `blocks` blocks is centred so it covers whole squares of the grid:
    on a line of the grid for an even number, in the middle of a square for an odd one."""
    return (blocks % 2) * block / 2


def game_distance(game: Any) -> float:
    """How far the game's camera is from the ground it looks at, in ground units: a prop that far,
    seen with the game's field of view, is as big as in game."""
    look = game.view.scenery.camera
    framing = frame_playfield(game.screen, look)
    scale = look.groundScale if look.groundScale is not None else 1
    height = look.flightAltitude + framing.height
    distance: float = height / math.cos(framing.tilt) / scale
    return distance


def close_up_distance(size: float, fov: float, fill: float) -> float:
    """How far something `size` across is when it fills `fill` of the screen's height, seen with
    the vertical field of view `fov`."""
    return size / (2 * math.tan(fov / 2) * fill)


def _block_size(game: Any) -> float:
    scenery = game.view.scenery
    if "propTiles" not in scenery or scenery["propTiles"] is None:
        return DEFAULT_BLOCK
    size: float = scenery["propTiles"]["tile"].size
    return size


class DevPropStage:
    """See the module doc. `show(item)` puts the prop of `item` on the floor; `update(turn,
    close_up)` places the camera."""

    def __init__(self, engine: Any, game: Any, environment: bool) -> None:
        props = CFG.props
        self._game = game
        scene = new_scene(engine)
        c = props.clear_color
        scene.clearColor = color4(c[0], c[1], c[2], c[3])
        ambient = new_hemispheric_light("dev-props-ambient", vector3_up(), scene)
        ambient.intensity = props.ambient_intensity
        ambient.specular = color3_black()
        key = props.key_direction
        light = new_directional_light("dev-props-key", vector3(key[0], key[1], key[2]), scene)
        light.intensity = props.key_intensity
        fill = props.fill_direction
        light = new_directional_light("dev-props-fill", vector3(fill[0], fill[1], fill[2]), scene)
        light.intensity = props.fill_intensity
        if environment:
            stops = [GradientStop(s[0], [s[1], s[2], s[3]]) for s in props.environment_stops]
            apply_showcase_environment(
                scene,
                ShowcaseEnvironmentOptions(
                    int(GAME_PLAY_CONFIG.environment_cube_size),
                    props.environment_intensity,
                    stops,
                    ShowcaseGlow(props.glow[0], props.glow[1]),
                ),
            )
        self.scene = scene
        self.block = _block_size(game)
        self._distance = game_distance(game)
        self._fov = frame_playfield(game.screen, game.view.scenery.camera).half_fov * 2
        self.camera = new_arc_rotate_camera(
            "dev-props-camera", -math.pi / 2, props.pitch, self._distance, vector3_zero(), scene
        )
        self.camera.fov = self._fov
        self.camera.minZ = 0.5
        self.camera.maxZ = self._distance * 20
        # The prop's materials, by the level whose look they have, and the floor's.
        self._materials: dict[str, Any] = {}
        self._floor_material = new_standard_material("dev-props-ground", scene)
        f = props.floor_color
        self._floor_material.diffuseColor = color3(f[0], f[1], f[2])
        self._floor_material.specularColor = color3_black()
        self._prop: Any = None
        self._floor: Any = None
        # The largest side of the prop shown, and the point the camera turns round.
        self.size = 0.0
        self.target = [0.0, 0.0, 0.0]

    def show(self, item: DevItem) -> None:
        """Puts the prop of `item` on the middle of the floor, its footprint on whole squares,
        and rules the floor round it."""
        self._drop()
        factory = self._game.view.scenery["propModels"].get(item.id)
        if factory is None:
            return
        b = prop_bounds(factory)
        block = self.block
        across = blocks_of(b[3] - b[0], block)
        along = blocks_of(b[5] - b[2], block)
        x = block_centre(across, block)
        z = block_centre(along, block)
        root = new_transform_node("dev-prop-" + item.id, self.scene)
        root.position.set(x - (b[0] + b[3]) / 2, 0, z - (b[2] + b[5]) / 2)
        materials = self._materials_of(item.host)
        geometry = prop_geometry(factory)
        parts = [[geometry.structure, materials.structure], [geometry.lights, materials.lights]]
        for part in parts:
            geo = part[0]
            if geo is None or len(geo.indices) == 0:
                continue
            mesh = mesh_of("dev-prop-" + item.id, geo, part[1], self.scene)
            mesh.parent = root
            set_enabled(mesh, True)
        self._prop = root
        self.size = max(b[3] - b[0], b[4] - b[1], b[5] - b[2])
        self.target = [x, max(0, b[4]) / 2, z]
        reach = int(CFG.props.grid_reach)
        self._floor = self._rule_floor(max(across, along) // 2 + 1 + reach)

    def update(self, turn: list[float], close_up: bool) -> None:
        """Turns the camera round the prop as far as dragged (`turn`: radians across and up or
        down, as Babylon's own orbiting camera turns), at the close-up's distance or the game's."""
        props = CFG.props
        camera = self.camera
        camera.alpha = -math.pi / 2 - turn[0]
        low = props.pitch_range[0]
        high = props.pitch_range[1]
        camera.beta = max(low, min(high, props.pitch - turn[1]))
        camera.radius = self._distance
        if close_up and self.size > 0:
            camera.radius = close_up_distance(self.size, self._fov, CFG.close_up_fill)
        t = self.target
        camera.setTarget(vector3(t[0], t[1], t[2]))

    def _materials_of(self, level_id: str) -> Any:
        materials = self._materials.get(level_id)
        if materials is None:
            look = scenery_look(self._game, level_of(self._game, level_id).scenery)
            materials = create_prop_materials(self.scene, look)
            self._materials[level_id] = materials
        return materials

    def _rule_floor(self, half: int) -> Any:
        """A floor `half` blocks each way from the middle, ruled with a line on every block's
        edge."""
        props = CFG.props
        block = self.block
        extent = half * block
        root = new_transform_node("dev-props-floor", self.scene)
        floor = create_ground_sized("dev-props-ground", 2 * extent, 2 * extent, self.scene)
        floor.material = self._floor_material
        floor.isPickable = False
        floor.parent = root
        y = props.grid_lift
        g = props.grid_color
        lines: list[list[Any]] = []
        colors: list[list[Any]] = []
        for k in range(-half, half + 1):
            at = k * block
            lines.append([vector3(at, y, -extent), vector3(at, y, extent)])
            lines.append([vector3(-extent, y, at), vector3(extent, y, at)])
            for _ in range(2):
                colors.append([color4(g[0], g[1], g[2], 1), color4(g[0], g[1], g[2], 1)])
        grid = create_colored_line_system("dev-props-grid", lines, colors, self.scene)
        grid.isPickable = False
        grid.parent = root
        return root

    def _drop(self) -> None:
        if self._prop is not None:
            dispose_node(self._prop)
        if self._floor is not None:
            dispose_node(self._floor)
        self._prop = None
        self._floor = None
        self.size = 0.0

    def dispose(self) -> None:
        self._drop()
        self.scene.dispose()
