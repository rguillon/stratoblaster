"""The sample `GameDefinition` (ENG-145): one enemy kind that never spawns in these tests, one
projectile weapon, one level of the sample scenery (`tests/helpers/sample_level.py`) with one wave,
and the menu texts of `tests/helpers/menu_game.py`."""

from types import SimpleNamespace
from typing import Any

from helpers.menu_game import make_texts
from helpers.sample_level import sample_level

from core.content.game_definition import GameDefinition, LogicalScreen
from core.content.game_level import GameLevel
from core.content.level_catalog import LevelCatalog, LevelEntry
from core.entities.enemy import EnemyEntry, EnemyKindDefinition
from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from core.entities.weapon import ProjectileWeaponDefinition, ShotStream
from core.systems.bonus_world import BonusChance, BonusRules
from core.systems.boss_fights import BossFightRules
from core.systems.enemy_world import EnemyDifficulty
from core.systems.player_bombs import BombRules
from core.systems.player_hull import HullDamage, HullRules
from core.systems.wave_runner import Wave
from fixtures.sample_game.look import PLAYFIELD_CAMERA, WINDOW_ATLAS


def _no_spawn(_area: Any) -> list[Any]:
    """The sample's enemy makes no enemy: the tests that use it never run its waves."""
    return []


def make_sample_game() -> GameDefinition:
    """A new sample game (`SAMPLE_GAME` is the one the tests share)."""
    gun = ProjectileWeaponDefinition(
        "sample-gun",
        "Sample gun",
        "muzzle",
        10,
        400,
        0,
        400,
        0,
        0,
        3,
        1,
        0,
        [[ShotStream(0, 0)]],
    )
    waves = [Wave(0, "sample-enemy", 1, 0.5, EnemyEntry("top", 0.5))]
    level = GameLevel("sample-1", sample_level(), waves, EnemyDifficulty(1, 1))
    return GameDefinition(
        id="sample",
        title="Sample game",
        screen=LogicalScreen(480, 640),
        player_ships=PlayerShipRoster(100, [PlayerShipDefinition("alpha", "Alpha", 1, 5)]),
        player_weapons=[gun],
        levels=LevelCatalog(1, [LevelEntry("sample-1", "1-1", 1, 1, True)]),
        game_levels=[level],
        enemy_kinds=[EnemyKindDefinition("sample-enemy", "Sample enemy", _no_spawn)],
        boss_kinds=[],
        boss_fights=BossFightRules(0.5, 1),
        bonuses=BonusRules(BonusChance(0.1, 0.05, 0.5), 60, 20),
        bombs=BombRules(1, 5, 2),
        hull=HullRules(3, 2, 4, HullDamage(1, 1, 1, 1), 1),
        texts=make_texts(),
        view=SimpleNamespace(playfield_camera=PLAYFIELD_CAMERA, window_atlas=WINDOW_ATLAS),
    )


SAMPLE_GAME = make_sample_game()
