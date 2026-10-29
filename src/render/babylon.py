"""The only place that touches the Babylon.js global (ENG-02, D-169).

Babylon is the UMD build vendored under `public/vendor/` (`make vendor`): it sets the global
`BABYLON`. Every other module of `render/` builds its objects through the functions below, and
the rest of the game reaches the engine only through `render/`. Objects are returned as plain
JavaScript handles (typed `Any`); their methods and properties are used by attribute access.

Rules that come from Transcrypt (see `01-engineering.md` §13):
- Babylon names that are Python keywords or special to Transcrypt (`name`, `from`...) are read and
  written in raw JavaScript, through the helpers below.
- Constructor calls and builder calls with option objects are raw JavaScript (`new BABYLON.X`),
  because a Python dict is not a JavaScript object and keyword arguments are dropped.
- Optional options are passed as `None` and left out of the JavaScript object.
"""

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# -- The global and its classes ------------------------------------------------------------------


def babylon_class(class_name: str) -> Any:
    """The Babylon class (or namespace) called `class_name`, e.g. `Camera`."""
    __pragma__("js", "{}", "return BABYLON[class_name];")
    return None


def babylon_constant(key: str) -> Any:
    """A value of `BABYLON.Constants`, e.g. `ALPHA_ADD` or `TEXTUREFORMAT_RGBA`."""
    __pragma__("js", "{}", "return BABYLON.Constants[key];")
    return None


def get_engine_global() -> Any:
    """The `BABYLON` global itself (for the few values not reachable through the helpers)."""
    return window.BABYLON


# -- Math ----------------------------------------------------------------------------------------


def vector2(x: float, y: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Vector2(x, y);")
    return None


def vector3(x: float, y: float, z: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Vector3(x, y, z);")
    return None


def vector4(x: float, y: float, z: float, w: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Vector4(x, y, z, w);")
    return None


def vector3_up() -> Any:
    """`Vector3.Up()`: (0, 1, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Up();")
    return None


def color3(r: float, g: float, b: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Color3(r, g, b);")
    return None


def color3_black() -> Any:
    __pragma__("js", "{}", "return BABYLON.Color3.Black();")
    return None


def color4(r: float, g: float, b: float, a: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Color4(r, g, b, a);")
    return None


def quaternion(x: float, y: float, z: float, w: float) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Quaternion(x, y, z, w);")
    return None


# -- Nodes, names and scene ----------------------------------------------------------------------


def node_name(node: Any) -> str:
    """`node.name` (a Python attribute of this name would be renamed by Transcrypt)."""
    __pragma__("js", "{}", "return node.name;")
    return ""


def set_node_name(node: Any, label: str) -> None:
    __pragma__("js", "{}", "node.name = label;")


def new_transform_node(label: str, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.TransformNode(label, scene);")
    return None


def get_hierarchy_bounding_vectors(node: Any) -> Any:
    """`node.getHierarchyBoundingVectors(true)`: the `{min, max}` Vector3 handles."""
    __pragma__("js", "{}", "return node.getHierarchyBoundingVectors(true);")
    return None


def new_engine(canvas: Any, antialias: bool) -> Any:
    """`new Engine(canvas, antialias, {adaptToDeviceRatio: false, stencil: true})`, as in the TS."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.Engine(canvas, antialias, {adaptToDeviceRatio: false, stencil: true});",
    )
    return None


def new_scene(engine: Any) -> Any:
    """`new Scene(engine)`."""
    __pragma__("js", "{}", "return new BABYLON.Scene(engine);")
    return None


def new_mesh(label: str, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.Mesh(label, scene);")
    return None


def set_enabled(node: Any, on: bool) -> None:
    """`node.setEnabled(on)`."""
    node.setEnabled(on)


def is_enabled(node: Any) -> bool:
    return bool(node.isEnabled())


def dispose_node(node: Any) -> None:
    node.dispose()


def child_meshes(node: Any, direct_only: bool) -> list[Any]:
    """`node.getChildMeshes(directOnly)`: a fresh array (safe to push into)."""
    __pragma__("js", "{}", "return node.getChildMeshes(direct_only);")
    return []


def descendants(node: Any, direct_only: bool) -> list[Any]:
    """`node.getDescendants(directOnly)`."""
    __pragma__("js", "{}", "return node.getDescendants(direct_only);")
    return []


def unique_id(node: Any) -> float:
    """`node.uniqueId`: Babylon numbers nodes from one counter, in creation order."""
    __pragma__("js", "{}", "return node.uniqueId;")
    return 0


def scene_unique_id(scene: Any) -> float:
    return float(scene.getUniqueId())


def scene_meshes(scene: Any) -> list[Any]:
    __pragma__("js", "{}", "return scene.meshes;")
    return []


def scene_transform_nodes(scene: Any) -> list[Any]:
    __pragma__("js", "{}", "return scene.transformNodes;")
    return []


# -- Typed arrays (for textures and buffers) -----------------------------------------------------


def uint8_array(length: int) -> Any:
    """A zero-filled `Uint8Array` of `length` bytes."""
    __pragma__("js", "{}", "return new Uint8Array(length);")
    return None


# -- Vertex data and meshes ----------------------------------------------------------------------


def new_vertex_data() -> Any:
    __pragma__("js", "{}", "return new BABYLON.VertexData();")
    return None


def compute_normals(positions: list[float], indices: list[Any]) -> list[float]:
    """`VertexData.ComputeNormals(positions, indices, normals)`: returns the normals array."""
    normals: list[float] = []
    __pragma__("js", "{}", "BABYLON.VertexData.ComputeNormals(positions, indices, normals);")
    return normals


def vertex_data_of(
    positions: list[float],
    indices: list[Any],
    normals: list[float] | None = None,
    colors: list[float] | None = None,
    uvs: list[float] | None = None,
) -> Any:
    """A `VertexData` with the given arrays set (the ones left as None are not set)."""
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


def apply_vertex_data(data: Any, mesh: Any) -> None:
    """`data.applyToMesh(mesh)`."""
    data.applyToMesh(mesh)


def create_torus(
    label: str, diameter: float, thickness: float, tessellation: int, scene: Any
) -> Any:
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateTorus(label, {diameter: diameter, thickness: thickness, "
        "tessellation: tessellation}, scene);",
    )
    return None


def create_plane(label: str, size: float, scene: Any) -> Any:
    __pragma__("js", "{}", "return BABYLON.CreatePlane(label, {size: size}, scene);")
    return None


def create_line_system(label: str, lines: list[list[Any]], scene: Any) -> Any:
    """A line system: `lines` is a list of polylines of Vector3 handles."""
    __pragma__("js", "{}", "return BABYLON.CreateLineSystem(label, {lines: lines}, scene);")
    return None


def create_colored_line_system(
    label: str, lines: list[list[Any]], colors: list[list[Any]], scene: Any
) -> Any:
    """A line system with a Color4 handle per vertex: `colors` mirrors `lines`."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateLineSystem(label, {lines: lines, colors: colors}, scene);",
    )
    return None


def create_lines(label: str, points: list[Any], scene: Any) -> Any:
    """`CreateLines(label, {points}, scene)`: one polyline of Vector3 handles."""
    __pragma__("js", "{}", "return BABYLON.CreateLines(label, {points: points}, scene);")
    return None


def create_lathe(label: str, shape: list[Any], tessellation: int, scene: Any) -> Any:
    """A lathe around Y of the Vector3 `shape` (x = radius, y = height)."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateLathe(label, {shape: shape, tessellation: tessellation}, scene);",
    )
    return None


def create_ground(label: str, width: float, height: float, subdivisions: int, scene: Any) -> Any:
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateGround(label, {width: width, height: height, "
        "subdivisions: subdivisions}, scene);",
    )
    return None


def create_box(label: str, options: Any, scene: Any) -> Any:
    """`CreateBox(label, options, scene)`: `options` is a JavaScript object (width, height,
    depth)."""
    __pragma__("js", "{}", "return BABYLON.CreateBox(label, options, scene);")
    return None


def create_cylinder(label: str, options: Any, scene: Any) -> Any:
    """`CreateCylinder(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreateCylinder(label, options, scene);")
    return None


def create_polyhedron(label: str, options: Any, scene: Any) -> Any:
    """`CreatePolyhedron(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreatePolyhedron(label, options, scene);")
    return None


def create_disc(label: str, options: Any, scene: Any) -> Any:
    """`CreateDisc(label, options, scene)`: `options` is a JavaScript object."""
    __pragma__("js", "{}", "return BABYLON.CreateDisc(label, options, scene);")
    return None


def bake_transform(mesh: Any) -> None:
    """`mesh.bakeCurrentTransformIntoVertices()`."""
    mesh.bakeCurrentTransformIntoVertices()


# -- Materials -----------------------------------------------------------------------------------


def new_standard_material(label: str, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.StandardMaterial(label, scene);")
    return None


def new_shader_material(label: str, scene: Any, shaders: Any, options: Any) -> Any:
    """`new ShaderMaterial(label, scene, shaders, options)`. `shaders` and `options` are JS
    objects built with `js_object` (a dict is not one)."""
    __pragma__("js", "{}", "return new BABYLON.ShaderMaterial(label, scene, shaders, options);")
    return None


def new_pbr_material(label: str, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.PBRMaterial(label, scene);")
    return None


def js_object() -> Any:
    """An empty JavaScript object, to fill with the fields Babylon reads (`js_set`)."""
    __pragma__("js", "{}", "return {};")
    return None


def js_set(target: Any, key: str, value: Any) -> None:
    """`target[key] = value` for a key that is a Python keyword or a computed name."""
    __pragma__("js", "{}", "target[key] = value;")


# -- Lights, cameras, textures, layers -----------------------------------------------------------


def new_hemispheric_light(label: str, direction: Any, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.HemisphericLight(label, direction, scene);")
    return None


def new_directional_light(label: str, direction: Any, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.DirectionalLight(label, direction, scene);")
    return None


def new_free_camera(label: str, position: Any, scene: Any) -> Any:
    __pragma__("js", "{}", "return new BABYLON.FreeCamera(label, position, scene);")
    return None


def new_arc_rotate_camera(
    label: str, alpha: float, beta: float, radius: float, target: Any, scene: Any
) -> Any:
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.ArcRotateCamera(label, alpha, beta, radius, target, scene);",
    )
    return None


def camera_fov_mode_horizontal_fixed() -> Any:
    """`Camera.FOVMODE_HORIZONTAL_FIXED`."""
    __pragma__("js", "{}", "return BABYLON.Camera.FOVMODE_HORIZONTAL_FIXED;")
    return None


def new_raw_cube_texture(
    scene: Any, faces: list[Any], size: int, format_: Any, texture_type: Any, mipmaps: bool
) -> Any:
    """`new RawCubeTexture(scene, faces, size, format, type, generateMipmaps)`."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RawCubeTexture(scene, faces, size, format_, texture_type, mipmaps);",
    )
    return None


def new_glow_layer(
    label: str, scene: Any, blur_kernel_size: float, ratio: float | None, samples: int | None
) -> Any:
    """`new GlowLayer(label, scene, options)`: `ratio` and `samples` are left out when None
    (Babylon's defaults apply)."""
    __pragma__(
        "js",
        "{}",
        "var options = {blurKernelSize: blur_kernel_size};"
        "if (ratio != null) options.mainTextureRatio = ratio;"
        "if (samples != null) options.mainTextureSamples = samples;"
        "return new BABYLON.GlowLayer(label, scene, options);",
    )
    return None


def image_processing_tone_mapping_aces() -> Any:
    """`ImageProcessingConfiguration.TONEMAPPING_ACES`."""
    __pragma__("js", "{}", "return BABYLON.ImageProcessingConfiguration.TONEMAPPING_ACES;")
    return None


def is_raw_cube_texture(value: Any) -> bool:
    """`value instanceof RawCubeTexture`."""
    __pragma__("js", "{}", "return value instanceof BABYLON.RawCubeTexture;")
    return False


def update_raw_cube_texture(
    texture: Any, faces: list[Any], format_: Any, texture_type: Any, mipmaps: bool
) -> None:
    """`texture.update(faces, format, type, generateMipmaps)`. Transcrypt renames `update`, so
    the method is called from raw JavaScript."""
    __pragma__("js", "{}", "texture.update(faces, format_, texture_type, mipmaps);")


def dispose_texture(texture: Any) -> None:
    texture.dispose()


# -- Textures, shadows and plugins (scenery) ------------------------------------------------------


def new_raw_texture(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    pixels: Any,
    width: int,
    height: int,
    format_: Any,
    scene: Any,
    generate_mipmaps: bool,
    invert_y: bool,
    sampling_mode: Any,
) -> Any:
    """`new RawTexture(pixels, width, height, format, scene, generateMipMaps, invertY,
    samplingMode)`."""
    __pragma__(
        "js",
        "{}",
        "return new BABYLON.RawTexture(pixels, width, height, format_, scene, generate_mipmaps, "
        "invert_y, sampling_mode);",
    )
    return None


def new_shadow_generator(map_size: int, light: Any) -> Any:
    """`new ShadowGenerator(mapSize, light)`."""
    __pragma__("js", "{}", "return new BABYLON.ShadowGenerator(map_size, light);")
    return None


def is_instance_of(value: Any, class_name: str) -> bool:
    """`value instanceof BABYLON[className]` (e.g. `Texture`, `StandardMaterial`)."""
    __pragma__("js", "{}", "return value instanceof BABYLON[class_name];")
    return False


def new_material_plugin(
    material: Any,
    owner: Any,
    plugin_name: str,
    priority: float,
    define_name: str,
    class_name: str,
) -> Any:
    """A `BABYLON.MaterialPluginBase` subclass whose hooks call the methods of `owner`: Transcrypt
    cannot subclass a JavaScript class, so the subclass is written here. `owner` provides
    `prepare_defines(defines)`, `get_samplers(samplers)`,
    `get_uniforms()` (a JavaScript object), `bind_for_sub_mesh(ubo)` and
    `get_custom_code(shader_type)` (a JavaScript object or None). `define_name` is the define
    switched on by the plugin."""
    __pragma__(
        "js",
        "{}",
        "class OwnedMaterialPlugin extends BABYLON.MaterialPluginBase {"
        "  constructor(material, owner, plugin_name, priority, define_name, class_name) {"
        "    var defines = {};"
        "    defines[define_name] = false;"
        "    super(material, plugin_name, priority, defines);"
        "    this.owner = owner;"
        "    this._enable(true);"
        "  }"
        "  getClassName() { return class_name; }"
        "  prepareDefines(defines) { this.owner.prepare_defines(defines); }"
        "  getSamplers(samplers) { this.owner.get_samplers(samplers); }"
        "  getUniforms() { return this.owner.get_uniforms(); }"
        "  bindForSubMesh(ubo) { this.owner.bind_for_sub_mesh(ubo); }"
        "  getCustomCode(shaderType) { return this.owner.get_custom_code(shaderType); }"
        "}"
        "return new OwnedMaterialPlugin(material, owner, plugin_name, priority, define_name,"
        " class_name);",
    )
    return None


# -- Scenery: typed arrays, instancing and textures (roads, props, lightning) -------------------


def float32_array(length: int) -> Any:
    """A zero-filled `Float32Array` of `length` numbers (thin-instance matrices)."""
    __pragma__("js", "{}", "return new Float32Array(length);")
    return None


def new_matrix() -> Any:
    """`new Matrix()`: the identity matrix."""
    __pragma__("js", "{}", "return new BABYLON.Matrix();")
    return None


def matrix_compose_to_ref(scale: Any, rotation: Any, position: Any, target: Any) -> None:
    """`Matrix.ComposeToRef(scale, rotation, position, target)`."""
    __pragma__("js", "{}", "BABYLON.Matrix.ComposeToRef(scale, rotation, position, target);")


def quaternion_yaw_pitch_roll_to_ref(yaw: float, pitch: float, roll: float, target: Any) -> None:
    """`Quaternion.RotationYawPitchRollToRef(yaw, pitch, roll, target)`."""
    __pragma__(
        "js",
        "{}",
        "BABYLON.Quaternion.RotationYawPitchRollToRef(yaw, pitch, roll, target);",
    )


def texture_trilinear_sampling_mode() -> Any:
    """`Texture.TRILINEAR_SAMPLINGMODE`."""
    __pragma__("js", "{}", "return BABYLON.Texture.TRILINEAR_SAMPLINGMODE;")
    return None


def raw_rgba_texture(
    data: Any, size: int, scene: Any, generate_mipmaps: bool, invert_y: bool, sampling_mode: Any
) -> Any:
    """`RawTexture.CreateRGBATexture(data, size, size, scene, generateMipmaps, invertY,
    samplingMode)`: a square RGBA texture from a `Uint8Array`."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.RawTexture.CreateRGBATexture(data, size, size, scene, generate_mipmaps, "
        "invert_y, sampling_mode);",
    )
    return None


def update_raw_texture(texture: Any, data: Any) -> None:
    """`texture.update(data)` (renamed by Transcrypt, so called from raw JavaScript)."""
    __pragma__("js", "{}", "texture.update(data);")


def new_glsl_material(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    label: str,
    scene: Any,
    vertex_source: str,
    fragment_source: str,
    attributes: list[str],
    uniforms: list[str],
    samplers: list[str] | None,
    need_alpha_blending: bool | None,
) -> Any:
    """`new ShaderMaterial(label, scene, {vertexSource, fragmentSource}, {attributes, uniforms,
    samplers, needAlphaBlending})`: the GLSL sources and the declared names, built as JavaScript
    objects. `samplers` and `need_alpha_blending` are left out of the options when None."""
    __pragma__(
        "js",
        "{}",
        "var shaders = {vertexSource: vertex_source, fragmentSource: fragment_source};"
        "var options = {attributes: attributes, uniforms: uniforms};"
        "if (samplers != null) options.samplers = samplers;"
        "if (need_alpha_blending != null) options.needAlphaBlending = need_alpha_blending;"
        "return new BABYLON.ShaderMaterial(label, scene, shaders, options);",
    )
    return None


# -- Helpers for the scenery port (render/scenery/) ----------------------------------------------


def uint32_array(length: int) -> Any:
    """A zero-filled `Uint32Array` of `length` entries (mesh indices)."""
    __pragma__("js", "{}", "return new Uint32Array(length);")
    return None


def vector3_zero() -> Any:
    """`Vector3.Zero()`: (0, 0, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Zero();")
    return None


def vector3_down() -> Any:
    """`Vector3.Down()`: (0, -1, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Down();")
    return None


def vector3_cross(a: Any, b: Any) -> Any:
    """`Vector3.Cross(a, b)`: a new vector."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Cross(a, b);")
    return None


def vector3_dot(a: Any, b: Any) -> float:
    """`Vector3.Dot(a, b)`."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Dot(a, b);")
    return 0


def fog_mode_linear() -> Any:
    """`Scene.FOGMODE_LINEAR`."""
    __pragma__("js", "{}", "return BABYLON.Scene.FOGMODE_LINEAR;")
    return None


def vertex_buffer_kind(key: str) -> Any:
    """`VertexBuffer[key]` for a kind name such as `PositionKind`, `NormalKind` or `ColorKind`."""
    __pragma__("js", "{}", "return BABYLON.VertexBuffer[key];")
    return None


def update_vertices_data(mesh: Any, kind: Any, data: Any) -> None:
    """`mesh.updateVerticesData(kind, data)`."""
    mesh.updateVerticesData(kind, data)


def apply_vertex_data_updatable(data: Any, mesh: Any) -> None:
    """`data.applyToMesh(mesh, true)`: the mesh's vertex data can be updated later."""
    __pragma__("js", "{}", "data.applyToMesh(mesh, true);")


def render_painter_sort_compare(a: Any, b: Any) -> float:
    """`RenderingGroup.PainterSortCompare(a, b)`: Babylon's order of two sub-meshes."""
    __pragma__("js", "{}", "return BABYLON.RenderingGroup.PainterSortCompare(a, b);")
    return 0


# -- Maps and metadata (render state keyed by Babylon objects) ----------------------------------


def new_weak_map() -> Any:
    """`new WeakMap()`: state keyed by Babylon objects (a Python dict only takes string keys)."""
    __pragma__("js", "{}", "return new WeakMap();")
    return None


def weak_map_get(weak_map: Any, key: Any) -> Any:
    """The value stored for `key`, or None when there is none (never `undefined`)."""
    __pragma__("js", "{}", "return weak_map.has(key) ? weak_map.get(key) : null;")
    return None


def weak_map_set(weak_map: Any, key: Any, value: Any) -> None:
    weak_map.set(key, value)


def object_with_field(old: Any, key: str, value: Any) -> Any:
    """`{ ...old, [key]: value }`: a copy of the own fields of `old` (an object or None), with
    `key` set to `value`."""
    __pragma__(
        "js",
        "{}",
        "var copy = {};"
        "if (old !== null && typeof old === 'object') { for (var k in old) copy[k] = old[k]; }"
        "copy[key] = value;"
        "return copy;",
    )
    return None


def metadata_field(metadata: Any, key: str) -> Any:
    """`metadata[key]` when `metadata` is an object that has `key` (`key in metadata`), else
    None."""
    __pragma__(
        "js",
        "{}",
        "if (metadata !== null && typeof metadata === 'object' && key in metadata) {"
        "return metadata[key];}"
        "return null;",
    )
    return None


def number_max_value() -> float:
    """`Number.MAX_VALUE`, Babylon's default draw order (`alphaIndex`) of a mesh."""
    __pragma__("js", "{}", "return Number.MAX_VALUE;")
    return 0


def new_map() -> Any:
    """`new Map()`, for maps keyed by objects that must be iterated in insertion order."""
    __pragma__("js", "{}", "return new Map();")
    return None


def vector3_right() -> Any:
    """`Vector3.Right()`: (1, 0, 0)."""
    __pragma__("js", "{}", "return BABYLON.Vector3.Right();")
    return None


def create_ground_sized(label: str, width: float, height: float, scene: Any) -> Any:
    """`CreateGround(label, {width, height}, scene)`: a ground without subdivision option (Babylon's
    default is one)."""
    __pragma__(
        "js",
        "{}",
        "return BABYLON.CreateGround(label, {width: width, height: height}, scene);",
    )
    return None
