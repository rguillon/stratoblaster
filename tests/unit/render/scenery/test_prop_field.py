# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/prop_field.py` (GFX-PROP-01, GFX-PROP-05).

The chunks' placements and instance matrices (D-212: a chunk's trees come a row at a time;
GFX-PROP-14, PERF-25), the meshes made for each kind of prop from its model (D-210 windows, D-212
shadow stand-ins and imposters, phase 10 plumes), what is uploaded as the window moves, and which
kinds a level stands on its ground (GFX-PROP-03). Babylon's meshes, vertex data and matrices are
plain Python stand-ins (ENG-47).
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.level_builders import section
from helpers.render_fakes import FakeNode, FakeTypedArray, FakeVector, patch_babylon
from helpers.sample_level import sample_level, sample_props

from core.scenery.ground_boxes import PropPlacement
from core.scenery.scenery_level import (
    BlockFill,
    CarRules,
    CliffRules,
    Drift,
    FloatRules,
    Landmark,
    Meander,
    PropKindRule,
    PropLine,
    SceneryLevel,
)
from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.textured import TexturedGeometry
from render.scenery import prop_field
from render.scenery.prop_field import (
    MATRIX_FLOATS,
    SHADOW_ONLY_LAYER,
    KindProps,
    PropField,
    PropMaterials,
    PropMeshes,
    _matrices_for,
    _part_mesh,
    check_prop_models,
    instance_matrices,
    level_prop_kinds,
    level_prop_models,
    level_tree_kinds,
    mesh_of,
    prop_drifts,
    prop_geometry,
    same_placements,
    shadow_only_material,
)
from render.scenery.scenery_look import PropGeometry, PropPlume

MADE: list[int] = []
MESHES: list["_Mesh"] = []
NORMALS: list[int] = []


class _Floats(FakeTypedArray):
    """A Float32Array: a fake typed array with `subarray` (a copy is enough here)."""

    def subarray(self, start: int, end: int) -> list[float]:
        return list(self[start:end])


class _Mesh(FakeNode):
    """A mesh: its vertex data and the thin instance buffers uploaded to it."""

    def __init__(self, name: str) -> None:
        super().__init__(name, is_mesh=True)
        self.data: Any = None
        self.buffers: list[tuple[str, list[float], int, bool]] = []

    def thinInstanceSetBuffer(self, kind: str, values: Any, stride: int, static: bool) -> None:
        self.buffers.append((kind, list(values), stride, static))


def _new_mesh(name: str, _scene: Any) -> _Mesh:
    mesh = _Mesh(name)
    MESHES.append(mesh)
    return mesh


def _apply_vertex_data(data: Any, mesh: _Mesh) -> None:
    mesh.data = data


def _compute_normals(positions: list[float], _indices: list[int]) -> list[float]:
    NORMALS.append(len(positions))
    return [0.0, 1.0, 0.0] * (len(positions) // 3)


def _build_plumes(_scene: Any, name: str, plumes: Any, material: Any) -> list[_Mesh]:
    """`build_plume_meshes`: one disabled mesh per plume kind of the model that has a material."""
    ids: list[str] = []
    for p in plumes:
        if p.kind not in ids:
            ids.append(p.kind)
    meshes: list[_Mesh] = []
    for kind_id in ids:
        mat = material(kind_id)
        if not mat:
            continue
        mesh = _new_mesh(name + "-plume-" + kind_id, None)
        mesh.material = mat
        mesh.enabled = False
        meshes.append(mesh)
    return meshes


def _fake_matrices(placements: list[PropPlacement]) -> Any:
    """One matrix per placement, all of its X (so a matrix tells which placement it is)."""
    MADE.append(len(placements))
    buffer = _Floats(len(placements) * MATRIX_FLOATS)
    for i, p in enumerate(placements):
        buffer.set([p.x] * MATRIX_FLOATS, i * MATRIX_FLOATS)
    return buffer


@pytest.fixture(autouse=True)
def _babylon(monkeypatch: pytest.MonkeyPatch) -> None:
    patch_babylon(monkeypatch, prop_field)
    monkeypatch.setattr(prop_field, "float32_array", _Floats)
    monkeypatch.setattr(prop_field, "instance_matrices", _fake_matrices)
    monkeypatch.setattr(prop_field, "new_mesh", _new_mesh)
    monkeypatch.setattr(prop_field, "new_vertex_data", SimpleNamespace)
    monkeypatch.setattr(prop_field, "apply_vertex_data", _apply_vertex_data)
    monkeypatch.setattr(prop_field, "compute_normals", _compute_normals)
    monkeypatch.setattr(prop_field, "is_enabled", lambda node: node.isEnabled())
    monkeypatch.setattr(
        prop_field,
        "new_standard_material",
        lambda name, scene: SimpleNamespace(name=name, scene=scene),
    )
    monkeypatch.setattr(prop_field, "build_plume_meshes", _build_plumes)
    MADE.clear()
    MESHES.clear()
    NORMALS.clear()


def tree(x: float, z: float) -> PropPlacement:
    return PropPlacement("tree", x, 0, z, 0, 1)


def field() -> PropField:
    f = PropField(None, {}, None)
    f._meshes = {"tree": PropMeshes(None, None, []), "hut": PropMeshes(None, None, [])}
    return f


def test_d212_trees_added_to_a_chunk_join_its_props() -> None:
    f = field()
    f.set_chunk(3, [PropPlacement("hut", 0, 0, 10, 0, 1)])
    f.add_to_chunk(3, [tree(1, 20), tree(2, 30)])
    f.add_to_chunk(3, [tree(3, 40)])
    assert f.count == 4
    assert [p.x for p in f._chunk_kinds[0]["tree"].placements] == [1, 2, 3]


def test_d212_trees_added_to_a_chunk_that_is_gone_are_dropped() -> None:
    f = field()
    f.set_chunk(3, [tree(1, 20)])
    f.remove_chunk(3)
    f.add_to_chunk(3, [tree(2, 30)])
    assert f.count == 0
    assert f._chunk_indices == []


def test_d212_trees_added_out_of_the_window_upload_nothing() -> None:
    f = field()
    f.set_chunk(3, [tree(1, 20)])
    f.set_window(0, 100, 10)
    f._dirty = False
    f.add_to_chunk(3, [tree(2, 500)])
    assert not f._dirty
    f.add_to_chunk(3, [tree(3, 50)])
    assert f._dirty


def test_a_chunk_set_again_replaces_its_props_and_a_missing_one_is_removed_quietly() -> None:
    f = field()
    f.set_chunk(1, [tree(1, 20)])
    f.set_chunk(2, [tree(2, 20)])
    f.set_chunk(1, [tree(3, 20), tree(4, 20)])
    assert f._chunk_indices == [1, 2]
    assert f.count == 3
    f._dirty = False
    f.remove_chunk(9)
    assert not f._dirty
    f.remove_chunk(1)
    assert f._dirty
    assert f._chunk_indices == [2]


def test_a_prop_without_a_model_is_refused() -> None:
    f = field()
    with pytest.raises(ValueError, match="No model"):
        f.set_chunk(1, [PropPlacement("ufo", 0, 0, 0, 0, 1)])
    f.set_chunk(1, [])
    with pytest.raises(ValueError, match="No model"):
        f.add_to_chunk(1, [PropPlacement("ufo", 0, 0, 0, 0, 1)])


def test_d212_the_matrices_are_made_once_and_only_those_of_new_trees_after() -> None:
    props = KindProps([tree(1, 0), tree(2, 0)])
    first = _matrices_for(props)
    # Made in one go the first time, and kept.
    assert MADE == [2]
    assert _matrices_for(props) is first
    assert MADE == [2]
    props.placements.append(tree(3, 0))
    grown = _matrices_for(props)
    assert MADE == [2, 1]
    assert list(grown) == [1] * MATRIX_FLOATS + [2] * MATRIX_FLOATS + [3] * MATRIX_FLOATS
    assert props.matrices is grown


def test_d199_a_prop_s_bounds_are_the_box_round_its_structure() -> None:
    positions = [0, 0, 0, 4, 1, -2, -1, 9, 3]
    geometry = SimpleNamespace(structure=SimpleNamespace(positions=positions))
    assert prop_field.prop_bounds(lambda: geometry) == [-1, 0, -2, 4, 9, 3]
    empty = SimpleNamespace(structure=SimpleNamespace(positions=[]))
    assert prop_field.prop_bounds(lambda: empty) == [0, 0, 0, 0, 0, 0]


# The meshes of each kind of prop, made from its model.

MATERIALS = PropMaterials("structure-material", "lights-material", "windows-material")


def _triangle(z: float = 0, textured: bool = False) -> ColoredGeometry:
    geo = TexturedGeometry() if textured else ColoredGeometry()
    geo.positions = [0.0, 0.0, z, 1.0, 0.0, z, 0.0, 1.0, z + 1]
    geo.indices = [0, 1, 2]
    geo.colors = [1.0] * 12
    if isinstance(geo, TexturedGeometry):
        geo.uvs = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    return geo


def _hut_model() -> PropGeometry:
    """Return a hut: walls, lamps, windows and a chimney sending up smoke (two puffs) and steam."""
    plumes = [
        PropPlume((0, 4, 0), "smoke"),
        PropPlume((1, 4, 0), "smoke", 2),
        PropPlume((0, 3, 1), "steam"),
    ]
    return PropGeometry(_triangle(), _triangle(1), plumes, _triangle(2, textured=True))


def _tree_model() -> PropGeometry:
    """Return a tree with a structure: it casts its own shadow, its stand-in is not needed."""
    return PropGeometry(_triangle(), shadow=_triangle(3))


def _car_model() -> PropGeometry:
    """D-211: a car's lights only (its body an imposter), with a stand-in for its shadow."""
    return PropGeometry(ColoredGeometry(), _triangle(1), shadow=_triangle(3))


class _PlumeMaterial:
    """A plume kind's material: the frames it was set to."""

    def __init__(self, kind: Any) -> None:
        self.kind = kind
        self.material = SimpleNamespace(name="plume", kind=kind)
        self.frames: list[Any] = []

    def set(self, frame: Any) -> None:
        self.frames.append(frame)


class _PlumeMaterials:
    """The plume material factory: the materials it made."""

    def __init__(self) -> None:
        self.made: list[_PlumeMaterial] = []

    def __call__(self, _scene: Any, kind: Any) -> _PlumeMaterial:
        material = _PlumeMaterial(kind)
        self.made.append(material)
        return material


def hut(x: float, z: float) -> PropPlacement:
    return PropPlacement("hut", x, 0, z, 0, 1)


def test_prop_materials_have_no_windows_unless_given() -> None:
    plain = PropMaterials("s", "l")
    assert (plain.structure, plain.lights, plain.windows) == ("s", "l", None)
    assert PropMaterials("s", "l", "w").windows == "w"


def test_gfx_prop_05_a_kind_s_structure_is_lit_shadowed_unpickable_hidden_and_drawn_always() -> (
    None
):
    casters: list[Any] = []
    f = PropField("scene", {"hut": _hut_model}, MATERIALS, casters.append)
    structure = f._meshes["hut"].structure
    assert structure.name == "prop-hut"
    assert structure.material == "structure-material"
    assert structure.data.positions == _triangle().positions
    assert structure.data.normals == [0.0, 1.0, 0.0] * 3
    assert not hasattr(structure.data, "uvs")
    assert structure.receiveShadows is True
    assert structure.isPickable is False
    assert structure.enabled is False
    # PERF-26: its bounds are never fitted to its instances.
    assert structure.alwaysSelectAsActiveMesh is True
    assert structure.doNotSyncBoundingInfo is True
    assert casters == [structure]
    assert "tower" not in f._meshes


def test_d210_a_kind_s_lights_and_windows_are_meshes_of_their_own_for_the_glow() -> None:
    """GFX-BLDG-16."""
    f = PropField("scene", {"hut": _hut_model, "tree": _tree_model}, MATERIALS)
    meshes = f._meshes["hut"]
    assert meshes.lights.name == "prop-hut-lights"
    assert meshes.lights.material == "lights-material"
    assert meshes.windows.name == "prop-hut-windows"
    assert meshes.windows.material == "windows-material"
    # The windows are mapped on their atlas.
    assert meshes.windows.data.uvs == [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    assert meshes.windows.alwaysSelectAsActiveMesh is True
    assert f.light_meshes == [meshes.lights, meshes.windows]
    assert f.window_meshes == [meshes.windows]
    assert f.structure_meshes == [meshes.structure, f._meshes["tree"].structure]
    # The tree has neither.
    assert (f._meshes["tree"].lights, f._meshes["tree"].windows) == (None, None)


def test_d210_without_a_windows_material_the_windows_are_not_drawn() -> None:
    f = PropField("scene", {"hut": _hut_model}, PropMaterials("s", "l"))
    assert f._meshes["hut"].windows is None
    assert f.window_meshes == []
    assert f.light_meshes == [f._meshes["hut"].lights]


def test_a_part_without_geometry_triangles_or_material_has_no_mesh() -> None:
    assert _part_mesh("part", None, "material", "scene") is None
    assert _part_mesh("part", _triangle(), None, "scene") is None
    assert _part_mesh("part", ColoredGeometry(), "material", "scene") is None
    assert MESHES == []
    mesh = _part_mesh("part", _triangle(), "material", "scene")
    assert mesh.name == "part"
    assert mesh.alwaysSelectAsActiveMesh is True


def test_a_mesh_of_a_geometry_takes_its_vertices_colours_and_normals() -> None:
    geo = _triangle(textured=True)
    mesh = mesh_of("m", geo, "material", "scene")
    assert mesh.data.positions is geo.positions
    assert mesh.data.indices is geo.indices
    assert mesh.data.colors is geo.colors
    assert mesh.data.uvs is geo.uvs
    assert mesh.material == "material"
    assert (mesh.isPickable, mesh.enabled) == (False, False)


def test_d212_the_shadow_only_material_writes_neither_colour_nor_depth() -> None:
    """GFX-PROP-12."""
    material = shadow_only_material("scene")
    assert material.name == "prop-shadow-only"
    assert material.scene == "scene"
    assert material.disableColorWrite is True
    assert material.disableDepthWrite is True
    assert material.disableLighting is True


def test_d212_a_model_without_structure_casts_its_shadow_through_a_stand_in() -> None:
    """GFX-PROP-12: on a layer no camera sees, all stand-ins sharing one material."""
    casters: list[Any] = []
    models = {"car": _car_model, "van": _car_model, "tree": _tree_model}
    f = PropField("scene", models, MATERIALS, casters.append)
    car = f._meshes["car"]
    assert car.structure is None
    assert car.shadow.name == "prop-car-shadow"
    assert car.shadow.layerMask == SHADOW_ONLY_LAYER
    assert car.shadow.material.disableColorWrite is True
    assert f._meshes["van"].shadow.material is car.shadow.material
    # The tree's structure casts its shadow: it has no stand-in.
    assert f._meshes["tree"].shadow is None
    assert casters == [car.shadow, f._meshes["van"].shadow, f._meshes["tree"].structure]
    # Its lights are drawn, and a kind without structure is no glow occluder.
    assert f.light_meshes == [car.lights, f._meshes["van"].lights]
    assert f.structure_meshes == [f._meshes["tree"].structure]


def test_d212_no_shadow_stand_in_without_shadows_or_without_its_geometry() -> None:
    without_shadows = PropField("scene", {"car": _car_model}, MATERIALS)
    assert without_shadows._meshes["car"].shadow is None
    assert without_shadows._shadow_material is None

    def no_stand_in() -> PropGeometry:
        return PropGeometry(ColoredGeometry(), _triangle())

    def empty_stand_in() -> PropGeometry:
        return PropGeometry(ColoredGeometry(), _triangle(), shadow=ColoredGeometry())

    casters: list[Any] = []
    f = PropField("scene", {"a": no_stand_in, "b": empty_stand_in}, MATERIALS, casters.append)
    assert f._meshes["a"].shadow is None
    assert f._meshes["b"].shadow is None
    assert casters == []


def test_gfx_prop_18_each_plume_kind_of_a_model_gets_a_mesh_with_one_material_per_kind() -> None:
    plumes = _PlumeMaterials()

    def glitter_hut() -> PropGeometry:
        geometry = _hut_model()
        geometry.plumes = [*geometry.plumes, PropPlume((0, 1, 0), "glitter")]
        return geometry

    f = PropField("scene", {"hut": glitter_hut, "shed": _hut_model}, MATERIALS, None, plumes)
    hut_plumes = f._meshes["hut"].plumes
    # Smoke and steam; no plume kind is called glitter.
    assert [m.name for m in hut_plumes] == ["prop-hut-plume-smoke", "prop-hut-plume-steam"]
    assert all(m.alwaysSelectAsActiveMesh for m in hut_plumes)
    # The shed's smoke and steam share the hut's materials.
    assert [m.kind for m in plumes.made] == [
        prop_field.PLUME_KINDS["smoke"],
        prop_field.PLUME_KINDS["steam"],
    ]
    assert f._meshes["shed"].plumes[0].material is hut_plumes[0].material
    assert f.plume_count == 0
    f.update_plumes("frame")
    assert [m.frames for m in plumes.made] == [["frame"], ["frame"]]


def test_gfx_prop_18_without_plume_materials_no_plume_is_drawn() -> None:
    f = PropField("scene", {"hut": _hut_model}, MATERIALS)
    assert f._meshes["hut"].plumes == []
    assert f.plume_count == 0
    f.update_plumes("frame")


def test_a_model_without_plumes_has_no_plume_meshes() -> None:
    f = PropField("scene", {"tree": _tree_model}, MATERIALS, None, _PlumeMaterials())
    assert f._meshes["tree"].plumes == []


def test_perf_11_the_geometry_of_a_model_and_its_normals_are_made_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PERF-22: kept on the model (a JavaScript property in the browser; a dict here)."""
    slots: dict[tuple[int, str], Any] = {}
    monkeypatch.setattr(prop_field, "_slot_get", lambda o, s: slots.get((id(o), s)))
    monkeypatch.setattr(prop_field, "_slot_set", lambda o, s, v: slots.__setitem__((id(o), s), v))
    made: list[PropGeometry] = []

    def model() -> PropGeometry:
        made.append(_tree_model())
        return made[-1]

    first = prop_geometry(model)
    assert prop_geometry(model) is first
    assert len(made) == 1
    PropField("scene", {"tree": model}, MATERIALS)
    PropField("scene", {"tree": model}, MATERIALS)
    assert len(made) == 1
    assert NORMALS == [9]


def test_the_cached_slots_are_javascript_only() -> None:
    """JavaScript-only: under CPython nothing is kept, so a model is made on each use."""
    made: list[int] = []

    def model() -> PropGeometry:
        made.append(1)
        return _tree_model()

    prop_geometry(model)
    prop_geometry(model)
    assert made == [1, 1]
    assert prop_field._slot_get(model, "x") is None


# What is drawn as the window and the chunks change (GFX-PROP-05, PERF-25).


def _hut_field() -> PropField:
    return PropField(
        "scene", {"hut": _hut_model, "tree": _tree_model}, MATERIALS, None, _PlumeMaterials()
    )


def test_perf_25_the_props_in_the_window_are_uploaded_to_every_mesh_of_their_kind() -> None:
    f = _hut_field()
    f.set_chunk(0, [hut(1, 10), hut(2, 500)])
    f.set_chunk(1, [hut(3, 60)])
    f.set_window(0, 90, 10)
    f.sync()
    meshes = f._mesh_list(f._meshes["hut"])
    # Structure, lights, windows, smoke and steam.
    assert len(meshes) == 5
    for mesh in meshes:
        assert mesh.enabled is True
        [(kind, values, stride, static)] = mesh.buffers
        assert (kind, stride, static) == ("matrix", MATRIX_FLOATS, False)
        # In the order of the chunks: the hut at Z 500 is out of the window.
        assert values == [1] * MATRIX_FLOATS + [3] * MATRIX_FLOATS
    assert f.plume_count == 2
    assert f.count == 3
    # A kind with no prop in the window is hidden, and nothing is uploaded to it.
    tree = f._meshes["tree"].structure
    assert tree.enabled is False
    assert tree.buffers == []


def test_perf_25_nothing_is_uploaded_again_while_the_window_stays_in_the_range_drawn() -> None:
    f = _hut_field()
    f.set_chunk(0, [hut(1, 10), hut(2, 500)])
    f.set_window(0, 90, 10)
    f.sync()
    structure = f._meshes["hut"].structure
    f.sync()
    # Inside [-10, 100], the range drawn: not even a new window.
    f.set_window(5, 95, 10)
    assert f._window == [-10, 100]
    assert f._dirty is False
    f.sync()
    assert len(structure.buffers) == 1
    # A wider window that still holds the same props uploads nothing either.
    f.set_window(0, 120, 10)
    assert f._dirty is True
    f.sync()
    assert len(structure.buffers) == 1


def test_perf_25_a_window_on_other_props_uploads_them_and_one_on_none_hides_the_kind() -> None:
    f = _hut_field()
    f.set_chunk(0, [hut(1, 10), hut(2, 500)])
    f.set_window(0, 90, 10)
    f.sync()
    f.set_window(450, 550, 10)
    f.sync()
    structure = f._meshes["hut"].structure
    assert structure.buffers[-1][1] == [2] * MATRIX_FLOATS
    assert structure.enabled is True
    f.set_window(1000, 1100, 10)
    f.sync()
    assert structure.enabled is False
    assert len(structure.buffers) == 2
    assert f.plume_count == 0


def test_without_a_window_every_prop_of_the_chunks_is_drawn() -> None:
    f = _hut_field()
    f.set_chunk(4, [hut(1, -900), hut(2, 9000)])
    f.sync()
    assert f._meshes["hut"].structure.buffers[-1][1] == [1] * MATRIX_FLOATS + [2] * MATRIX_FLOATS


class _Imposters:
    """D-212: the kinds drawn as imposters, their models, quads, bakes and placements."""

    def __init__(self, models: dict[str, Any], kinds: list[str]) -> None:
        self.models = models
        self.kinds = kinds
        self.meshes = ["imposter-quads"]
        self.bakes = 0
        self.placed: list[list[PropPlacement]] = []

    def bake_once(self) -> None:
        self.bakes += 1

    def place(self, placements: list[PropPlacement]) -> None:
        self.placed.append(list(placements))


def test_d212_kinds_drawn_as_imposters_are_made_from_the_imposters_models() -> None:
    """GFX-PROP-11."""
    imposters = _Imposters({"tree": _car_model, "hut": _hut_model}, ["tree", "oak"])
    f = PropField("scene", {"ignored": _hut_model}, MATERIALS, None, None, imposters)  # type: ignore[arg-type]
    assert list(f._meshes) == ["tree", "hut"]
    # The imposters' quads hide the lights behind them, as the structures do.
    assert f.structure_meshes == [f._meshes["hut"].structure, "imposter-quads"]
    assert imposters.bakes == 0
    f.bake_imposters()
    assert imposters.bakes == 1


def test_d212_the_imposters_are_placed_where_their_kinds_props_are_drawn() -> None:
    imposters = _Imposters({"tree": _car_model, "hut": _hut_model}, ["tree", "oak"])
    f = PropField("scene", {}, MATERIALS, None, None, imposters)  # type: ignore[arg-type]
    trees = [tree(1, 5), tree(3, 7)]
    f.set_chunk(0, [trees[0], hut(2, 6), trees[1]])
    f.sync()
    # The oaks have no prop drawn: only the trees are placed.
    assert imposters.placed == [trees]


def test_without_imposters_there_is_nothing_to_bake() -> None:
    f = _hut_field()
    f.bake_imposters()
    assert f._imposters is None
    assert f.structure_meshes == [f._meshes["hut"].structure, f._meshes["tree"].structure]


def test_gfx_prop_15_drifting_kinds_move_every_mesh_to_and_fro_where_they_were_placed() -> None:
    """GFX-PROP-16: each kind on its own course; kinds the field has not are left out."""
    casters: list[Any] = []
    models = {"hut": _hut_model, "car": _car_model, "tree": _tree_model}
    f = PropField("scene", models, MATERIALS, casters.append, _PlumeMaterials())
    f.drift({"hut": Drift(4, 2, 10), "car": Drift(1, 3, 5), "boat": Drift(9, 9, 1)}, 2.5)
    hut_phase = 2 * math.pi * 2.5 / 10
    for mesh in f._mesh_list(f._meshes["hut"]):
        position = (mesh.position.x, mesh.position.y, mesh.position.z)
        expected = (4 * math.sin(hut_phase), 0, 2 * math.sin(hut_phase * 0.7 + 1))
        assert position == pytest.approx(expected)
    car = f._meshes["car"]
    # The car's lights and its shadow's stand-in move together.
    assert f._mesh_list(car) == [car.lights, car.shadow]
    car_phase = 2 * math.pi * 2.5 / 5
    assert car.shadow.position.x == pytest.approx(math.sin(car_phase))
    assert car.lights.position.z == car.shadow.position.z
    tree_mesh = f._meshes["tree"].structure
    assert (tree_mesh.position.x, tree_mesh.position.z) == (0, 0)


def test_same_placements_are_the_same_objects_in_the_same_order() -> None:
    a, b = tree(1, 2), tree(1, 2)
    assert same_placements([a, b], [a, b])
    assert same_placements([], [])
    assert not same_placements([a], [a, b])
    assert not same_placements([a, b], [b, a])
    # Equal values are not the same placement.
    assert not same_placements([a], [tree(1, 2)])


class _Vector(FakeVector):
    def setAll(self, value: float) -> None:
        self.set(value, value, value)


class _Matrix:
    """A matrix that copies out what it was composed of: scale, yaw and position."""

    def __init__(self) -> None:
        self.values = [0.0] * MATRIX_FLOATS

    def copyToArray(self, array: Any, offset: int) -> None:
        array.set(self.values, offset)


def _compose(scale: _Vector, turn: Any, position: _Vector, matrix: _Matrix) -> None:
    head = [scale.x, scale.y, scale.z, turn.yaw, position.x, position.y, position.z]
    matrix.values = head + [0.0] * (MATRIX_FLOATS - len(head))


def _yaw_to_ref(yaw: float, pitch: float, roll: float, ref: Any) -> None:
    assert (pitch, roll) == (0, 0)
    ref.yaw = yaw


def test_eng_104_each_placement_gets_a_matrix_of_its_scale_turn_and_position(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(prop_field, "vector3", _Vector)
    monkeypatch.setattr(prop_field, "quaternion", lambda *_q: SimpleNamespace(yaw=None))
    monkeypatch.setattr(prop_field, "new_matrix", _Matrix)
    monkeypatch.setattr(prop_field, "matrix_compose_to_ref", _compose)
    monkeypatch.setattr(prop_field, "quaternion_yaw_pitch_roll_to_ref", _yaw_to_ref)
    placements = [
        PropPlacement("tree", 1, 2, 3, 0.5, 1.5),
        # A podium stretched to its block: its size per axis.
        PropPlacement("podium", 4, 5, 6, 1.0, 1, [10, 2, 8]),
    ]
    buffer = instance_matrices(placements)
    assert len(buffer) == 2 * MATRIX_FLOATS
    assert buffer[:7] == [1.5, 1.5, 1.5, 0.5, 1, 2, 3]
    assert buffer[MATRIX_FLOATS : MATRIX_FLOATS + 7] == [10, 2, 8, 1.0, 4, 5, 6]
    assert list(instance_matrices([])) == []


# The kinds a level stands on its ground (GFX-PROP-03).


def _kind(kind_id: str, drift: Drift | None = None) -> PropKindRule:
    return PropKindRule(kind_id, 1, 2, [1, 1], drift=drift)


def _rich_level() -> SceneryLevel:
    """Return a level with every source of props, and cars.

    Building groups, trees, floating props, lines, podiums, set pieces and lots.
    """
    city = section("city", trees=[], blocks=BlockFill(["podium"], (1, 2), (1, 2)))
    woods = section("woods", trees=["stick"])
    props = sample_props(
        floating=FloatRules(10, 1, 2, [_kind("floe", Drift(3, 1, 8)), _kind("berg")]),
        lines=[
            PropLine("pipe", Meander(0, 0, 100), 10, 2, 0.5),
            PropLine("wagon", Meander(0, 0, 100), 20, 2, 0.5, drift=Drift(5, 0, 6)),
            PropLine("pipe", Meander(50, 0, 100), 10, 2, 0.5),
        ],
        landmarks=[Landmark("dam", 100, (10, 10))],
        lots=[_kind("park")],
        cars=CarRules(["sedan"], 0.1, 0.2, 1, 4, (5, 10)),
        cliffs=CliffRules(["crag"], 0.5, 7, (6, 10), (4, 8), 2),
    )
    return sample_level(sections=[city, woods], props=props)


RICH_KINDS = ["block", "stick", "floe", "berg", "pipe", "wagon", "podium", "dam", "park", "crag"]


def test_gfx_prop_03_a_level_stands_every_kind_of_its_sections_and_set_pieces_once() -> None:
    assert level_prop_kinds(_rich_level()) == RICH_KINDS


def test_gfx_prop_03_a_plain_level_stands_its_buildings_and_trees_only() -> None:
    assert level_prop_kinds(sample_level()) == ["block", "stick"]


def test_d214_the_tree_kinds_are_those_its_sections_allow() -> None:
    """GFX-PROP-10: the ones the imposters are baked for."""
    assert level_tree_kinds(_rich_level()) == ["stick"]
    assert level_tree_kinds(sample_level(sections=[section("bare", trees=[])])) == []


def test_gfx_prop_15_the_kinds_that_drift_are_the_floating_ones_and_lines_with_a_drift() -> None:
    """GFX-PROP-16."""
    drifts = prop_drifts(_rich_level())
    assert sorted(drifts) == ["floe", "wagon"]
    assert (drifts["floe"].x, drifts["wagon"].period) == (3, 6)
    assert prop_drifts(sample_level()) == {}


def test_perf_22_only_the_models_of_the_level_s_kinds_are_built() -> None:
    models = dict.fromkeys([*RICH_KINDS, "sedan", "castle"], _tree_model)
    built = level_prop_models(_rich_level(), models)
    # Not the cars (the traffic builds those), nor kinds of other levels.
    assert sorted(built) == sorted(RICH_KINDS)


def test_a_level_kind_or_car_without_a_model_is_refused() -> None:
    level = _rich_level()
    models = dict.fromkeys(RICH_KINDS, _tree_model)
    with pytest.raises(ValueError, match='No model for prop "sedan"'):
        check_prop_models(level, models)
    del models["dam"]
    models["sedan"] = _tree_model
    with pytest.raises(ValueError, match='No model for prop "dam"'):
        level_prop_models(level, models)
    # A level without cars needs no car model.
    check_prop_models(sample_level(), {"block": _tree_model, "stick": _tree_model})
