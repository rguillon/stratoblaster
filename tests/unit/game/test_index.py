# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/index.py`: the single entry point of the game's content (ENG-144)."""

from core.content.game_definition import GameDefinition
from game.config.game import GAME_CONFIG
from game.config.menu_texts import MENU_TEXTS
from game.config.player_ships import PLAYER_SHIPS
from game.config.player_weapons import PLAYER_WEAPONS
from game.config.readability import READABILITY
from game.config.ship_look import PLAYER_SHIP_SCALE
from game.index import GAME, GameBindings
from game.sim.boss_kinds import BOSS_KINDS
from game.sim.enemy_kinds import ENEMY_KINDS
from game.sim.levels import GAME_LEVELS, LEVELS
from game.view.audio.game_audio import GAME_AUDIO
from game.view.bombs.bomb_renderer import create_bomb_renderer
from game.view.bonuses.bonus_renderer import create_bonus_renderer
from game.view.enemies.enemy_bindings import ENEMY_BINDINGS
from game.view.player_ship_models import PLAYER_SHIP_MODELS
from game.view.scenery_bindings import SCENERY_BINDINGS
from game.view.shots.player_shot_renderers import PLAYER_SHOT_RENDERERS
from game.view.title_backdrop import build_title_backdrop


def test_eng_144_the_game_is_one_definition_of_its_config_and_content() -> None:
    assert isinstance(GAME, GameDefinition)
    assert (GAME.id, GAME.title, GAME.screen) == (
        GAME_CONFIG.id,
        GAME_CONFIG.title,
        GAME_CONFIG.screen,
    )
    assert GAME.levels is LEVELS
    assert GAME.game_levels is GAME_LEVELS
    assert GAME.enemy_kinds is ENEMY_KINDS
    assert GAME.boss_kinds is BOSS_KINDS
    assert GAME.texts is MENU_TEXTS
    assert len(GAME.player_weapons) == len(PLAYER_WEAPONS)
    assert [ship.id for ship in GAME.player_ships.ships] == [s.id for s in PLAYER_SHIPS.ships]
    assert GAME.player_ships.base_speed_px_per_sec == PLAYER_SHIPS.baseSpeedPxPerSec


def test_eng_144_the_view_binds_the_models_sounds_and_renderers_of_the_content() -> None:
    """GFX-READ-07 and GFX-READ-14: every ship is trimmed and every shot toned, none left out."""
    view = GAME.view
    assert isinstance(view, GameBindings)
    assert set(view.player_ship_models) == set(PLAYER_SHIP_MODELS)
    assert view.player_ship_scale == PLAYER_SHIP_SCALE
    assert set(view.player_shot_renderers) == set(PLAYER_SHOT_RENDERERS)
    assert view.menu_backdrop is build_title_backdrop
    assert view.scenery is SCENERY_BINDINGS
    assert view.enemies is ENEMY_BINDINGS
    assert view.bonuses is create_bonus_renderer
    assert view.bombs is create_bomb_renderer
    assert view.audio is GAME_AUDIO
    assert view.outline is READABILITY.outline
