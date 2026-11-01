"""The contract between the engine and a game built on it (ENG-144)

The game exports exactly one object of this type; the engine discovers all game content
through it. The view type parameter is `object` here: the presentation bindings
(meshes, materials...) are defined by the presentation layers, so `core/` stays free of Babylon.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.content.game_level import GameLevel  # noqa: E402
from core.content.level_catalog import LevelCatalog  # noqa: E402
from core.content.menu_texts import MenuTexts  # noqa: E402
from core.entities.enemy import EnemyKindDefinition  # noqa: E402
from core.entities.player_ship import PlayerShipRoster  # noqa: E402
from core.entities.weapon import WeaponDefinition  # noqa: E402
from core.systems.bonus_world import BonusRules  # noqa: E402
from core.systems.boss_fights import BossFightRules, BossKindDefinition  # noqa: E402
from core.systems.player_bombs import BombRules  # noqa: E402
from core.systems.player_hull import HullRules  # noqa: E402

__pragma__("noskip")


class LogicalScreen:
    """The logical resolution the game is laid out on (GAME-SCREEN-01), scaled to fit the window
    (GAME-SCREEN-02).
    """

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height


class GameDefinition:
    """Contract between the engine and a game built on it (ENG-144)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        id: str,
        title: str,
        screen: LogicalScreen,
        player_ships: PlayerShipRoster,
        player_weapons: list[WeaponDefinition],
        levels: LevelCatalog,
        game_levels: list[GameLevel],
        enemy_kinds: list[EnemyKindDefinition],
        boss_kinds: list[BossKindDefinition],
        boss_fights: BossFightRules,
        bonuses: BonusRules,
        bombs: BombRules,
        hull: HullRules,
        texts: MenuTexts,
        view: object,
    ) -> None:
        """Fields, in the same order:

        - `id`: stable identifier, used e.g. as a storage key prefix; `title`: shown by the engine.
        - `screen`: logical resolution of the screens (GAME-SCREEN-01).
        - `player_ships`: the ships the player can fly (data only); the first is selected by
          default.
        - `player_weapons`: the weapons every player ship can fire (data only).
        - `levels`: the levels shown on the level select screen, and which ones can be played.
        - `game_levels`: the levels that can be played (GAME-LEVEL-16), keyed by the id of their
          entry in `levels`.
        - `enemy_kinds`: the kinds of enemies (ENM-04), which the levels' waves bring in by id.
        - `boss_kinds`: the kinds of bosses (BOSS-07), which the levels bring in by id.
        - `boss_fights`: how boss fights go (GAME-LEVEL-07, UI-HUD-14).
        - `bonuses`: bonuses dropped by destroyed enemies (GAME-BONUS-02, GAME-BONUS-03).
        - `bombs`: the player's bombs (GAME-BOMB-01).
        - `hull`: what hurts the player, and its lives (GAME-LIFE-02, GAME-LIFE-03).
        - `texts`: texts of the menu screens.
        - `view`: presentation bindings for the content above.
        """
        self.id = id
        self.title = title
        self.screen = screen
        self.player_ships = player_ships
        self.player_weapons = player_weapons
        self.levels = levels
        self.game_levels = game_levels
        self.enemy_kinds = enemy_kinds
        self.boss_kinds = boss_kinds
        self.boss_fights = boss_fights
        self.bonuses = bonuses
        self.bombs = bombs
        self.hull = hull
        self.texts = texts
        self.view = view
