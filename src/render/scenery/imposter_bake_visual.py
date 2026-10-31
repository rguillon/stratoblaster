"""The imposters' bake (D-211): every frame of every model drawn once into an atlas (a render target
texture) by an orthographic camera looking the way the playfield camera does, then the material
that shows them. Needs a WebGL engine. See `imposters.py` for the layout.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    apply_vertex_data,
    babylon_class,
    color3,
    color3_black,
    color4,
    new_free_camera,
    new_mesh,
    new_standard_material,
    new_vertex_data,
    vector3,
)
from render.scenery.imposters import atlas_size, bake_geometry, view_axes

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402

__pragma__("noskip")

# The layer only the bake camera sees (the scene's cameras see 0x0FFFFFFF).
BAKE_LAYER = 0x10000000
# Where the bake happens, far out of every view.
BAKE_AT = [0, -20000, 0]
# How far the bake camera stands from the frames.
BAKE_DISTANCE = 500
# How much brighter the imposters are drawn than the props' structure.
BRIGHTER = 1.3
# Frames the bake mesh must be ready for before the bake is done (its texture drawn).
READY_FRAMES = 2


def _render_target(label: str, size: list[int], scene: Any) -> Any:  # noqa: ANN401
    """`new RenderTargetTexture(label, {width, height}, scene, generateMipMaps)`."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RenderTargetTexture(label, {width: size[0], height: size[1]}, scene,"
        " true);",
    )
    return None


def _remove(array: Any, value: Any) -> None:  # noqa: ANN401
    """Removes `value` from the JavaScript array `array` (not named `items`: Transcrypt renames
    that, and the JavaScript below would miss it)."""
    __pragma__("js", "{}", "const i = array.indexOf(value); if (i >= 0) array.splice(i, 1);")


def _bake_mesh(scene: Any, geometry: ColoredGeometry) -> Any:  # noqa: ANN401
    """The frames' mesh, drawn unlit in its baked colours, seen by the bake camera only."""
    mesh = new_mesh("imposter-bake", scene)
    data = new_vertex_data()
    data.positions = geometry.positions
    data.indices = geometry.indices
    data.colors = geometry.colors
    apply_vertex_data(data, mesh)
    mesh.position = vector3(BAKE_AT[0], BAKE_AT[1], BAKE_AT[2])
    mesh.layerMask = BAKE_LAYER
    mesh.isPickable = False
    material = new_standard_material("imposter-bake", scene)
    material.disableLighting = True
    material.emissiveColor = color3(1, 1, 1)
    material.diffuseColor = color3_black()
    material.specularColor = color3_black()
    material.fogEnabled = False
    material.backFaceCulling = True
    mesh.material = material
    return mesh


def _bake_camera(scene: Any, look: Any, size: list[int], tilt: float) -> Any:  # noqa: ANN401
    """The orthographic camera that sees the frames as the playfield camera would, one frame per
    `look.frameSize` across."""
    axes = view_axes(tilt)
    towards = axes[2]
    d = BAKE_DISTANCE
    camera = new_free_camera(
        "imposter-bake-camera",
        vector3(
            BAKE_AT[0] + towards[0] * d, BAKE_AT[1] + towards[1] * d, BAKE_AT[2] + towards[2] * d
        ),
        scene,
    )
    camera.setTarget(vector3(BAKE_AT[0], BAKE_AT[1], BAKE_AT[2]))
    camera.mode = babylon_class("Camera").ORTHOGRAPHIC_CAMERA
    half_width = size[0] / look.framePx * look.frameSize / 2
    half_height = size[1] / look.framePx * look.frameSize / 2
    camera.orthoLeft = -half_width
    camera.orthoRight = half_width
    camera.orthoBottom = -half_height
    camera.orthoTop = half_height
    camera.minZ = 1
    camera.maxZ = d * 2
    camera.layerMask = BAKE_LAYER
    return camera


def _imposter_material(scene: Any, texture: Any, tone: float) -> Any:  # noqa: ANN401
    """The material of the imposters' quads: the atlas, cut out by its alpha, lit by the scene."""
    material = new_standard_material("imposters", scene)
    material.diffuseTexture = texture
    # A little brighter than the props: lit by one normal, a car has no face turned to the sun.
    bright = tone * BRIGHTER
    material.diffuseColor = color3(bright, bright, bright)
    material.specularColor = color3_black()
    # Drawn from either side; lit by their own normals (up, see `ImposterField`), whichever side
    # shows.
    material.backFaceCulling = False
    return material


class ImposterAtlas:
    """The atlas of `kinds` kinds of model, and the material that shows it (`material`). Its
    frames are drawn by `bake`, over the next frames drawn; `baked` turns true once done. `tone`:
    how bright the scene keeps its props (the structure's diffuse)."""

    def __init__(
        self,
        scene: Any,  # noqa: ANN401
        look: Any,  # noqa: ANN401 (a config record)
        kinds: int,
        tone: float,
    ) -> None:
        self.look = look
        self._scene = scene
        self._size = atlas_size(look, kinds)
        texture = _render_target("imposter-atlas", self._size, scene)
        texture.clearColor = color4(0, 0, 0, 0)
        texture.hasAlpha = True
        texture.wrapU = babylon_class("Texture").CLAMP_ADDRESSMODE
        texture.wrapV = babylon_class("Texture").CLAMP_ADDRESSMODE
        self.texture = texture
        self.material = _imposter_material(scene, texture, tone)
        self.baked = False

    def bake(self, models: list[ColoredGeometry], tilt: float) -> None:
        """Draws every frame of `models` (by kind) into the atlas as the camera tilted by `tilt`
        sees them. Makes a mesh and a camera, gone once the bake is done."""
        scene = self._scene
        texture = self.texture
        mesh = _bake_mesh(scene, bake_geometry(models, self.look, tilt))
        camera = _bake_camera(scene, self.look, self._size, tilt)
        texture.activeCamera = camera
        texture.renderList = [mesh]
        scene.customRenderTargets.append(texture)
        ready = [0]
        observer: list[Any] = []

        def after_render() -> None:
            if not mesh.isReady(True):
                return
            ready[0] += 1
            if ready[0] < READY_FRAMES:
                return
            # Drawn with the mesh ready: stop drawing it, and drop what drew it.
            _remove(scene.customRenderTargets, texture)
            scene.onAfterRenderObservable.remove(observer[0])
            texture.renderList = []
            texture.activeCamera = None
            mesh.material.dispose()
            mesh.dispose()
            camera.dispose()
            self.baked = True

        observer.append(scene.onAfterRenderObservable.add(after_render))
