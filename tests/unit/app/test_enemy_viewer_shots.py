"""Unit tests of `src/app/enemy_viewer_shots.py`."""
# the shots and explosions of the enemies page, drawn through the renderers the game provides
# (the renderers are fakes here).

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.enemy_viewer_shots import EnemyViewerShots, ShotsToDraw


def make_game() -> tuple[SimpleNamespace, MagicMock, MagicMock]:
    fire_renderer = MagicMock(name="fire-renderer")
    factory = MagicMock(return_value=fire_renderer)
    enemy_renderer = MagicMock(name="enemy-renderer")
    blasts = MagicMock(name="blasts-renderer")
    game = SimpleNamespace(
        player_weapons=[SimpleNamespace(id="guns")],
        view=SimpleNamespace(
            player_shot_renderers={"guns": factory},
            enemies=SimpleNamespace(
                shots=MagicMock(return_value=enemy_renderer),
                blasts=MagicMock(return_value=blasts),
            ),
        ),
    )
    return game, enemy_renderer, blasts


def make_playfield() -> SimpleNamespace:
    scene = MagicMock(name="scene")
    return SimpleNamespace(
        root=SimpleNamespace(getScene=lambda: scene),
        run=lambda build: build(),
    )


def test_p10_r07_the_shot_renderers_are_built_once_on_the_playfield() -> None:
    game, enemy_renderer, blasts = make_game()
    shots = EnemyViewerShots(game, make_playfield(), "laser")
    assert shots._enemy is enemy_renderer
    assert shots._blasts is blasts
    assert list(shots._player) == ["guns"]
    game.view.enemies.shots.assert_called_once()


def test_p10_r07_a_weapon_without_a_shot_renderer_is_an_error() -> None:
    game, _, _ = make_game()
    game.view.player_shot_renderers = {}
    with pytest.raises(ValueError, match="guns"):
        EnemyViewerShots(game, make_playfield())


def test_gd62_each_frame_draws_the_player_shots_the_enemy_shots_and_the_blasts() -> None:
    game, enemy_renderer, blasts = make_game()
    shots = EnemyViewerShots(game, make_playfield())
    player_renderer = shots._player["guns"]
    live = SimpleNamespace(alive=True, weapon=SimpleNamespace(id="guns"))
    dead = SimpleNamespace(alive=False, weapon=SimpleNamespace(id="guns"))
    run_shots = SimpleNamespace(
        projectiles=[live, dead],
        beam=[],
        weapon=SimpleNamespace(id="guns"),
    )
    enemy_shots = SimpleNamespace(
        bullets=[SimpleNamespace(alive=True), SimpleNamespace(alive=False)],
        missiles=[SimpleNamespace(alive=True)],
        lasers=["laser"],
    )
    to_draw = ShotsToDraw(
        SimpleNamespace(shots=enemy_shots),
        run_shots,
        ["blast"],
        [],
        0.5,
    )
    shots.sync(to_draw)
    frame = player_renderer.sync.call_args.args[0]
    assert frame.projectiles == [live]
    assert frame.dt_seconds == 0.5
    enemy_frame = enemy_renderer.sync.call_args.args[0]
    assert len(enemy_frame.bullets) == 1
    assert len(enemy_frame.missiles) == 1
    assert enemy_frame.lasers == ["laser"]
    blasts.sync.assert_called_once_with(["blast"], 0.5)
