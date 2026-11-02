# Copyright (c) 2026 Renaud Guillon
"""Typed stand-ins for the Babylon.js objects the game holds (ENG-113).

Babylon objects are plain JavaScript handles at run time. These classes and aliases exist for mypy
only, so the modules of `render/` and `game/view/` can name what they hold instead of `Any`. Only
`render/babylon.py` creates them. Transcrypt skips this module: it is imported only inside skip
blocks.

A member is listed here when a module uses it.
"""

from __future__ import annotations

# isort: split
# __pragma__ ("skip")
from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence
V = TypeVar("V")
# A plain JavaScript object built for Babylon (`js_object`, `js_set`): its fields are keyed by name.
JsObject = dict[str, object]


class Float32Array(Protocol):
    """A `Float32Array`: a fixed-length array of numbers with `set`."""

    def __len__(self) -> int:
        """Return the number of elements."""

    def __getitem__(self, index: int) -> float:
        """Return the element at `index`."""

    def __setitem__(self, index: int, value: float) -> None:
        """Set the element at `index`."""

    def __iter__(self) -> Iterator[float]:
        """Iterate over the elements."""

    def set(self, values: Sequence[float], offset: int = 0) -> None:
        """Copy `values` into the array, starting at `offset`."""


class Uint8Array(Protocol):
    """A `Uint8Array`: a fixed-length array of bytes with `set`."""

    def __len__(self) -> int:
        """Return the number of elements."""

    def __getitem__(self, index: int) -> int:
        """Return the element at `index`."""

    def __setitem__(self, index: int, value: int) -> None:
        """Set the element at `index`."""

    def __iter__(self) -> Iterator[int]:
        """Iterate over the elements."""

    def set(self, values: Sequence[int], offset: int = 0) -> None:
        """Copy `values` into the array, starting at `offset`."""


class Uint32Array(Protocol):
    """A `Uint32Array`: a fixed-length array of 32-bit integers with `set`."""

    def __len__(self) -> int:
        """Return the number of elements."""

    def __getitem__(self, index: int) -> int:
        """Return the element at `index`."""

    def __setitem__(self, index: int, value: int) -> None:
        """Set the element at `index`."""

    def __iter__(self) -> Iterator[int]:
        """Iterate over the elements."""

    def set(self, values: Sequence[int], offset: int = 0) -> None:
        """Copy `values` into the array, starting at `offset`."""


class Canvas(Protocol):
    """The DOM canvas element Babylon renders into."""

    width: int
    height: int


class Vector2(Protocol):
    """A Babylon `Vector2`: two components."""

    x: float
    y: float

    def set(self, x: float, y: float) -> Vector2:
        """Set the two components and return the vector."""


class Vector3(Protocol):
    """A Babylon `Vector3`: three components."""

    x: float
    y: float
    z: float

    def set(self, x: float, y: float, z: float) -> Vector3:
        """Set the three components and return the vector."""

    def setAll(self, value: float) -> None:
        """Set all three components to `value`."""

    def normalize(self) -> Vector3:
        """Normalize the vector in place and return it."""

    def copyFrom(self, source: Vector3) -> Vector3:
        """Copy the components of `source` into this vector and return it."""


class Vector4(Protocol):
    """A Babylon `Vector4`: four components."""

    x: float
    y: float
    z: float
    w: float

    def set(self, x: float, y: float, z: float, w: float) -> Vector4:
        """Set the four components and return the vector."""


class Color3(Protocol):
    """A Babylon `Color3`: an RGB color."""

    r: float
    g: float
    b: float

    def set(self, r: float, g: float, b: float) -> Color3:
        """Set the three channels and return the color."""

    def scale(self, factor: float) -> Color3:
        """Return the color multiplied by `factor`."""


class Color4(Protocol):
    """A Babylon `Color4`: an RGBA color."""

    r: float
    g: float
    b: float
    a: float

    def set(self, r: float, g: float, b: float, a: float) -> Color4:
        """Set the four channels and return the color."""


class Quaternion(Protocol):
    """A Babylon `Quaternion`: a rotation."""

    x: float
    y: float
    z: float
    w: float


class Matrix(Protocol):
    """A Babylon `Matrix`: a 4x4 transform, `m` in row order."""

    m: list[float]

    def copyToArray(self, array: Float32Array, offset: int = 0) -> None:
        """Copy the matrix values into `array`, starting at `offset`."""


class BoundingVectors(Protocol):
    """`getHierarchyBoundingVectors`: the corners of a node's bounding box."""

    min: Vector3
    max: Vector3


class Named(Protocol):
    """Anything with a Babylon `name`: a node, a material, a texture."""

    name: str


class Node(Named, Protocol):
    """Anything in the scene graph: a mesh, a transform node, a camera or a light."""

    name: str
    position: Vector3
    rotation: Vector3
    scaling: Vector3
    uniqueId: int

    def setEnabled(self, on: bool) -> None:
        """Show or hide the node, with its descendants."""

    def isEnabled(self) -> bool:
        """Whether the node is enabled."""

    def dispose(self) -> None:
        """Releases the node and its resources."""

    parent: Node | None
    isPickable: bool
    renderingGroupId: int
    layerMask: int
    alwaysSelectAsActiveMesh: bool
    receiveShadows: bool
    isVisible: bool
    metadata: object

    def getScene(self) -> Scene:
        """Return the scene the node belongs to."""

    def getEngine(self) -> Engine:
        """Return the engine the node belongs to."""

    def getBoundingInfo(self) -> BoundingInfo:
        """Return the bounding information of the node."""


class TransformNode(Node, Protocol):
    """A node that only moves its children (no geometry)."""


class Mesh(Node, Protocol):
    """A Babylon `Mesh`: a node with geometry."""

    material: Material | None
    visibility: float

    def bakeCurrentTransformIntoVertices(self) -> None:
        """Bakes the current transform into the vertex data."""

    def updateVerticesData(self, kind: str, data: list[float] | Float32Array) -> None:
        """Replace the vertex data of `kind`."""

    alphaIndex: float
    hasVertexAlpha: bool
    zOffset: float
    normalBias: float
    thinInstanceCount: int

    def convertToFlatShadedMesh(self) -> None:
        """Convert the mesh to flat shading (unshared vertices)."""

    def setVerticesData(
        self, kind: str, data: list[float] | Float32Array, updatable: bool = False, stride: int = 0
    ) -> None:
        """Set the vertex data of `kind`."""

    def thinInstanceSetBuffer(
        self, kind: str, buffer: Float32Array, stride: int = 16, staticBuffer: bool = False
    ) -> None:
        """Set the thin instance buffer of `kind`."""

    def thinInstanceBufferUpdated(self, kind: str) -> None:
        """Tells Babylon that the thin instance buffer of `kind` changed."""

    def getTotalVertices(self) -> int:
        """Return the number of vertices of the mesh."""

    applyFog: bool


class Camera(Node, Protocol):
    """A Babylon camera: its position is set through `alpha`, `beta` and `radius`."""

    radius: float
    alpha: float
    beta: float
    minZ: float
    maxZ: float
    fov: float
    fovMode: int
    layerMask: int
    orthoLeft: float
    orthoRight: float
    orthoTop: float
    orthoBottom: float
    mode: int
    targetScreenOffset: Vector2
    includedOnlyMeshes: list[Mesh]
    renderList: list[Mesh]

    def setTarget(self, target: Vector3) -> None:
        """Points the camera at `target`."""


class FreeCamera(Camera, Protocol):
    """A camera that moves freely."""


class ArcRotateCamera(Camera, Protocol):
    """A camera orbiting a target."""


class Light(Node, Protocol):
    """A Babylon light."""

    intensity: float
    includedOnlyMeshes: list[Mesh]
    specular: Color3


class HemisphericLight(Light, Protocol):
    """A light from the sky direction."""


class DirectionalLight(Light, Protocol):
    """A light from a direction, like the sun."""


class ShadowGenerator(Protocol):
    """Renders the shadows of the casters it was given."""

    usePercentageCloserFiltering: bool
    bias: float
    normalBias: float
    filteringQuality: int

    def setDarkness(self, darkness: float) -> None:
        """Set how dark the shadows are."""

    def addShadowCaster(self, mesh: Mesh, includeDescendants: bool = False) -> None:
        """Add `mesh` to the meshes casting shadows."""


class Material(Protocol):
    """A Babylon material."""

    name: str
    alpha: float
    backFaceCulling: bool
    alphaMode: int
    alphaIndex: float
    disableDepthWrite: bool
    disableLighting: bool
    disableColorWrite: bool
    depthFunction: int
    hasAlpha: bool
    fogEnabled: bool
    zOffset: float
    diffuseColor: Color3
    specularColor: Color3
    emissiveColor: Color3
    diffuseTexture: Texture | None
    useAlphaFromDiffuseTexture: bool

    def dispose(self) -> None:
        """Releases the material."""


class StandardMaterial(Material, Protocol):
    """A standard (Blinn-Phong) material."""


class PBRMaterial(Material, Protocol):
    """A physically based material."""

    roughness: float
    metallic: float
    directIntensity: float
    environmentIntensity: float
    albedoColor: Color3
    transparencyMode: int
    bumpTexture: Texture | None


class ShaderMaterial(Material, Protocol):
    """A material with a custom shader."""

    alphaMode: int
    disableDepthWrite: bool

    def setFloat(self, name: str, value: float) -> None:
        """Set the float uniform `name`."""

    def setColor3(self, name: str, value: Color3) -> None:
        """Set the color uniform `name`."""

    def setVector2(self, name: str, value: Vector2) -> None:
        """Set the 2D vector uniform `name`."""

    def setVector3(self, name: str, value: Vector3) -> None:
        """Set the 3D vector uniform `name`."""

    def setVector4(self, name: str, value: Vector4) -> None:
        """Set the 4D vector uniform `name`."""

    def setTexture(self, name: str, value: Texture) -> None:
        """Set the texture uniform `name`."""


class MaterialPluginBase(Protocol):
    """The base class of a material plugin."""


class MaterialOwner(Protocol):
    """The Python object behind a material plugin: its hooks are called from Babylon."""

    def prepare_defines(self, defines: JsObject) -> None:
        """Add the shader defines of the material to `defines`."""

    def get_samplers(self, samplers: list[str]) -> None:
        """Add the sampler names of the material to `samplers`."""

    def get_uniforms(self) -> JsObject:
        """Return the uniform names of the material."""

    def bind_for_sub_mesh(self, ubo: object) -> None:
        """Binds the material's uniforms for one sub-mesh."""

    def get_custom_code(self, shader_type: str) -> JsObject | None:
        """Return the custom shader code for `shader_type`, if any."""


class Texture(Protocol):
    """A Babylon texture."""

    name: str

    def dispose(self) -> None:
        """Releases the texture."""

    wrapU: int
    wrapV: int
    anisotropicFilteringLevel: int
    hasAlpha: bool
    clearColor: Color4


class RawTexture(Texture, Protocol):
    """A texture made from raw pixels."""


class RawCubeTexture(Texture, Protocol):
    """A cube texture made from raw pixels."""


class RenderTargetTexture(Texture, Protocol):
    """A texture rendered to by the scene (for example a shadow map)."""

    renderList: list[Mesh]
    activeCamera: Camera | None
    clearColor: Color4


class GlowLayer(Protocol):
    """The glow layer, which blurs the emissive parts of the scene."""

    intensity: float
    renderingGroupId: int


class Scene(Protocol):
    """A Babylon scene."""

    meshes: list[Mesh]
    transformNodes: list[TransformNode]
    activeCamera: Camera | None

    def getUniqueId(self) -> int:
        """Return a new unique id for the scene."""

    clearColor: Color4
    fogEnabled: bool

    def dispose(self) -> None:
        """Releases the scene."""

    def getEngine(self) -> Engine:
        """Return the engine the scene runs on."""


class Observable(Protocol):
    """A Babylon observable: `add` registers a callback, `remove` takes it back."""

    def add(self, callback: Callable[..., None]) -> object:
        """Register `callback`; return the observer to remove it with."""

    def remove(self, observer: object) -> None:
        """Remove the observer `observer`."""


class BoundingBox(Protocol):
    """The world-space corners of a bounding box."""

    minimumWorld: Vector3
    maximumWorld: Vector3


class BoundingInfo(Protocol):
    """The bounding information of a node."""

    boundingBox: BoundingBox


class Engine(Protocol):
    """The rendering engine."""

    def setHardwareScalingLevel(self, level: float) -> None:
        """Set the hardware scaling level (1 is full resolution)."""

    def getAspectRatio(self, camera: Camera) -> float:
        """Return the aspect ratio of `camera`'s viewport."""

    onContextLostObservable: Observable


class VertexData(Protocol):
    """The vertex arrays of a mesh."""

    positions: list[float] | None
    indices: list[int] | None
    normals: list[float] | None
    colors: list[float] | None
    uvs: list[float] | None

    def applyToMesh(self, mesh: Mesh, updatable: bool = False) -> None:
        """Apply this vertex data to `mesh`."""


class DrawCallCounter(Protocol):
    """Counts the draw calls of each frame (`new_draw_call_counter`)."""

    count: int

    def dispose(self) -> None:
        """Stop counting."""


class WeakMap(Protocol[V]):
    """A JavaScript `WeakMap` keyed by Babylon handles, its values of one type `V`."""

    def get(self, key: object) -> V | None:
        """Return the value stored for `key`, or None."""

    def set(self, key: object, value: V) -> None:
        """Store `value` for `key`."""


class ImageProcessingConfiguration(Protocol):
    """The image processing settings of a scene."""


# __pragma__ ("noskip")
