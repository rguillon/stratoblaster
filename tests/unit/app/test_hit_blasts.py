# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/hit_blasts.py`."""
# (phase 6 review: sparks and the blast of a lost life).

from types import SimpleNamespace

from app.hit_blasts import hit_blasts, impact_blasts
from config.game_play import GAME_PLAY_CONFIG
from core.systems.level_run_types import LandedHit
from core.systems.shot_world import ShotImpact


def test_gfx_fx_04_a_hit_that_landed_sparks_where_it_landed() -> None:
    ship = SimpleNamespace(x=100, y=50)
    blasts = hit_blasts([LandedHit("bullet", 30, 40, "hit")], ship)
    assert len(blasts) == 1
    assert (blasts[0].kind, blasts[0].x, blasts[0].y) == ("missile", 30, 40)
    assert blasts[0].radius == GAME_PLAY_CONFIG.damage.hit_spark


def test_game_life_08_a_hit_that_cost_a_life_blows_up_the_ship() -> None:
    ship = SimpleNamespace(x=100, y=50)
    blasts = hit_blasts([LandedHit("bullet", 30, 40, "dead")], ship)
    assert (blasts[0].kind, blasts[0].x, blasts[0].y) == ("enemy", 100, 50)
    assert blasts[0].radius == GAME_PLAY_CONFIG.damage.ship_blast


def test_gfx_fx_01_one_blast_per_landed_hit_and_none_for_no_hits() -> None:
    ship = SimpleNamespace(x=0, y=0)
    assert hit_blasts([], ship) == []
    blasts = hit_blasts([LandedHit("bullet", 1, 2, "hit"), LandedHit("bullet", 3, 4, "dead")], ship)
    assert [blast.kind for blast in blasts] == ["missile", "enemy"]


def test_gfx_fx_03_a_missile_hit_blows_up_a_little_where_it_hit() -> None:
    """D-321: a small layered explosion, the size of the missile's blast."""
    blasts = impact_blasts([ShotImpact("missile", 30, 40, 10, False)])
    assert len(blasts) == 1
    assert (blasts[0].kind, blasts[0].x, blasts[0].y, blasts[0].radius) == ("missile", 30, 40, 10)


def test_gfx_fx_03_direct_hits_make_no_explosion() -> None:
    """Bullets and the laser have no blast radius: they keep their sparks (GFX-FX-02)."""
    assert impact_blasts([ShotImpact("bullet", 30, 40, 0, False)]) == []
    assert impact_blasts([]) == []
