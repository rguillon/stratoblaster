"""The boss kinds of the game (P07-R05)"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import with_own_lasers
from game.config.bosses.final_bosses import (
    GULL_MOTHERSHIP,
    MESA_FORTRESS,
    OVERLORD,
    REFINERY_TITAN,
    STORM_PETREL,
)
from game.config.bosses.mini_bosses import BREAKWATER, DUST_DEVIL, REEF_WARDEN, SCORPION, SENTINEL
from game.config.bosses.world_2.aurora_station import AURORA_STATION
from game.config.bosses.world_2.avalanche import AVALANCHE
from game.config.bosses.world_2.boreal_citadel import BOREAL_CITADEL
from game.config.bosses.world_2.fjord_lynx import FJORD_LYNX
from game.config.bosses.world_2.floe_breaker import FLOE_BREAKER
from game.config.bosses.world_2.glacier_colossus import GLACIER_COLOSSUS
from game.config.bosses.world_2.harbour_kraken import HARBOUR_KRAKEN
from game.config.bosses.world_2.ice_queen import ICE_QUEEN
from game.config.bosses.world_2.narwhal import NARWHAL
from game.config.bosses.world_2.snow_owl import SNOW_OWL
from game.config.bosses.world_3.canopy_spider import CANOPY_SPIDER
from game.config.bosses.world_3.dam_breaker import DAM_BREAKER
from game.config.bosses.world_3.jaguar import JAGUAR
from game.config.bosses.world_3.mangrove_croc import MANGROVE_CROC
from game.config.bosses.world_3.mosquito import MOSQUITO
from game.config.bosses.world_3.river_leviathan import RIVER_LEVIATHAN
from game.config.bosses.world_3.sky_temple import SKY_TEMPLE
from game.config.bosses.world_3.stone_idol import STONE_IDOL
from game.config.bosses.world_3.toucan import TOUCAN
from game.config.bosses.world_3.verdant_crown import VERDANT_CROWN
from game.config.bosses.world_4.ash_wraith import ASH_WRAITH
from game.config.bosses.world_4.caldera_throne import CALDERA_THRONE
from game.config.bosses.world_4.cinder_crab import CINDER_CRAB
from game.config.bosses.world_4.ember_herald import EMBER_HERALD
from game.config.bosses.world_4.foundry_ark import FOUNDRY_ARK
from game.config.bosses.world_4.furnace_drake import FURNACE_DRAKE
from game.config.bosses.world_4.geyser_rig import GEYSER_RIG
from game.config.bosses.world_4.magma_salamander import MAGMA_SALAMANDER
from game.config.bosses.world_4.obsidian_golem import OBSIDIAN_GOLEM
from game.config.bosses.world_4.steam_dreadnought import STEAM_DREADNOUGHT
from game.sim.bosses.world_boss import WorldBoss

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

from core.entities.boss import Boss  # noqa: E402
from core.entities.enemy import EnemySpawnArea  # noqa: E402
from core.systems.boss_fights import BossKindDefinition  # noqa: E402

# A boss design is a config record (`game/config/record.py`), typed as Any there.
__pragma__("skip")
BossDesign = Any  # noqa: E402
__pragma__("noskip")

__pragma__("noskip")


class BossKind:
    """A kind of boss a game offers (P07-R05): a name, and how one boss of it comes in."""

    def __init__(self, id: str, name: str, spawn: Callable[[EnemySpawnArea], Boss]) -> None:
        self.id = id
        self.name = name
        self.spawn = spawn


# The boss designs, mini and final boss of 1-1, then of 1-2... (P07-R05), then the ten of World 2
# (P08-R10), the ten of World 3 (P09-R09) and the ten of World 4 (P10-R11) in the same order.
BOSS_DESIGNS: list[BossDesign] = [
    REEF_WARDEN,
    STORM_PETREL,
    BREAKWATER,
    GULL_MOTHERSHIP,
    DUST_DEVIL,
    MESA_FORTRESS,
    SCORPION,
    REFINERY_TITAN,
    SENTINEL,
    OVERLORD,
    FLOE_BREAKER,
    NARWHAL,
    FJORD_LYNX,
    HARBOUR_KRAKEN,
    SNOW_OWL,
    AURORA_STATION,
    AVALANCHE,
    GLACIER_COLOSSUS,
    ICE_QUEEN,
    BOREAL_CITADEL,
    MANGROVE_CROC,
    RIVER_LEVIATHAN,
    TOUCAN,
    CANOPY_SPIDER,
    STONE_IDOL,
    SKY_TEMPLE,
    MOSQUITO,
    DAM_BREAKER,
    JAGUAR,
    VERDANT_CROWN,
    CINDER_CRAB,
    STEAM_DREADNOUGHT,
    ASH_WRAITH,
    GEYSER_RIG,
    MAGMA_SALAMANDER,
    OBSIDIAN_GOLEM,
    FURNACE_DRAKE,
    FOUNDRY_ARK,
    EMBER_HERALD,
    CALDERA_THRONE,
]


def _spawner(own: BossDesign) -> Callable[[EnemySpawnArea], Boss]:
    """How one boss of `own` comes in: a world boss from its design, at the area's top."""

    def spawn(area: EnemySpawnArea) -> Boss:
        return WorldBoss(own, area)

    return spawn


def _boss_kind(design: BossDesign) -> BossKind:
    """The boss kind of a design, its lasers in its own colour."""
    own = with_own_lasers(design)
    return BossKind(design.id, design.stats["name"], _spawner(own))


def _all_kinds() -> list[BossKindDefinition]:
    kinds: list[BossKindDefinition] = []
    for design in BOSS_DESIGNS:
        kinds.append(_boss_kind(design))
    return kinds


# One boss kind per design, its lasers in its own colour.
BOSS_KINDS = _all_kinds()
