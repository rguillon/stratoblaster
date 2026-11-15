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
from game.view import ship_model, ship_parts
from game.view.player_ship_models import PLAYER_SHIP_MODELS
from game.view.ship_hull import hull_sections
from game.view.ship_model import build_player_ship
from game.view.ship_parts import REACTOR_INTAKE
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
    """D-331: one over the other; D-371: the wing runs a little into the fixed pod's flank."""
    pod = ship_model.TIP_REACTOR
    tip = ship_model.MAIN_WING[2]
    intake = ship_model.TIP_INTAKE
    flank = pod["x"] - intake["radius"] * math.cos(math.pi / 8)
    assert flank < tip[0] < flank + 0.05
    assert not hasattr(ship_model, "TIP_FAIRING")
    assert not hasattr(ship_model, "TIP_COLLAR")
    upper, lower = pod["ys"]
    assert upper > 0 > lower
    assert upper - lower >= 2 * pod["radius"]
    x = pod["x"]
    assert ship_model._trailing_edge(x) < pod["z"] < ship_model._leading_edge(x)


def test_gfx_ship_01_the_flaps_and_panel_lines_lie_on_the_wing() -> None:
    for outline in [ship_model.WING_FLAP, *ship_model.WING_LINES]:
        for x, z in outline:
            assert ship_model._trailing_edge(x) <= z <= ship_model._leading_edge(x), (x, z)


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
    roots = [z + shift for x, z in ship_model.TAIL if x == 0]
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
        # D-360: the ventral fin is the tail's mirror image under the pod; D-361: canted 40°.
        fin = nodes["ship-ventral-" + side]
        assert fin.rotation.z == pytest.approx(-tail.rotation.z)
        assert abs(math.pi / 2 - abs(tail.rotation.z)) == pytest.approx(math.radians(40), abs=0.01)


def test_gfx_ship_01_one_body_wraps_each_wing_tips_twin_reactors() -> None:
    """D-332, D-339: its section round both reactors, from their fronts to short of the nozzles."""
    pod = ship_model.TIP_REACTOR
    intake = ship_model.TIP_INTAKE
    radius = pod["radius"]
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    flat = intake["radius"] * math.cos(math.pi / 8)
    assert flat > radius
    assert flat * intake["stretch"] > pod["ys"][0] - middle + radius * math.cos(math.pi / 6)
    # D-395: from the intake to the nozzles' plane, a flat back face there.
    front = max(z for z, _k in ship_model.TIP_BODY_PROFILE)
    back = min(z for z, _k in ship_model.TIP_BODY_PROFILE)
    assert front == pytest.approx(pod["length"] / 2)
    assert back == pytest.approx(-pod["length"] / 2)
    assert ship_model.TIP_BODY_PROFILE[-2][0] == back
    # D-404: at the back its octagon's chamfers clear the nozzles' rings.
    scale = ship_model.TIP_BODY_PROFILE[-2][1]
    ring = radius * 0.9 + radius * 0.09
    rise = (pod["ys"][0] - middle) / intake["stretch"]
    assert flat * scale * math.sqrt(2) - rise > ring


def test_gfx_ship_01_one_octagonal_intake_feeds_both_tip_reactors(
    scene: Any, monkeypatch: Any
) -> None:
    """D-339: the tip reactors have no intakes of their own; one octagon, the body's height."""
    intakes: list[list[Any]] = []
    monkeypatch.setattr(
        ship_model,
        "add_reactor_intake",
        lambda name, radius, _front, _parent, sides, _stretch=1.0, rake=None: intakes.append([
            name,
            radius,
            sides,
            rake,
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
    # D-364: the mouth stepped, its top forward of its bottom, in the intake's stretched frame.
    rake = intakes[0][3]
    assert rake(0.12) == pytest.approx(ship_model.TIP_INTAKE["rake"])
    assert rake(-0.12) == 0
    intake = ship_model.TIP_INTAKE
    flat = intake["radius"] * math.cos(math.pi / 8)
    body = ship_model.TIP_BODY
    # D-404: wider than the body's old rectangle; as tall.
    assert flat > body["halfWidth"]
    assert flat * intake["stretch"] == pytest.approx(body["halfHeight"], abs=0.01)
    for name, rest in reactors.items():
        if "-tip-" in name:
            # D-385, D-395: no front ring and no nacelle: the body carries the nozzle.
            assert rest == [False, ship_parts.REACTOR_SIDES, 1.0, False, False]
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
    real_lathe = ship_model.smooth_lathe

    def lathe(name: str, *args: Any) -> Any:
        lathes.append(name)
        return real_lathe(name, *args)

    monkeypatch.setattr(ship_model, "smooth_lathe", lathe)
    build_player_ship(scene)
    assert "ship-laser-core" in rods
    for side in ["right", "left"]:
        prefix = "ship-minigun-" + side + "-barrel-"
        barrels = [n for n in lathes if n.startswith(prefix) and not n.endswith("-bore")]
        assert len(barrels) == 6
        # D-351: each with its bore, matte black, apart.
        assert len([n for n in lathes if n.startswith(prefix) and n.endswith("-bore")]) == 6
        # D-386: a solid clamp at their back, a thicker one near their muzzles.
        assert "ship-minigun-" + side + "-clamp" in lathes
        assert "ship-minigun-" + side + "-muzzle-clamp" in lathes
    laser = ship_model.LASER
    # D-340: the laser runs out past the ship's nose tip.
    nose = hull.STATIONS[0][hull.Z]
    core = laser["core"]
    assert core["zs"][1] > nose
    assert ship_model.LASER_EMITTER[0][0] > core["zs"][1]
    # D-400, D-405: its blades reach past the core's tip, either side of it, under the nose.
    rows = ship_model.LASER_RAIL_SECTIONS
    assert rows[-1][0] > ship_model.LASER_EMITTER[0][0]
    assert min(row[1] for row in rows) > core["radius"]
    for row in rows:
        assert laser["y"] + row[3] < -hull.station_at(row[0])[hull.BELLY_DEPTH]


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


def test_gfx_ship_01_no_canards() -> None:
    """D-363: the little front wings are gone."""
    assert not hasattr(ship_model, "CANARD")
    assert "canard" not in ship_model.EDGE_GLOW


def test_gfx_ship_09_only_the_tails_and_ventral_fins_glow(scene: Any, monkeypatch: Any) -> None:
    """D-370: glowing edges on the tails and ventral fins only (D-346), not the wings or strakes."""
    names: list[str] = []
    real = ship_model.edge_strip

    def record(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "edge_strip", record)
    build_player_ship(scene)
    expected = [
        "ship-glow-" + side + "-" + part
        for side in ["right", "left"]
        for part in ["tail-0", "tail-1", "ventral-0", "ventral-1"]
    ]
    assert sorted(names) == sorted(expected)


def test_gfx_ship_09_the_player_ship_has_no_trim_round_it() -> None:
    """D-335: the game's ship models are the bare ones, no edge trim wrapped round them."""
    assert GAME.view.player_ship_models is PLAYER_SHIP_MODELS


def test_gfx_ship_09_the_canopy_sills_are_gunmetal(scene: Any, monkeypatch: Any) -> None:
    """D-354: sill rails along the canopy of tinted glass; D-370: gunmetal (glowing before)."""
    meshes: dict[str, Any] = {}

    def loft(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(ship_model, "create_section_loft", loft)
    materials = MagicMock(name="materials")
    monkeypatch.setattr(ship_model, "get_ship_materials", lambda _scene: materials)
    build_player_ship(scene)
    for side in ["right", "left"]:
        assert meshes["ship-canopy-rail-" + side].material is materials.hullDark
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
    assert sections[-1][0] == pytest.approx(scoop["back"])
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
    # D-351: three fins fit the mouth at the intakes' spacing; D-368: a scoop on top only.
    assert len(fins) == 2 * 3
    assert not any("-scoop-bottom" in n for n in names)
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
def test_gfx_ship_01_a_scoops_mouth_is_built_as_the_main_intakes(up: int) -> None:
    """D-369: the scoop's front section, straight on, angled in to a lip, back into its duct."""
    skin = ship_model.scoop_intake_sections(REACTOR_INTAKE, up)
    lining = ship_model.scoop_intake_sections(ship_model.REACTOR_INTAKE_DUCT, up)
    front = ship_model.scoop_sections(up)[0]
    # It starts on the scoop's front, flush with it.
    assert skin[0][0] == front[0]
    assert [v for p in skin[0][1] for v in p] == pytest.approx([v for p in front[1] for v in p])
    counts = {len(ring) for _z, ring in skin + lining}
    assert counts == {len(front[1])}
    middle, radius = ship_model.scoop_mouth_frame()

    def size(ring: list[list[float]]) -> tuple[float, float]:
        ys = [p[1] * up for p in ring]
        return max(p[0] for p in ring), max(ys) - middle

    # The lip ahead of the scoop, narrower than the skin; the duct inside the lip.
    lip = max(range(len(skin)), key=lambda k: skin[k][0])
    assert skin[lip][0] == pytest.approx(front[0] + max(p[0] for p in REACTOR_INTAKE) * radius)
    assert size(skin[lip][1])[0] < size(skin[0][1])[0]
    assert size(skin[lip][1])[1] < size(skin[0][1])[1]
    assert all(size(ring)[0] < size(skin[lip][1])[0] for _z, ring in lining)


def test_gfx_ship_01_a_scoops_fins_span_its_duct_into_the_lips_wall() -> None:
    """D-351, D-369: the intakes' spacing, ends between the duct's lining and the lip's skin."""
    fins = ship_model.scoop_intake_fins(1)
    assert len(fins) == 3
    heights = [h for h, _outline in fins]
    middle, _radius = ship_model.scoop_mouth_frame()
    assert heights[1] == pytest.approx(middle)
    for height, outline in fins:
        half = max(p[0] for p in outline)
        assert min(p[0] for p in outline) == pytest.approx(-half)
        lining = ship_model.scoop_intake_sections(ship_model.REACTOR_INTAKE_DUCT, 1)[0][1]
        assert half > ship_model.ring_half_width(lining, height)
        lip = ship_model.scoop_intake_sections(REACTOR_INTAKE, 1)
        skin = max(lip, key=lambda s: s[0])[1]
        assert half < ship_model.ring_half_width(skin, height) + 0.01
    assert [h for h, _o in ship_model.scoop_intake_fins(-1)] == [-h for h in heights]


def test_gfx_ship_01_a_rings_half_width_at_a_height() -> None:
    """D-369: how far a closed ring reaches out at a height; nothing outside it."""
    square = [[1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0], [1.0, -1.0]]
    assert ship_model.ring_half_width(square, 0.0) == 1.0
    diamond = [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.0, -1.0]]
    assert ship_model.ring_half_width(diamond, 0.5) == pytest.approx(0.5)
    assert ship_model.ring_half_width(diamond, 2.0) == 0.0


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

    # D-387: the gun's round parts are smooth lathes.
    monkeypatch.setattr(ship_model, "smooth_lathe", lathe)
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


@pytest.mark.parametrize(
    ("height", "share"),
    [(0.255, 1), (0.1, 1), (0.0, 0.5), (-0.1, 0), (-0.255, 0), (0.0425, 0.75)],
)
def test_gfx_ship_01_the_tip_intake_is_stepped_in_thirds(height: float, share: float) -> None:
    """D-364: upper third forward, middle third a diagonal, lower third where it stood."""
    rake = ship_model.TIP_INTAKE["rake"]
    assert ship_model.tip_intake_rake(height) == pytest.approx(rake * share)


def test_gfx_ship_01_the_reactor_scoops_reach_past_the_main_intakes() -> None:
    """D-366: the scoops' fronts stand out ahead of the main intakes' lips."""
    reactor = ship_model.REACTOR
    lip = reactor["length"] / 2 + max(p[0] for p in REACTOR_INTAKE) * reactor["radius"]
    assert ship_model.REACTOR_SCOOP["front"] > lip


def test_gfx_ship_01_a_main_nacelles_top_is_flat_then_falls_at_its_chamfers() -> None:
    """D-367: the seat the scoops blend into, tapering towards the nacelle's back."""
    radius = ship_model.REACTOR["radius"]
    flat = radius * math.cos(math.pi / 8)
    edge = radius * math.sin(math.pi / 8)
    assert ship_model.nacelle_top(0.0, 1.0) == pytest.approx(flat)
    assert ship_model.nacelle_top(edge + 0.05, 1.0) == pytest.approx(flat - 0.05)
    assert ship_model.nacelle_scale(2.0) == 1
    assert ship_model.nacelle_scale(-0.8) == pytest.approx(0.95)
    assert ship_model.nacelle_scale(-0.9) == pytest.approx(0.9)
    assert ship_model.nacelle_scale(-3.0) == pytest.approx(0.85)


def test_gfx_ship_01_a_scoop_is_filleted_into_the_nacelle_and_crowned() -> None:
    """D-367: its feet sink just under the nacelle's top, its walls over it; a flat base ahead."""
    sections = ship_model.scoop_sections(1)
    assert len({len(ring) for _z, ring in sections}) == 1
    end = ship_model.scoop_seat_end()
    seated = [s for s in sections if s[0] < end - ship_model.REACTOR_SCOOP["flareRun"] + 0.001]
    assert seated
    z, ring = seated[0]
    foot = ring[0]
    assert -0.01 < foot[1] - ship_model.nacelle_top(foot[0], z) < 0
    wall = ring[ship_model.REACTOR_SCOOP["filletSteps"]]
    assert wall[1] - ship_model.nacelle_top(wall[0], z) > 0.0
    over = [s for s in sections if s[0] > end]
    assert over
    low = min(p[1] for p in over[0][1])
    assert len([p for p in over[0][1] if p[1] < low + 0.001]) >= 2
    # The crown: the middle of the top stands over the shoulders.
    top = max(p[1] for p in ring)
    assert any(abs(p[0]) < 1e-9 and p[1] == top for p in ring)


def test_gfx_ship_01_two_missile_pods_a_wing_over_and_under_it_between_its_edges(
    scene: Any, monkeypatch: Any
) -> None:
    """D-373: one over, one under each wing, between its edges, clear of its faces.

    D-390, D-392: boxes clear of its faces; D-374, D-402: between its edges across their width,
    from the nacelle to short of the tip pod.
    """
    pod = ship_model.MISSILE_POD
    wing = ship_model.MAIN_WING
    inner = pod["x"] - pod["halfWidth"]
    outer = pod["x"] + pod["halfWidth"]
    assert ship_model.REACTOR_OFFSET_X + ship_model.REACTOR["radius"] < inner
    assert outer < wing[2][0] - 0.05
    assert pod["front"] < min(ship_model._leading_edge(inner), ship_model._leading_edge(outer))
    for up in [1, -1]:
        sections = ship_model.missile_pod_sections(up)
        face = ship_model.WING_THICKNESS / 2
        for z, ring in sections:
            ys = [p[1] * up for p in ring]
            assert min(ys) >= face
            half = max(p[0] for p in ring)
            assert ship_model._trailing_edge(ship_model.MISSILE_POD["x"] + half) < z
        # D-403: the tail tapers evenly in width and height, then ends at its rear vent's rim.
        widths = [max(p[0] for p in ring) for _z, ring in sections[1:-1]]
        assert widths == sorted(widths, reverse=True)
        assert widths[-1] == pytest.approx(pod["halfWidth"] * pod["tail"])
    names: list[str] = []
    real = ship_model.create_section_loft

    def loft(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "create_section_loft", loft)
    build_player_ship(scene)
    for side in ["right", "left"]:
        for level in ["upper", "lower"]:
            name = "ship-missiles-" + side + "-" + level
            assert {name + "-pod", name + "-recess", name + "-vent"} <= set(names)


def test_gfx_ship_01_each_missile_pod_holds_26_black_launch_holes(
    scene: Any, monkeypatch: Any
) -> None:
    """D-375: staggered rows, 9, 8 and 9; D-391: black holes, not tips."""
    holes: list[str] = []
    real = ship_model.create_disc

    def disc(name: str, *args: Any) -> Any:
        holes.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "create_disc", disc)
    build_player_ship(scene)
    for side in ["right", "left"]:
        for level in ["upper", "lower"]:
            prefix = "ship-missiles-" + side + "-" + level + "-hole-"
            assert len([n for n in holes if n.startswith(prefix)]) == 26


def test_gfx_ship_01_the_minigun_rings_and_body() -> None:
    """D-378: a barrel on top; D-386, D-389: its rings and its shaped body.

    The muzzle ring ahead of the rear one, short of the muzzles; the drum's profile closed at both
    ends, its collar the widest.
    """
    gun = ship_model.MINIGUN
    barrels = gun["barrels"]
    assert barrels["turn"] == pytest.approx(math.pi / 6)
    rear = gun["clamp"]
    muzzle = gun["muzzleClamp"]
    assert rear["z"] + rear["half"] < muzzle["z"] - muzzle["half"]
    assert muzzle["half"] > rear["half"]
    assert muzzle["z"] + muzzle["half"] < barrels["z"] + barrels["length"] / 2
    drum = gun["drumProfile"]
    assert drum[0][1] == 0
    assert drum[-1][1] == 0
    assert max(r for _z, r in drum) == drum[-2][1]
    # The barrels start inside its collar.
    assert drum[-1][0] > barrels["z"] - barrels["length"] / 2


def test_gfx_ship_01_the_laser_rails_are_shaped_blades_with_clamps(
    scene: Any, monkeypatch: Any
) -> None:
    """D-400, D-401: seven-sided sections, sharp outside, mirrored; accent clamps round them."""
    for sign in [1, -1]:
        sections = ship_model.laser_rail_sections(sign)
        assert len(sections) == len(ship_model.LASER_RAIL_SECTIONS)
        for (_z, ring), row in zip(sections, ship_model.LASER_RAIL_SECTIONS, strict=True):
            assert len(ring) == 7
            xs = [p[0] * sign for p in ring]
            assert max(xs) == row[2]
            assert min(xs) == row[1]
    middle = ship_model.laser_rail_at(2.6)
    first, second = ship_model.LASER_RAIL_SECTIONS[0], ship_model.LASER_RAIL_SECTIONS[1]
    t = (2.6 - first[0]) / (second[0] - first[0])
    assert middle == pytest.approx([first[i] + (second[i] - first[i]) * t for i in range(1, 4)])
    last = ship_model.LASER_RAIL_SECTIONS[-1]
    assert ship_model.laser_rail_at(9.0) == [last[1], last[2], last[3]]
    assert ship_model.laser_rail_at(-9.0) == [first[1], first[2], first[3]]
    names: list[str] = []
    real = ship_model.panel

    def record(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(ship_model, "panel", record)
    build_player_ship(scene)
    clamps = [n for n in names if n.startswith("ship-laser-clamp-")]
    assert len(clamps) == 2 * len(ship_model.LASER_CLAMPS["zs"])


def test_gfx_ship_01_the_minigun_pylons_are_swept_airfoils() -> None:
    """D-399: root in the keel, tip in the drum; swept back; thinner at the tip; airfoil rings."""
    pylon = ship_model.MINIGUN_PYLON
    gun = ship_model.MINIGUN
    assert pylon["xs"][0] < ship_model.GUN_FAIRING[3][1]
    assert gun["x"] - gun["drum"]["radius"] < pylon["xs"][1] < gun["x"]
    assert pylon["leading"][0] > pylon["leading"][1]
    assert pylon["thickness"][0] > pylon["thickness"][1]
    for sign in [1, -1]:
        sections = pylon_rings = ship_model.pylon_sections(sign)
        assert [z for z, _r in sections] == [sign * x for x in pylon["xs"]]
        for _z, ring in pylon_rings:
            assert len(ring) == 6
            ys = [p[1] for p in ring]
            assert max(ys) > gun["y"] > min(ys)


def test_gfx_ship_01_the_tip_pods_are_fixed(scene: Any, monkeypatch: Any) -> None:
    """D-371: no pivot, no tilt, no joint geometry: the pods' parts are built on the ship."""
    assert not hasattr(ship_model, "TIP_TILT")
    assert not hasattr(ship_model, "tip_tilt_target")
    nodes: dict[str, Any] = {}
    real = ship_model.new_transform_node

    def node(name: str, *args: Any) -> Any:
        nodes[name] = real(name, *args)
        return nodes[name]

    monkeypatch.setattr(ship_model, "new_transform_node", node)
    root = build_player_ship(scene)
    assert not any("pivot" in name or "collar" in name for name in nodes)
    assert nodes["ship-tail-right"].parent is root


def test_gfx_ship_01_a_scoops_sections_never_repeat_a_place(monkeypatch: Any) -> None:
    """D-367: where the seat's joint falls on a ramp section, the section is made once."""
    scoop = ship_model.REACTOR_SCOOP
    lip = scoop["front"] - scoop["lip"]
    ramp = lip + (scoop["back"] - lip) / scoop["rampSteps"]
    monkeypatch.setattr(ship_model, "scoop_seat_end", lambda: ramp + scoop["flareRun"])
    zs = [z for z, _ring in ship_model.scoop_sections(1)]
    assert len(zs) == len(set(zs))
    assert zs == sorted(zs, reverse=True)
