# Copyright (c) 2026 Renaud Guillon
"""Unit tests of the tier 2 enemy models (Harrier, Sweeper, Hatchery)."""

from typing import Any

import pytest
from helpers.view_probes import drawings_of, drawn, probe_builder

from game.config.enemy_harrier import HARRIER_CONFIG
from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.config.enemy_look import ENEMY_LOOK
from game.view.enemies import tier2_harrier_model, tier2_hatchery_model, tier2_sweeper_model
from game.view.enemies.enemy_mesh import UNSEEN_BELOW
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.weapon_ports import port_radius
from render.geometry.facing import seen_from_above

# Triangles of one reactor (`ENEMY_LOOK.reactor`: about 40).
REACTOR_TRIANGLES = 40

MODELS = [
    ("harrier", tier2_harrier_model.build_harrier),
    ("sweeper", tier2_sweeper_model.build_sweeper),
    ("hatchery", tier2_hatchery_model.build_hatchery),
]

HATCH = tier2_hatchery_model


def _body(monkeypatch: Any, builder: Any) -> tuple[Any, Any]:
    capture = probe_builder(monkeypatch, builder)
    return capture, drawings_of(capture)["body"]


def _triangles(body: Any) -> int:
    """Count the triangles the game draws of a body: its faces pointing down are dropped."""
    parts = body["parts"]
    total = len(body["reactors"]) * REACTOR_TRIANGLES
    for builder in (parts.hull, parts.flesh, parts.vein, parts.neon, parts.charge):
        total += len(seen_from_above(builder.geometry, UNSEEN_BELOW).indices) // 3
    return total


def _xyz(positions: list[float]) -> list[tuple[float, float, float]]:
    return [(positions[i], positions[i + 1], positions[i + 2]) for i in range(0, len(positions), 3)]


def _points(parts: Any) -> list[tuple[float, float, float]]:
    out: list[tuple[float, float, float]] = []
    for name in ("hull", "flesh", "neon", "vein", "charge"):
        builder = getattr(parts, name, None)
        if builder is not None:
            out.extend(_xyz(builder.geometry.positions))
    return out


@pytest.mark.parametrize(("kind", "builder"), MODELS)
def test_enm_tier2_the_kind_is_built_under_its_own_key_in_its_tier_neon(
    monkeypatch: Any, kind: str, builder: Any
) -> None:
    """ENM-HARRIER-04, ENM-SWEEPER-04, ENM-HATCHERY-04: tier 2's lime neon, under the kind's key."""
    capture, body = _body(monkeypatch, builder)
    assert capture.name == kind
    assert capture.neon == ENEMY_LOOK.neon[kind]
    assert ENEMY_MODELS[kind] is builder
    assert len(body["parts"].neon.geometry.positions) > 0
    assert len(body["parts"].hull.geometry.positions) > 0
    assert len(body["parts"].flesh.geometry.positions) > 0


@pytest.mark.parametrize(("kind", "builder"), MODELS)
def test_enm_tier2_the_model_stays_in_the_tier_2_triangle_budget(
    monkeypatch: Any, kind: str, builder: Any
) -> None:
    """ENM-HARRIER-10, ENM-SWEEPER-10, ENM-HATCHERY-10: the triangle budget of tier 2.

    Counted on what the game draws: the faces pointing down are dropped when the mesh is built.
    """
    _capture, body = _body(monkeypatch, builder)
    assert _triangles(body) <= ENEMY_LOOK.budget.tier2, kind


def test_enm_harrier_01_the_harrier_is_a_bulky_gunship_with_two_reactors(
    monkeypatch: Any,
) -> None:
    """Also ENM-HARRIER-04: two reactors side by side at the tail, lime neon."""
    _capture, body = _body(monkeypatch, tier2_harrier_model.build_harrier)
    reactors = body["reactors"]
    assert len(reactors) == 2
    xs = sorted(r.at[0] for r in reactors)
    assert xs[0] == -xs[1] != 0
    # At the tail, behind the hull.
    tail = min(z for _x, _y, z in _xyz(body["parts"].flesh.geometry.positions))
    assert all(r.at[2] <= tail for r in reactors)
    # Bulky: the shoulder pods' stub wings reach well out past the flesh hull, on both sides.
    hull = _xyz(body["parts"].hull.geometry.positions)
    flesh = _xyz(body["parts"].flesh.geometry.positions)
    assert max(x for x, _y, _z in hull) >= 2 * max(x for x, _y, _z in flesh)
    assert min(x for x, _y, _z in hull) == -max(x for x, _y, _z in hull)
    # The angry eyes and the wing lights are lime neon, the veins lit.
    assert len(body["parts"].neon.geometry.positions) > 0
    assert len(body["parts"].vein.geometry.positions) > 0


def test_enm_harrier_02_the_harrier_has_two_hollow_launchers_lit_along_their_sides(
    monkeypatch: Any,
) -> None:
    """Also ENM-HARRIER-03 (the Rocketeer's, WPN-07): lit along its sides, no glow at its mouth."""
    _capture, body = _body(monkeypatch, tier2_harrier_model.build_harrier)
    muzzles = body["muzzles"]
    assert [kind for _at, kind in muzzles] == ["missile", "missile"]
    # The model's muzzles are the config's: config `[x, y, height]` is model `[-x, height, -y]`.
    drawn_at = sorted(tuple(at) for at, _kind in muzzles)
    wanted = sorted((-m[0], m[2], -m[1]) for m in HARRIER_CONFIG.muzzles)
    assert drawn_at == wanted
    # Each launcher holds a rocket (WPN-07's launchers 0 and 1), the first on the model's +X.
    rockets = {s.index: s.pivot[0] for s in body["slides"] if s.kind == "rocket"}
    assert sorted(rockets) == [0, 1]
    assert rockets[0] > 0 > rockets[1]
    # Nothing glows at the mouths: no charge light. A neon line along each side of each tube.
    assert body["parts"].charge.geometry.positions == []
    tube = port_radius(HARRIER_CONFIG.missile.radius)
    neon = _xyz(body["parts"].neon.geometry.positions)
    for at, _kind in muzzles:
        for side in [-1, 1]:
            x = at[0] + side * tube
            line = [z for nx, _y, z in neon if abs(nx - x) <= 0.15 + 1e-9]
            assert line
            assert max(line) - min(line) >= tier2_harrier_model.HARRIER_LAUNCHER - 0.5


def test_enm_sweeper_02_the_sweeper_has_one_laser_emitter_with_a_charge_light(
    monkeypatch: Any,
) -> None:
    """Also ENM-SWEEPER-01 (a disc and its barrel) and ENM-SWEEPER-03 (the charge light)."""
    _capture, body = _body(monkeypatch, tier2_sweeper_model.build_sweeper)
    assert [kind for _at, kind in body["muzzles"]] == ["laser"]
    assert len(body["parts"].charge.geometry.positions) > 0


def test_enm_sweeper_04_the_sweeper_has_three_reactors(monkeypatch: Any) -> None:
    _capture, body = _body(monkeypatch, tier2_sweeper_model.build_sweeper)
    assert len(body["reactors"]) == 3


def test_enm_hatchery_02_each_bay_has_two_sliding_doors_a_wasp_lift_and_charge_strips(
    monkeypatch: Any,
) -> None:
    """Also ENM-HATCHERY-03: the bays' edges are the charge light."""
    _capture, body = _body(monkeypatch, HATCH.build_hatchery)
    bays = [-entry[1] for entry in HATCHERY_CONFIG.bays]
    n = len(bays)
    tracks = [s for s in body["slides"] if s.kind == "track"]
    for k, c in enumerate(bays):
        doors = [s for s in tracks if s.index == k]
        lifts = [s for s in tracks if s.index == n + k]
        # Two half doors over the bay, sliding apart (one each way along X).
        assert len(doors) == 2
        assert sorted(d.back[0] for d in doors) == [-1, 1]
        assert all(d.pivot[2] == c for d in doors)
        # One Wasp on its lift at the bottom of the well, rising straight up to the Wasps' plane.
        assert len(lifts) == 1
        lift = lifts[0]
        assert lift.pivot == [0, HATCH.LIFT_LOW, c]
        assert lift.down == 1
        assert lift.pivot[1] + lift.distance == 0
        assert len(lift.parts.hull.geometry.positions) > 0
    assert len(tracks) == 3 * n
    # Charge strips along both sides of each bay, on the deck.
    charge = _xyz(body["parts"].charge.geometry.positions)
    for c in bays:
        for s in [-1, 1]:
            strip = [p for p in charge if p[0] * s > HATCH.BAY and abs(p[2] - c) <= HATCH.BAY]
            assert strip
            assert all(abs(y - HATCH.DECK_TOP) <= 0.1 for _x, y, _z in strip)


def test_enm_hatchery_04_the_hatchery_has_two_reactors(monkeypatch: Any) -> None:
    _capture, body = _body(monkeypatch, HATCH.build_hatchery)
    assert len(body["reactors"]) == 2


def test_enm_hatchery_01_the_flight_deck_lies_under_the_wasps_plane(monkeypatch: Any) -> None:
    """The deck, its hulls, bays, doors and docked Wasps are all below Y = 0, where Wasps fly.

    Only the turrets' domes and barrels rise above it.
    """
    _capture, body = _body(monkeypatch, HATCH.build_hatchery)
    below = _points(body["parts"])
    for s in body["slides"]:
        if s.kind == "track":
            below.extend(_points(s.parts))
    assert max(y for _x, y, _z in below) <= HATCH.DECK_TOP + 0.1
    # The deck spans its whole width, between the side hulls.
    hull = _xyz(body["parts"].hull.geometry.positions)
    assert max(x for x, _y, _z in hull) >= HATCH.DECK_HALF
    assert min(x for x, _y, _z in hull) <= -HATCH.DECK_HALF
    # The turrets' domes stand above the deck.
    domes = [s for s in body["slides"] if s.kind == "barrel"]
    assert max(y for s in domes for _x, y, _z in _points(s.parts)) > 0


def test_enm_hatchery_01_two_gun_turrets_fire_from_the_config_barrel_tips(
    monkeypatch: Any,
) -> None:
    """A turret on each hull: its dome and barrel swivel together, its gun at the config's tip."""
    _capture, body = _body(monkeypatch, HATCH.build_hatchery)
    guns = HATCHERY_CONFIG.turrets
    assert [kind for _at, kind in body["muzzles"]] == ["gun"] * len(guns.pivots)
    wanted = sorted((-p[0], guns.height, -p[1] + guns.barrel) for p in guns.pivots)
    assert sorted(tuple(at) for at, _kind in body["muzzles"]) == wanted
    for k in range(len(guns.pivots)):
        swivels = [s for s in body["slides"] if s.kind == "barrel" and s.turret == k]
        # The dome and the barrel, both turning about the turret's pivot.
        assert len(swivels) == 2
        centre = [-guns.pivots[k][0], 0, -guns.pivots[k][1]]
        assert all(s.swivel and s.centre == centre for s in swivels)


def _overlap(a: list[list[float]], b: list[list[float]]) -> float:
    """Return the area two axis-aligned rectangles (`[x, z]` outlines) share."""
    ax = [q[0] for q in a]
    az = [q[1] for q in a]
    bx = [q[0] for q in b]
    bz = [q[1] for q in b]
    dx = min(max(ax), max(bx)) - max(min(ax), min(bx))
    dz = min(max(az), max(bz)) - max(min(az), min(bz))
    return max(dx, 0) * max(dz, 0)


def _area(r: list[list[float]]) -> float:
    xs = [q[0] for q in r]
    zs = [q[1] for q in r]
    return (max(xs) - min(xs)) * (max(zs) - min(zs))


@pytest.mark.parametrize("bays", [[-20, 0, 20], [0], [20, -20]])
def test_enm_hatchery_01_the_deck_pieces_leave_the_bays_open_and_cover_the_rest(
    bays: list[float],
) -> None:
    pieces = HATCH.deck_pieces(bays)
    holes = [HATCH.rect(-HATCH.BAY, HATCH.BAY, c - HATCH.BAY, c + HATCH.BAY) for c in bays]
    # No piece covers a bay, and no two pieces overlap.
    for piece in pieces:
        for hole in holes:
            assert _overlap(piece, hole) == 0
    for i in range(len(pieces)):
        for j in range(i + 1, len(pieces)):
            assert _overlap(pieces[i], pieces[j]) == 0
    # Pieces and bays together are the whole deck.
    deck = 2 * HATCH.DECK_HALF * 2 * HATCH.DECK_LENGTH
    assert sum(_area(p) for p in pieces) + sum(_area(h) for h in holes) == pytest.approx(deck)


def test_enm_hatchery_01_bays_touching_the_deck_ends_leave_no_empty_piece() -> None:
    end = HATCH.DECK_LENGTH - HATCH.BAY
    pieces = HATCH.deck_pieces([-end, end])
    assert all(_area(p) > 0 for p in pieces)
    # The two side strips and the strip between the bays.
    assert len(pieces) == 3


def test_enm_hatchery_01_a_turret_scales_and_lifts_its_profiles_by_its_size() -> None:
    guns = HATCHERY_CONFIG.turrets
    scale = 1.5
    lift = 3
    plain = drawn(lambda p: HATCH.turret(p, 0, guns))
    big = drawn(lambda p: HATCH.turret(p, 0, guns, [scale, lift]))
    assert HATCH.scaled([[2, 1], [0, -1]], [scale, lift]) == [[3, 4.5], [0, 1.5]]

    def ys(body: Any, part: str = "hull") -> list[float]:
        return [y for _x, y, _z in _xyz(getattr(body, part).geometry.positions)]

    # The pedestal: its foot and top scaled, then lifted.
    base = HATCH.TURRET_BASE
    assert min(ys(plain["parts"])) == pytest.approx(base[0][1])
    assert min(ys(big["parts"])) == pytest.approx(base[0][1] * scale + lift)
    # The dome's top too.
    domes = [s for s in big["slides"] if s.kind == "barrel" and s.distance == 0]
    top = HATCH.TURRET_DOME[len(HATCH.TURRET_DOME) - 1][1]
    assert max(ys(domes[0].parts)) == pytest.approx(top * scale + lift)
    # The barrel is `scale` times as long, and recoils `scale` times as far.
    small = next(s for s in plain["slides"] if s.distance > 0)
    large = next(s for s in big["slides"] if s.distance > 0)
    assert large.distance == pytest.approx(small.distance * scale)
    zs = [z for _x, _y, z in _xyz(large.parts.hull.geometry.positions)]
    assert max(zs) - min(zs) == pytest.approx(HATCH.TURRET_BARREL[0] * scale)


def test_enm_hatchery_01_a_turret_without_pedestal_draws_no_pedestal() -> None:
    guns = HATCHERY_CONFIG.turrets
    bare = drawn(lambda p: HATCH.turret(p, 0, guns, None, False))
    full = drawn(lambda p: HATCH.turret(p, 0, guns))
    # The pedestal is the only thing a turret draws on the body: the rest turns with it.
    assert bare["parts"].hull.geometry.positions == []
    assert len(full["parts"].hull.geometry.positions) > 0
    # Its dome, barrel and gun are still there.
    assert len(bare["slides"]) == len(full["slides"]) == 2
    assert bare["muzzles"] == full["muzzles"]
