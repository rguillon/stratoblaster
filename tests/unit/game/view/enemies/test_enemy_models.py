"""Unit tests of `src/game/view/enemies/enemy_models.py`."""

from game.view.enemies import carrier_model, enemy_models
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.heavy_beetle_models import build_splitter_pod


def test_p05_every_basic_kind_has_its_model_builder():
    basic = {
        "gnat": "build_gnat",
        "hornet": "build_hornet",
        "scout": "build_scout",
        "strafer": "build_strafer",
        "weaver": "build_weaver",
        "spinner": "build_spinner",
        "lancer": "build_lancer",
        "rocketeer": "build_rocketeer",
        "bulwark": "build_bulwark",
        "splitter": "build_splitter",
        "splitter-pod": "build_splitter_pod",
        "carrier": "build_carrier",
    }
    for key, builder_name in basic.items():
        assert key in ENEMY_MODELS
        assert ENEMY_MODELS[key].__name__ == builder_name


def test_p05_the_splitter_pod_is_its_own_model_not_the_splitter():
    assert ENEMY_MODELS["splitter-pod"] is build_splitter_pod
    assert ENEMY_MODELS["carrier"] is carrier_model.build_carrier


def test_p05_the_veteran_and_elite_models_follow_the_basic_ones():
    veteran_keys = {"wasp", "mortar", "mantis", "phantom", "minelayer"}
    elite_keys = {"hydra", "orbiter", "scissor", "juggernaut", "hive"}
    assert veteran_keys <= set(ENEMY_MODELS)
    assert elite_keys <= set(ENEMY_MODELS)
    assert len(ENEMY_MODELS) == 12 + len(veteran_keys) + len(elite_keys)


def test_every_model_key_is_a_builder_of_a_scene():
    for key, builder in ENEMY_MODELS.items():
        assert callable(builder), key


def test_the_module_keeps_the_veteran_and_elite_tables_apart():
    assert set(enemy_models.VETERAN_MODELS).isdisjoint(enemy_models.ELITE_MODELS)
