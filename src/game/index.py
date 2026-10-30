"""The single entry point of this game's content (ENG-144), ported from `game/index.ts`.

`main.py` passes `GAME` to `app/`; the engine discovers all content through it.
"""

from core.content.game_definition import GameDefinition
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
from game.view.readability_view import build_hitbox_marker, outlined_ships, toned_shots
from game.view.scenery_bindings import SCENERY_BINDINGS
from game.view.shots.player_shot_renderers import PLAYER_SHOT_RENDERERS
from game.view.title_backdrop import build_title_backdrop


class GameBindings:
    """The presentation bindings of this game (its `view`, typed as `GameView` in `render/`):
    meshes, sounds and renderers for the content the sim defines.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
        hitbox_marker: object,
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
        self.hitbox_marker = hitbox_marker


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
    # Phase 14: the ships with a rim glow (P14-R03), the shots toned down (P14-R06).
    GameBindings(
        outlined_ships(PLAYER_SHIP_MODELS),
        PLAYER_SHIP_SCALE,
        toned_shots(PLAYER_SHOT_RENDERERS),
        build_title_backdrop,
        SCENERY_BINDINGS,
        ENEMY_BINDINGS,
        create_bonus_renderer,
        create_bomb_renderer,
        GAME_AUDIO,
        READABILITY.outline,
        build_hitbox_marker,
    ),
)
