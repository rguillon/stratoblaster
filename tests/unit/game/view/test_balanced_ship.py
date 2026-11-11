# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_ship.py` (GFX-SHIP-01)."""

import math
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.index import GAME
from game.view import balanced_hull as hull
from game.view import balanced_ship
from game.view.balanced_hull import hull_sections
from game.view.balanced_ship import build_balanced_ship
from game.view.player_ship_models import PLAYER_SHIP_MODELS
from render.geometry.lathe_z import build_smooth_top_lathe_vertex_data, smooth_profile
from render.geometry.section_loft import build_section_loft


@pytest.fixture
def scene(monkeypatch: Any) -> Any:
    stub_babylon(monkeypatch, balanced_ship)
    monkeypatch.setattr(
        balanced_ship, "get_ship_materials", lambda _scene: MagicMock(name="materials")
    )
    return MagicMock(name="scene")


def test_the_balanced_ship_is_built_under_a_root_node(scene: Any) -> None:
    assert build_balanced_ship(scene) is not None


def _upper_share(profile: list[list[float]], halves: Any) -> float:
    """Share of the lathe's triangles whose centre lies over the upper half (Y >= 0)."""
    positions, indices, _normals = build_smooth_top_lathe_vertex_data(profile, halves)
    upper = 0
    for t in range(0, len(indices), 3):
        y = sum(positions[indices[t + k] * 3 + 1] for k in range(3))
        upper += 1 if y >= 0 else 0
    return upper / (len(indices) / 3)


@pytest.mark.parametrize(
    ("profile", "halves"),
    [
        (
            smooth_profile(balanced_ship.CANOPY, balanced_ship.PROFILE_STEPS),
            balanced_ship.CANOPY_SECTION,
        ),
    ],
)
def test_gfx_ship_05_the_round_parts_put_their_triangles_on_the_upper_half(
    profile: list[list[float]], halves: Any
) -> None:
    """D-327: at least three quarters of each round part's triangles are over the upper half."""
    assert _upper_share(profile, halves) >= 0.75


def test_gfx_ship_05_the_faceted_hull_stays_cheap() -> None:
    """D-336: the faceted body, every face flat, keeps well under a thousand triangles."""
    _positions, indices, _normals = build_section_loft(hull_sections(), 0)
    assert len(indices) / 3 < 1000


def test_gfx_ship_01_the_wings_are_forward_swept() -> None:
    """D-330: the tip's leading and trailing edges lie ahead of the root's."""
    wing = balanced_ship.BALANCED_WING
    assert wing[1][1] > wing[0][1]
    assert wing[3][1] > wing[4][1]


def test_gfx_ship_01_twin_reactors_sit_one_over_the_other_on_each_wing_tip() -> None:
    """D-331: one above the wing's plane, one below, not overlapping; the fins canted 45°."""
    pod = balanced_ship.TIP_REACTOR
    tip = balanced_ship.BALANCED_WING[2]
    assert tip[0] < pod["x"] < tip[0] + pod["radius"]
    upper, lower = pod["ys"]
    assert upper > 0 > lower
    assert upper - lower >= 2 * pod["radius"]
    tip_front = balanced_ship.BALANCED_WING[2][1]
    tip_back = balanced_ship.BALANCED_WING[3][1]
    assert tip_back < pod["z"] < tip_front
    assert pytest.approx(math.pi / 4) == balanced_ship.TIP_FIN_CANT


def test_gfx_ship_01_the_flaps_and_panel_lines_lie_on_the_wing() -> None:
    for outline in [balanced_ship.WING_FLAP, *balanced_ship.WING_LINES]:
        for x, z in outline:
            assert balanced_ship._trailing_edge(x) <= z <= balanced_ship._leading_edge(x), (x, z)


def test_gfx_ship_01_the_missile_pods_hang_under_the_wings_their_tips_in_view() -> None:
    """D-330: under the wing, between root and tip; the front out ahead of the leading edge."""
    assert not hasattr(balanced_ship, "CANNON")
    pod = balanced_ship.MISSILE_POD
    profile = balanced_ship.MISSILE_POD_PROFILE
    radius = max(r for _z, r in profile)
    wing = balanced_ship.BALANCED_WING
    assert wing[0][0] < pod["x"] - radius
    assert pod["x"] + radius < wing[2][0]
    # Wholly under the wing's underside.
    assert pod["y"] + radius < -balanced_ship.WING_THICKNESS / 2
    front = pod["z"] + profile[0][0]
    assert front > balanced_ship._leading_edge(pod["x"] + radius) + 0.2


def test_gfx_ship_01_the_strakes_join_the_body_to_the_nacelles() -> None:
    """D-336: the body's chines widen into strakes reaching the nacelles, along the wing roots."""
    radius = balanced_ship.REACTOR["radius"]
    inner = balanced_ship.REACTOR_OFFSET_X - radius
    front = balanced_ship.REACTOR_Z + balanced_ship.REACTOR["length"] / 2
    for z in [front - 0.2, balanced_ship.BALANCED_WING[0][1], balanced_ship.BALANCED_WING[4][1]]:
        assert hull.station_at(z)[hull.CHINE_HALF_WIDTH] > inner
    # The body itself stays slim; the main wing's root lies in the nacelle.
    assert max(s[hull.BODY_HALF_WIDTH] for s in hull.STATIONS) < inner / 2
    assert balanced_ship.BALANCED_WING[0][0] == pytest.approx(balanced_ship.REACTOR_OFFSET_X)


def test_gfx_ship_01_the_body_has_seams_and_vents_on_its_strakes() -> None:
    """D-336: the seams lie along the body, the vents on the flat of the strakes."""
    nose = hull.STATIONS[0][hull.Z]
    tail = hull.STATIONS[-1][hull.Z]
    assert all(tail < z < nose for z in balanced_ship.SEAM_ZS)
    for vent in balanced_ship.VENTS:
        for x, z in vent:
            station = hull.station_at(z)
            assert station[hull.BODY_HALF_WIDTH] * hull.CHINE_ROOT < x
            assert x < station[hull.CHINE_HALF_WIDTH]


def test_gfx_ship_01_the_central_body_is_long_and_slim_with_no_reactor_at_its_back() -> None:
    """D-332: 5.2 long, closing to a point at the tail; about half as wide as before."""
    nose = hull.STATIONS[0]
    tail = hull.STATIONS[-1]
    assert nose[hull.Z] - tail[hull.Z] == pytest.approx(5.2)
    assert all(v == 0 for v in tail[1:])
    assert max(s[hull.BODY_HALF_WIDTH] for s in hull.STATIONS) <= 0.3
    # The nacelles' nozzles are well clear of the body's centre line.
    assert balanced_ship.REACTOR_OFFSET_X - balanced_ship.REACTOR["radius"] > 0.5


def test_gfx_trim_the_tails_lean_out_no_further_than_the_nacelles_edge() -> None:
    """D-330, D-332: seen from above, the canted tails stay inside their nacelle's outline."""
    span = max(x for x, _z in balanced_ship.TAIL)
    tip_x = balanced_ship.REACTOR_OFFSET_X + span * math.sin(balanced_ship.TAIL_CANT)
    assert tip_x < balanced_ship.REACTOR_OFFSET_X + balanced_ship.REACTOR["radius"] - 0.03
    front = balanced_ship.REACTOR_Z + balanced_ship.REACTOR["length"] / 2
    back = balanced_ship.REACTOR_Z - balanced_ship.REACTOR["length"] / 2
    assert all(back < z < front for _x, z in balanced_ship.TAIL)


def test_gfx_ship_01_one_body_wraps_each_wing_tips_twin_reactors() -> None:
    """D-332: its section round both reactors, its ends short of their intakes and nozzles."""
    pod = balanced_ship.TIP_REACTOR
    body = balanced_ship.TIP_BODY
    radius = pod["radius"]
    middle = (pod["ys"][0] + pod["ys"][1]) / 2
    assert body["halfWidth"] > radius
    assert body["halfHeight"] > pod["ys"][0] - middle + radius * math.cos(math.pi / 6)
    front = max(z for z, _k in balanced_ship.TIP_BODY_PROFILE)
    back = min(z for z, _k in balanced_ship.TIP_BODY_PROFILE)
    assert front < pod["length"] / 2
    assert back > -pod["length"] / 2


def test_gfx_ship_01_the_wings_sit_towards_the_nacelles_back() -> None:
    """D-333: the wing root's middle behind the nacelle's, its trailing edge still inside it."""
    root_front = balanced_ship.BALANCED_WING[0][1]
    root_back = balanced_ship.BALANCED_WING[4][1]
    middle = balanced_ship.REACTOR_Z
    back = middle - balanced_ship.REACTOR["length"] / 2
    assert (root_front + root_back) / 2 < middle
    assert back < root_back


def test_gfx_trim_the_canards_top_lies_at_the_bodys_chine_edge() -> None:
    """D-333: the canards' trim runs on from the body's beside the cockpit."""
    root_x = balanced_ship.CANARD[0][0]
    for _x, z in balanced_ship.CANARD:
        assert root_x < hull.station_at(z)[hull.CHINE_HALF_WIDTH]
    assert pytest.approx(hull.CHINE_EDGE) == balanced_ship.CHINE_EDGE


def test_gfx_ship_09_the_wings_canards_and_canopy_glow_not_the_guns(
    scene: Any, monkeypatch: Any
) -> None:
    """D-335: glowing leading edges on the wings, strakes and canards; none on the guns."""
    names: list[str] = []
    real = balanced_ship.edge_strip

    def record(name: str, *args: Any) -> Any:
        names.append(name)
        return real(name, *args)

    monkeypatch.setattr(balanced_ship, "edge_strip", record)
    build_balanced_ship(scene)
    for side in ["right", "left"]:
        for part in ["wing", "strake-0", "strake-4", "canard-0", "canard-1"]:
            assert "balanced-glow-" + side + "-" + part in names
    assert not any("missile" in n or "gun" in n for n in names)


def test_gfx_ship_09_the_player_ship_has_no_trim_round_it() -> None:
    """D-335: the game's ship models are the bare ones, no edge trim wrapped round them."""
    assert GAME.view.player_ship_models is PLAYER_SHIP_MODELS


def test_gfx_ship_09_the_canopy_frame_glows(scene: Any, monkeypatch: Any) -> None:
    """D-335: the cockpit's rim glows: the canopy frame is of the glowing material."""
    meshes: dict[str, Any] = {}

    def lathe(name: str, *_args: Any) -> Any:
        meshes[name] = MagicMock(name=name)
        return meshes[name]

    monkeypatch.setattr(balanced_ship, "create_smooth_top_lathe_along_z", lathe)
    materials = MagicMock(name="materials")
    monkeypatch.setattr(balanced_ship, "get_ship_materials", lambda _scene: materials)
    build_balanced_ship(scene)
    assert meshes["balanced-canopy-frame"].material is materials.edgeGlow
    assert meshes["balanced-canopy"].material is materials.canopy


def test_gfx_ship_01_the_main_reactors_are_taller_than_wide(scene: Any, monkeypatch: Any) -> None:
    """D-337: the main nacelles are stretched upright, the tip reactors are not."""
    reactors: dict[str, Any] = {}

    def reactor(name: str, *_args: Any) -> Any:
        reactors[name] = MagicMock(name=name)
        reactors[name].scaling.y = 1
        return reactors[name]

    monkeypatch.setattr(balanced_ship, "build_reactor", reactor)
    build_balanced_ship(scene)
    assert balanced_ship.REACTOR_HEIGHT > 1
    for side in ["right", "left"]:
        assert reactors["balanced-reactor-" + side].scaling.y == balanced_ship.REACTOR_HEIGHT
    tips = [m for name, m in reactors.items() if "-tip-" in name or "tip" in name]
    assert tips
    assert all(m.scaling.y == 1 for m in tips)
