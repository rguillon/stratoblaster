"""The contract between the engine and a game built on it (ENG-144), ported from
`core/content/game-definition.ts`.

`src/game/index.ts` exports exactly one object of this type; the engine discovers all game content
through it. The TypeScript `TView` type parameter is `object` here: the presentation bindings
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
    """The logical resolution the game is laid out on, scaled to fit the window (GD-02)."""

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
        """Fields as in the TypeScript, in the same order:

        - `id`: stable identifier, used e.g. as a storage key prefix; `title`: shown by the engine.
        - `screen`: logical resolution of the screens (GD-02).
        - `player_ships`: the ships the player can fly (data only); the first is selected by
          default.
        - `player_weapons`: the weapons every player ship can fire (data only).
        - `levels`: the levels shown on the level select screen, and which ones can be played.
        - `game_levels`: the levels that can be played (P06), keyed by the id of their entry in
          `levels`.
        - `enemy_kinds`: the kinds of enemies (P05), which the levels' waves bring in by id.
        - `boss_kinds`: the kinds of bosses (P07), which the levels bring in by id.
        - `boss_fights`: how boss fights go (P07-R02, R03).
        - `bonuses`: bonuses dropped by destroyed enemies (P11-R07).
        - `bombs`: the player's bombs (GD-32, P11-R05).
        - `hull`: what hurts the player, and its lives (GD-20..GD-22).
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
