# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/ship_model.py` (GFX-SHIP-01)."""

import math
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.config.readability import READABILITY
from game.config.ship_look import PLAYER_SHIP_SCALE
from game.index import GAME
from game.view import ship_hull as hull
from game.view import ship_model
from game.view.player_ship_models import PLAYER_SHIP_MODELS
from game.view.ship_hull import hull_sections
from game.view.ship_model import build_player_ship
from render.geometry.lathe_z import (
    build_faceted_lathe_vertex_data,
    build_smooth_top_lathe_vertex_data,
)
from render.geometry.section_loft import build_section_loft


@pytest.fixture
def scene(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, ship_model)
    monkeypatch.setattr(
        ship_model, "get_ship_materials", lambda _scene: MagicMock(name="materials")
    )
    return MagicMock(name="scene")


def test_the_ship_model_is_built_under_a_root_node(scene: Any) -> None:
    assert build_player_ship(scene) is not None


def _upper_share(profile: list[list[float]], halves: Any) -> float:
    """Share of the lathe's triangles whose centre lies over the upper half (Y >= 0)."""
    positions, indices, _normals = build_smooth_top_lathe_vertex_data(profile, halves)
    upper = 0
    for t in range(0, len(indices), 3):
        y = sum(positions[indices[t + k] * 3 + 1] for k in range(3))
        upper += 1 if y >= 0 else 0
    return upper / (len(indices) / 3)


def test_gfx_ship_05_the_faceted_hull_stays_cheap() -> None:
    """D-336: the faceted body, every face flat, keeps well under a thousand triangles."""
    _positions, indices, _normals = build_section_loft(hull_sections(), 0)
    assert len(indices) / 3 < 1000


def test_gfx_ship_01_the_wings_are_forward_swept() -> None:
    """D-330: the tip's leading and trailing edges lie ahead of the root's."""
    wing = ship_model.MAIN_WING
    assert wing[1][1] > wing[0][1]
    assert wing[3][1] > wing[4][1]


def test_gfx_ship_01_twin_reactors_sit_one_over_the_other_on_each_wing_tip() -> None:
    """D-331, D-339: one over the other, the fins canted 45°; the wing runs on past them."""
    pod = ship_model.TIP_REACTOR
    tip = ship_model.MAIN_WING[2]
    body = ship_model.TIP_BODY
    assert pod["x"] + body["halfWidth"] < tip[0] < pod["x"] + body["halfWidth"] + 0.3
    upper, lower = pod["ys"]
    assert upper > 0 > lower
    assert upper - lower >= 2 * pod["radius"]
    x = pod["x"]
    assert ship_model._trailing_edge(x) < pod["z"] < ship_model._leading_edge(x)


def test_gfx_ship_01_the_flaps_and_panel_lines_lie_on_the_wing() -> None:
    for outline in [ship_model.WING_FLAP, *ship_model.WING_LINES]:
        for x, z in outline:
            assert ship_model._trailing_edge(x) <= z <= ship_model._leading_edge(x), (x, z)


def test_gfx_ship_01_the_missile_pods_run_through_the_wings_their_tips_in_view() -> None:
    """D-330, D-343, D-344: through the wing, root to tip; the front ahead of the leading edge."""
    assert not hasattr(ship_model, "CANNON")
    pod = ship_model.MISSILE_POD
    profile = ship_model.MISSILE_POD_PROFILE
    radius = max(r for _z, r in profile)
    wing = ship_model.MAIN_WING
    assert wing[0][0] < pod["x"] - radius
    assert pod["x"] + radius < wing[2][0]
    # The wing runs through it: its flat top above the wing's top face, its bottom below; taller
    # than wide.
    half_height = radius * math.cos(math.pi / 8) * pod["stretch"]
    assert pod["y"] + half_height > ship_model.WING_THICKNESS / 2
    assert pod["y"] - half_height < -ship_model.WING_THICKNESS / 2
    assert half_height > radius
    front = pod["z"] + profile[0][0]
    assert front > ship_model._leading_edge(pod["x"] + radius) + 0.2


def test_gfx_ship_01_the_strakes_join_the_body_to_the_nacelles() -> None:
    """D-336: the body's chines widen into strakes reaching the nacelles, along the wing roots."""
    radius = ship_model.REACTOR["radius"]
    inner = ship_model.REACTOR_OFFSET_X - radius
    front = ship_model.REACTOR_Z + ship_model.REACTOR["length"] / 2
    for z in [front - 0.2, ship_model.MAIN_WING[0][1], hull.STATIONS[-1][hull.Z]]:
        assert hull.station_at(z)[hull.CHINE_HALF_WIDTH] > inner
    # D-356: behind the body's back, the strake's tail runs into the nacelle to the wing's root.
    tail = ship_model.STRAKE_TAIL
    assert max(x for x, _z in tail) > inner
    assert min(z for _x, z in tail) < ship_model.MAIN_WING[4][1]
    # The body itself stays slim; the main wing's root lies in the nacelle.
    assert max(s[hull.BODY_HALF_WIDTH] for s in hull.STATIONS) < inner / 2
    assert ship_model.MAIN_WING[0][0] == pytest.approx(ship_model.REACTOR_OFFSET_X)


def test_gfx_ship_01_the_body_has_seams_and_vents_on_its_strakes() -> None:
    """D-336: the seams lie along the body, the vents on the flat of the strakes."""
    nose = hull.STATIONS[0][hull.Z]
    tail = hull.STATIONS[-1][hull.Z]
    assert all(tail < z < nose for z in ship_model.SEAM_ZS)
    for vent in ship_model.VENTS:
        for x, z in vent:
            station = hull.station_at(z)
            assert station[hull.BODY_HALF_WIDTH] * hull.CHINE_ROOT < x
            assert x < station[hull.CHINE_HALF_WIDTH]


def test_gfx_ship_01_the_central_body_is_long_and_slim_with_no_reactor_at_its_back() -> None:
    """D-354: the nose 0.55 longer; D-356: the back cut square at -1.45, 4.75 long, not pointy."""
    nose = hull.STATIONS[0]
    tail = hull.STATIONS[-1]
    assert nose[hull.Z] - tail[hull.Z] == pytest.approx(4.75)
    assert all(v > 0 for v in tail[1:])
    assert max(s[hull.BODY_HALF_WIDTH] for s in hull.STATIONS) <= 0.3
    # The nacelles' nozzles are well clear of the body's centre line.
    assert ship_model.REACTOR_OFFSET_X - ship_model.REACTOR["radius"] > 0.5


def test_gfx_ship_01_the_tails_and_ventral_fins_stand_on_the_wing_tip_pods() -> None:
    """D-353: moved from the main nacelles, their roots run along the tip pod's length."""
    pod = ship_model.TIP_REACTOR
    front = pod["z"] + pod["length"] / 2
    back = pod["z"] - pod["length"] / 2
    shift = ship_model.TIP_TAIL_SHIFT
    for outline in [ship_model.TAIL, ship_model.VENTRAL_FIN]:
        roots = [z + shift for x, z in outline if x == 0]
        assert roots
        assert all(back < z < front for z in roots)


def test_gfx_ship_01_the_tip_pods_carry_a_tail_and_a_ventral_fin_not_45_degree_fins(
    scene: Any, monkeypatch: Any
) -> None:
    """D-353: the tails replace the pods' 45° fins; the main nacelles carry none."""
    nodes: dict[str, Any] = {}
    real = ship_model.new_transform_node

    def node(name: str, *args: Any) -> Any:
        nodes[name] = real(name, *args)
        return nodes[name]

    monkeypatch.setattr(ship_model, "new_transform_node", node)
    build_player_ship(scene)
    assert not any(name.startswith("ship-tip-") and "-fin-" in name for name in nodes)
    for side, sign in [("right", 1), ("left", -1)]:
        tail = nodes["ship-tail-" + side]
        assert tail.position.set.call_args[0][0] == pytest.approx(
            sign * ship_model.TIP_REACTOR["x"]
        )


def test_gfx_ship_01_one_body_wraps_each_wing_tips_twin_reactors() -> None:
    """D-332, D-339: its section round both reactors, from their fronts to short of the nozzles."""
    pod = ship_model.TIP_REACTOR
    body = ship_model.TIP_BODY
    radius = pod["radius"]
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    assert body["halfWidth"] > radius
    assert body["halfHeight"] > pod["ys"][0] - middle + radius * math.cos(math.pi / 6)
    front = max(z for z, _k in ship_model.TIP_BODY_PROFILE)
    back = min(z for z, _k in ship_model.TIP_BODY_PROFILE)
    assert front == pytest.approx(pod["length"] / 2)
    assert back > -pod["length"] / 2


def test_gfx_ship_01_one_octagonal_intake_feeds_both_tip_reactors(
    scene: Any, monkeypatch: Any
) -> None:
    """D-339: the tip reactors have no intakes of their own; one octagon, the body's height."""
    intakes: list[list[Any]] = []
    monkeypatch.setattr(
        ship_model,
        "add_reactor_intake",
        lambda name, radius, _front, _parent, sides, _stretch=1.0: intakes.append([
            name,
            radius,
            sides,
        ]),
    )
    reactors: dict[str, list[Any]] = {}

    def reactor(name: str, _size: Any, _scene: Any, *rest: Any) -> Any:
        reactors[name] = list(rest)
        return MagicMock(name=name)

    monkeypatch.setattr(ship_model, "build_reactor", reactor)
    build_player_ship(scene)
    assert sorted(i[0] for i in intakes) == ["ship-tip-left", "ship-tip-right"]
    assert all(i[2] == 8 for i in intakes)
    intake = ship_model.TIP_INTAKE
    flat = intake["radius"] * math.cos(math.pi / 8)
    body = ship_model.TIP_BODY
    assert flat == pytest.approx(body["halfWidth"], abs=0.02)
    assert flat * intake["stretch"] == pytest.approx(body["halfHeight"], abs=0.03)
    for name, rest in reactors.items():
        if "-tip-" in name:
            assert rest == []
        else:
            assert rest == [True, ship_model.OCTAGON, ship_model.REACTOR_HEIGHT]


def test_gfx_ship_01_a_laser_with_a_minigun_either_side_under_the_belly(
    scene: Any, monkeypatch: Any
) -> None:
    """D-339, D-342: the laser on the centre line, a minigun of six barrels each side."""
    rods: dict[str, Any] = {}
    real = ship_model.faceted_rod

    def rod(name: str, size: Any, position: Any, *rest: Any) -> Any:
        rods[name] = position
        return real(name, size, position, *rest)

    monkeypatch.setattr(ship_model, "faceted_rod", rod)
    lathes: list[str] = []
    real_lathe = ship_model.create_faceted_lathe_along_z

    def lathe(name: str, *args: Any) -> Any:
        lathes.append(name)
        return real_lathe(name, *args)

    monkeypatch.setattr(ship_model, "create_faceted_lathe_along_z", lathe)
    build_player_ship(scene)
    assert "ship-laser-core" in rods
    for side in ["right", "left"]:
        prefix = "ship-minigun-" + side + "-barrel-"
        barrels = [n for n in lathes if n.startswith(prefix) and not n.endswith("-bore")]
        assert len(barrels) == 6
        # D-351: each with its bore, matte black, apart.
        assert len([n for n in lathes if n.startswith(prefix) and n.endswith("-bore")]) == 6
    gun = ship_model.MINIGUN
    laser = ship_model.LASER
    # D-340: the laser runs out past the ship's nose tip.
    nose = hull.STATIONS[0][hull.Z]
    core = laser["core"]
    assert core["zs"][1] > nose
    assert ship_model.LASER_EMITTER[0][0] > core["zs"][1]
    # D-342: its prongs reach past the core's tip, either side of it, and clear under the nose.
    rail = ship_model.LASER_RAIL
    assert max(z for _x, z in rail) > ship_model.LASER_EMITTER[0][0]
    assert min(x for x, _z in rail) > core["radius"]
    top = laser["y"] + laser["railThickness"] / 2
    for _x, z in rail:
        assert top < -hull.station_at(z)[hull.BELLY_DEPTH]
    # The minigun drums sit in the fairing's flanks: half in, half out.
    # D-357: the fairing's size where the drums are, between its two sizes around them.
    fairing = ship_model.GUN_FAIRING
    k = next(i for i in range(len(fairing) - 1) if fairing[i][0] <= gun["z"] <= fairing[i + 1][0])
    t = (gun["z"] - fairing[k][0]) / (fairing[k + 1][0] - fairing[k][0])
    size = [gun["z"]] + [fairing[k][c] + (fairing[k + 1][c] - fairing[k][c]) * t for c in [1, 2]]
    _z, ring = ship_model.fairing_section(gun["z"], size)
    widest = max(p[0] for p in ring)
    assert gun["x"] - gun["drum"]["radius"] < widest < gun["x"] + gun["drum"]["radius"]


def test_gfx_ship_01_the_gun_fairing_grows_out_of_the_belly() -> None:
    """D-340: the fairing's top lies inside the belly; it closes at both ends."""
    fairing = ship_model.GUN_FAIRING
    assert fairing[0][1] == 0
    assert fairing[-1][1] == 0
    for size in fairing:
        _z, ring = ship_model.fairing_section(size[0], size)
        top = max(p[1] for p in ring)
        assert top > -hull.station_at(size[0])[hull.BELLY_DEPTH]


def test_gfx_ship_01_the_wings_sit_towards_the_nacelles_back() -> None:
    """D-333: the wing root's middle behind the nacelle's, its trailing edge still inside it."""
    root_front = ship_model.MAIN_WING[0][1]
    root_back = ship_model.MAIN_WING[4][1]
    middle = ship_model.REACTOR_Z
    back = middle - ship_model.REACTOR["length"] / 2
    assert (root_front + root_back) / 2 < middle
    assert back < root_back


def test_gfx_trim_the_canards_top_lies_at_the_bodys_chine_edge() -> None:
    """D-333: the canards' trim runs on from the body's beside the cockpit."""
    root_x = ship_model.CANARD[0][0]
    for _x, z in ship_model.CANARD:
        assert root_x < hull.station_at(z)[hull.CHINE_HALF_WIDTH]
    assert pytest.approx(hull.CHINE_EDGE) == ship_model.CHINE_EDGE


def test_gfx_ship_09_the_wings_canards_and_canopy_glow_not_the_guns(
    scene: Any, monkeypatch: Any
) -> None:
    """D-335: glowing leading edges on the wings, strakes and canards; none on the guns."""
    names: list[str] = []
    real = ship_model.edge_strip

    def record(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "edge_strip", record)
    build_player_ship(scene)
    for side in ["right", "left"]:
        # D-346: the tails and ventral fins too, their leading edge and tip.
        parts = ["wing", "strake-0", "strake-4", "canard-0", "canard-1"]
        parts.extend(["tail-0", "tail-1", "ventral-0", "ventral-1"])
        for part in parts:
            assert "ship-glow-" + side + "-" + part in names
    assert not any("missile" in n or "gun" in n for n in names)


def test_gfx_ship_09_the_player_ship_has_no_trim_round_it() -> None:
    """D-335: the game's ship models are the bare ones, no edge trim wrapped round them."""
    assert GAME.view.player_ship_models is PLAYER_SHIP_MODELS


def test_gfx_ship_09_the_canopy_sills_glow(scene: Any, monkeypatch: Any) -> None:
    """D-335, D-354: the cockpit glows along its sill rails; the canopy is of tinted glass."""
    meshes: dict[str, Any] = {}

    def loft(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(ship_model, "create_section_loft", loft)
    materials = MagicMock(name="materials")
    monkeypatch.setattr(ship_model, "get_ship_materials", lambda _scene: materials)
    build_player_ship(scene)
    for side in ["right", "left"]:
        assert meshes["ship-canopy-rail-" + side].material is materials.edgeGlow
    assert meshes["ship-canopy"].material is materials.glass
    assert meshes["ship-cockpit-floor"].material is materials.intakeBlack


def test_gfx_ship_01_the_main_reactors_are_taller_than_wide(scene: Any, monkeypatch: Any) -> None:
    """D-337: the main nacelles are stretched upright, the tip reactors are not."""
    reactors: dict[str, Any] = {}

    def reactor(name: str, *_args: Any) -> Any:
        reactors[name] = MagicMock(name=name)
        reactors[name].scaling.y = 1
        return reactors[name]

    monkeypatch.setattr(ship_model, "build_reactor", reactor)
    build_player_ship(scene)
    assert ship_model.REACTOR_HEIGHT > 1
    for side in ["right", "left"]:
        assert reactors["ship-reactor-" + side].scaling.y == ship_model.REACTOR_HEIGHT
    tips = [m for name, m in reactors.items() if "-tip-" in name or "tip" in name]
    assert tips
    assert all(m.scaling.y == 1 for m in tips)


def test_gfx_ship_01_the_minigun_barrels_are_hollow_at_their_muzzles() -> None:
    """D-345: the profile runs in from the muzzle's rim to a bore, then out round the barrel."""
    bore = {"radius": 0.5, "depth": 0.06}
    profile = ship_model.barrel_profile(0.5, 0.02, bore)
    assert profile[0] == pytest.approx([0.25 - 0.06, 0])
    assert profile[1] == pytest.approx([0.19, 0.01])
    assert profile[2] == pytest.approx([0.25, 0.01])
    assert profile[3] == pytest.approx([0.25, 0.02])
    assert profile[-1] == pytest.approx([-0.25, 0])


@pytest.mark.parametrize("up", [1, -1])
def test_gfx_ship_01_the_reactor_scoops_stand_on_the_nacelle_and_ramp_to_its_back(up: int) -> None:
    """D-347: full height at the mouth, down to the nacelle at its back; faces turned outward."""
    sections = ship_model.scoop_sections(up)
    scoop = ship_model.REACTOR_SCOOP
    assert sections[0][0] == scoop["front"]
    assert sections[-1][0] == pytest.approx(-ship_model.REACTOR["length"] / 2)
    heights = [max(abs(p[1]) for p in ring) for _z, ring in sections]
    assert heights[0] > heights[-1]
    positions, indices, normals = build_section_loft(sections, 0)
    top = max(abs(positions[k * 3 + 1]) for k in range(len(positions) // 3))
    for t in range(0, len(indices), 3):
        ys = [positions[indices[t + k] * 3 + 1] for k in range(3)]
        # The faces on the scoop's top face away from the nacelle.
        if all(abs(y) > top - 0.001 for y in ys):
            assert normals[indices[t] * 3 + 1] * up > 0


def test_gfx_ship_01_the_reactor_scoops_have_fins_across_their_mouths(
    scene: Any, monkeypatch: Any
) -> None:
    """D-348: flat fins across each scoop's mouth, as the main intakes have; the ramp eases down."""
    names: list[str] = []
    real = ship_model.panel

    def record(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "panel", record)
    build_player_ship(scene)
    fins = [n for n in names if "-scoop-" in n and "-fin-" in n]
    # D-351: three fins fit the mouth at the intakes' spacing.
    assert len(fins) == 2 * 2 * 3
    heights = [max(p[1] for p in ring) for _z, ring in ship_model.scoop_sections(1)]
    assert heights == sorted(heights, reverse=True)


def test_gfx_ship_01_the_fairing_meets_the_hull_under_its_flanks() -> None:
    """D-349: the widened fairing's top corners lie inside the hull's underside, not under it."""
    for size in ship_model.GUN_FAIRING:
        if size[1] == 0:
            continue
        _z, ring = ship_model.fairing_section(size[0], size)
        x, y = ring[0]
        assert y > hull.underside_height(hull.station_at(size[0]), x)


@pytest.mark.parametrize("up", [1, -1])
def test_gfx_ship_01_a_scoops_collar_rings_its_mouth_and_holds_its_fins(up: int) -> None:
    """D-351: the mouth inside the collar's outer ring; the fins' ends in the collar's wall."""
    outer, mouth, lining = ship_model.scoop_collar_rings(up)
    assert len(outer) == len(mouth) == len(lining)
    scoop = ship_model.REACTOR_SCOOP

    def extent(ring: list[list[float]]) -> tuple[float, float, float]:
        ys = [p[1] * up for p in ring]
        return max(p[0] for p in ring), min(ys), max(ys)

    o_half, o_low, o_high = extent(outer)
    m_half, m_low, m_high = extent(mouth)
    l_half, l_low, l_high = extent(lining)
    assert o_low < m_low < l_low < l_high < m_high < o_high
    assert m_half < o_half
    assert l_half < m_half
    fin_half = scoop["width"] / 2 * (1 + scoop["mouth"]) / 2
    assert m_half < fin_half < o_half
    room = scoop["height"] * scoop["mouth"] / 2 * ship_model.REACTOR_HEIGHT
    heights = ship_model.intake_fin_heights(room)
    assert len(heights) == 3


def test_gfx_ship_01_the_minigun_bores_face_the_axis(scene: Any, monkeypatch: Any) -> None:
    """D-352: the bore's lathe alone faces outward, so the builder turns it round to be seen."""
    gun = ship_model.MINIGUN
    barrels = gun["barrels"]
    profile = ship_model.barrel_profile(barrels["length"], barrels["radius"], gun["bore"])
    positions, indices = build_faceted_lathe_vertex_data(profile[0:3], 6)
    walls = 0
    for t in range(0, len(indices), 3):
        a, b, c = (positions[indices[t + k] * 3 : indices[t + k] * 3 + 3] for k in range(3))
        u = [b[i] - a[i] for i in range(3)]
        v = [c[i] - a[i] for i in range(3)]
        # Babylon's front normal: (c - a) x (b - a).
        n = [v[1] * u[2] - v[2] * u[1], v[2] * u[0] - v[0] * u[2], v[0] * u[1] - v[1] * u[0]]
        if abs(n[2]) < 1e-12:
            walls += 1
            middle = [(a[i] + b[i] + c[i]) / 3 for i in range(2)]
            assert n[0] * middle[0] + n[1] * middle[1] > 0
    assert walls > 0
    meshes: dict[str, Any] = {}

    def lathe(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(ship_model, "create_faceted_lathe_along_z", lathe)
    build_player_ship(scene)
    bores = [m for name, m in meshes.items() if name.endswith("-bore")]
    assert len(bores) == 12
    for bore in bores:
        bore.flipFaces.assert_called_once_with(True)


def test_gfx_ship_09_on_the_playfield_the_glowing_edges_are_wide_enough_to_show(
    scene: Any, monkeypatch: Any
) -> None:
    """D-355: the playfield's ship has its strips some logical pixels across, the menus' thin."""
    widths: dict[str, float] = {}
    real = ship_model.edge_strip

    def record(name: str, edge: Any, inside: Any, size: Any, *args: Any) -> Any:
        widths[name] = size["width"]
        return real(name, edge, inside, size, *args)

    monkeypatch.setattr(ship_model, "edge_strip", record)
    build_player_ship(scene)
    assert set(widths.values()) == {ship_model.EDGE_GLOW["width"]}
    widths.clear()
    PLAYER_SHIP_MODELS["player"](scene)
    width = READABILITY.playerGlow.width / PLAYER_SHIP_SCALE
    assert all(w == pytest.approx(width) for w in widths.values())
    assert widths
    # At least a logical pixel across on the playfield.
    assert width * PLAYER_SHIP_SCALE >= 1


def test_gfx_ship_01_the_trailing_edges_form_a_w() -> None:
    """D-356: the trailing edges across the ship form a W.

    The main wings' run back from their tips to their roots, the strakes' forward again from the
    nacelles to the body's square back.
    """
    wing = ship_model.MAIN_WING
    tip = wing[3]
    root = wing[4]
    assert tip[1] > root[1]
    tail = ship_model.STRAKE_TAIL
    # The strake's trailing edge: from its corner in the nacelle to the body's back corner.
    outer = tail[3]
    inner = tail[0]
    assert outer[0] > inner[0]
    assert inner[1] - outer[1] > 0.3
    assert inner[1] == pytest.approx(hull.STATIONS[-1][hull.Z])
    # The body's back corner: at the side of the body, inside its strake.
    back = hull.STATIONS[-1]
    assert back[hull.BODY_HALF_WIDTH] <= inner[0] < back[hull.CHINE_HALF_WIDTH]


def test_gfx_ship_01_a_dark_plate_lies_on_the_bodys_square_back() -> None:
    """D-356: inside the back's section, standing out behind it."""
    back = hull.STATIONS[-1]
    sections = ship_model.tail_plate_sections()
    front_z, front = sections[0]
    back_z, rear = sections[1]
    assert back_z < back[hull.Z] < front_z
    for ring in [front, rear]:
        assert len(ring) >= 6
        assert max(abs(p[0]) for p in ring) < back[hull.BODY_HALF_WIDTH] * hull.CHINE_ROOT
        assert max(p[1] for p in ring) < back[hull.BODY_HEIGHT] + back[hull.SPINE]
        assert min(p[1] for p in ring) > -back[hull.BELLY_DEPTH]
