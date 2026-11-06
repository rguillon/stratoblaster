# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_shot_renderer.py`."""

import math
from types import SimpleNamespace
from typing import Any, ClassVar
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon
from helpers.render_fakes import FakeTypedArray

from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY
from game.config.record import record
from game.view.enemies import enemy_shot_renderer as sr
from render import node_pool

BULLETS = ENEMY_LOOK.bullets
RED = [1.0, 0.0, 0.0]
GREEN = [0.0, 1.0, 0.0]
BLACK = [0.0, 0.0, 0.0]


def test_disc_alphas_are_the_centre_then_each_ring_at_its_fade() -> None:
    # The centre vertex is one vertex; each further ring has `segments` vertices.
    alphas = sr.disc_alphas(4, [1.0, 0.5, 0.0])
    assert alphas == [1.0, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0]


def test_disc_with_no_rings_has_no_vertices() -> None:
    assert sr.disc_alphas(8, []) == []


def test_halo_flickers_around_its_size_at_its_flicker_rate() -> None:
    halo = BULLETS.halo
    assert sr.halo_scale(0) == pytest.approx(halo.size)
    quarter = 1 / (4 * halo.flickerHz)
    assert sr.halo_scale(quarter) == pytest.approx(halo.size * (1 + halo.flicker))
    assert sr.halo_scale(3 * quarter) == pytest.approx(halo.size * (1 - halo.flicker))


def test_core_pulses_around_its_size_at_its_pulse_rate() -> None:
    core = BULLETS.core
    assert sr.core_scale(0) == pytest.approx(core.size)
    quarter = 1 / (4 * core.pulse.hz)
    assert sr.core_scale(quarter) == pytest.approx(core.size * (1 + core.pulse.amount))


def test_drawn_radius_follows_the_bullet_but_never_goes_under_half_the_minimum_size() -> None:
    minimum = READABILITY.minEnemyBulletSize
    big = SimpleNamespace(radius=10)
    tiny = SimpleNamespace(radius=0.0001)
    assert sr.drawn_radius(big) == pytest.approx(10 * BULLETS.scale)
    assert sr.drawn_radius(tiny) == pytest.approx(minimum / 2)


def test_placements_scale_the_radius_by_the_layer_rule() -> None:
    b = SimpleNamespace(age=0.0, heading=0.0)
    assert sr.body_placement(b, 2.0) == pytest.approx([2.0, 0])
    assert sr.halo_placement(b, 2.0) == pytest.approx([2.0 * BULLETS.halo.size, 0])
    assert sr.core_placement(b, 2.0) == pytest.approx([2.0 * BULLETS.core.size, 0])
    assert sr.fixed_placement(0.25)(b, 4.0) == pytest.approx([1.0, 0])


def test_swirl_grows_with_its_size_and_turns_with_heading_and_age() -> None:
    swirl = SimpleNamespace(size=0.5, spinRadPerSec=2.0)
    b = SimpleNamespace(age=0.5, heading=1.0)
    place = sr.swirl_placement(swirl)
    assert place(b, 10.0) == pytest.approx([5.0, 1.0 * 3 + 2.0 * 0.5])


# --- The bullet layers, missiles and the renderer, over Babylon stand-ins (ENG-47). ---


def _mesh(label: str = "mesh", material: bool = True) -> MagicMock:
    """Return a mesh stand-in: `name` is its node name, with a material unless told otherwise."""
    mesh = MagicMock(name=label)
    mesh.name = label
    if not material:
        mesh.material = None
    return mesh


@pytest.fixture
def typed_arrays(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make the layers' buffers typed arrays (`set(values, offset)`), as in the browser."""
    monkeypatch.setattr(sr, "_float32_array", FakeTypedArray)
    monkeypatch.setattr(sr, "babylon_constant", lambda key: key)


def test_float32_array_falls_back_to_a_zero_filled_list_in_cpython() -> None:
    """The `__pragma__("skip")` body CPython runs: a list of zeros, not a typed array."""
    assert sr._float32_array(3) == [0.0, 0.0, 0.0]


@pytest.mark.parametrize(("n", "expected"), [(0, 0), (1, 0), (2, 1), (3, 2), (16, 4), (17, 5)])
def test_ceil_log2_is_the_power_of_two_a_count_rounds_up_to(n: int, expected: int) -> None:
    assert sr._ceil_log2(n) == expected


@pytest.mark.usefixtures("typed_arrays")
def test_perf_20_a_bullet_layer_starts_thin_instanced_and_hidden() -> None:
    mesh = _mesh()
    layer = sr.BulletLayer(mesh, -1.1, 2)
    # One instance (a zero matrix) in a buffer of 16, so the shader compiles before play.
    assert len(layer.matrices) == 16 * 16
    mesh.thinInstanceSetBuffer.assert_called_once_with("matrix", layer.matrices, 16, False)
    assert mesh.thinInstanceCount == 1
    mesh.setEnabled.assert_called_once_with(False)


@pytest.mark.usefixtures("typed_arrays")
def test_gfx_read_10_a_bullet_layer_is_drawn_over_everything_in_layer_order() -> None:
    mesh = _mesh()
    sr.BulletLayer(mesh, -1.0, 3)
    assert mesh.alphaIndex == sr.ON_TOP + 3
    assert mesh.alphaIndex > sr.ON_TOP_ALPHA_INDEX
    assert mesh.alwaysSelectAsActiveMesh is True
    assert mesh.material.depthFunction == "ALWAYS"


@pytest.mark.usefixtures("typed_arrays")
def test_a_bullet_layer_without_a_material_has_no_depth_function_to_set() -> None:
    mesh = _mesh(material=False)
    sr.BulletLayer(mesh, -1.0, 0)
    assert mesh.material is None
    assert mesh.alphaIndex == sr.ON_TOP


@pytest.mark.usefixtures("typed_arrays")
def test_a_bullet_layer_with_no_spots_is_hidden() -> None:
    mesh = _mesh()
    layer = sr.BulletLayer(mesh, -1.0, 0)
    mesh.reset_mock()
    layer.show([])
    mesh.setEnabled.assert_called_once_with(False)
    mesh.thinInstanceBufferUpdated.assert_not_called()


@pytest.mark.usefixtures("typed_arrays")
def test_gfx_shot_13_each_spot_is_one_instance_turned_and_scaled_at_the_layer_depth() -> None:
    mesh = _mesh()
    layer = sr.BulletLayer(mesh, -1.2, 0)
    mesh.reset_mock()
    layer.show([[10.0, 20.0, 2.0, 0.0], [5.0, 6.0, 3.0, math.pi / 2]])
    mesh.setEnabled.assert_called_once_with(True)
    assert layer.matrices[0:16] == pytest.approx([
        2.0,
        0,
        0,
        0,
        0,
        2.0,
        0,
        0,
        0,
        0,
        1,
        0,
        10.0,
        20.0,
        -1.2,
        1,
    ])
    # A quarter turn: the X axis is along +Y.
    assert layer.matrices[16:32] == pytest.approx(
        [0, 3.0, 0, 0, -3.0, 0, 0, 0, 0, 0, 1, 0, 5.0, 6.0, -1.2, 1], abs=1e-12
    )
    assert mesh.thinInstanceCount == 2
    # The buffer was big enough: it is only marked as updated.
    mesh.thinInstanceBufferUpdated.assert_called_once_with("matrix")
    mesh.thinInstanceSetBuffer.assert_not_called()


@pytest.mark.usefixtures("typed_arrays")
def test_gfx_shot_13_a_bullet_layer_grows_its_buffer_by_powers_of_two() -> None:
    mesh = _mesh()
    layer = sr.BulletLayer(mesh, -1.0, 0)
    mesh.reset_mock()
    layer.show([[float(i), 0.0, 1.0, 0.0] for i in range(17)])
    assert len(layer.matrices) == 32 * 16
    mesh.thinInstanceSetBuffer.assert_called_once_with("matrix", layer.matrices, 16, False)
    mesh.thinInstanceBufferUpdated.assert_not_called()
    assert mesh.thinInstanceCount == 17
    assert layer.matrices[16 * 16 + 12] == 16.0


@pytest.mark.usefixtures("typed_arrays")
@pytest.mark.parametrize("material", [True, False])
def test_a_bullet_layer_disposes_its_mesh_and_any_material(material: bool) -> None:
    mesh = _mesh(material=material)
    own = mesh.material
    sr.BulletLayer(mesh, -1.0, 0).dispose()
    mesh.dispose.assert_called_once()
    if material:
        own.dispose.assert_called_once()


@pytest.fixture
def templates(monkeypatch: pytest.MonkeyPatch) -> list[SimpleNamespace]:
    """Record the templates made (`kind`, `name`, `geo`, `alphas`, `mesh`), each a fresh mesh."""
    made: list[SimpleNamespace] = []

    def additive(name: str, geo: Any, _scene: Any) -> Any:
        made.append(SimpleNamespace(kind="additive", name=name, geo=geo, alphas=None))
        made[-1].mesh = _mesh(name)
        return made[-1].mesh

    def blended(name: str, geo: Any, alphas: Any, _scene: Any) -> Any:
        made.append(SimpleNamespace(kind="blended", name=name, geo=geo, alphas=alphas))
        made[-1].mesh = _mesh(name)
        return made[-1].mesh

    monkeypatch.setattr(sr, "additive_template", additive)
    monkeypatch.setattr(sr, "blended_template", blended)
    return made


def test_gfx_read_11_the_contrast_spark_is_a_white_glow_named_after_its_bullet(
    templates: list[SimpleNamespace],
) -> None:
    spark = sr.contrast_spark("enemy-bullet-red", "scene")
    assert spark is templates[0].mesh
    assert (templates[0].kind, templates[0].name) == ("additive", "enemy-bullet-red-spark")
    # The centre is white (the spark has no dark rim).
    assert templates[0].geo.colors[0:3] == [1, 1, 1]


def test_gfx_shot_10_a_swirl_takes_its_own_colour(templates: list[SimpleNamespace]) -> None:
    colors = SimpleNamespace(swirls=[[GREEN, BLACK]], halo=[RED, BLACK])
    swirl = record({"size": 0.5, "spinRadPerSec": 1.0, "lobes": 3, "depth": 0.5, "twist": 1.0})
    mesh, place = sr.swirl_layer("b", "scene", swirl, 0, colors)
    assert mesh.name == "b-swirl-0"
    assert templates[0].geo.colors[0:3] == GREEN
    assert place(SimpleNamespace(heading=0.0, age=0.0), 2.0) == pytest.approx([1.0, 0.0])


def test_gfx_shot_10_a_swirl_without_a_colour_of_its_own_takes_the_halo_colour(
    templates: list[SimpleNamespace],
) -> None:
    colors = SimpleNamespace(swirls=[[GREEN, BLACK], None], halo=[RED, BLACK])
    swirl = record({"size": 1.0, "spinRadPerSec": 0.0, "lobes": 2, "depth": 0.5, "twist": 0.0})
    sr.swirl_layer("b", "scene", swirl, 1, colors)
    assert templates[0].name == "b-swirl-1"
    assert templates[0].geo.colors[0:3] == RED


@pytest.mark.usefixtures("typed_arrays")
@pytest.mark.parametrize("contrast", [False, True])
def test_gfx_shot_10_a_bullet_is_an_aura_a_body_swirls_and_a_core_back_to_front(
    templates: list[SimpleNamespace], contrast: bool
) -> None:
    """Also GFX-READ-11: the contrast style adds a white spark on top."""
    layers = sr.bullet_layers("red", "scene", contrast)
    names = [mesh.name for mesh in (entry[0].mesh for entry in layers)]
    expected = ["enemy-bullet-red-halo", "enemy-bullet-red"]
    expected += [f"enemy-bullet-red-swirl-{i}" for i in range(len(BULLETS.swirls))]
    expected += ["enemy-bullet-red-core"]
    if contrast:
        expected += ["enemy-bullet-red-spark"]
    assert names == expected
    # The body is the only blended layer, faded by the look's alphas.
    blended = [entry for entry in templates if entry.kind == "blended"]
    assert [entry.name for entry in blended] == ["enemy-bullet-red"]
    assert blended[0].alphas == sr.disc_alphas(BULLETS.segments, BULLETS.fade)
    # Towards the camera (-Z) and later in the draw order, layer after layer.
    depths = [entry[0].z for entry in layers]
    assert depths == pytest.approx([-1 - 0.05 * i for i in range(len(layers))])
    orders = [entry[0].mesh.alphaIndex for entry in layers]
    assert orders == [sr.ON_TOP + i for i in range(len(layers))]
    assert layers[0][1] is sr.halo_placement
    assert layers[1][1] is sr.body_placement
    assert layers[len(BULLETS.swirls) + 2][1] is sr.core_placement


@pytest.mark.usefixtures("typed_arrays", "templates")
def test_gfx_shot_13_one_set_of_layers_per_bullet_colour() -> None:
    pools = sr.bullet_pools("scene", False)
    assert list(pools) == sr.STYLES
    assert list(BULLETS.styles.keys()) == sr.STYLES
    first = pools[sr.STYLES[0]][0][0].mesh.name
    assert first == "enemy-bullet-" + sr.STYLES[0] + "-halo"


class _Layer:
    """A bullet layer stand-in: the spots of each `show`."""

    def __init__(self) -> None:
        self.shown: list[list[list[float]]] = []

    def show(self, spots: list[list[float]]) -> None:
        self.shown.append(spots)


def _fake_pools() -> dict[str, list[list[Any]]]:
    return {style: [[_Layer(), sr.body_placement]] for style in sr.STYLES}


def test_perf_20_warming_shows_one_bullet_in_every_layer_then_hides_them() -> None:
    pools = _fake_pools()
    sr.warm_bullets(pools, True)
    sr.warm_bullets(pools, False)
    for style in sr.STYLES:
        assert pools[style][0][0].shown == [[[0, 0, 0, 0]], []]


def test_gfx_shot_13_each_bullet_is_drawn_in_the_layers_of_its_colour() -> None:
    pools = _fake_pools()
    red = SimpleNamespace(style="red", x=1.0, y=2.0, radius=5.0, age=0.0, heading=0.0)
    blue = SimpleNamespace(style="blue", x=3.0, y=4.0, radius=5.0, age=0.0, heading=0.0)
    sr.sync_bullets(pools, [red, blue])
    r = sr.drawn_radius(red)
    assert pools["red"][0][0].shown == [[[1.0, 2.0, r, 0]]]
    assert pools["blue"][0][0].shown == [[[3.0, 4.0, r, 0]]]
    assert pools["green"][0][0].shown == [[]]


def test_a_bullet_of_an_unknown_style_is_drawn_in_the_first_colour() -> None:
    pools = _fake_pools()
    odd = SimpleNamespace(style="plaid", x=1.0, y=1.0, radius=5.0, age=0.0, heading=0.0)
    sr.sync_bullets(pools, [odd])
    assert len(pools[sr.STYLES[0]][0][0].shown[0]) == 1
    assert all(pools[style][0][0].shown == [[]] for style in sr.STYLES[1:])


@pytest.fixture
def missile_parts(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Stand-ins for what a missile is built with: its nodes, meshes, materials and outline."""
    parts = SimpleNamespace(meshes=[], outlines=[], nodes=[])

    def node(label: str, _scene: Any) -> Any:
        parts.nodes.append(_mesh(label))
        return parts.nodes[-1]

    def mesh_of(name: str, geo: Any, material: Any, _scene: Any) -> Any:
        mesh = _mesh(name)
        mesh.geo = geo
        mesh.mat = material
        parts.meshes.append(mesh)
        return mesh

    mats = SimpleNamespace(hull="hull-material", neon="neon-material")
    monkeypatch.setattr(sr, "new_transform_node", node)
    monkeypatch.setattr(sr, "node_name", lambda n: n.name)
    monkeypatch.setattr(sr, "mesh_of", mesh_of)
    monkeypatch.setattr(sr, "enemy_materials", lambda _scene: mats)
    monkeypatch.setattr(sr, "set_outline", lambda mesh, color: parts.outlines.append((mesh, color)))
    parts.flames = []
    monkeypatch.setattr(
        sr, "flame_materials", lambda _scene, color: SimpleNamespace(color=list(color))
    )
    monkeypatch.setattr(
        sr,
        "build_reactor_flame",
        lambda name, options, parent, mats: parts.flames.append((name, options, parent, mats)),
    )
    return parts


def test_gfx_shot_15_a_missile_is_a_dark_body_an_orange_tip_and_a_flame(
    missile_parts: SimpleNamespace,
) -> None:
    """Also GFX-READ-12: its rim glows in the enemy shots' colour; ENM-40: its reactor flame."""
    look = ENEMY_LOOK.missile
    root = sr.build_missile("scene", 4)
    assert root.name == "enemy-missile-4"
    # WPN-09: its body, tip and nozzle are on a node of their own, which tilts its nose up.
    tilt, nozzle = missile_parts.nodes[1:]
    assert (tilt.name, tilt.parent) == ("enemy-missile-4-tilt", root)
    hull, tip = missile_parts.meshes
    assert (hull.name, hull.mat, hull.parent) == ("enemy-missile-4-body", "hull-material", tilt)
    assert (tip.name, tip.mat, tip.parent) == ("enemy-missile-4-tip", "neon-material", tilt)
    assert missile_parts.outlines == [(hull, look.tip)]
    assert len(hull.geo.positions) > 0
    assert len(tip.geo.positions) > 0
    # The flame streams out of its tail, the reactor flame turned onto -Y.
    assert nozzle.parent is tilt
    nozzle.position.set.assert_called_once_with(0, -look.length / 2, 0)
    assert nozzle.rotation.x == pytest.approx(-math.pi / 2)
    [(name, options, parent, mats)] = missile_parts.flames
    assert (name, parent) == ("enemy-missile-4-flame", nozzle)
    assert mats.color == look.flameColor
    assert options["length"] > 0
    assert options["diameter"] > 0


def test_gfx_shot_15_each_missile_node_sits_on_its_shot_facing_its_heading() -> None:
    nodes = [MagicMock(), MagicMock(), MagicMock()]
    pool = MagicMock()
    # A pool may hand back spare nodes: they are left alone.
    pool.show.return_value = nodes
    base = sr.LOOK.missile.baseRadius
    missiles = [
        SimpleNamespace(x=1.0, y=2.0, heading=0.3, radius=base, height=0),
        SimpleNamespace(x=4, y=5, heading=0, radius=2 * base, height=0),
    ]
    sr.sync_missiles(pool, missiles)
    pool.show.assert_called_once_with(2)
    nodes[0].position.set.assert_called_once_with(1.0, 2.0, -0.5)
    assert nodes[0].rotation.z == pytest.approx(-0.3)
    nodes[1].position.set.assert_called_once_with(4, 5, -0.5)
    # ENM-MORTAR-08: a bigger missile is drawn bigger in proportion.
    nodes[0].scaling.set.assert_called_once_with(1, 1, 1)
    nodes[1].scaling.set.assert_called_once_with(2, 2, 2)
    nodes[2].position.set.assert_not_called()


class _Lasers:
    """The enemy lasers' stand-in: what each sync was given, and whether it was disposed."""

    made: ClassVar[list[Any]] = []

    def __init__(self, scene: Any, contrast: bool) -> None:
        self.scene = scene
        self.contrast = contrast
        self.synced: list[Any] = []
        self.disposed = False
        _Lasers.made.append(self)

    def sync(self, lasers: list[Any], time: float) -> None:
        self.synced.append((lasers, time))

    def dispose(self) -> None:
        self.disposed = True


class _BareTrail:
    """A smoke trail layer whose mesh has no material (nothing to draw over the models)."""

    def __init__(self, name: str, *_args: Any) -> None:
        self.name = name
        self.mesh = _mesh(name, material=False)

    def dispose(self) -> None:
        """Nothing to free."""


class _Trail:
    """The smoke trail's layer stand-in: what it was made with and shown, and its disposal."""

    made: ClassVar[list[Any]] = []

    def __init__(self, name: str, geo: Any, add: bool, z: float, order: int, scene: Any) -> None:
        self.name = name
        self.geo = geo
        self.add = add
        self.place = (z, order, scene)
        self.mesh = _mesh(name)
        self.shown: list[Any] = []
        self.disposed = False
        _Trail.made.append(self)

    def show(self, spots: list[Any]) -> None:
        self.shown.append(spots)

    def dispose(self) -> None:
        self.disposed = True


@pytest.fixture
def renderer(
    monkeypatch: pytest.MonkeyPatch,
    missile_parts: SimpleNamespace,
    templates: list[SimpleNamespace],
) -> SimpleNamespace:
    """Return the enemy shot renderer over Babylon stand-ins, its lasers recorded."""
    stub_babylon(monkeypatch, sr, node_pool)
    monkeypatch.setattr(sr, "_float32_array", FakeTypedArray)
    monkeypatch.setattr(sr, "babylon_constant", lambda key: key)
    monkeypatch.setattr(sr, "new_transform_node", lambda label, _scene: _mesh(label))
    monkeypatch.setattr(sr, "node_name", lambda n: n.name)
    monkeypatch.setattr(node_pool, "dispose_node", lambda node: node.dispose())
    monkeypatch.setattr(sr, "EnemyLasers", _Lasers)
    monkeypatch.setattr(sr, "LayerMesh", _Trail)
    monkeypatch.setattr(sr, "child_meshes", lambda node, _direct: node.getChildMeshes())
    _Lasers.made = []
    _Trail.made = []
    handle = sr.create_enemy_shot_renderer("scene")
    return SimpleNamespace(
        handle=handle,
        lasers=_Lasers.made[0],
        trail=_Trail.made[0],
        templates=templates,
        meshes=missile_parts.meshes,
    )


def _bullet_meshes(made: list[SimpleNamespace]) -> list[Any]:
    return [entry.mesh for entry in made if entry.name.startswith("enemy-bullet-")]


def test_gfx_read_11_the_renderer_draws_the_contrast_look_with_its_lasers(
    renderer: SimpleNamespace,
) -> None:
    assert isinstance(renderer.handle, sr.ShotRendererHandle)
    assert renderer.lasers.scene == "scene"
    assert renderer.lasers.contrast is True
    names = [entry.name for entry in renderer.templates]
    assert "enemy-bullet-red-spark" in names
    # One set of layers per colour, a spark on each.
    assert len(_bullet_meshes(renderer.templates)) == len(sr.STYLES) * (len(BULLETS.swirls) + 4)


def test_gfx_shot_15_the_missile_smoke_is_a_blended_layer_drawn_over_the_models(
    renderer: SimpleNamespace,
) -> None:
    """WPN-09: a lofted missile's smoke never passes under the boss it rises over."""
    trail = renderer.trail
    assert (trail.name, trail.add) == ("enemy-missile-smoke", False)
    assert trail.mesh.material.depthFunction == "ALWAYS"


def test_gfx_shot_15_the_renderer_draws_bullets_missiles_and_lasers_each_frame(
    renderer: SimpleNamespace,
) -> None:
    bullet = SimpleNamespace(style="red", x=1.0, y=2.0, radius=3.0, age=0.0, heading=0.0)
    missile = SimpleNamespace(x=7.0, y=8.0, heading=0.5, radius=5, height=0)
    lasers = [SimpleNamespace(spec=SimpleNamespace(style="lancer"))]
    frame = SimpleNamespace(dt_seconds=0.25, bullets=[bullet], missiles=[missile], lasers=lasers)
    renderer.handle.sync(frame)
    renderer.handle.sync(frame)
    # The lasers blink on the renderer's own clock: the sum of the frames' times.
    assert renderer.lasers.synced == [(lasers, 0.25), (lasers, 0.5)]
    # The red bullet is drawn in each red layer, no other colour's.
    for mesh in _bullet_meshes(renderer.templates):
        drawn = mesh.name.startswith("enemy-bullet-red")
        mesh.setEnabled.assert_called_with(drawn)
        assert mesh.thinInstanceCount == 1
    # The missile was built in the pool and placed on its shot.
    root = renderer.meshes[0].parent.parent
    assert root.name == "enemy-missile-0"
    root.position.set.assert_called_with(7.0, 8.0, -0.5)
    assert root.rotation.z == pytest.approx(-0.5)
    # Its smoke trail is stepped and drawn every frame (GFX-SHOT-15).
    assert len(renderer.trail.shown) == 2


@pytest.mark.parametrize("on", [True, False])
def test_perf_20_the_renderer_warms_every_bullet_layer(renderer: SimpleNamespace, on: bool) -> None:
    renderer.handle.warm(on)
    for mesh in _bullet_meshes(renderer.templates):
        mesh.setEnabled.assert_called_with(on)


def test_the_renderer_disposes_its_layers_lasers_missiles_and_flame(
    renderer: SimpleNamespace,
) -> None:
    frame = SimpleNamespace(
        dt_seconds=0.0,
        bullets=[],
        missiles=[SimpleNamespace(x=0, y=0, heading=0, radius=5, height=0)],
        lasers=[],
    )
    renderer.handle.sync(frame)
    renderer.handle.dispose()
    for mesh in _bullet_meshes(renderer.templates):
        mesh.dispose.assert_called_once()
        mesh.material.dispose.assert_called_once()
    assert renderer.lasers.disposed
    renderer.meshes[0].parent.parent.dispose.assert_called_once()
    assert renderer.trail.disposed


def test_wpn_09_a_lofted_missile_is_raised_by_its_height_tilted_and_drawn_on_top(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mesh = SimpleNamespace(renderingGroupId=1)
    monkeypatch.setattr(sr, "child_meshes", lambda _node, _direct: [mesh])
    tilt = SimpleNamespace(rotation=SimpleNamespace(x=0))
    seen: list[tuple[float, ...]] = []
    node = SimpleNamespace(
        position=SimpleNamespace(set=lambda *a: seen.append(a)),
        rotation=SimpleNamespace(z=0),
        scaling=SimpleNamespace(set=lambda *_a: None),
        getChildren=lambda: [tilt],
    )
    pool = SimpleNamespace(show=lambda n: [node][:n])
    lofted = SimpleNamespace(
        x=1.0, y=2.0, heading=0.0, radius=5, height=12.0, pitch=0.4, loft_seconds=1
    )
    sr.sync_missiles(pool, [lofted])
    assert seen == [(1.0, 2.0, -12.5)]
    assert tilt.rotation.x == pytest.approx(-0.4)
    # In the rendering group after the playfield's, back in it once its node shows a flat one.
    assert mesh.renderingGroupId == 2
    flat = SimpleNamespace(x=1.0, y=2.0, heading=0.0, radius=5, height=0.0, pitch=0.0)
    sr.sync_missiles(pool, [flat])
    assert mesh.renderingGroupId == 1
    assert tilt.rotation.x == 0


def test_a_smoke_trail_without_a_material_is_left_as_it_is(
    monkeypatch: pytest.MonkeyPatch,
    missile_parts: SimpleNamespace,
    templates: list[SimpleNamespace],
) -> None:
    stub_babylon(monkeypatch, sr, node_pool)
    monkeypatch.setattr(sr, "_float32_array", FakeTypedArray)
    monkeypatch.setattr(sr, "babylon_constant", lambda key: key)
    monkeypatch.setattr(sr, "EnemyLasers", _Lasers)
    monkeypatch.setattr(sr, "LayerMesh", _BareTrail)
    handle = sr.create_enemy_shot_renderer("scene")
    assert isinstance(handle, sr.ShotRendererHandle)
    assert missile_parts.meshes == []
    assert templates
