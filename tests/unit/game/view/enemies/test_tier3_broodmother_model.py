# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/tier3_broodmother_model.py`."""

import math
from typing import Any

import pytest
from helpers.view_probes import drawings_of, probe_builder

from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import tier3_broodmother_model as module
from game.view.enemies.enemy_mesh import UNSEEN_BELOW
from render.geometry.facing import seen_from_above

# About the triangles of one reactor's nozzle, core and flame (`ENEMY_LOOK.reactor`).
REACTOR_TRIANGLES = 40


def _body(monkeypatch: Any) -> Any:
    return drawings_of(probe_builder(monkeypatch, module.build_broodmother))["body"]


def _xyz(positions: list[float]) -> list[tuple[float, float, float]]:
    return [(positions[i], positions[i + 1], positions[i + 2]) for i in range(0, len(positions), 3)]


def _signed_area(outline: list[list[float]]) -> float:
    n = len(outline)
    return (
        sum(
            outline[i][0] * outline[(i + 1) % n][1] - outline[(i + 1) % n][0] * outline[i][1]
            for i in range(n)
        )
        / 2
    )


def _crosses(a: list[float], b: list[float], c: list[float], d: list[float]) -> bool:
    """Whether the segments `a b` and `c d` cross (touching ends do not count)."""

    def side(p: list[float], q: list[float], r: list[float]) -> float:
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    return side(a, b, c) * side(a, b, d) < 0 and side(c, d, a) * side(c, d, b) < 0


def _simple(outline: list[list[float]]) -> bool:
    n = len(outline)
    for i in range(n):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            a, b = outline[i], outline[(i + 1) % n]
            c, d = outline[j], outline[(j + 1) % n]
            if _crosses(a, b, c, d):
                return False
    return True


def _inside(point: list[float], outline: list[list[float]]) -> bool:
    """Whether `point` (`[x, z]`) lies inside `outline` (even-odd rule)."""
    x, z = point
    inside = False
    n = len(outline)
    for i in range(n):
        a, b = outline[i], outline[(i + 1) % n]
        if (a[1] > z) != (b[1] > z):
            cut = a[0] + (z - a[1]) / (b[1] - a[1]) * (b[0] - a[0])
            if x < cut:
                inside = not inside
    return inside


def test_enm_broodmother_01_it_is_built_as_the_broodmother_kind_in_its_neon(
    monkeypatch: Any,
) -> None:
    capture = probe_builder(monkeypatch, module.build_broodmother)
    assert capture.name == "broodmother"
    assert capture.neon == ENEMY_LOOK.neon.broodmother


def test_enm_broodmother_02_a_metal_deck_and_hangar_with_a_flesh_radar_dome(
    monkeypatch: Any,
) -> None:
    parts = _body(monkeypatch)["parts"]
    hull = _xyz(parts.hull.geometry.positions)
    # The metal deck spans the carrier, bow to stern, and the hangar's roof rises over its stern.
    zs = [z for _x, _y, z in hull]
    assert max(zs) == pytest.approx(max(q[1] for q in module.DECK))
    assert min(zs) <= min(q[1] for q in module.DECK)
    roof = [y for _x, y, z in hull if z < module.HANGAR_FRONT]
    assert max(roof) == pytest.approx(module.ROOF_HEIGHTS[2])
    # Its only flesh is the radar's sensor dome on the right shoulder (the model's -X).
    flesh = _xyz(parts.flesh.geometry.positions)
    assert flesh
    rx, rz = module.RADAR_AT
    for x, y, z in flesh:
        assert math.hypot(x - rx, z - rz) <= module.RADAR_DOME + 1e-6
        assert y >= module.SHOULDER_TOP
    # Lights: the deck's edge, the runway, the bridge.
    assert len(parts.neon.geometry.positions) > 0


def test_enm_broodmother_03_the_hangar_mouth_lintel_is_the_charge_light(
    monkeypatch: Any,
) -> None:
    charge = _xyz(_body(monkeypatch)["parts"].charge.geometry.positions)
    assert charge
    # Right across the hangar's mouth, under the roof's front edge.
    xs = [x for x, _y, _z in charge]
    assert min(xs) == pytest.approx(-module.HANGAR_INNER)
    assert max(xs) == pytest.approx(module.HANGAR_INNER)
    assert all(abs(z - module.HANGAR_FRONT) <= 0.5 for _x, _y, z in charge)
    assert all(module.DECK_TOP < y <= module.ROOF_HEIGHTS[0] for _x, y, _z in charge)


def test_enm_broodmother_04_the_launch_muzzle_is_where_the_phantom_rolls_out_to(
    monkeypatch: Any,
) -> None:
    body = _body(monkeypatch)
    muzzles = body["muzzles"]
    assert [kind for _at, kind in muzzles] == ["launch", "gun"]
    at = muzzles[0][0]
    # The config's port: model X is the screen's left, model Z down the screen's Y; on the
    # Phantom's plane, just out of the hangar's mouth.
    port = BROODMOTHER_CONFIG.port
    assert at == [-port[0], 0, -port[1]]
    assert at[2] > module.HANGAR_FRONT
    # The docked Phantom waits in the hangar and rolls out (track 0) to there.
    tracks = [s for s in body["slides"] if s.kind == "track"]
    assert len(tracks) == 1
    phantom = tracks[0]
    assert phantom.index == 0
    assert phantom.pivot[2] < module.HANGAR_FRONT
    assert phantom.pivot[2] + phantom.back[1] * phantom.distance == at[2]
    assert len(phantom.parts.flesh.geometry.positions) > 0


def test_enm_broodmother_04_its_gun_turret_stands_on_the_left_shoulder(monkeypatch: Any) -> None:
    body = _body(monkeypatch)
    guns = BROODMOTHER_CONFIG.turrets
    pivot = guns.pivots[0]
    at = body["muzzles"][1][0]
    assert at == [-pivot[0], guns.height, -pivot[1] + guns.barrel]
    # The model's +X is the screen's left.
    assert at[0] > 0
    swivels = [s for s in body["slides"] if s.kind == "barrel"]
    assert len(swivels) == 2
    assert all(s.swivel and s.turret == 0 for s in swivels)
    # Its dome stands on the shoulder, with no pedestal.
    dome = next(s for s in swivels if s.distance == 0)
    ys = [y for _x, y, _z in _xyz(dome.parts.hull.geometry.positions)]
    assert min(ys) >= module.SHOULDER_TOP


def test_enm_broodmother_05_it_has_six_reactors_within_the_tier_3_triangle_budget(
    monkeypatch: Any,
) -> None:
    body = _body(monkeypatch)
    reactors = body["reactors"]
    # Four along the stern, one in each bow wing's nacelle.
    assert len(reactors) == 6
    stern = [r for r in reactors if r.at[2] == module.REACTOR_Z]
    assert sorted(r.at[0] for r in stern) == sorted(q[0] for q in module.REACTORS)
    bow = [r for r in reactors if r.at[2] > 0]
    assert sorted(r.at[0] for r in bow) == [-module.BOW_NACELLE["x"], module.BOW_NACELLE["x"]]
    # Counted on what the game draws: the faces pointing down are dropped when built.
    parts = body["parts"]
    triangles = sum(
        len(seen_from_above(builder.geometry, UNSEEN_BELOW).indices) // 3
        for builder in [parts.hull, parts.flesh, parts.neon, parts.vein, parts.charge]
    )
    triangles += REACTOR_TRIANGLES * len(reactors)
    assert triangles <= ENEMY_LOOK.budget.tier3


def test_enm_broodmother_01_the_deck_outline_is_a_simple_clockwise_outline() -> None:
    deck = module.deck_outline()
    assert deck == module.DECK
    assert _simple(deck)
    # Clockwise seen from above (X right, Z up the page): a negative signed area.
    assert _signed_area(deck) < 0
    # Left and right flanks each carry their sponson, so it is not mirrored.
    assert max(q[0] for q in deck) == pytest.approx(
        module.LEFT_SPONSON[3] + module.LEFT_SPONSON[4], abs=0.5
    )
    assert min(q[0] for q in deck) == pytest.approx(
        -(module.RIGHT_SPONSON[3] + module.RIGHT_SPONSON[4]), abs=0.5
    )


@pytest.mark.parametrize("spec", [module.LEFT_SPONSON, module.RIGHT_SPONSON])
def test_enm_broodmother_01_a_sponson_bulges_out_of_its_flank_between_its_ends(
    spec: list[float],
) -> None:
    side, z0, z1, flank, bulge = spec
    points = module.sponson(spec)
    assert len(points) == module.SPONSON_POINTS + 1
    # Its ends lie on the flank.
    assert points[0] == pytest.approx([side * flank, z0])
    assert points[-1] == pytest.approx([side * flank, z1])
    # Its Zs run steadily from one end to the other, all on its side, out past the flank.
    zs = [q[1] for q in points]
    assert zs == sorted(zs, reverse=z0 > z1)
    outs = [q[0] * side - flank for q in points]
    assert all(-1e-9 <= o <= bulge + 1e-9 for o in outs)
    assert max(outs) > 0.9 * bulge


@pytest.mark.parametrize(
    ("side", "end"), [(1, module.LEFT_SHOULDER_END), (-1, module.RIGHT_SHOULDER_END)]
)
def test_enm_broodmother_01_a_shoulder_runs_from_the_hangar_to_its_end_beside_the_runway(
    side: int, end: float
) -> None:
    outline = module.shoulder_outline(side)
    assert _simple(outline)
    zs = [q[1] for q in outline]
    assert min(zs) == module.SHOULDER_BACK
    assert outline[0] == [side * (module.HANGAR_INNER + module.HANGAR_WALL), module.SHOULDER_BACK]
    assert end <= max(zs) <= end + 1
    # All on its own side, clear of the runway.
    assert all(q[0] * side >= module.RUNWAY_HALF for q in outline)
    # Out along the deck's edge, never past it.
    for x, z in outline:
        assert abs(x) <= module.deck_edge_x(side, z) + 1e-6


def test_enm_broodmother_01_the_deck_edge_x_follows_the_outline() -> None:
    # Along the straight edge from (23, 20) to (21, 40), and the right one from its sponson's end.
    assert module.deck_edge_x(1, 30) == pytest.approx(22)
    assert module.deck_edge_x(-1, 40) == pytest.approx(21)
    # At a sponson's top it is out past the flank.
    assert module.deck_edge_x(1, -14) > module.LEFT_SPONSON[3] + 0.9 * module.LEFT_SPONSON[4]
    # Past the bow, nothing.
    assert module.deck_edge_x(1, 100) == 0


def test_enm_broodmother_01_shoulders_hide_the_edge_lights_under_them() -> None:
    assert module.under_shoulder([23, 0])
    assert module.under_shoulder([-23, 20])
    # The left shoulder ends before the right one, and neither reaches the stern.
    assert not module.under_shoulder([23, 20])
    assert not module.under_shoulder([-23, 30])
    assert not module.under_shoulder([23, module.SHOULDER_BACK - 1])
    assert not module.under_shoulder([-23, module.SHOULDER_BACK - 1])


def test_enm_broodmother_01_the_edge_lights_lie_just_inside_the_deck() -> None:
    deck = module.DECK
    n = len(deck)
    for i in range(n):
        a, b = deck[i], deck[(i + 1) % n]
        light = module.edge_light(a, b)
        assert len(light) == 4
        # Its middle, between its long sides, is inside the deck, within 1.2 of the edge.
        mid = [sum(q[0] for q in light) / 4, sum(q[1] for q in light) / 4]
        assert _inside(mid, deck)
        edge_mid = [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]
        assert math.dist(mid, edge_mid) == pytest.approx(0.9)
