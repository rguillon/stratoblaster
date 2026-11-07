# Copyright (c) 2026 Renaud Guillon
"""The models of the hidden weapons (BOSS-40, D-229).

Spec: docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-design.md, Part A. Each
kind has its pod; its gun mount rises out of it (BOSS-58, drawn by `boss_gun_models`), a hangar's
doors slide apart.
"""

from typing import Any

import pytest

from game.config.bosses.weapon_kinds import KINDS, weapon_mounts
from game.config.record import record
from game.view.bosses.boss_armour import LAYERS
from game.view.bosses.hidden_weapon_shapes import weapon_drawing, weapon_slides
from game.view.enemies.enemy_mesh import collect_parts
from render.geometry.mesh_triangles import bounds_of, triangles

NEON = [1.0, 0.0, 1.0]


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
def test_every_kind_has_its_pod_and_a_gun_mount_or_doors_that_slide_out(kind: str) -> None:
    look = _look(kind)
    assert len(_tris(weapon_drawing(look, NEON), [0, 0, 0])) > 0
    slides = weapon_slides(look, NEON)
    mounts = weapon_mounts(kind, kind, [0, 0], 10, 5)
    if kind == "hangar":
        assert mounts == []
        assert len(slides) == 2
        for slide in slides:
            assert len(_tris(slide[0], [0, 0, 0])) > 0
            assert slide[2] > 0
    else:
        # Its mount rises out of the pod (BOSS-58): nothing else slides out.
        assert len(mounts) == 1
        assert slides == []


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
