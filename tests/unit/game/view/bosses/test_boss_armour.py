# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_armour.py` and `boss_frame.py`.

A boss's armour is cut out of its body (BOSS-42), bursts off in chunks (BOSS-43) and leaves a dark
metal frame (BOSS-44; docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md).
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.bosses_top_fakes import FakeNode, patch_models
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.hidden_weapons import armour_region
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import record
from game.sim.boss_kinds import BOSS_DESIGNS
from game.view.bosses import boss_armour
from game.view.bosses.boss_armour import (
    LAYERS,
    ArmourChunk,
    ArmourView,
    FrameView,
    MovingView,
    build_armour,
    chunk_layers,
    chunk_pose,
    cut_armour,
    model_outline,
    rooted,
    supports_in,
)
from game.view.bosses.boss_frame import (
    frame_segments,
)
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.shatter import centroid, triangles, up_facing
from render.geometry.solids import Placement, SolidBuilder

GREY = [0.5, 0.5, 0.5]
LOOK = BOSS_LOOK.reveal
# A wing on the boss's right (X right, Y up): model space is mirrored (+X is the screen's left).
WING = armour_region("wings", 1, [[10, -20], [50, -20], [50, 20], [10, 20]], "wing")


def _plane(p: Any) -> None:
    """Add a wide, flat delta: a slab 120 x 60, a fuselage box on it, a muzzle and a reactor."""
    p.hull.box([120, 4, 60], GREY, Placement([0, -2, 0]))
    p.flesh.box([12, 10, 60], GREY, Placement([0, 2, 0]))
    p.neon.box([2, 1, 50], GREY, Placement([40, 2, 0]))
    p.muzzle([0, 0, 30])
    p.reactor([0, 0, -30], 3)


def _tris(*boxes: tuple[list[float], list[float]]) -> list[Any]:
    b = SolidBuilder()
    for size, at in boxes:
        b.box(size, GREY, Placement(at))
    return triangles(b.geometry)


def _area_xz(tris: list[Any]) -> float:
    total = 0.0
    for t in tris:
        a, b, c = (v.position for v in t)
        total += abs((b[0] - a[0]) * (c[2] - a[2]) - (c[0] - a[0]) * (b[2] - a[2])) / 2
    return total


def test_outlines_turn_into_model_space() -> None:
    assert model_outline([[10, -20], [50, 4]]) == [[-10, 20], [-50, -4]]


def test_the_cut_moves_the_faces_inside_a_region_out_of_the_core() -> None:
    cut = cut_armour(_plane, [WING])
    region = cut.regions[0]
    tops = [t for t in region["hull"] if up_facing(t, 0.9)]
    # Both wings, 40 x 40 each, of the slab's top.
    assert _area_xz(tops) == pytest.approx(2 * 40 * 40, rel=0.05)
    for t in region["hull"]:
        assert 10 - 4 <= abs(centroid(t)[0]) <= 50 + 4
    # The neon strip at x = 40 goes with the left wing; the fuselage stays.
    assert region["neon"]
    assert not region["flesh"]
    kept = collect_parts(cut.core_drawing())
    kept_tops = [t for t in triangles(kept["parts"].hull.geometry) if up_facing(t, 0.9)]
    assert _area_xz(kept_tops) == pytest.approx(120 * 60 - 2 * 40 * 40, rel=0.05)
    # The core still gets its muzzle and reactor.
    assert [m[1] for m in kept["muzzles"]] == ["gun"]
    assert len(kept["reactors"]) == 1


def test_a_face_goes_to_the_first_region_that_holds_it() -> None:
    inner = armour_region("inner", 2, [[10, -20], [30, -20], [30, 20], [10, 20]], "shell")
    cut = cut_armour(_plane, [inner, WING])
    first = [t for t in cut.regions[0]["hull"] if up_facing(t, 0.9)]
    second = [t for t in cut.regions[1]["hull"] if up_facing(t, 0.9)]
    assert _area_xz(first) == pytest.approx(2 * 20 * 40, rel=0.05)
    assert _area_xz(second) == pytest.approx(2 * 20 * 40, rel=0.05)


def test_heights_keep_what_is_above_or_below_a_region() -> None:
    low = armour_region(
        "low", 1, [[0, -40], [70, -40], [70, 40], [0, 40]], "wing", [-10, 1], mirror=False
    )
    cut = cut_armour(_plane, [low])
    assert not cut.regions[0]["flesh"] or all(centroid(t)[1] <= 1 for t in cut.regions[0]["flesh"])


def test_chunks_share_out_every_face_and_stay_under_the_cap() -> None:
    layers = cut_armour(_plane, [WING]).regions[0]
    chunks = chunk_layers(layers, 6)
    assert 2 <= len(chunks) <= 6
    for layer in LAYERS:
        assert sum(len(c[0][layer]) for c in chunks) == len(layers[layer])
    assert chunk_layers({layer: [] for layer in LAYERS}, 6) == []


def test_a_chunk_flies_out_up_then_down_tumbling_and_shrinking_away() -> None:
    centre = [30.0, 2.0, 10.0]
    rest = chunk_pose(centre, 0, 0)
    assert rest[0] == pytest.approx(centre)
    assert rest[1] == 0
    assert rest[3] == 1
    mid = chunk_pose(centre, 0, 0.3)
    assert math.hypot(mid[0][0], mid[0][2]) > math.hypot(centre[0], centre[2])
    assert mid[0][1] > centre[1]
    end = chunk_pose(centre, 0, 1)
    assert end[0][1] < centre[1]
    assert end[3] == 0
    assert end[1] != 0


def _node() -> SimpleNamespace:
    position = SimpleNamespace(x=0.0, y=0.0, z=0.0)

    def set_(x: float, y: float, z: float) -> None:
        position.x, position.y, position.z = x, y, z

    position.set = set_
    scaling = SimpleNamespace(x=1.0)
    scaling.set = lambda x, _y, _z: setattr(scaling, "x", x)
    return SimpleNamespace(position=position, scaling=scaling, rotation=SimpleNamespace(x=0, z=0))


class _Model:
    def __init__(self) -> None:
        self.root = _node()
        self.synced = 0

    def sync(self, _lit: Any, _dt: float) -> None:
        self.synced += 1


class _Flash:
    def __init__(self) -> None:
        self.since: list[float] = []

    def show(self, since_hit: float) -> None:
        self.since.append(since_hit)


@pytest.fixture
def view(monkeypatch: pytest.MonkeyPatch) -> Any:
    enabled: dict[int, bool] = {}
    monkeypatch.setattr(boss_armour, "set_enabled", lambda n, on: enabled.__setitem__(id(n), on))
    whole = _Model()
    frame = FrameView(_node(), [_Model(), _Model()])
    chunks = [ArmourChunk(_node(), [10.0, 0.0, 5.0], 0), ArmourChunk(_node(), [-10.0, 0, 5], 1)]
    flash = _Flash()
    region = SimpleNamespace(form=1)
    return SimpleNamespace(
        view=ArmourView(region, whole, flash, chunks, frame),
        on=lambda node: enabled.get(id(node)),
        whole=whole,
        frame=frame,
        chunks=chunks,
        flash=flash,
    )


def _boss(form: int, into: int, t: float) -> SimpleNamespace:
    return SimpleNamespace(
        form=form, transforming_into=into, transform=t, core=SimpleNamespace(since_hit=7.0)
    )


def test_at_rest_the_armour_is_whole_and_flashes_with_the_core(view: Any) -> None:
    view.view.show(_boss(0, 0, 0), {}, 0.1)
    assert view.on(view.whole.root) is True
    assert view.on(view.frame.root) is False
    assert all(view.on(c.node) is False for c in view.chunks)
    assert view.flash.since == [7.0]
    view.view.show(None, {}, 0.1)
    assert view.on(view.whole.root) is True


def test_it_strains_then_bursts_into_flying_chunks_baring_the_frame(view: Any) -> None:
    view.view.show(_boss(0, 1, LOOK.burst * 0.7), {}, 0.1)
    assert view.on(view.whole.root) is True
    assert view.on(view.frame.root) is False
    view.view.show(_boss(0, 1, (LOOK.burst + LOOK.burstEnd) / 2), {}, 0.1)
    assert view.on(view.whole.root) is False
    assert view.on(view.frame.root) is True
    assert all(view.on(c.node) is True for c in view.chunks)
    assert view.chunks[0].node.position.x > 10
    assert all(m.synced == 1 for m in view.frame.models)
    view.view.show(_boss(0, 1, LOOK.burstEnd + 0.01), {}, 0.1)
    assert all(view.on(c.node) is False for c in view.chunks)


def test_once_shed_only_the_frame_is_left(view: Any) -> None:
    view.view.show(_boss(1, 0, 0), {}, 0.1)
    assert view.on(view.whole.root) is False
    assert view.on(view.frame.root) is True
    assert all(view.on(c.node) is False for c in view.chunks)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=[d.id for d in BOSS_DESIGNS])
def test_every_boss_region_cuts_armour_and_stays_in_the_chunk_budget(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        capture = probe_builder(mp, BOSS_MODELS[design.id])
    finally:
        mp.undo()
    cut = cut_armour(record(capture.drawing).core, design.armour)
    most = min(BOSS_LOOK.armour.chunks, BOSS_LOOK.armour.bossChunks // len(design.armour))
    total = 0
    for k, region in enumerate(design.armour):
        layers = cut.regions[k]
        tops = [t for layer in ("hull", "flesh") for t in layers[layer] if up_facing(t, 0.3)]
        assert len(tops) >= 20, region.id
        assert frame_segments(tops, region.frame), region.id
        total += len(chunk_layers(layers, most))
    assert total <= BOSS_LOOK.armour.bossChunks


def test_supports_stand_in_a_region_even_in_part_and_root_on_what_lasts() -> None:
    region = armour_region("wings", 1, [[10, -10], [30, -10], [30, 10], [10, 10]], "wing")
    # Model space: +X is the screen's left (a region's X right is model -X).
    inside = [-20, 0, 5, 4]
    edge = [-8, 0, 5, 4]
    away = [-50, 0, 5, 4]
    assert supports_in(region, [inside, edge, away]) == [inside, edge]
    deck = _tris(([10, 2, 10], [-20, 0, 0]))
    assert rooted([inside, away], deck) == [[-20, 0, 5, 4, pytest.approx(2)], away]


def _winged_plane(p: Any) -> None:
    """`_plane` with a flapping wing and a rotor: nodes the core adds, not faces to cut."""
    _plane(p)
    p.flap([20, 0, 0], 1, 30, lambda wing: wing.hull.box([30, 1, 10], GREY, Placement([35, 0, 0])))
    p.rotor([0, 4, -10], 5)


def test_the_core_keeps_its_wings_rotors_reactors_and_muzzles_through_the_cut() -> None:
    cut = cut_armour(_winged_plane, [WING])
    kept = collect_parts(cut.core_drawing())
    assert len(kept["wings"]) == 1
    assert kept["wings"][0].span == 30
    assert len(kept["wings"][0].parts.hull.geometry.positions) > 0
    assert [r.radius for r in kept["rotors"]] == [5]
    assert [r.radius for r in kept["reactors"]] == [3]
    assert [m[1] for m in kept["muzzles"]] == ["gun"]


# A hatch sliding 10 px up the screen as the boss transforms (D-230), leaving a shell frame.
HATCH = moving_region(
    "hatch",
    1,
    [[-8, 8], [8, 8], [8, 18], [-8, 18]],
    slide([[0, 0, 0], [0, 10, 0]]),
    "shell",
    None,
    False,
)[0]


@pytest.fixture
def moving(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Return the armour of a plane with a moving hatch, on fake nodes, given no carrier."""
    builder = patch_models(monkeypatch, boss_armour)
    trims: list[tuple[str, str]] = []
    monkeypatch.setattr(boss_armour, "set_trim_group", lambda n: trims.append(("group", n.name)))
    monkeypatch.setattr(boss_armour, "clear_trim", lambda n: trims.append(("clear", n.name)))
    root = FakeNode("plane", "scene")
    flashes: list[_Flash] = []

    def flash_of(_model: Any) -> _Flash:
        flashes.append(_Flash())
        return flashes[-1]

    design = SimpleNamespace(id="plane", armour=[HATCH])
    views = build_armour(design, cut_armour(_plane, [HATCH]), root, GREY, None, flash_of)
    return SimpleNamespace(view=views[0], root=root, builder=builder, flash=flashes[0], trims=trims)


def test_d230_a_moving_piece_hangs_on_its_mover_with_a_carrier_and_a_hidden_frame(
    moving: Any,
) -> None:
    view = moving.view
    assert isinstance(view, MovingView)
    assert view.whole.root.parent is view.mover
    assert view.mover.name == "plane-armour-hatch-mover"
    assert view.mover.parent is moving.root
    # No carrier was given: the piece gets its own.
    assert view.carrier.name == "plane-armour-hatch-carrier"
    assert view.carrier.parent is moving.root
    assert view.frame.root.parent is moving.root
    assert view.frame.root.enabled is False
    # The floor is trimmed along its own outline, the ribs are not (GFX-TRIM-09).
    assert ("group", "plane-armour-hatch-frame-floor") in moving.trims
    assert ("clear", "plane-armour-hatch-frame-ribs") in moving.trims
    assert moving.builder.faces("plane-armour-hatch") > 0


def test_d230_a_moving_piece_strains_then_moves_into_its_new_pose(moving: Any) -> None:
    view = moving.view
    view.show(None, {}, 0.1)
    # At rest: the piece as drawn, the weapons riding it drawn where they end up (10 px back).
    assert view.mover.position.xyz() == pytest.approx([0, 0, 0])
    assert view.carrier.position.xyz() == pytest.approx([0, 0, 10])
    assert view.frame.root.enabled is False
    assert moving.flash.since == [1000]
    # It strains as armour does: it shudders and strobes before the burst.
    t = LOOK.burst / 2
    view.show(_boss(0, 1, t), {}, 0.1)
    jolt = math.sin(t * 90) * LOOK.shudder * 0.5
    assert view.whole.root.position.xyz() == pytest.approx([jolt, 0, -jolt * 0.6])
    assert moving.flash.since[-1] == (0 if math.floor(t * LOOK.strobeHz * 4) % 2 == 0 else 1000)
    assert view.frame.root.enabled is False
    # Once moved: at its end pose (10 px up the screen is model -Z), its frame bared.
    view.show(_boss(1, 0, 0), {}, 0.1)
    assert view.mover.position.xyz() == pytest.approx([0, 0, -10])
    assert view.carrier.position.xyz() == pytest.approx([0, 0, 0])
    assert view.whole.root.position.xyz() == [0, 0, 0]
    assert moving.flash.since[-1] == 7.0
    assert view.frame.root.enabled is True
    assert all(len(m.synced) == 1 for m in view.frame.models)
