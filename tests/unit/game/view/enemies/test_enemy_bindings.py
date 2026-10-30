"""Unit tests of `src/game/view/enemies/enemy_bindings.py`."""

from game.config.enemy_look import ENEMY_LOOK
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.enemies import enemy_bindings
from game.view.enemies.enemy_bindings import ENEMY_BINDINGS, merged_models
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.living_motion import set_living_motion


def test_p05_the_bindings_draw_every_enemy_and_every_boss_by_its_key():
    models = ENEMY_BINDINGS.models
    for key in ENEMY_MODELS:
        assert key in models
    for key in BOSS_MODELS:
        assert key in models


def test_p16_r10_the_idle_motion_switch_is_the_living_motion_switch():
    assert ENEMY_BINDINGS.setIdleMotion is set_living_motion


def test_the_glow_and_the_shot_and_blast_renderers_come_from_their_modules():
    assert ENEMY_BINDINGS.glow is ENEMY_LOOK.glow
    assert callable(ENEMY_BINDINGS.shots)
    assert callable(ENEMY_BINDINGS.blasts)


def test_a_boss_model_wins_over_an_enemy_with_the_same_key(monkeypatch):
    def enemy_builder(scene):
        return "enemy"

    def boss_builder(scene):
        return "boss"

    monkeypatch.setattr(
        enemy_bindings, "ENEMY_MODELS", {"shared": enemy_builder, "only": enemy_builder}
    )
    monkeypatch.setattr(enemy_bindings, "BOSS_MODELS", {"shared": boss_builder})
    models = merged_models()
    assert models["shared"] is boss_builder
    assert models["only"] is enemy_builder
