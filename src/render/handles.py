"""Typed stand-ins for the Babylon.js objects the game holds (ENG-113).

Babylon objects are plain JavaScript handles at run time. These classes and aliases exist for mypy
only, so the modules of `render/` and `game/view/` can name what they hold instead of `Any`. Only
`render/babylon.py` creates them. Transcrypt skips this module: it is imported only inside skip
blocks.

A member is listed here when a module uses it.
"""

# ruff: noqa: N802, N803, N815 (Babylon's own camelCase names, ENG-113)
from __future__ import annotations

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Iterator, Sequence  # noqa: E402 (after the Transcrypt skip block, ENG-153)
from typing import Protocol, TypeVar  # noqa: E402 (after the Transcrypt skip block, ENG-153)

V = TypeVar("V")


# A plain JavaScript object built for Babylon (`js_object`, `js_set`): its fields are keyed by name.
JsObject = dict[str, object]


class Float32Array(Protocol):
    """A `Float32Array`: a fixed-length array of numbers with `set`."""

    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> float: ...

    def __setitem__(self, index: int, value: float) -> None: ...

    def __iter__(self) -> Iterator[float]: ...

    def set(self, values: Sequence[float], offset: int = 0) -> None: ...


class Uint8Array(Protocol):
    """A `Uint8Array`: a fixed-length array of bytes with `set`."""

    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> int: ...

    def __setitem__(self, index: int, value: int) -> None: ...

    def __iter__(self) -> Iterator[int]: ...

    def set(self, values: Sequence[int], offset: int = 0) -> None: ...


class Uint32Array(Protocol):
    """A `Uint32Array`: a fixed-length array of 32-bit integers with `set`."""

    def __len__(self) -> int: ...

    def __getitem__(self, index: int) -> int: ...

    def __setitem__(self, index: int, value: int) -> None: ...

    def __iter__(self) -> Iterator[int]: ...

    def set(self, values: Sequence[int], offset: int = 0) -> None: ...


class Canvas(Protocol):
    """The DOM canvas element Babylon renders into."""

    width: int
    height: int


class Vector2(Protocol):
    x: float
    y: float

    def set(self, x: float, y: float) -> Vector2: ...


class Vector3(Protocol):
    x: float
    y: float
    z: float

    def set(self, x: float, y: float, z: float) -> Vector3: ...
    def setAll(self, value: float) -> None: ...
    def normalize(self) -> Vector3: ...


class Vector4(Protocol):
    x: float
    y: float
    z: float
    w: float

    def set(self, x: float, y: float, z: float, w: float) -> Vector4: ...


class Color3(Protocol):
    r: float
    g: float
    b: float

    def set(self, r: float, g: float, b: float) -> Color3: ...
    def scale(self, factor: float) -> Color3: ...


class Color4(Protocol):
    r: float
    g: float
    b: float
    a: float

    def set(self, r: float, g: float, b: float, a: float) -> Color4: ...


class Quaternion(Protocol):
    x: float
    y: float
    z: float
    w: float


class Matrix(Protocol):
    m: list[float]

    def copyToArray(self, array: Float32Array, offset: int = 0) -> None: ...


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

    def setEnabled(self, on: bool) -> None: ...

    def isEnabled(self) -> bool: ...

    def dispose(self) -> None: ...

    parent: Node | None
    isPickable: bool
    renderingGroupId: int
    layerMask: int
    alwaysSelectAsActiveMesh: bool
    receiveShadows: bool
    isVisible: bool
    metadata: object

    def getScene(self) -> Scene: ...
    def getEngine(self) -> Engine: ...
    def getBoundingInfo(self) -> BoundingInfo: ...


class TransformNode(Node, Protocol):
    pass


class Mesh(Node, Protocol):
    material: Material | None
    visibility: float

    def bakeCurrentTransformIntoVertices(self) -> None: ...

    def updateVerticesData(self, kind: str, data: list[float] | Float32Array) -> None: ...

    alphaIndex: float
    hasVertexAlpha: bool
    zOffset: float
    normalBias: float
    thinInstanceCount: int

    def convertToFlatShadedMesh(self) -> None: ...
    def setVerticesData(
        self, kind: str, data: list[float] | Float32Array, updatable: bool = False, stride: int = 0
    ) -> None: ...
    def thinInstanceSetBuffer(
        self, kind: str, buffer: Float32Array, stride: int = 16, staticBuffer: bool = False
    ) -> None: ...
    def thinInstanceBufferUpdated(self, kind: str) -> None: ...
    def getTotalVertices(self) -> int: ...

    applyFog: bool


class Camera(Node, Protocol):
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

    def setTarget(self, target: Vector3) -> None: ...


class FreeCamera(Camera, Protocol):
    pass


class ArcRotateCamera(Camera, Protocol):
    pass


class Light(Node, Protocol):
    intensity: float
    includedOnlyMeshes: list[Mesh]
    specular: Color3


class HemisphericLight(Light, Protocol):
    pass


class DirectionalLight(Light, Protocol):
    pass


class ShadowGenerator(Protocol):
    usePercentageCloserFiltering: bool
    bias: float
    normalBias: float
    filteringQuality: int

    def setDarkness(self, darkness: float) -> None: ...

    def addShadowCaster(self, mesh: Mesh, includeDescendants: bool = False) -> None: ...


class Material(Protocol):
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

    def dispose(self) -> None: ...


class StandardMaterial(Material, Protocol):
    pass


class PBRMaterial(Material, Protocol):
    roughness: float
    metallic: float
    directIntensity: float
    environmentIntensity: float
    albedoColor: Color3
    transparencyMode: int
    bumpTexture: Texture | None


class ShaderMaterial(Material, Protocol):
    alphaMode: int
    disableDepthWrite: bool

    def setFloat(self, name: str, value: float) -> None: ...
    def setColor3(self, name: str, value: Color3) -> None: ...
    def setVector2(self, name: str, value: Vector2) -> None: ...
    def setVector3(self, name: str, value: Vector3) -> None: ...
    def setVector4(self, name: str, value: Vector4) -> None: ...
    def setTexture(self, name: str, value: Texture) -> None: ...


class MaterialPluginBase(Protocol):
    pass


class MaterialOwner(Protocol):
    """The Python object behind a material plugin: its hooks are called from Babylon."""

    def prepare_defines(self, defines: JsObject) -> None: ...

    def get_samplers(self, samplers: list[str]) -> None: ...

    def get_uniforms(self) -> JsObject: ...

    def bind_for_sub_mesh(self, ubo: object) -> None: ...

    def get_custom_code(self, shader_type: str) -> JsObject | None: ...


class Texture(Protocol):
    name: str

    def dispose(self) -> None: ...

    wrapU: int
    wrapV: int
    anisotropicFilteringLevel: int
    hasAlpha: bool
    clearColor: Color4


class RawTexture(Texture, Protocol):
    pass


class RawCubeTexture(Texture, Protocol):
    pass


class RenderTargetTexture(Texture, Protocol):
    renderList: list[Mesh]
    activeCamera: Camera | None
    clearColor: Color4


class GlowLayer(Protocol):
    intensity: float
    renderingGroupId: int


class Scene(Protocol):
    meshes: list[Mesh]
    transformNodes: list[TransformNode]
    activeCamera: Camera | None

    def getUniqueId(self) -> int: ...

    clearColor: Color4
    fogEnabled: bool

    def dispose(self) -> None: ...
    def getEngine(self) -> Engine: ...


class Observable(Protocol):
    """A Babylon observable: `add` registers a callback, `remove` takes it back."""

    def add(self, callback: Callable[..., None]) -> object: ...

    def remove(self, observer: object) -> None: ...


class BoundingBox(Protocol):
    minimumWorld: Vector3
    maximumWorld: Vector3


class BoundingInfo(Protocol):
    boundingBox: BoundingBox


class Engine(Protocol):
    def setHardwareScalingLevel(self, level: float) -> None: ...
    def getAspectRatio(self, camera: Camera) -> float: ...

    onContextLostObservable: Observable


class VertexData(Protocol):
    positions: list[float] | None
    indices: list[int] | None
    normals: list[float] | None
    colors: list[float] | None
    uvs: list[float] | None

    def applyToMesh(self, mesh: Mesh, updatable: bool = False) -> None: ...


class DrawCallCounter(Protocol):
    """Counts the draw calls of each frame (`new_draw_call_counter`)."""

    count: int

    def dispose(self) -> None: ...


class WeakMap(Protocol[V]):
    """A JavaScript `WeakMap` keyed by Babylon handles, its values of one type `V`."""

    def get(self, key: object) -> V | None: ...

    def set(self, key: object, value: V) -> None: ...


class ImageProcessingConfiguration(Protocol):
    pass
