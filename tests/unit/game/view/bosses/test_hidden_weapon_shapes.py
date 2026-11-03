# Copyright (c) 2026 Renaud Guillon
"""The models of the hidden weapons (BOSS-40, D-229).

Spec: docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-design.md, Part A. Each
kind has its pod, and its turret or what slides out.
"""

from typing import Any

import pytest

from game.config.bosses.weapon_kinds import KINDS, WEAPON_SHAPE, weapon_guns
from game.config.record import record
from game.view.bosses.boss_armour import LAYERS
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.hidden_weapon_shapes import (
    turret_slide,
    weapon_drawing,
    weapon_slides,
    weapon_turret_drawing,
)
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.mesh_triangles import bounds_of, triangles

NEON = [1.0, 0.0, 1.0]
TURRETS = ["gatling", "cannon", "sweeper"]


def _look(kind: str) -> Any:
    return record({"kind": kind, "radius": 10, "height": 5})


def _tris(draw: Any, at: list[float]) -> list[Any]:
    def build(p: Any) -> None:
        draw(p, at)

    parts = collect_parts(build)["parts"]
    result: list[Any] = []
    for layer in LAYERS:
        result.extend(triangles(getattr(parts, layer).geometry))
    return result


@pytest.mark.parametrize("kind", [k for k in KINDS if k != "beam"])
def test_every_kind_has_its_pod_and_a_turret_or_something_that_slides_out(kind: str) -> None:
    look = _look(kind)
    assert len(_tris(weapon_drawing(look, NEON), [0, 0, 0])) > 0
    turret = weapon_turret_drawing(look, NEON)
    slides = weapon_slides(look, NEON)
    if kind in TURRETS:
        assert turret is not None
        assert slides == []
        assert len(_tris(turret, [0, 0, 0])) > 0
        assert turret_slide(look) > 0
    else:
        assert turret is None
        assert len(slides) >= 1
        for slide in slides:
            assert len(_tris(slide[0], [0, 0, 0])) > 0
            assert slide[2] > 0


def test_the_hangar_s_two_doors_slide_apart() -> None:
    slides = weapon_slides(_look("hangar"), NEON)
    assert [s[1] for s in slides] == [[1, 0, 0], [-1, 0, 0]]


def test_the_kinds_stand_on_different_pods() -> None:
    def footprint(kind: str) -> list[float]:
        b = bounds_of(_tris(weapon_drawing(_look(kind), NEON), [0, 0, 0]))
        return [round(b[3] - b[0], 1), round(b[5] - b[2], 1)]

    # The battery's deck is long across, the hangar's box wide, the mortar's base round.
    battery = footprint("battery")
    assert battery[0] > battery[1] * 1.5
    assert footprint("hangar") != footprint("gatling")
    assert footprint("mortar") != footprint("gatling")
    assert footprint("cannon") != footprint("gatling")


def test_the_battery_barrels_end_at_its_muzzles() -> None:
    look = _look("battery")
    at = boss_point(0, 0)
    [slide] = weapon_slides(look, NEON)
    b = bounds_of(_tris(slide[0], at))
    muzzle = weapon_guns("battery", [0, 0], 10, 5).gun[0]
    # Model +Z is down the screen (config -Y).
    assert b[5] == pytest.approx(-muzzle[1], abs=0.6)
    assert b[3] - b[0] >= 4 * 10 * WEAPON_SHAPE.barrelGap


def test_the_mortar_tube_reaches_its_mouth() -> None:
    look = _look("mortar")
    [slide] = weapon_slides(look, NEON)
    b = bounds_of(_tris(slide[0], boss_point(0, 0)))
    [mouth] = weapon_guns("mortar", [0, 0], 10, 5).gun
    assert b[4] >= mouth[2] - 1
    assert b[5] >= -mouth[1] - 1
