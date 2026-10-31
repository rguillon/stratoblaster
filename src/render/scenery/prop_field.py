"""The props standing on the terrain (P04-R04): each kind of prop is one mesh (plus one for its
self-lit accents) drawn once per placement with thin instances (ENG-104). Placements are grouped by
terrain chunk, so they come and go with the chunks. A window is a `[z_min, z_max]` pair. D-212:
some kinds may be drawn as imposters instead (`ImposterKinds`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from config.plumes import PLUME_KINDS
from core.scenery.draws import allowed
from render.babylon import (
    apply_vertex_data,
    compute_normals,
    float32_array,
    is_enabled,
    matrix_compose_to_ref,
    new_matrix,
    new_mesh,
    new_standard_material,
    new_vertex_data,
    quaternion,
    quaternion_yaw_pitch_roll_to_ref,
    set_enabled,
    vector3,
)
from render.geometry.textured import TexturedGeometry
from render.scenery.plume_layer import build_plume_meshes

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import TYPE_CHECKING, Any  # noqa: E402

from core.scenery.ground_boxes import PropPlacement  # noqa: E402
from core.scenery.scenery_level import SceneryLevel  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402
from render.scenery.plume_layer import PlumeFrame, PlumeMaterial, PlumeMaterialFactory  # noqa: E402
from render.scenery.scenery_look import PropGeometry, PropModelFactory  # noqa: E402

if TYPE_CHECKING:
    # It imports this module.
    from render.scenery.imposter_kinds import ImposterKinds

PropDrift = Any
Window = list[float]
__pragma__("noskip")

MATRIX_FLOATS = 16
# D-212: the layer of the shadows' stand-ins, which no camera sees (theirs is 0x0FFFFFFF).
SHADOW_ONLY_LAYER = 0x20000000

# Keys of the objects that hold their cached results (a WeakMap keyed by the object).
_GEOMETRY_SLOT = "render_prop_geometry"
_NORMALS_SLOT = "render_prop_normals"


def _slot_get(owner: Any, slot: str) -> Any:
    """The value kept on `owner` under `slot`, or undefined (a WeakMap entry on the object)."""
    __pragma__("js", "{}", "return owner[slot];")
    return None


def _slot_set(owner: Any, slot: str, value: Any) -> None:
    __pragma__("js", "{}", "owner[slot] = value;")


class PropMaterials:
    """Materials of the props: the lit structure, the self-lit accents and the windows (D-210;
    None: the props' windows are not drawn)."""

    def __init__(self, structure: Any, lights: Any, windows: Any = None) -> None:  # noqa: ANN401
        self.structure = structure
        self.lights = lights
        self.windows = windows


class PropMeshes:
    """The meshes of one kind of prop."""

    def __init__(
        self,
        structure: Any,  # noqa: ANN401
        lights: Any,  # noqa: ANN401
        plumes: list[Any],
        windows: Any = None,  # noqa: ANN401
        shadow: Any = None,  # noqa: ANN401
    ) -> None:
        self.structure = structure
        self.lights = lights
        """Phase 10: its smoke or steam, drawn with the same instances."""
        self.plumes = plumes
        """D-210: its windows (None if it has none)."""
        self.windows = windows
        """D-212: its shadow's stand-in, drawn in the shadows only (None if it has none)."""
        self.shadow = shadow


class KindProps:
    """The props of one kind in a chunk, with their instance matrices, made on their first upload
    and kept while the chunk is (reviewer, 2026-10-28: not made again each time the window
    moves)."""

    def __init__(self, placements: list[PropPlacement]) -> None:
        self.placements = placements
        self.matrices: Any = None


class Drawn:
    """The props of a kind to draw: each placement, and the chunk's props it comes from, at `at`."""

    def __init__(
        self, placements: list[PropPlacement], from_: list[KindProps], at: list[int]
    ) -> None:
        self.placements = placements
        self.from_ = from_
        self.at = at


def _geometry_of(factory: PropModelFactory) -> PropGeometry:
    """The geometry of `factory`, made on first use (reviewer, 2026-10-28: the models are the same
    every time, and nothing changes a geometry once made)."""
    geometry = _slot_get(factory, _GEOMETRY_SLOT)
    if not geometry:
        geometry = factory()
        _slot_set(factory, _GEOMETRY_SLOT, geometry)
    result: PropGeometry = geometry
    return result


def prop_geometry(factory: PropModelFactory) -> PropGeometry:
    """The geometry of `factory` (made once: see `_geometry_of`)."""
    return _geometry_of(factory)


def prop_bounds(factory: PropModelFactory) -> list[float]:
    """The box round the prop `factory` makes (its structure), in ground units, as
    [x0, y0, z0, x1, y1, z1]; all 0 when it has no structure."""
    positions = _geometry_of(factory).structure.positions
    if len(positions) == 0:
        return [0, 0, 0, 0, 0, 0]
    low = [positions[0], positions[1], positions[2]]
    high = [positions[0], positions[1], positions[2]]
    for i in range(0, len(positions), 3):
        for axis in range(3):
            value = positions[i + axis]
            low[axis] = min(low[axis], value)
            high[axis] = max(high[axis], value)
    return [low[0], low[1], low[2], high[0], high[1], high[2]]


def prop_extent(factory: PropModelFactory) -> float:
    """The largest side of the prop `factory` makes (its structure), in ground units."""
    b = prop_bounds(factory)
    return max(b[3] - b[0], b[4] - b[1], b[5] - b[2])


def _normals_of(geo: ColoredGeometry) -> list[float]:
    """The normals of each geometry, worked out once."""
    normals = _slot_get(geo, _NORMALS_SLOT)
    if not normals:
        normals = compute_normals(geo.positions, geo.indices)
        _slot_set(geo, _NORMALS_SLOT, normals)
    values: list[float] = normals
    return values


def _draw_always(mesh: Any) -> None:
    """Draws `mesh` without checking whether it is in view, so its bounds are never fitted to its
    instances (reviewer, 2026-10-28): for the cars, placed again every frame, that was the largest
    single cost of a frame in Worlds 3 and 4, and for the other props half of each upload. Their
    instances are near the view anyway, and the sun's shadows have a fixed frustum
    (`shadowFrustumSize`), which no bounds change."""
    mesh.alwaysSelectAsActiveMesh = True
    mesh.doNotSyncBoundingInfo = True


def _part_mesh(name: str, geo: Any, material: Any, scene: Any) -> Any:  # noqa: ANN401
    """The mesh of a part of a prop (its lights, its windows), drawn always; None if it has no
    such part or no material for it."""
    # `== None`: a materials object made without windows has the field undefined.
    if geo == None or material == None or len(geo.indices) == 0:  # noqa: E711
        return None
    mesh = mesh_of(name, geo, material, scene)
    _draw_always(mesh)
    return mesh


def shadow_only_material(scene: Any) -> Any:  # noqa: ANN401
    """D-212: a material that draws nothing (no colour, no depth): a mesh with it only shows in
    the shadow maps, which draw it with their own shader."""
    material = new_standard_material("prop-shadow-only", scene)
    material.disableColorWrite = True
    material.disableDepthWrite = True
    material.disableLighting = True
    return material


def mesh_of(name: str, geo: ColoredGeometry, material: Any, scene: Any) -> Any:
    """A disabled, unpickable mesh of `geo`, drawn with `material`."""
    mesh = new_mesh(name, scene)
    data = new_vertex_data()
    data.positions = geo.positions
    data.indices = geo.indices
    data.colors = geo.colors
    data.normals = _normals_of(geo)
    if isinstance(geo, TexturedGeometry):
        data.uvs = geo.uvs
    apply_vertex_data(data, mesh)
    mesh.material = material
    mesh.isPickable = False
    set_enabled(mesh, False)
    return mesh


def prop_drifts(level: SceneryLevel) -> dict[str, PropDrift]:
    """The kinds of `level` that drift, and how (phase 8: floating ice; phase 10: wagons)."""
    floating = level.props.floating
    kinds = floating.kinds if floating is not None else []
    lines = level.props.lines if level.props.lines is not None else []
    drifts: dict[str, PropDrift] = {}
    for k in kinds:
        if k.drift:
            drifts[k.id] = k.drift
    for line in lines:
        if line.drift:
            drifts[line.kind] = line.drift
    return drifts


def _unique(ids: list[str]) -> list[str]:
    out: list[str] = []
    for i in ids:
        if i not in out:
            out.append(i)
    return out


def level_tree_kinds(level: SceneryLevel) -> list[str]:
    """The kinds of tree `level`'s sections allow (D-214), unique, in order."""
    ids: list[str] = []
    for s in level.sections:
        for t in allowed(level.props.trees, s.trees):
            ids.append(t.id)
    return _unique(ids)


def level_prop_kinds(level: SceneryLevel) -> list[str]:  # noqa: PLR0912, C901
    """The kinds of prop `level` can stand on its ground (not its cars): the buildings and trees its
    sections allow, its floating props, lines, podiums, set pieces and lots. Unique, in order."""
    props = level.props
    sections = level.sections
    ids: list[str] = []
    for s in sections:
        for g in allowed(props.groups, s.groups):
            for k in g.kinds:
                ids.append(k.id)
    ids.extend(level_tree_kinds(level))
    if props.floating is not None:
        for k in props.floating.kinds:
            ids.append(k.id)
    if props.lines is not None:
        for line in props.lines:
            ids.append(line.kind)
    for s in sections:
        if s.blocks is not None and s.blocks.podiums is not None:
            ids.extend(s.blocks.podiums)
    if props.landmarks is not None:
        for landmark in props.landmarks:
            ids.append(landmark.kind)
    # Phase 15: the lots of the districts on tiles.
    if props.lots is not None:
        for k in props.lots:
            ids.append(k.id)
    return _unique(ids)


def level_prop_models(
    level: SceneryLevel,
    models: dict[str, PropModelFactory],
) -> dict[str, PropModelFactory]:
    """The models of the props of `level` (`level_prop_kinds`): only those are built (reviewer,
    2026-10-28: building all the game's took about 36 ms and 841 meshes per level). Throws if one of
    them, or one of its cars, has no model."""
    check_prop_models(level, models)
    kinds = level_prop_kinds(level)
    return {k: v for k, v in models.items() if k in kinds}


def check_prop_models(level: SceneryLevel, models: dict[str, PropModelFactory]) -> None:
    """Throws if a prop kind of `level`, or one of its cars, has no model."""
    for kind in level_prop_kinds(level):
        if kind not in models:
            raise ValueError('No model for prop "' + kind + '"')
    cars = level.props.cars
    if cars is not None:
        for kind in cars.kinds:
            if kind not in models:
                raise ValueError('No model for prop "' + kind + '"')


class PropField:
    """The props standing on the terrain (P04-R04). Each kind of prop is one mesh (plus one for its
    self-lit accents) drawn once per placement with thin instances (ENG-104). Placements are grouped
    by terrain chunk, so they come and go with the chunks."""

    def __init__(
        self,
        scene: Any,
        models: dict[str, PropModelFactory],
        materials: PropMaterials,
        on_structure: Any = None,
        plume_materials: PlumeMaterialFactory | None = None,
        imposters: "ImposterKinds | None" = None,
    ) -> None:
        """`on_structure(mesh)`: called with each structure mesh (optional). `plume_materials`: the
        material factory of the plumes (phase 10, optional). `imposters` (D-212, optional): the
        kinds drawn as imposters (`models` then the imposters' own, making only their lights)."""
        self._imposters = imposters
        if imposters is not None:
            models = imposters.models
        self._meshes: dict[str, PropMeshes] = {}
        """Phase 10: one material per kind of plume, driven every frame."""
        self._plume_materials: dict[str, PlumeMaterial] = {}
        """The placements of each chunk, by kind (chunks in insertion order, as parallel lists)."""
        self._chunk_indices: list[int] = []
        self._chunk_kinds: list[dict[str, KindProps]] = []
        """The placements uploaded last for each kind (P13-R04: unchanged kinds are kept)."""
        self._drawn: dict[str, list[PropPlacement]] = {}
        self._dirty = False
        """Only the props whose Z is in this range are drawn, if set (see `set_window`)."""
        self._window: Window | None = None

        def plume_material(id: str) -> Any:
            kind = PLUME_KINDS.get(id)
            if plume_materials is None or not kind:
                return None
            material = self._plume_materials.get(id)
            if not material:
                material = plume_materials(scene, kind)
                self._plume_materials[id] = material
            return material.material

        self._shadow_material: Any = None
        self._on_structure = on_structure
        for kind, factory in models.items():
            geometry = _geometry_of(factory)
            # D-211: a model may have no structure (the cars' lights, their bodies imposters).
            structure = None
            if len(geometry.structure.indices) > 0:
                structure = mesh_of("prop-" + kind, geometry.structure, materials.structure, scene)
                structure.receiveShadows = True
                if on_structure is not None:
                    on_structure(structure)
                _draw_always(structure)
            lights = _part_mesh(
                "prop-" + kind + "-lights", geometry.lights, materials.lights, scene
            )
            windows = _part_mesh(
                "prop-" + kind + "-windows", geometry.windows, materials.windows, scene
            )
            # D-212: a stand-in drawn only in the shadows, with the instances: for a model with no
            # structure (an imposter's, whose quad casts no shadow), not to cast a second one.
            shadow = None if structure is not None else self._shadow_mesh(scene, kind, geometry)
            if shadow is not None:
                on_structure(shadow)
            plumes_of = geometry.plumes if geometry.plumes is not None else []
            plumes = build_plume_meshes(scene, "prop-" + kind, plumes_of, plume_material)
            for plume in plumes:
                _draw_always(plume)
            self._meshes[kind] = PropMeshes(structure, lights, plumes, windows, shadow)

    def _shadow_mesh(self, scene: Any, kind: str, geometry: PropGeometry) -> Any:  # noqa: ANN401
        """D-212: the mesh of the shadow's stand-in of `kind`, if it has one and there are shadows
        (`on_structure`)."""
        if geometry.shadow == None or self._on_structure is None:  # noqa: E711 (absent: undefined)
            return None
        if self._shadow_material is None:
            self._shadow_material = shadow_only_material(scene)
        mesh = _part_mesh("prop-" + kind + "-shadow", geometry.shadow, self._shadow_material, scene)
        if mesh is not None:
            # On a layer no camera sees: only the shadow map draws it.
            mesh.layerMask = SHADOW_ONLY_LAYER
        return mesh

    def update_plumes(self, frame: PlumeFrame) -> None:
        """Phase 10: moves the smoke and steam of the props on to this frame."""
        for material in self._plume_materials.values():
            material.set(frame)

    @property
    def plume_count(self) -> int:
        """Plume meshes drawn (phase 10)."""
        count = 0
        for m in self._meshes.values():
            for p in m.plumes:
                if is_enabled(p):
                    count += 1
        return count

    @property
    def count(self) -> int:
        """Number of props in the scene."""
        count = 0
        for kinds in self._chunk_kinds:
            for props in kinds.values():
                count += len(props.placements)
        return count

    @property
    def light_meshes(self) -> list[Any]:
        """Meshes of the self-lit accents and windows (e.g. for a glow layer)."""
        out: list[Any] = []
        for m in self._meshes.values():
            if m.lights is not None:
                out.append(m.lights)
            if m.windows is not None:
                out.append(m.windows)
        return out

    @property
    def window_meshes(self) -> list[Any]:
        """Meshes of the windows (D-210: a glow layer draws them with their own material)."""
        return [m.windows for m in self._meshes.values() if m.windows is not None]

    @property
    def structure_meshes(self) -> list[Any]:
        """Meshes of the lit structures and of the imposters (e.g. to hide the lights behind them
        in a glow layer)."""
        meshes = [m.structure for m in self._meshes.values() if m.structure is not None]
        if self._imposters is not None:
            meshes.extend(self._imposters.meshes)
        return meshes

    def bake_imposters(self) -> None:
        """D-212: bakes the imposters' pictures (the first time only). Not while the ground adopts
        what is made: the bake's mesh must not hang from it."""
        if self._imposters is not None:
            self._imposters.bake_once()

    def structure_of(self, kind: str) -> Any:
        """The structure mesh of a kind of prop."""
        m = self._meshes.get(kind)
        return m.structure if m else None

    def set_chunk(self, index: int, placements: list[PropPlacement]) -> None:
        """Sets the placements of chunk `index`, grouped by kind."""
        kinds: dict[str, KindProps] = {}
        self._group(kinds, placements)
        at = self._chunk_at(index)
        if at < 0:
            self._chunk_indices.append(index)
            self._chunk_kinds.append(kinds)
        else:
            self._chunk_kinds[at] = kinds
        self._dirty = True

    def add_to_chunk(self, index: int, placements: list[PropPlacement]) -> None:
        """Adds `placements` to those of chunk `index` (D-212: a row of trees at a time): the
        props already there keep their instance matrices, and nothing is uploaded again unless one
        of `placements` is in the window. A chunk that is not set (removed meanwhile) takes none."""
        at = self._chunk_at(index)
        if at < 0:
            return
        self._group(self._chunk_kinds[at], placements)
        window = self._window
        for p in placements:
            if window is None or (p.z >= window[0] and p.z <= window[1]):
                self._dirty = True
                return

    def _group(self, kinds: dict[str, KindProps], placements: list[PropPlacement]) -> None:
        """Adds `placements` to `kinds`, by kind (each must have a model)."""
        for p in placements:
            if p.kind not in self._meshes:
                raise ValueError('No model for prop "' + p.kind + '"')
            props = kinds.get(p.kind)
            if props:
                props.placements.append(p)
            else:
                kinds[p.kind] = KindProps([p])

    def _chunk_at(self, index: int) -> int:
        """Where chunk `index` is in the chunk lists, or -1 if it is not set."""
        for i in range(len(self._chunk_indices)):
            if self._chunk_indices[i] == index:
                return i
        return -1

    def remove_chunk(self, index: int) -> None:
        at = self._chunk_at(index)
        if at < 0:
            return
        self._chunk_indices.pop(at)
        self._chunk_kinds.pop(at)
        self._dirty = True

    def clear(self) -> None:
        self._chunk_indices = []
        self._chunk_kinds = []
        self._dirty = True

    def set_window(self, z_min: float, z_max: float, step: float) -> None:
        """Draws only the props whose Z is in [z_min, z_max] (phase 4 review): the terrain chunks
        reach well past the view, and their props would be drawn for nothing. The instances are
        uploaded again only when the window leaves the range drawn, which is `step` wider on both
        sides."""
        drawn = self._window
        if drawn is not None and z_min >= drawn[0] and z_max <= drawn[1]:
            return
        # A step wider than asked, so the view can move by a step before the next upload.
        self._window = [z_min - step, z_max + step]
        self._dirty = True

    def drift(self, drifts: dict[str, PropDrift], time: float) -> None:
        """Moves the kinds that drift (phase 8: ice floes on the sea) to where they are `time`
        seconds in: to and fro around where they were placed, each kind on its own course."""
        for kind, d in drifts.items():
            meshes = self._meshes.get(kind)
            if not meshes:
                continue
            phase = (2 * math.pi * time) / d.period
            for mesh in self._mesh_list(meshes):
                mesh.position.set(d.x * math.sin(phase), 0, d.z * math.sin(phase * 0.7 + 1))

    def _mesh_list(self, meshes: PropMeshes) -> list[Any]:
        out: list[Any] = [meshes.structure] if meshes.structure is not None else []
        if meshes.lights is not None:
            out.append(meshes.lights)
        if meshes.windows is not None:
            out.append(meshes.windows)
        if meshes.shadow is not None:
            out.append(meshes.shadow)
        for plume in meshes.plumes:
            out.append(plume)
        return out

    def sync(self) -> None:
        """Uploads the instance matrices if the placements or the window changed since the last
        call."""
        if not self._dirty:
            return
        self._dirty = False
        by_kind = self._by_kind()
        for kind, meshes in self._meshes.items():
            drawn = by_kind.get(kind)
            placements = drawn.placements if drawn else []
            if kind in self._drawn and same_placements(self._drawn[kind], placements):
                continue
            self._drawn[kind] = placements
            matrices = _matrices_of(drawn) if drawn else float32_array(0)
            for mesh in self._mesh_list(meshes):
                if not mesh:
                    continue
                set_enabled(mesh, len(matrices) > 0)
                if len(matrices) == 0:
                    continue
                mesh.thinInstanceSetBuffer("matrix", matrices, MATRIX_FLOATS, False)
        if self._imposters is not None:
            self._place_imposters(by_kind, self._imposters)

    def _place_imposters(self, by_kind: dict[str, Drawn], imposters: "ImposterKinds") -> None:
        """D-212: the imposters of the props drawn."""
        placements: list[PropPlacement] = []
        for kind in imposters.kinds:
            drawn = by_kind.get(kind)
            if drawn:
                placements.extend(drawn.placements)
        imposters.place(placements)

    def _by_kind(self) -> dict[str, Drawn]:
        """The props to draw (in the window, if any), by kind, in the order of the chunks."""
        window = self._window
        by_kind: dict[str, Drawn] = {}
        for kinds in self._chunk_kinds:
            for kind, props in kinds.items():
                for i in range(len(props.placements)):
                    p = props.placements[i]
                    if window is not None and (p.z < window[0] or p.z > window[1]):
                        continue
                    drawn = by_kind.get(kind)
                    if not drawn:
                        drawn = Drawn([], [], [])
                        by_kind[kind] = drawn
                    drawn.placements.append(p)
                    drawn.from_.append(props)
                    drawn.at.append(i)
        return by_kind


def _matrices_of(drawn: Drawn) -> Any:
    """The instance matrices of `drawn`, copied from those of their chunks (made on first use)."""
    buffer = float32_array(len(drawn.at) * MATRIX_FLOATS)
    for j in range(len(drawn.at)):
        i = drawn.at[j]
        matrices = _matrices_for(drawn.from_[j])
        start = i * MATRIX_FLOATS
        buffer.set(matrices.subarray(start, start + MATRIX_FLOATS), j * MATRIX_FLOATS)
    return buffer


def _matrices_for(props: KindProps) -> Any:
    """The instance matrices of `props`, made on first use; those of placements added since are
    made then, the others kept (D-212)."""
    old = props.matrices
    if old is None:
        props.matrices = instance_matrices(props.placements)
        return props.matrices
    count = len(props.placements)
    made = len(old) // MATRIX_FLOATS
    if made == count:
        return old
    buffer = float32_array(count * MATRIX_FLOATS)
    buffer.set(old, 0)
    buffer.set(instance_matrices(props.placements[made:]), made * MATRIX_FLOATS)
    props.matrices = buffer
    return buffer


def same_placements(a: list[PropPlacement], b: list[PropPlacement]) -> bool:
    """Whether `a` and `b` hold the same placements in the same order."""
    if len(a) != len(b):
        return False
    for i in range(len(a)):  # noqa: SIM110
        if a[i] is not b[i]:
            return False
    return True


def instance_matrices(placements: list[PropPlacement]) -> Any:
    """One world matrix per placement (scale, or per-axis size, then turn around Y and position),
    packed for thin instances."""
    buffer = float32_array(len(placements) * MATRIX_FLOATS)
    scale = vector3(0, 0, 0)
    position = vector3(0, 0, 0)
    turn = quaternion(0, 0, 0, 1)
    matrix = new_matrix()
    for i in range(len(placements)):
        p = placements[i]
        if p.size:
            scale.set(p.size[0], p.size[1], p.size[2])
        else:
            scale.setAll(p.scale)
        position.set(p.x, p.y, p.z)
        quaternion_yaw_pitch_roll_to_ref(p.rotation, 0, 0, turn)
        matrix_compose_to_ref(scale, turn, position, matrix)
        matrix.copyToArray(buffer, i * MATRIX_FLOATS)
    return buffer
