# Copyright (c) 2026 Renaud Guillon
"""D-314: each tier's shots hit as hard as its tier says, harder tier after tier."""

import pytest

from core.systems.enemy_shots import shot_damage
from game.config.enemies import ENEMY_CONFIG
from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.enemy_broodmother import BROODMOTHER_CONFIG
from game.config.enemy_harrier import HARRIER_CONFIG
from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.config.enemy_prism import PRISM_CONFIG
from game.config.enemy_sweeper import SWEEPER_CONFIG
from game.config.enemy_tiers import TIER_DAMAGE
from game.sim.enemies.enemy_helpers import missile_spec
from game.sim.enemies.lancer import _laser_spec
from game.sim.enemies.mortar import mortar_missile


def test_d_314_each_tier_hits_harder_than_the_one_before() -> None:
    for shot in ("bullet", "missile", "laser"):
        damages = [TIER_DAMAGE[str(tier)][shot] for tier in range(1, 5)]
        assert damages == sorted(damages), shot
        assert damages[0] < damages[-1], shot
    # Tier 1 hits as the hull's rules always had it (`hull.py`).
    assert dict(TIER_DAMAGE["1"]) == {"bullet": 10, "missile": 20, "laser": 25}


@pytest.mark.parametrize(
    ("tier", "shot", "record"),
    [
        (1, "bullet", ENEMY_CONFIG.scout.bullet),
        (1, "missile", ENEMY_CONFIG.rocketeer.missile),
        (1, "laser", ENEMY_CONFIG.lancer.laser),
        (2, "bullet", ENEMY_CONFIG.strafer.bullet),
        (2, "bullet", VETERAN_CONFIG.wasp.bullet),
        (2, "missile", HARRIER_CONFIG.missile),
        (2, "laser", SWEEPER_CONFIG.laser),
        (2, "bullet", HATCHERY_CONFIG.turrets.bullet),
        (3, "bullet", ENEMY_CONFIG.spinner.bullet),
        (3, "bullet", VETERAN_CONFIG.phantom.bullet),
        (3, "missile", VETERAN_CONFIG.mortar.missile),
        (3, "bullet", VETERAN_CONFIG.mortar.missile.burst.bullet),
        (3, "laser", PRISM_CONFIG.laser),
        (3, "bullet", BROODMOTHER_CONFIG.turrets.bullet),
        (4, "bullet", ELITE_CONFIG.hydra.bullet),
        (4, "bullet", ELITE_CONFIG.juggernaut.bullet),
        (4, "missile", ELITE_CONFIG.juggernaut.missile),
        (4, "laser", ELITE_CONFIG.scissor.laser),
        (4, "bullet", ELITE_CONFIG.hive.ringBullet),
    ],
)
def test_d_314_every_shot_of_a_kind_carries_its_tier_s_damage(
    tier: int, shot: str, record: object
) -> None:
    assert shot_damage(record) == TIER_DAMAGE[str(tier)][shot]


def test_d_314_the_engine_s_specs_keep_the_damage() -> None:
    assert missile_spec(HARRIER_CONFIG.missile).damage == TIER_DAMAGE["2"].missile
    mortar = mortar_missile()
    assert mortar.damage == TIER_DAMAGE["3"].missile
    assert mortar.burst is not None
    assert mortar.burst.bullet.damage == TIER_DAMAGE["3"].bullet
    assert _laser_spec().damage == TIER_DAMAGE["1"].laser
