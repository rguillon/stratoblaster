"""The model view of the enemies page (P05-R11, phase 5 review), ported from
`app/enemy-close-up.ts`: one enemy model alone on a dark background, turning, with the camera close
up on it. Drag to orbit, wheel to zoom; the arrow keys are left to the page (they switch the enemy).
In the wireframe view it draws the model's edges, the hull's in a light unlit colour, and the
enemy's hit circle."""

import math

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from config.enemy_viewer import ENEMY_VIEWER_CONFIG  # noqa: E402
from config.ship_viewer import SHIP_VIEWER_CONFIG  # noqa: E402
from render.babylon import (  # noqa: E402
    camera_fov_mode_horizontal_fixed,
    child_meshes,
    color3,
    color4,
    create_lines,
    get_hierarchy_bounding_vectors,
    new_arc_rotate_camera,
    new_directional_light,
    new_hemispheric_light,
    new_scene,
    new_standard_material,
    new_transform_node,
    node_name,
    vector3,
    vector3_up,
    vector3_zero,
)
from render.environment.showcase_environment_visual import (  # noqa: E402
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
)

CFG = ENEMY_VIEWER_CONFIG.close_up


class HitCircle:
    """A hit circle drawn in the wireframe view: its centre as an offset from the enemy's centre on
    the playfield (X right, Y up), its radius and colour (`[r, g, b]`). For a boss, one per part and
    its core."""

    def __init__(self, x: float, y: float, radius: float, color: Any) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color


def _vec(v: Any) -> Any:
    """A Babylon Vector3 from a tuple of three numbers."""
    return vector3(v[0], v[1], v[2])


def _color3(c: Any) -> Any:
    """A Babylon Color3 from a tuple of three numbers."""
    return color3(c[0], c[1], c[2])


class EnemyCloseUp:
    """The model view of the enemies page: the model turns on its pivot, the camera close up."""

    def __init__(self, engine: Any, environment: bool, glow: Any) -> None:
        look = SHIP_VIEWER_CONFIG
        self.scene = new_scene(engine)
        clear = CFG.clear_color
        self.scene.clearColor = color4(clear[0], clear[1], clear[2], clear[3])
        horizontal_fov = look.camera.horizontal_fov
        self.camera = new_arc_rotate_camera(
            "close-up-camera", CFG.alpha, CFG.beta, 1, vector3_zero(), self.scene
        )
        self.camera.fovMode = camera_fov_mode_horizontal_fixed()
        self.camera.fov = horizontal_fov
        self.camera.inputs.removeByType("ArcRotateCameraKeyboardMoveInput")
        if engine.getRenderingCanvas():
            self.camera.attachControl(True)
        lights = look.lights
        ambient = new_hemispheric_light("close-up-ambient", vector3_up(), self.scene)
        ambient.intensity = lights.ambient_intensity
        key = new_directional_light("close-up-key", _vec(lights.key_direction), self.scene)
        key.intensity = lights.key_intensity
        rim = new_directional_light("close-up-rim", _vec(lights.rim_direction), self.scene)
        rim.intensity = lights.rim_intensity
        self._glow: Any = None
        if environment:
            env: Any = look.environment
            options = ShowcaseEnvironmentOptions(
                env.cube_size,
                env.intensity,
                env.stops,
                ShowcaseGlow(glow.intensity, glow.blur_kernel_size),
            )
            self._glow = apply_showcase_environment(self.scene, options)
        self.pivot = new_transform_node("close-up-pivot", self.scene)
        self._wire = new_standard_material("close-up-wire", self.scene)
        self._wire.emissiveColor = _color3(CFG.wire_color)
        self._wire.disableLighting = True
        self._model: Any = None
        self._enemy: Any = None
        self._circles: list[HitCircle] | None = None
        self._warmed = False
        self._build: Any = None
        self._wireframe = False
        self._hitbox = False

    @property
    def hitbox(self) -> bool:
        """P16-R10: whether the hit circles are drawn over the model in the model view too."""
        return self._hitbox

    @hitbox.setter
    def hitbox(self, on: bool) -> None:
        if on == self._hitbox:
            return
        self._hitbox = on
        if self._build and self._enemy:
            self.show(self._build, self._enemy, self._circles)

    @property
    def wireframe(self) -> bool:
        return self._wireframe

    @wireframe.setter
    def wireframe(self, on: bool) -> None:
        """Switches the wireframe view on or off, building the model again for it."""
        if on == self._wireframe:
            return
        self._wireframe = on
        self.scene.forceWireframe = on
        if self._build and self._enemy:
            self.show(self._build, self._enemy, self._circles)

    def show(self, build: Any, enemy: Any, circles: list[HitCircle] | None = None) -> None:
        """Replaces the model with `build`'s, its lights fully charged, and frames it. The wireframe
        view draws `circles`; when omitted, the circles of what can be hit of the enemy (its own,
        and those of its moving parts, P05-R24), from its centre."""
        if self._model:
            self._model.root.dispose()
        self._model = build(self.scene)
        self._build = build
        self._circles = circles
        own: list[HitCircle] = []
        for t in enemy.hit_targets:
            own.append(HitCircle(t.x - enemy.x, t.y - enemy.y, t.radius, CFG.hitbox_color))
        if self._wireframe:
            self._show_wires(self._model.root)
        if self._wireframe or self._hitbox:
            self._show_circles(self._model.root, circles if circles is not None else own)
        # Measured before it joins the turning pivot, in its own axes.
        self._frame(self._model.root)
        self._model.root.parent = self.pivot
        self._enemy = enemy
        enemy.charge = 1
        self._model.sync(enemy, 0)
        if not self._warmed:
            self._warmed = True
            # Compiles the scene's shaders in the background, before it is first drawn: entering
            # the model view would otherwise stall for as long as they take.
            self.scene.whenReadyAsync()

    def _show_wires(self, root: Any) -> None:
        """Hull edges in the light wire colour, without glow."""
        for mesh in child_meshes(root, False):
            material = mesh.material
            name = node_name(material) if material else ""
            if name not in CFG.body_materials:
                continue
            mesh.material = self._wire
            mesh.useVertexColors = False
            if self._glow:
                self._glow.addExcludedMesh(mesh)

    def _show_circles(self, root: Any, circles: list[HitCircle]) -> None:
        """The hit circles around the model."""
        n = int(CFG.hitbox_segments)
        for k in range(len(circles)):
            circle = circles[k]
            # Model space: the nose (+Z) points down the screen, so the playfield's (x, y) is
            # (-x, -y).
            points: list[Any] = []
            for i in range(n + 1):
                a = 2 * math.pi * i / n
                points.append(
                    vector3(
                        -circle.x + math.sin(a) * circle.radius,
                        0,
                        -circle.y + math.cos(a) * circle.radius,
                    )
                )
            hitbox = create_lines("close-up-hitbox-" + str(k), points, self.scene)
            hitbox.color = _color3(circle.color)
            hitbox.parent = root

    def _frame(self, root: Any) -> None:
        """Puts the camera at the distance where the model fills `CFG.fill` of the screen width."""
        root.computeWorldMatrix(True)
        bounds = get_hierarchy_bounding_vectors(root)
        low = bounds.min
        high = bounds.max
        size = window.Math.max(high.x - low.x, high.z - low.z, 1)
        radius = size / 2 / CFG.fill / math.tan(self.camera.fov / 2)
        # Keeps the camera's angles (and radius, set right after) when moving its target.
        self.camera.setTarget(vector3(0, (low.y + high.y) / 2, 0), False, False, True)
        self.camera.lowerRadiusLimit = radius * CFG.zoom[0]
        self.camera.upperRadiusLimit = radius * CFG.zoom[1]
        self.camera.radius = radius
        self.camera.minZ = radius / 100

    def update(self, dt: float) -> None:
        """Turns the model and steps its animations by `dt` seconds."""
        self.pivot.rotation.y = self.pivot.rotation.y + CFG.spin_rad_per_sec * dt
        if self._model and self._enemy:
            self._model.sync(self._enemy, dt)

    def dispose(self) -> None:
        self.scene.dispose()
