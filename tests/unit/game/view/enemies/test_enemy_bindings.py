# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/enemies/enemy_bindings.py`."""

from types import SimpleNamespace
from typing import Any

from helpers.enemy_steps import run
from helpers.fakes import FakeContext

from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY
from game.sim.bosses.boss_launches import launch_fire
from game.sim.enemies.carrier import Carrier
from game.sim.enemies.hive import Hive
from game.view.bosses.boss_models import BOSS_MODELS
from game.view.enemies import enemy_bindings
from game.view.enemies.enemy_bindings import ENEMY_BINDINGS, merged_models
from game.view.enemies.enemy_models import ENEMY_MODELS
from game.view.enemies.living_motion import set_living_motion


def test_p05_the_bindings_draw_every_enemy_and_every_boss_by_its_key() -> None:
    models = ENEMY_BINDINGS.models
    for key in ENEMY_MODELS:
        assert key in models
    for key in BOSS_MODELS:
        assert key in models


def test_the_idle_motion_switch_is_the_living_motion_switch() -> None:
    assert ENEMY_BINDINGS.setIdleMotion is set_living_motion


def test_the_glow_and_the_shot_and_blast_renderers_come_from_their_modules() -> None:
    assert ENEMY_BINDINGS.glow is ENEMY_LOOK.glow
    assert callable(ENEMY_BINDINGS.shots)
    assert callable(ENEMY_BINDINGS.blasts)


def test_a_boss_model_wins_over_an_enemy_with_the_same_key(monkeypatch: Any) -> None:
    def enemy_builder(_scene: Any) -> Any:
        return SimpleNamespace(root="enemy")

    def boss_builder(_scene: Any) -> Any:
        return SimpleNamespace(root="boss")

    trimmed_roots = []
    monkeypatch.setattr(
        enemy_bindings, "add_edge_trim", lambda root, _options: trimmed_roots.append(root)
    )
    monkeypatch.setattr(
        enemy_bindings, "ENEMY_MODELS", {"shared": enemy_builder, "only": enemy_builder}
    )
    monkeypatch.setattr(enemy_bindings, "BOSS_MODELS", {"shared": boss_builder})
    models = merged_models()
    assert models["shared"]("scene").root == "boss"
    assert models["only"]("scene").root == "enemy"
    # Each model gets its glowing edge trim once built whole (GFX-TRIM-01).
    assert trimmed_roots == ["boss", "enemy"]


def test_gfx_trim_06_the_trim_options_are_the_enemy_trim_look(monkeypatch: Any) -> None:
    seen = []
    monkeypatch.setattr(
        enemy_bindings, "add_edge_trim", lambda _root, options: seen.append(options)
    )
    enemy_bindings.trimmed(lambda _scene: SimpleNamespace(root="r"))("scene")
    look = READABILITY.enemyTrim
    assert (seen[0].width, seen[0].offset) == (look.width, look.offset)


def _models_spawned(enemy: Any) -> Any:
    ctx = FakeContext()
    run(enemy, ctx, 10.0)
    if callable(getattr(enemy, "on_destroyed", None)):
        enemy.on_destroyed(ctx)
    return {e.model for e in ctx.spawned}


def test_perf_21_the_child_models_cover_every_enemy_another_one_sends_out() -> None:
    # The children are built with the level's own models, so none is built in play.
    children = set(ENEMY_BINDINGS.child_models)
    assert _models_spawned(Carrier(200, 500)) <= children
    assert _models_spawned(Hive(200, 500)) <= children
    for kind in ["gnats", "hornets"]:
        assert {e.model for e in launch_fire(kind, 2, 1)(200, 500)} <= children
    for key in children:
        assert key in ENEMY_BINDINGS.models
    assert {"gnat", "wasp", "hornet", "splitter-pod"} <= children
