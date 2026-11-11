# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/balanced_ship.py` (GFX-SHIP-01)."""

import math
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.babylon_stub import stub_babylon

from game.view import balanced_hull as hull
from game.view import balanced_ship
from game.view.balanced_hull import TOP_POINTS, hull_sections
from game.view.balanced_ship import build_balanced_ship
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


def test_gfx_ship_05_the_hull_puts_its_triangles_on_the_upper_half() -> None:
    """D-327: at least three quarters of the blended hull's triangles are over the upper half."""
    positions, indices, _normals = build_section_loft(hull_sections(), TOP_POINTS)
    upper = 0
    for t in range(0, len(indices), 3):
        y = sum(positions[indices[t + k] * 3 + 1] for k in range(3))
        upper += 1 if y >= 0 else 0
    assert upper / (len(indices) / 3) >= 0.75


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


def test_gfx_ship_01_the_main_reactors_stand_out_from_the_slim_body() -> None:
    """D-332: the nacelles stand clear of the body, a stub wing reaching from one into the other."""
    widest_body = max(s[hull.CHINE_HALF_WIDTH] for s in hull.STATIONS)
    radius = balanced_ship.REACTOR["radius"]
    inner = balanced_ship.REACTOR_OFFSET_X - radius
    assert inner > widest_body + 0.2
    stub = balanced_ship.STUB_WING
    for x, z in stub:
        station = hull.station_at(z)
        # Each end inside the body's chine or the nacelle.
        assert x < station[hull.CHINE_HALF_WIDTH] or inner < x < balanced_ship.REACTOR_OFFSET_X
    # The main wing's root lies in the nacelle.
    assert balanced_ship.BALANCED_WING[0][0] == pytest.approx(balanced_ship.REACTOR_OFFSET_X)


def test_gfx_ship_01_the_central_body_is_long_and_slim_with_no_reactor_at_its_back() -> None:
    """D-332: 5.2 long, closing to a point at the tail; about half as wide as before."""
    nose = hull.STATIONS[0]
    tail = hull.STATIONS[-1]
    assert nose[hull.Z] - tail[hull.Z] == pytest.approx(5.2)
    assert all(v == 0 for v in tail[1:])
    assert max(s[hull.CHINE_HALF_WIDTH] for s in hull.STATIONS) <= 0.35
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
