# Copyright (c) 2026 Renaud Guillon
"""The single entry point of this game's content (ENG-144).

`main.py` passes `GAME` to `app/`; the engine discovers all content through it.
"""

from core.content.game_definition import GameDefinition, LogicalScreen
from game.config.bombs import BOMB_RULES
from game.config.bonuses import BONUS_RULES
from game.config.boss_fights import BOSS_FIGHT_RULES
from game.config.game import GAME_CONFIG
from game.config.hull import HULL_RULES
from game.config.menu_texts import MENU_TEXTS
from game.config.player_ships import PLAYER_SHIPS
from game.config.player_weapons import PLAYER_WEAPONS
from game.config.readability import READABILITY
from game.config.ship_look import PLAYER_SHIP_SCALE
from game.sim.boss_kinds import BOSS_KINDS
from game.sim.enemy_kinds import ENEMY_KINDS
from game.sim.levels import GAME_LEVELS, LEVELS
from game.sim.player_build import player_roster, player_weapons
from game.sim.rules_build import bomb_rules, bonus_rules, boss_fight_rules, hull_rules
from game.view.audio.game_audio import GAME_AUDIO
from game.view.bombs.bomb_renderer import create_bomb_renderer
from game.view.bonuses.bonus_renderer import create_bonus_renderer
from game.view.enemies.enemy_bindings import ENEMY_BINDINGS
from game.view.player_ship_models import PLAYER_SHIP_MODELS
from game.view.readability_view import toned_shots
from game.view.scenery_bindings import SCENERY_BINDINGS
from game.view.shots.player_shot_renderers import PLAYER_SHOT_RENDERERS
from game.view.title_backdrop import build_title_backdrop


class GameBindings:
    """The presentation bindings of this game (its `view`, typed as `GameView` in `render/`).

    Meshes, sounds and renderers for the content the sim defines.
    """

    def __init__(
        self,
        player_ship_models: object,
        player_ship_scale: float,
        player_shot_renderers: object,
        menu_backdrop: object,
        scenery: object,
        enemies: object,
        bonuses: object,
        bombs: object,
        audio: object,
        outline: object,
    ) -> None:
        self.player_ship_models = player_ship_models
        self.player_ship_scale = player_ship_scale
        self.player_shot_renderers = player_shot_renderers
        self.menu_backdrop = menu_backdrop
        self.scenery = scenery
        self.enemies = enemies
        self.bonuses = bonuses
        self.bombs = bombs
        self.audio = audio
        self.outline = outline


# The playfield window (D-252): its viewport as shares of the screen.
_PLAYFIELD = GAME_CONFIG.playfield
_SCREEN = GAME_CONFIG.screen
PLAYFIELD = LogicalScreen(
    _PLAYFIELD.width,
    _PLAYFIELD.height,
    (_PLAYFIELD.left / _SCREEN.width, 0, _PLAYFIELD.width / _SCREEN.width, 1),
)

# The single entry point of this game's content (ENG-144).
GAME = GameDefinition(
    GAME_CONFIG.id,
    GAME_CONFIG.title,
    GAME_CONFIG.screen,
    player_roster(PLAYER_SHIPS),
    player_weapons(PLAYER_WEAPONS),
    LEVELS,
    GAME_LEVELS,
    ENEMY_KINDS,
    BOSS_KINDS,
    boss_fight_rules(BOSS_FIGHT_RULES),
    bonus_rules(BONUS_RULES),
    bomb_rules(BOMB_RULES),
    hull_rules(HULL_RULES),
    MENU_TEXTS,
    # The ships with a glowing edge trim (GFX-READ-07), the shots toned down (GFX-READ-14), the
    # ships drawn at their playfield scale (GFX-SHIP-07).
    GameBindings(
        # GFX-SHIP-09 (D-335): no trim round the player ship; its edges glow.
        PLAYER_SHIP_MODELS,
        PLAYER_SHIP_SCALE,
        toned_shots(PLAYER_SHOT_RENDERERS),
        build_title_backdrop,
        SCENERY_BINDINGS,
        ENEMY_BINDINGS,
        create_bonus_renderer,
        create_bomb_renderer,
        GAME_AUDIO,
        READABILITY.outline,
    ),
    PLAYFIELD,
)
