"""Unit tests of `src/game/view/bosses/boss_armour.py` and `boss_frame.py`: a boss's armour cut
out of its body, bursting off in chunks and leaving a dark metal frame (docs/superpowers/specs/
2026-10-31-boss-armour-shedding-design.md)."""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.view_probes import probe_builder

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.hidden_weapons import armour_region
from game.config.record import record
from game.sim.boss_kinds import BOSS_DESIGNS
from game.view.bosses import boss_armour
from game.view.bosses.boss_armour import (
    LAYERS,
    ArmourChunk,
    ArmourView,
    FrameView,
    chunk_layers,
    chunk_pose,
    cut_armour,
    model_outline,
)
from game.view.bosses.boss_frame import (
    floor_height,
    floor_triangles,
    frame_drawings,
    frame_segments,
    longest_two,
)
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.shatter import centroid, triangles, up_facing
from render.geometry.solids import Placement

GREY = [0.5, 0.5, 0.5]
LOOK = BOSS_LOOK.reveal
# A wing on the boss's right (X right, Y up): model space is mirrored (+X is the screen's left).
WING = armour_region("wings", 1, [[10, -20], [50, -20], [50, 20], [10, 20]], "wing")


def _plane(p: Any) -> None:
    """A wide, flat delta: a slab 120 x 60, a fuselage box on it, a muzzle and a reactor."""
    p.hull.box([120, 4, 60], GREY, Placement([0, -2, 0]))
    p.flesh.box([12, 10, 60], GREY, Placement([0, 2, 0]))
    p.neon.box([2, 1, 50], GREY, Placement([40, 2, 0]))
    p.muzzle([0, 0, 30])
    p.reactor([0, 0, -30], 3)


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
    assert region["neon"] and not region["flesh"]
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
    low = armour_region("low", 1, [[0, -40], [70, -40], [70, 40], [0, 40]], "wing", [-10, 1], False)
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
    assert rest[1] == 0 and rest[3] == 1
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
    scaling.set = lambda x, y, z: setattr(scaling, "x", x)
    return SimpleNamespace(position=position, scaling=scaling, rotation=SimpleNamespace(x=0, z=0))


class _Model:
    def __init__(self) -> None:
        self.root = _node()
        self.synced = 0

    def sync(self, lit: Any, dt: float) -> None:
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


def test_the_frame_floor_lies_flat_and_dark_under_the_armour() -> None:
    tris = cut_armour(_plane, [WING]).regions[0]["hull"]
    y = floor_height(tris)
    assert y == pytest.approx(-2 + BOSS_LOOK.frame.lift)
    floor = floor_triangles(tris, y)
    assert floor and all(v.position[1] == y for t in floor for v in t)
    assert all(up_facing(t, 0.9) for t in floor)
    assert all(v.color[:3] == BOSS_LOOK.frame.floor for t in floor for v in t)


def test_the_frame_ribs_lie_within_the_armour_top_view() -> None:
    tris = cut_armour(_plane, [WING]).regions[0]["hull"]
    segments = frame_segments(tris, "wing")
    assert len(segments) >= 6
    for a, b in segments:
        for x in (a[0], b[0]):
            assert 10 - 4 <= abs(x) <= 50 + 4
    assert frame_segments([], "wing") == []
    floor, ribs = frame_drawings(tris, "wing", [1, 0, 1])
    drawn_floor = collect_parts(floor)["parts"]
    drawn_ribs = collect_parts(ribs)["parts"]
    assert drawn_floor.hull.geometry.positions and not drawn_floor.neon.geometry.positions
    assert drawn_ribs.hull.geometry.positions and drawn_ribs.neon.geometry.positions


def test_longest_two_picks_the_two_longest_segments() -> None:
    segs = [[[0, 0], [0, n]] for n in [3, 9, 1, 7, 4]]
    assert [s[1][1] for s in longest_two(segs)] == [9, 7]
    assert longest_two(segs[:1]) == segs[:1]


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
