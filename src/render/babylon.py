# Copyright (c) 2026 Renaud Guillon
"""The only place that touches the Babylon.js global (ENG-02, ENG-113, D-169).

Babylon is the UMD build vendored under `public/vendor/` (`make vendor`), the game's only rendering
library (ENG-103): it sets the global `BABYLON`. Every other module of `render/` builds its objects
through the functions below, and the rest of the game reaches the engine only through `render/`.
Objects are returned as plain JavaScript handles, typed with the stand-ins of `render/handles.py`;
their methods and properties are used by attribute access.

Rules that come from Transcrypt (see `01-engineering.md` §13): - Babylon names that are Python
keywords or special to Transcrypt (`name`, `from`...) are read and written in raw JavaScript,
through the helpers below (ENG-156). - Constructor calls and builder calls with option objects are
raw JavaScript (`new BABYLON.X`), because a Python dict is not a JavaScript object and keyword
arguments are dropped (ENG-151, ENG-158). - Optional options are passed as `None` and left out of
the JavaScript object.
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any, cast

from render.handles import (
    ArcRotateCamera,
    BoundingVectors,
    Canvas,
    Color3,
    Color4,
    DirectionalLight,
    DrawCallCounter,
    Engine,
    Float32Array,
    FreeCamera,
    GlowLayer,
    HemisphericLight,
    JsObject,
    Light,
    Material,
    MaterialOwner,
    MaterialPluginBase,
    Matrix,
    Mesh,
    Named,
    Node,
    PBRMaterial,
    Quaternion,
    RawCubeTexture,
    RawTexture,
    RenderTargetTexture,
    Scene,
    ShaderMaterial,
    ShadowGenerator,
    StandardMaterial,
    Texture,
    TransformNode,
    Uint8Array,
    Uint32Array,
    V,
    Vector2,
    Vector3,
    Vector4,
    VertexData,
    WeakMap,
)

# __pragma__ ("noskip")


def babylon_class(class_name: str) -> Any:
    """Return the Babylon class (or namespace) called `class_name`, e.g. `Camera`."""
    __pragma__("js", "{}", "return BABYLON[class_name];")
    return None


def babylon_constant(key: str) -> int:
    """Return a value of `BABYLON.Constants`, e.g. `ALPHA_ADD` or `TEXTUREFORMAT_RGBA`."""
    __pragma__("js", "{}", "return BABYLON.Constants[key];")
    return cast("int", None)


# -- Math ----------------------------------------------------------------------------------------


def vector2(x: float, y: float) -> Vector2:
    """Return a `new BABYLON.Vector2(x, y)`."""
    __pragma__("js", "{}", "return new BABYLON.Vector2(x, y);")
    return cast("Vector2", None)


def vector3(x: float, y: float, z: float) -> Vector3:
    """Return a `new BABYLON.Vector3(x, y, z)`."""
    __pragma__("js", "{}", "return new BABYLON.Vector3(x, y, z);")
    return cast("Vector3", None)


def vector4(x: float, y: float, z: float, w: float) -> Vector4:
    """Return a `new BABYLON.Vector4(x, y, z, w)`."""
    __pragma__("js", "{}", "return new BABYLON.Vector4(x, y, z, w);")
    return cast("Vector4", None)


def vector3_up() -> Vector3:
    """`Vector3.Up()`: (0, 1, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Up();")
    return cast("Vector3", None)


def color3(r: float, g: float, b: float) -> Color3:
    """Return a `new BABYLON.Color3(r, g, b)`."""
    __pragma__("js", "{}", "return new BABYLON.Color3(r, g, b);")
    return cast("Color3", None)


def color3_black() -> Color3:
    """`BABYLON.Color3.Black()`."""
    __pragma__("js", "{}", "return BABYLON.Color3.Black();")
    return cast("Color3", None)


def color4(r: float, g: float, b: float, a: float) -> Color4:
    """Return a `new BABYLON.Color4(r, g, b, a)`."""
    __pragma__("js", "{}", "return new BABYLON.Color4(r, g, b, a);")
    return cast("Color4", None)


def quaternion(x: float, y: float, z: float, w: float) -> Quaternion:
    """Return a `new BABYLON.Quaternion(x, y, z, w)`."""
    __pragma__("js", "{}", "return new BABYLON.Quaternion(x, y, z, w);")
    return cast("Quaternion", None)


# -- Nodes, names and scene ----------------------------------------------------------------------


def node_name(node: Named) -> str:
    """`node.name` (a Python attribute of this name would be renamed by Transcrypt)."""
    __pragma__("js", "{}", "return node.name;")
    return ""


def new_transform_node(label: str, scene: Scene) -> TransformNode:
    """Return a `new BABYLON.TransformNode(label, scene)`."""
    __pragma__("js", "{}", "return new BABYLON.TransformNode(label, scene);")
    return cast("TransformNode", None)


def get_hierarchy_bounding_vectors(node: Node) -> BoundingVectors:
    """`node.getHierarchyBoundingVectors(true)`: the `{min, max}` Vector3 handles."""
    __pragma__("js", "{}", "return node.getHierarchyBoundingVectors(true);")
    return cast("BoundingVectors", None)


def new_engine(canvas: Canvas, antialias: bool) -> Engine:
    """Return a new Babylon `Engine` on `canvas`, as in the TS.

    It is `new Engine(canvas, antialias, {adaptToDeviceRatio: false, stencil: true})`. Always WebGL:
    no WebGPU backend (ENG-08, MAY, not implemented).
    """
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.Engine(canvas, antialias, {adaptToDeviceRatio: false, stencil: true});",
    )
    return cast("Engine", None)


def new_scene(engine: Engine) -> Scene:
    """Return `new Scene(engine)`."""
    __pragma__("js", "{}", "return new BABYLON.Scene(engine);")
    return cast("Scene", None)


def new_mesh(label: str, scene: Scene) -> Mesh:
    """Return a `new BABYLON.Mesh(label, scene)`."""
    __pragma__("js", "{}", "return new BABYLON.Mesh(label, scene);")
    return cast("Mesh", None)


def set_enabled(node: Node, on: bool) -> None:
    """`node.setEnabled(on)`."""
    node.setEnabled(on)


def is_enabled(node: Node) -> bool:
    """Whether `node` is enabled."""
    return bool(node.isEnabled())


def dispose_node(node: Node) -> None:
    """Disposes `node`."""
    node.dispose()


def child_meshes(node: Node, direct_only: bool) -> list[Mesh]:
    """`node.getChildMeshes(directOnly)`: a fresh array (safe to push into)."""
    __pragma__("js", "{}", "return node.getChildMeshes(direct_only);")
    return []


def descendants(node: Node, direct_only: bool) -> list[Node]:
    """`node.getDescendants(directOnly)`."""
    __pragma__("js", "{}", "return node.getDescendants(direct_only);")
    return []


def unique_id(node: Node) -> float:
    """`node.uniqueId`: Babylon numbers nodes from one counter, in creation order."""
    __pragma__("js", "{}", "return node.uniqueId;")
    return 0


def scene_unique_id(scene: Scene) -> float:
    """Return the unique id of `scene`, as a number."""
    return float(scene.getUniqueId())


def scene_meshes(scene: Scene) -> list[Mesh]:
    """Return the meshes of `scene` (the live Babylon array)."""
    __pragma__("js", "{}", "return scene.meshes;")
    return []


def scene_transform_nodes(scene: Scene) -> list[TransformNode]:
    """Return the transform nodes of `scene` (the live Babylon array)."""
    __pragma__("js", "{}", "return scene.transformNodes;")
    return []


# -- Draw calls (ENG-106) ------------------------------------------------------------------------


def new_draw_call_counter(scene: Scene) -> DrawCallCounter:
    """Count the draw calls of each frame of `scene`, as Babylon's own `DrawCallsStrategy` does.

    The engine's draw-call counter is restarted before the animations and read after the render.

    Returns an object whose `count` is the last frame's draw calls (0 before the first frame) and
    whose `dispose()` removes the two observers. The scene's dispose removes them too.
    """
    __pragma__(
        "js",
        "{}",
        "var engine = scene.getEngine();"
        "var counter = { count: 0 };"
        "var before = scene.onBeforeAnimationsObservable.add(function () {"
        "engine._drawCalls.fetchNewFrame();"
        "});"
        "var after = scene.onAfterRenderObservable.add(function () {"
        "counter.count = engine._drawCalls.current;"
        "});"
        "counter.dispose = function () {"
        "scene.onBeforeAnimationsObservable.remove(before);"
        "scene.onAfterRenderObservable.remove(after);"
        "};"
        "return counter;",
    )
    return cast("DrawCallCounter", None)


def draw_calls_last_frame(counter: DrawCallCounter) -> float:
    """Return the draw calls of the last frame rendered, as counted by `new_draw_call_counter`."""
    return float(counter.count)


# -- Typed arrays (for textures and buffers) -----------------------------------------------------


def block_material_marks(scene: Scene, block: bool) -> bool:
    """Set whether Babylon re-marks a material's meshes each time one of its properties is set.

    That is a scan of the whole scene per set.

    Materials made and set before any mesh uses them need no marks: block them while they are built
    (PERF-31). Returns the previous setting, to put back.

    The scene's setter, when it is set back to false, marks every material dirty (a scan of all of
    them), so the backing field is written instead: the vendored Babylon is pinned (D-173).
    """
    __pragma__(
        "js",
        "{}",
        """
    var was = scene._blockMaterialDirtyMechanism;
    scene._blockMaterialDirtyMechanism = block;
    return was;
    """,
    )
    return False


def uint8_array(length: int) -> Uint8Array:
    """Return a zero-filled `Uint8Array` of `length` bytes."""
    __pragma__("js", "{}", "return new Uint8Array(length);")
    return cast("Uint8Array", None)


# -- Vertex data and meshes ----------------------------------------------------------------------


def new_vertex_data() -> VertexData:
    """Return a new, empty `VertexData`."""
    __pragma__("js", "{}", "return new BABYLON.VertexData();")
    return cast("VertexData", None)


def compute_normals(positions: list[float], indices: list[int]) -> list[float]:
    """`VertexData.ComputeNormals(positions, indices, normals)`: returns the normals array."""
    normals: list[float] = []
    __pragma__("js", "{}", "BABYLON.VertexData.ComputeNormals(positions, indices, normals);")
    return normals


def vertex_data_of(
    positions: list[float],
    indices: list[int],
    normals: list[float] | None = None,
    colors: list[float] | None = None,
    uvs: list[float] | None = None,
) -> VertexData:
    """Return a `VertexData` with the given arrays set (the ones left as None are not set)."""
    data = new_vertex_data()
    data.positions = positions
    data.indices = indices
    if normals is not None:
        data.normals = normals
    if colors is not None:
        data.colors = colors
    if uvs is not None:
        data.uvs = uvs
    return data


def mesh_positions(mesh: Mesh) -> list[float]:
    """`mesh.getVerticesData("position")` as a plain array (empty when it has none)."""
    __pragma__(
        "js",
        "{}",
        'var p = mesh.getVerticesData("position"); return p ? Array.from(p) : [];',
    )
    return []


def mesh_indices(mesh: Mesh) -> list[int]:
    """`mesh.getIndices()` as a plain array (empty when it has none)."""
    __pragma__("js", "{}", "var i = mesh.getIndices(); return i ? Array.from(i) : [];")
    return []


def world_matrix(node: Node) -> list[float]:
    """Return the 16 numbers of `node`'s world matrix, computed afresh from its parents down."""
    __pragma__(
        "js",
        "{}",
        """
    var chain = [];
    for (var n = node; n; n = n.parent) chain.unshift(n);
    for (var k = 0; k < chain.length; k++) chain[k].computeWorldMatrix(true);
    return Array.from(node.getWorldMatrix().m);
    """,
    )
    return []


def apply_vertex_data(data: VertexData, mesh: Mesh) -> None:
    """`data.applyToMesh(mesh)`."""
    data.applyToMesh(mesh)


def create_torus(
    label: str, diameter: float, thickness: float, tessellation: int, scene: Scene
) -> Mesh:
    """Return a torus mesh (`BABYLON.CreateTorus`)."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateTorus(label, {diameter: diameter, thickness: thickness, "
        "tessellation: tessellation}, scene);",
    )
    return cast("Mesh", None)


def create_colored_line_system(
    label: str, lines: list[list[Vector3]], colors: list[list[Color4]], scene: Scene
) -> Mesh:
    """Return a line system with a Color4 handle per vertex: `colors` mirrors `lines`."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateLineSystem(label, {lines: lines, colors: colors}, scene);",
    )
    return cast("Mesh", None)


def create_lathe(label: str, shape: list[Vector3], tessellation: int, scene: Scene) -> Mesh:
    """Return a lathe around Y of the Vector3 `shape` (x = radius, y = height)."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateLathe(label, {shape: shape, tessellation: tessellation}, scene);",
    )
    return cast("Mesh", None)


def create_ground(label: str, width: float, height: float, subdivisions: int, scene: Scene) -> Mesh:
    """Return a flat ground mesh (`BABYLON.CreateGround`)."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateGround(label, {width: width, height: height, "
        "subdivisions: subdivisions}, scene);",
    )
    return cast("Mesh", None)


def create_box(label: str, options: JsObject, scene: Scene) -> Mesh:
    """`CreateBox(label, options, scene)`, whose `options` has width, height and depth."""
    __pragma__("js", "{}", "return BABYLON.CreateBox(label, options, scene);")
    return cast("Mesh", None)


def create_cylinder(label: str, options: JsObject, scene: Scene) -> Mesh:
    """`CreateCylinder(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreateCylinder(label, options, scene);")
    return cast("Mesh", None)


def create_polyhedron(label: str, options: JsObject, scene: Scene) -> Mesh:
    """`CreatePolyhedron(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreatePolyhedron(label, options, scene);")
    return cast("Mesh", None)


def create_disc(label: str, options: JsObject, scene: Scene) -> Mesh:
    """`CreateDisc(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreateDisc(label, options, scene);")
    return cast("Mesh", None)


def bake_transform(mesh: Mesh) -> None:
    """`mesh.bakeCurrentTransformIntoVertices()`."""
    mesh.bakeCurrentTransformIntoVertices()


# -- Materials -----------------------------------------------------------------------------------


def new_standard_material(label: str, scene: Scene) -> StandardMaterial:
    """Return a `new BABYLON.StandardMaterial(label, scene)`."""
    __pragma__("js", "{}", "return new BABYLON.StandardMaterial(label, scene);")
    return cast("StandardMaterial", None)


def new_pbr_material(label: str, scene: Scene) -> PBRMaterial:
    """Return a `new BABYLON.PBRMaterial(label, scene)`."""
    __pragma__("js", "{}", "return new BABYLON.PBRMaterial(label, scene);")
    return cast("PBRMaterial", None)


def js_object() -> JsObject:
    """Return an empty JavaScript object, to fill with the fields Babylon reads (`js_set`)."""
    __pragma__("js", "{}", "return {};")
    return cast("JsObject", None)


def js_set(target: JsObject, key: str, value: object) -> None:
    """`target[key] = value` for a key that is a Python keyword or a computed name."""
    __pragma__("js", "{}", "target[key] = value;")


# -- Lights, cameras, textures, layers -----------------------------------------------------------


def new_hemispheric_light(label: str, direction: Vector3, scene: Scene) -> HemisphericLight:
    """Return a `new BABYLON.HemisphericLight` pointing along `direction`."""
    __pragma__("js", "{}", "return new BABYLON.HemisphericLight(label, direction, scene);")
    return cast("HemisphericLight", None)


def new_directional_light(label: str, direction: Vector3, scene: Scene) -> DirectionalLight:
    """Return a `new BABYLON.DirectionalLight` shining along `direction`."""
    __pragma__("js", "{}", "return new BABYLON.DirectionalLight(label, direction, scene);")
    return cast("DirectionalLight", None)


def new_viewport(x: float, y: float, width: float, height: float) -> Any:
    """Return a `new BABYLON.Viewport(x, y, width, height)`: shares of the canvas (D-252)."""
    __pragma__("js", "{}", "return new BABYLON.Viewport(x, y, width, height);")
    return None


def new_free_camera(label: str, position: Vector3, scene: Scene) -> FreeCamera:
    """Return a `new BABYLON.FreeCamera` at `position`."""
    __pragma__("js", "{}", "return new BABYLON.FreeCamera(label, position, scene);")
    return cast("FreeCamera", None)


def new_arc_rotate_camera(
    label: str, alpha: float, beta: float, radius: float, target: Vector3, scene: Scene
) -> ArcRotateCamera:
    """Return a `new BABYLON.ArcRotateCamera` orbiting `target`."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.ArcRotateCamera(label, alpha, beta, radius, target, scene);",
    )
    return cast("ArcRotateCamera", None)


def camera_fov_mode_horizontal_fixed() -> int:
    """`Camera.FOVMODE_HORIZONTAL_FIXED`."""
    __pragma__("js", "{}", "return BABYLON.Camera.FOVMODE_HORIZONTAL_FIXED;")
    return cast("int", None)


def new_raw_cube_texture(
    scene: Scene, faces: list[Uint8Array], size: int, format_: int, texture_type: int, mipmaps: bool
) -> RawCubeTexture:
    """Return `new RawCubeTexture(scene, faces, size, format, type, generateMipmaps)`."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RawCubeTexture(scene, faces, size, format_, texture_type, mipmaps);",
    )
    return cast("RawCubeTexture", None)


def new_glow_layer(
    label: str, scene: Scene, blur_kernel_size: float, ratio: float | None, samples: int | None
) -> GlowLayer:
    """Return `new GlowLayer(label, scene, options)`.

    `ratio` and `samples` are left out when None (Babylon's defaults apply).
    """
    __pragma__(
        "js",
        "{}",
        "var options = {blurKernelSize: blur_kernel_size};"
        "if (ratio != null) options.mainTextureRatio = ratio;"
        "if (samples != null) options.mainTextureSamples = samples;"
        "return new BABYLON.GlowLayer(label, scene, options);",
    )
    return cast("GlowLayer", None)


def image_processing_tone_mapping_aces() -> int:
    """`ImageProcessingConfiguration.TONEMAPPING_ACES`."""
    __pragma__("js", "{}", "return BABYLON.ImageProcessingConfiguration.TONEMAPPING_ACES;")
    return cast("int", None)


def is_raw_cube_texture(value: object) -> bool:
    """`value instanceof RawCubeTexture`."""
    __pragma__("js", "{}", "return value instanceof BABYLON.RawCubeTexture;")
    return False


def update_raw_cube_texture(
    texture: Texture, faces: list[Uint8Array], format_: int, texture_type: int, invert_y: bool
) -> None:
    """`texture.update(faces, format, type, invertY)`.

    Transcrypt renames `update`, so the method is called from raw JavaScript.
    """
    __pragma__("js", "{}", "texture.update(faces, format_, texture_type, invert_y);")


def set_cube_sphere_lighting(texture: Texture, faces: list[Uint8Array], size: int) -> None:
    """Give the RGBA8 cube `texture` the spherical polynomial of its `faces`.

    The faces are in Babylon's order (+X, -X, +Y, -Y, +Z, -Z), as
    `CubeMapToSphericalPolynomialTools` would from the texture's pixels read back from the GPU,
    which waits for all the GPU's work (PERF-30: about a second).

    An update of the texture keeps the polynomial set, so it is set again after each one.
    """
    __pragma__(
        "js",
        "{}",
        "texture.sphericalPolynomial = "
        "BABYLON.CubeMapToSphericalPolynomialTools.ConvertCubeMapToSphericalPolynomial({"
        "size: size, right: faces[0], left: faces[1], up: faces[2], down: faces[3],"
        " front: faces[4], back: faces[5], format: BABYLON.Constants.TEXTUREFORMAT_RGBA,"
        " type: BABYLON.Constants.TEXTURETYPE_UNSIGNED_BYTE, gammaSpace: texture.gammaSpace});",
    )


# -- Textures, shadows and plugins (scenery) ------------------------------------------------------


def new_raw_texture(
    pixels: Uint8Array,
    width: int,
    height: int,
    format_: int,
    scene: Scene,
    generate_mipmaps: bool,
    invert_y: bool,
    sampling_mode: int,
) -> RawTexture:
    """Make a `new RawTexture` from `pixels`, `width` by `height`, with the given options.

    The call is `new RawTexture(pixels, width, height, format, scene, generateMipMaps, invertY,
    samplingMode)`.
    """
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RawTexture(pixels, width, height, format_, scene, generate_mipmaps, "
        "invert_y, sampling_mode);",
    )
    return cast("RawTexture", None)


def new_render_target_texture(label: str, size: list[int], scene: Scene) -> RenderTargetTexture:
    """Return a `new RenderTargetTexture` with mipmaps, for the imposter atlas (D-211).

    The call is `new RenderTargetTexture(label, {width, height}, scene, generateMipMaps)`.
    """
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RenderTargetTexture(label, {width: size[0], height: size[1]}, scene,"
        " true);",
    )
    return cast("RenderTargetTexture", None)


def new_shadow_generator(map_size: int, light: Light) -> ShadowGenerator:
    """Return `new ShadowGenerator(mapSize, light)`."""
    __pragma__("js", "{}", "return new BABYLON.ShadowGenerator(map_size, light);")
    return cast("ShadowGenerator", None)


def is_instance_of(value: object, class_name: str) -> bool:
    """Return `value instanceof BABYLON[className]` (e.g. `Texture`, `StandardMaterial`)."""
    __pragma__("js", "{}", "return value instanceof BABYLON[class_name];")
    return False


def new_material_plugin(
    material: Material,
    owner: MaterialOwner,
    plugin_name: str,
    priority: float,
    define_name: str,
    class_name: str,
) -> MaterialPluginBase:
    """Return a `BABYLON.MaterialPluginBase` subclass whose hooks call the methods of `owner`.

    Transcrypt cannot subclass a JavaScript class, so the subclass is written here (ENG-158).

    `owner` provides `prepare_defines(defines)`, `get_samplers(samplers)`, `get_uniforms()` (a
    JavaScript object), `bind_for_sub_mesh(ubo)` and `get_custom_code(shader_type)` (a JavaScript
    object or None). `define_name` is the define switched on by the plugin.
    """
    __pragma__(
        "js",
        "{}",
        "class OwnedMaterialPlugin extends BABYLON.MaterialPluginBase {"
        "  constructor(material, owner, plugin_name, priority, define_name, class_name) {"
        "    var defines = {};"
        "    defines[define_name] = false;"
        "    super(material, plugin_name, priority, defines);"
        "    this._enable(true);"
        "  }"
        "  getClassName() { return class_name; }"
        "  prepareDefines(defines) { owner.prepare_defines(defines); }"
        "  getSamplers(samplers) { owner.get_samplers(samplers); }"
        "  getUniforms() { return owner.get_uniforms(); }"
        "  bindForSubMesh(ubo) { owner.bind_for_sub_mesh(ubo); }"
        "  getCustomCode(shaderType) { return owner.get_custom_code(shaderType); }"
        "}"
        "return new OwnedMaterialPlugin(material, owner, plugin_name, priority, define_name,"
        " class_name);",
    )
    return cast("MaterialPluginBase", None)


# -- Scenery: typed arrays, instancing and textures (roads, props, lightning) -------------------


def float32_array(length: int) -> Float32Array:
    """Return a zero-filled `Float32Array` of `length` numbers (thin-instance matrices)."""
    __pragma__("js", "{}", "return new Float32Array(length);")
    return cast("Float32Array", None)


def new_matrix() -> Matrix:
    """Return `new Matrix()`: the identity matrix."""
    __pragma__("js", "{}", "return new BABYLON.Matrix();")
    return cast("Matrix", None)


def matrix_compose_to_ref(
    scale: Vector3, rotation: Quaternion, position: Vector3, target: Matrix
) -> None:
    """`Matrix.ComposeToRef(scale, rotation, position, target)`."""
    __pragma__("js", "{}", "BABYLON.Matrix.ComposeToRef(scale, rotation, position, target);")


def quaternion_yaw_pitch_roll_to_ref(
    yaw: float, pitch: float, roll: float, target: Quaternion
) -> None:
    """`Quaternion.RotationYawPitchRollToRef(yaw, pitch, roll, target)`."""
    __pragma__(
        "js",
        "{}",
        "BABYLON.Quaternion.RotationYawPitchRollToRef(yaw, pitch, roll, target);",
    )


def texture_trilinear_sampling_mode() -> int:
    """`Texture.TRILINEAR_SAMPLINGMODE`."""
    __pragma__("js", "{}", "return BABYLON.Texture.TRILINEAR_SAMPLINGMODE;")
    return cast("int", None)


def raw_rgba_texture(
    data: Uint8Array,
    size: int,
    scene: Scene,
    generate_mipmaps: bool,
    invert_y: bool,
    sampling_mode: int,
) -> RawTexture:
    """Return a square RGBA texture from a `Uint8Array`, made by `RawTexture.CreateRGBATexture`.

    The call is `RawTexture.CreateRGBATexture(data, size, size, scene, generateMipmaps, invertY,
    samplingMode)`.
    """
    __pragma__(
        "js",
        "{}",
        "return BABYLON.RawTexture.CreateRGBATexture(data, size, size, scene, generate_mipmaps, "
        "invert_y, sampling_mode);",
    )
    return cast("RawTexture", None)


def update_raw_texture(texture: Texture, data: Uint8Array) -> None:
    """`texture.update(data)` (renamed by Transcrypt, so called from raw JavaScript)."""
    __pragma__("js", "{}", "texture.update(data);")


def new_glsl_material(
    label: str,
    scene: Scene,
    vertex_source: str,
    fragment_source: str,
    attributes: list[str],
    uniforms: list[str],
    samplers: list[str] | None,
    need_alpha_blending: bool | None,
) -> ShaderMaterial:
    """Return a `ShaderMaterial` from GLSL sources and declared names.

    The sources and the names are built as JavaScript objects. The call is
    `new ShaderMaterial(label, scene, {vertexSource, fragmentSource}, {attributes, uniforms,
    samplers, needAlphaBlending})`.

    `samplers` and `need_alpha_blending` are left out of the options when None.
    """
    __pragma__(
        "js",
        "{}",
        "var shaders = {vertexSource: vertex_source, fragmentSource: fragment_source};"
        "var options = {attributes: attributes, uniforms: uniforms};"
        "if (samplers != null) options.samplers = samplers;"
        "if (need_alpha_blending != null) options.needAlphaBlending = need_alpha_blending;"
        "return new BABYLON.ShaderMaterial(label, scene, shaders, options);",
    )
    return cast("ShaderMaterial", None)


# -- Helpers for the scenery (render/scenery/) ----------------------------------------------


def uint32_array(length: int) -> Uint32Array:
    """Return a zero-filled `Uint32Array` of `length` entries (mesh indices)."""
    __pragma__("js", "{}", "return new Uint32Array(length);")
    return cast("Uint32Array", None)


def vector3_zero() -> Vector3:
    """`Vector3.Zero()`: (0, 0, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Zero();")
    return cast("Vector3", None)


def vector3_down() -> Vector3:
    """`Vector3.Down()`: (0, -1, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Down();")
    return cast("Vector3", None)


def vector3_cross(a: Vector3, b: Vector3) -> Vector3:
    """`Vector3.Cross(a, b)`: a new vector."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Cross(a, b);")
    return cast("Vector3", None)


def vector3_dot(a: Vector3, b: Vector3) -> float:
    """`Vector3.Dot(a, b)`."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Dot(a, b);")
    return 0


def fog_mode_linear() -> int:
    """`Scene.FOGMODE_LINEAR`."""
    __pragma__("js", "{}", "return BABYLON.Scene.FOGMODE_LINEAR;")
    return cast("int", None)


def vertex_buffer_kind(key: str) -> str:
    """`VertexBuffer[key]` for a kind name such as `PositionKind`, `NormalKind` or `ColorKind`."""
    __pragma__("js", "{}", "return BABYLON.VertexBuffer[key];")
    return cast("str", None)


def update_vertices_data(mesh: Mesh, kind: str, data: Float32Array) -> None:
    """`mesh.updateVerticesData(kind, data)`."""
    mesh.updateVerticesData(kind, data)


def apply_vertex_data_updatable(data: VertexData, mesh: Mesh) -> None:
    """`data.applyToMesh(mesh, true)`: the mesh's vertex data can be updated later."""
    __pragma__("js", "{}", "data.applyToMesh(mesh, true);")


def render_painter_sort_compare(a: Node, b: Node) -> float:
    """`RenderingGroup.PainterSortCompare(a, b)`: Babylon's order of two sub-meshes."""
    __pragma__("js", "{}", "return BABYLON.RenderingGroup.PainterSortCompare(a, b);")
    return 0


# -- Maps and metadata (render state keyed by Babylon objects) ----------------------------------


def new_weak_map() -> WeakMap[V]:
    """State keyed by Babylon objects: a `new WeakMap()`.

    A Python dict only takes string keys (ENG-159).
    """
    __pragma__("js", "{}", "return new WeakMap();")
    return cast("WeakMap[V]", None)


def weak_map_get(weak_map: WeakMap[V], key: object) -> V | None:
    """Return the value stored for `key`, or None when there is none (never `undefined`)."""
    __pragma__("js", "{}", "return weak_map.has(key) ? weak_map.get(key) : null;")
    return cast("V | None", None)


def weak_map_set(weak_map: WeakMap[V], key: object, value: V) -> None:
    """Store `value` for `key` in `weak_map`."""
    weak_map.set(key, value)


def object_with_field(old: object, key: str, value: object) -> JsObject:
    """Return `{ ...old, [key]: value }`.

    A copy of the own fields of `old` (an object or None), with `key` set to `value`.
    """
    __pragma__(
        "js",
        "{}",
        "var copy = {};"
        "if (old !== null && typeof old === 'object') { for (var k in old) copy[k] = old[k]; }"
        "copy[key] = value;"
        "return copy;",
    )
    return cast("JsObject", None)


def metadata_field(metadata: object, key: str) -> Any:
    """Return `metadata[key]` when `metadata` is an object that has `key`, else None.

    It has `key` when `key in metadata`.
    """
    __pragma__(
        "js",
        "{}",
        "if (metadata !== null && typeof metadata === 'object' && key in metadata) {"
        "return metadata[key];}"
        "return null;",
    )
    return cast("object", None)


def number_max_value() -> float:
    """`Number.MAX_VALUE`, Babylon's default draw order (`alphaIndex`) of a mesh."""
    __pragma__("js", "{}", "return Number.MAX_VALUE;")
    return 0


def vector3_right() -> Vector3:
    """`Vector3.Right()`: (1, 0, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Right();")
    return cast("Vector3", None)


def create_ground_sized(label: str, width: float, height: float, scene: Scene) -> Mesh:
    """Return a ground without the subdivision option.

    `CreateGround(label, {width, height}, scene)`: Babylon's default is one.
    """
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateGround(label, {width: width, height: height}, scene);",
    )
    return cast("Mesh", None)
