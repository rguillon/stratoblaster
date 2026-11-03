# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/bosses/boss_armour.py`.

A boss's armour regions are drawn as pieces of their own (BOSS-42, D-254), burst off in pieces
(BOSS-43) and leave a dark metal frame (BOSS-44).
"""

import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.boss_wholeness import boss_drawing, region_drawings
from helpers.bosses_top_fakes import FakeNode, patch_models

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.hidden_weapons import armour_region
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import record
from game.sim.boss_kinds import BOSS_DESIGNS
from game.view.bosses import boss_armour
from game.view.bosses.boss_armour import (
    GREY,
    ArmourChunk,
    ArmourView,
    FrameView,
    MovingView,
    RegionDrawing,
    all_triangles,
    build_armour,
    chunk_pose,
    drawn_layers,
    model_outline,
    most_pieces,
    region_drawing,
)
from render.geometry.mesh_triangles import bounds_of
from render.geometry.solids import Placement

DARK = [0.2, 0.2, 0.25]
LIGHT = [0.8, 0.8, 0.8]
LOOK = BOSS_LOOK.reveal
# A wing on the boss's right (X right, Y up): model space is mirrored (+X is the screen's left).
WING = armour_region("wings", 1, [[10, -20], [50, -20], [50, 20], [10, 20]], "wing")
# A hatch sliding 10 px up the screen as the boss transforms (BOSS-45), leaving a shell frame.
HATCH = moving_region(
    "hatch",
    1,
    [[-8, 8], [8, 8], [8, 18], [-8, 18]],
    slide([[0, 0, 0], [0, 10, 0]]),
    "shell",
    None,
    False,
)[0]
# A flap sliding away, leaving no frame.
FLAP = moving_region(
    "flap",
    1,
    [[-20, -18], [-12, -18], [-12, -8], [-20, -8]],
    slide([[0, 0, 0], [0, 10, 0]]),
    None,
    None,
    False,
)[0]


def _wing_armour(p: Any) -> None:
    """Draw the wing's armour: a dark hull plate over the wing (y 0..3), a neon strip set in it."""
    p.hull.box([40, 3, 40], DARK, Placement([-30, 0, 0]))
    p.neon.box([2, 0.5, 30], LIGHT, Placement([-30, 2.4, 0]))


def _masted_armour(p: Any) -> None:
    """Draw the wing's armour with a mast standing on it: 12 faces of 0..3, 12 faces of 3..13."""
    p.hull.box([40, 3, 40], DARK, Placement([-30, 0, 0]))
    p.hull.box([1, 10, 1], DARK, Placement([-30, 3, 0]))


def _flesh_armour(p: Any) -> None:
    p.flesh.box([10, 2, 10], LIGHT, Placement([0, 1, -13]))


def _lights_only(p: Any) -> None:
    p.neon.box([4, 1, 4], LIGHT, Placement([16, 1, 13]))


def _nothing(_p: Any) -> None:
    pass


def _piece(p: Any) -> None:
    p.hull.box([6, 2, 6], DARK, Placement([-20, 1, 5]))


def _area_xz(tris: list[Any]) -> float:
    total = 0.0
    for t in tris:
        a, b, c = (v.position for v in t)
        total += abs((b[0] - a[0]) * (c[2] - a[2]) - (c[0] - a[0]) * (b[2] - a[2])) / 2
    return total


def _top_faces(tris: list[Any], y: float) -> list[Any]:
    return [t for t in tris if all(abs(v.position[1] - y) < 1e-6 for v in t)]


def test_outlines_turn_into_model_space() -> None:
    assert model_outline([[10, -20], [50, 20]]) == [[-10, 20], [-50, -20]]


def test_most_pieces_is_the_region_cap_within_the_boss_cap() -> None:
    assert most_pieces([WING]) == BOSS_LOOK.armour.chunks
    assert most_pieces([WING, WING, WING]) == BOSS_LOOK.armour.bossChunks // 3


def test_a_region_the_model_does_not_draw_has_no_drawing() -> None:
    assert region_drawing(None, WING, LIGHT, 12) is None
    assert region_drawing(record({"other": {"whole": _nothing}}), WING, LIGHT, 12) is None


def test_a_region_drawn_without_its_whole_is_an_error() -> None:
    with pytest.raises(ValueError, match='"wings" has no whole drawing'):
        region_drawing(record({"wings": {"pieces": []}}), WING, LIGHT, 12)


def test_the_default_pieces_are_plates_at_the_top_of_the_armour_in_its_colour() -> None:
    drawn = region_drawing(record({"wings": {"whole": _wing_armour}}), WING, LIGHT, 12)
    assert isinstance(drawn, RegionDrawing)
    assert drawn.whole is _wing_armour
    assert 1 < len(drawn.pieces) <= 12
    tris: list[Any] = []
    for draw, centre in drawn.pieces:
        piece = all_triangles(drawn_layers(draw))
        tris.extend(piece)
        b = bounds_of(piece)
        # Each plate is `plate` thick at the top of the armour (its hull, 0..3), inside one of the
        # region's outlines (the wing's and its mirror image's: the outline rules, not the drawing).
        assert b[4] == pytest.approx(3)
        assert b[1] == pytest.approx(3 - BOSS_LOOK.armour.plate)
        assert min(abs(b[0]), abs(b[3])) >= 10 - 1e-6
        assert max(abs(b[0]), abs(b[3])) <= 50 + 1e-6
        assert b[2] >= -20 - 1e-6
        assert b[5] <= 20 + 1e-6
        assert b[0] <= centre[0] <= b[3]
        assert centre[1] == pytest.approx((b[1] + b[4]) / 2)
        # In the armour's hull colour on top, darker underneath.
        tops = _top_faces(piece, 3)
        assert all(v.color[:3] == pytest.approx(DARK) for t in tops for v in t)
        assert all(v.color[0] < DARK[0] for t in _top_faces(piece, b[1]) for v in t)
    # Together the plates cover both outlines.
    assert _area_xz(_top_faces(tris, 3)) == pytest.approx(2 * 40 * 40)


def test_the_plates_lie_at_the_top_of_the_armour_s_body_not_of_what_stands_on_it() -> None:
    drawn = region_drawing(record({"wings": {"whole": _masted_armour}}), WING, LIGHT, 12)
    for draw, _centre in drawn.pieces:
        b = bounds_of(all_triangles(drawn_layers(draw)))
        assert b[4] == pytest.approx(3)


def test_the_pieces_take_the_flesh_colour_or_the_lights_when_there_is_no_hull() -> None:
    flesh = region_drawing(record({"hatch": {"whole": _flesh_armour}}), HATCH, LIGHT, 4)
    tops = _top_faces(all_triangles(drawn_layers(flesh.pieces[0][0])), 3)
    assert tops[0][0].color[:3] == pytest.approx(LIGHT)
    lights = region_drawing(record({"flap": {"whole": _lights_only}}), FLAP, LIGHT, 4)
    tops = _top_faces(all_triangles(drawn_layers(lights.pieces[0][0])), 2)
    assert tops[0][0].color[:3] == pytest.approx(LIGHT)
    assert GREY != LIGHT


def test_an_armour_drawing_nothing_has_no_pieces() -> None:
    drawn = region_drawing(record({"wings": {"whole": _nothing}}), WING, LIGHT, 12)
    assert drawn.pieces == []
    # Its frame still lies in its outline, over the model's floor.
    assert len(drawn.frame) == 2


def test_the_boss_may_draw_the_pieces_and_the_frame_itself() -> None:
    entry = {"whole": _wing_armour, "pieces": [_piece, _nothing], "frame": _piece}
    drawn = region_drawing(record({"wings": entry}), WING, LIGHT, 12)
    assert [p[0] for p in drawn.pieces] == [_piece, _nothing]
    # A piece's node sits at the middle of what it draws.
    assert drawn.pieces[0][1] == pytest.approx([-20, 2, 5])
    assert drawn.pieces[1][1] == [0, 0, 0]
    assert drawn.frame == [_piece]


def test_the_default_frame_lies_just_over_the_armour_s_lowest_point_or_is_none() -> None:
    drawn = region_drawing(record({"wings": {"whole": _wing_armour}}), WING, LIGHT, 12)
    floor = all_triangles(drawn_layers(drawn.frame[0]))
    assert bounds_of(floor)[4] == pytest.approx(0 + BOSS_LOOK.frame.lift)
    # A moving region without a frame style leaves no frame.
    assert region_drawing(record({"flap": {"whole": _lights_only}}), FLAP, LIGHT, 4).frame is None


def test_a_chunk_flies_out_up_then_down_tumbling_and_shrinking_away() -> None:
    centre = [20.0, 2.0, 10.0]
    start = chunk_pose(centre, 0, 0)
    assert start[0] == pytest.approx(centre)
    assert start[3] == 1
    mid = chunk_pose(centre, 0, 0.3)
    assert math.hypot(mid[0][0], mid[0][2]) > math.hypot(centre[0], centre[2])
    assert mid[0][1] > centre[1]
    end = chunk_pose(centre, 0, 1)
    assert end[0][1] < centre[1]
    assert end[3] == 0
    assert end[1] != 0
    # A piece at the centre is thrown by its index.
    assert chunk_pose([0.0, 0.0, 0.0], 3, 0.5)[0] != chunk_pose([0.0, 0.0, 0.0], 4, 0.5)[0]


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


def test_it_strains_then_bursts_into_flying_pieces_baring_the_frame(view: Any) -> None:
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


@pytest.fixture
def built(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Return the armour of a plane, on fake nodes: a bursting wing, a moving hatch and flap.

    The hatch's carrier is given; the flap's is not, and a fourth region is not drawn.
    """
    builder = patch_models(monkeypatch, boss_armour)
    trims: list[tuple[str, str]] = []
    monkeypatch.setattr(boss_armour, "set_trim_group", lambda n: trims.append(("group", n.name)))
    monkeypatch.setattr(boss_armour, "clear_trim", lambda n: trims.append(("clear", n.name)))
    root = FakeNode("plane", "scene")
    flashes: list[_Flash] = []

    def flash_of(_model: Any) -> _Flash:
        flashes.append(_Flash())
        return flashes[-1]

    bare = armour_region("bare", 1, [[-40, -30], [-30, -30], [-30, -20], [-40, -20]], "ring")
    design = SimpleNamespace(id="plane", armour=[WING, HATCH, FLAP, bare])
    drawing = record({
        "core": _nothing,
        "armour": {
            "wings": {"whole": _wing_armour, "pieces": [_piece, _nothing]},
            "hatch": {"whole": _flesh_armour},
            "flap": {"whole": _lights_only},
        },
    })
    carriers = {"hatch": FakeNode("plane-hatch-carrier", "scene")}
    views = build_armour(design, drawing, root, LIGHT, None, flash_of, carriers)
    return SimpleNamespace(
        views=views, root=root, builder=builder, flashes=flashes, trims=trims, carriers=carriers
    )


def test_a_bursting_region_is_its_whole_its_pieces_on_their_nodes_and_its_hidden_frame(
    built: Any,
) -> None:
    wings = built.views[0]
    assert isinstance(wings, ArmourView)
    models = built.builder.models
    assert wings.whole is models["plane-armour-wings"]
    assert wings.whole.root.parent is built.root
    assert built.builder.faces("plane-armour-wings") == 12
    # Each piece on a node at its centre, the drawing drawn back round it, untrimmed and hidden.
    assert [c.centre for c in wings.chunks] == [pytest.approx([-20, 2, 5]), [0, 0, 0]]
    chunk = wings.chunks[0]
    assert chunk.node.name == "plane-armour-wings-chunk-0"
    assert chunk.node.parent is built.root
    assert chunk.node.position.xyz() == pytest.approx([-20, 2, 5])
    assert chunk.node.enabled is False
    piece = models["plane-armour-wings-chunk-0"]
    assert piece.root.parent is chunk.node
    assert piece.root.position.xyz() == pytest.approx([20, -2, -5])
    assert ("clear", "plane-armour-wings-chunk-0") in built.trims
    # The frame: its floor trimmed along its outline (GFX-TRIM-09), its ribs not; hidden until the
    # burst.
    assert wings.frame.root.name == "plane-armour-wings-frame"
    assert wings.frame.root.parent is built.root
    assert wings.frame.root.enabled is False
    assert [m.root.name for m in wings.frame.models] == [
        "plane-armour-wings-frame-floor",
        "plane-armour-wings-frame-ribs",
    ]
    assert ("group", "plane-armour-wings-frame-floor") in built.trims
    assert ("clear", "plane-armour-wings-frame-ribs") in built.trims
    assert wings.flash is built.flashes[0]


def test_a_region_the_model_does_not_draw_has_no_view(built: Any) -> None:
    assert [v.region.id for v in built.views] == ["wings", "hatch", "flap"]
    assert "plane-armour-bare" not in built.builder.models


def test_a_moving_piece_hangs_on_its_mover_with_its_carrier_and_frame(built: Any) -> None:
    hatch = built.views[1]
    assert isinstance(hatch, MovingView)
    assert hatch.whole.root.parent is hatch.mover
    assert hatch.mover.name == "plane-armour-hatch-mover"
    assert hatch.mover.parent is built.root
    assert hatch.carrier is built.carriers["hatch"]
    assert hatch.frame.root.parent is built.root
    assert hatch.frame.root.enabled is False
    # No carrier was given for the flap: the piece gets its own; no frame style: no frame.
    flap = built.views[2]
    assert flap.carrier.name == "plane-armour-flap-carrier"
    assert flap.carrier.parent is built.root
    assert flap.frame is None


def test_a_moving_piece_strains_then_moves_into_its_new_pose(built: Any) -> None:
    view = built.views[1]
    view.show(None, {}, 0.1)
    # At rest: the piece as drawn, the weapons riding it drawn where they end up (10 px back).
    assert view.mover.position.xyz() == pytest.approx([0, 0, 0])
    assert view.carrier.position.xyz() == pytest.approx([0, 0, 10])
    assert view.frame.root.enabled is False
    assert view.flash.since == [1000]
    # It strains as armour does: it shudders and strobes before the burst.
    t = LOOK.burst / 2
    view.show(_boss(0, 1, t), {}, 0.1)
    jolt = math.sin(t * 90) * LOOK.shudder * 0.5
    assert view.whole.root.position.xyz() == pytest.approx([jolt, 0, -jolt * 0.6])
    assert view.flash.since[-1] == (0 if math.floor(t * LOOK.strobeHz * 4) % 2 == 0 else 1000)
    assert view.frame.root.enabled is False
    # Once moved: at its end pose (10 px up the screen is model -Z), its frame bared.
    view.show(_boss(1, 0, 0), {}, 0.1)
    assert view.mover.position.xyz() == pytest.approx([0, 0, -10])
    assert view.carrier.position.xyz() == pytest.approx([0, 0, 0])
    assert view.whole.root.position.xyz() == [0, 0, 0]
    assert view.flash.since[-1] == 7.0
    assert view.frame.root.enabled is True
    assert all(len(m.synced) == 1 for m in view.frame.models)
    # A piece without a frame shows none.
    built.views[2].show(_boss(1, 0, 0), {}, 0.1)


# BOSS-42 (D-254): every boss draws each of its armour regions.


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=[d.id for d in BOSS_DESIGNS])
def test_boss_42_every_region_of_the_boss_is_drawn(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        drawn = region_drawings(design, boss_drawing(design.id, mp))
    finally:
        mp.undo()
    assert len(drawn) == len(design.armour)
    assert all(d is not None for d in drawn), [
        r.id for r, d in zip(design.armour, drawn, strict=True) if d is None
    ]


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=[d.id for d in BOSS_DESIGNS])
def test_boss_43_the_drawn_regions_stay_in_the_piece_budget(design: Any) -> None:
    mp = pytest.MonkeyPatch()
    try:
        drawn = region_drawings(design, boss_drawing(design.id, mp))
    finally:
        mp.undo()
    total = 0
    for region, d in zip(design.armour, drawn, strict=True):
        if d is None:
            continue
        assert len(d.pieces) <= BOSS_LOOK.armour.chunks, region.id
        assert len(all_triangles(drawn_layers(d.whole))) > 0, region.id
        total += len(d.pieces)
    assert total <= BOSS_LOOK.armour.bossChunks
