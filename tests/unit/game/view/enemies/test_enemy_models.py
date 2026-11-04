# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_models.py`."""

from game.view.enemies import carrier_model, enemy_models
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.heavy_beetle_models import build_splitter_pod


def test_p05_every_basic_kind_has_its_model_builder() -> None:
    basic = {
        "hornet": "build_hornet",
        "scout": "build_scout",
        "strafer": "build_strafer",
        "spinner": "build_spinner",
        "lancer": "build_lancer",
        "rocketeer": "build_rocketeer",
        "splitter": "build_splitter",
        "splitter-pod": "build_splitter_pod",
        "carrier": "build_carrier",
    }
    for key, builder_name in basic.items():
        assert key in ENEMY_MODELS
        assert ENEMY_MODELS[key].__name__ == builder_name


def test_p05_the_splitter_pod_is_its_own_model_not_the_splitter() -> None:
    assert ENEMY_MODELS["splitter-pod"] is build_splitter_pod
    assert ENEMY_MODELS["carrier"] is carrier_model.build_carrier


def test_p05_the_veteran_and_elite_models_follow_the_basic_ones() -> None:
    veteran_keys = {"wasp", "mortar", "phantom"}
    elite_keys = {"hydra", "scissor", "juggernaut", "hive"}
    assert veteran_keys <= set(ENEMY_MODELS)
    assert elite_keys <= set(ENEMY_MODELS)
    # The 20 kinds of the four tiers, and the Splitter's pod.
    assert len(ENEMY_MODELS) == 21


def test_every_model_key_is_a_builder_of_a_scene() -> None:
    for key, builder in ENEMY_MODELS.items():
        assert callable(builder), key


def test_the_module_keeps_the_veteran_and_elite_tables_apart() -> None:
    assert set(enemy_models.VETERAN_MODELS).isdisjoint(enemy_models.ELITE_MODELS)
