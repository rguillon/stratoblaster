# Copyright (c) 2026 Renaud Guillon
"""The boss kinds of the game (BOSS-01)."""

from game.config.bosses.boss_kit import with_own_lasers
from game.config.bosses.final_bosses import (
    GULL_MOTHERSHIP,
    MESA_FORTRESS,
    OVERLORD,
    REFINERY_TITAN,
    STORM_PETREL,
)
from game.config.bosses.lab.aegis_wing import AEGIS_WING
from game.config.bosses.lab.aerial_ark import AERIAL_ARK
from game.config.bosses.lab.anvil_barge import ANVIL_BARGE
from game.config.bosses.lab.aqueduct_leviathan import AQUEDUCT_LEVIATHAN
from game.config.bosses.lab.arrow_lance import ARROW_LANCE
from game.config.bosses.lab.bastion_cube import BASTION_CUBE
from game.config.bosses.lab.bell_keep import BELL_KEEP
from game.config.bosses.lab.bunker_saucer import BUNKER_SAUCER
from game.config.bosses.lab.canard_gunship import CANARD_GUNSHIP
from game.config.bosses.lab.carapace_drum import CARAPACE_DRUM
from game.config.bosses.lab.cathedral_engine import CATHEDRAL_ENGINE
from game.config.bosses.lab.clockwork_citadel import CLOCKWORK_CITADEL
from game.config.bosses.lab.cloud_dreadnought import CLOUD_DREADNOUGHT
from game.config.bosses.lab.condor_lifter import CONDOR_LIFTER
from game.config.bosses.lab.crescent_halo import CRESCENT_HALO
from game.config.bosses.lab.drill_fort import DRILL_FORT
from game.config.bosses.lab.floating_dam import FLOATING_DAM
from game.config.bosses.lab.folding_citadel import FOLDING_CITADEL
from game.config.bosses.lab.gale_corvette import GALE_CORVETTE
from game.config.bosses.lab.hive_carrier import HIVE_CARRIER
from game.config.bosses.lab.iron_lighthouse import IRON_LIGHTHOUSE
from game.config.bosses.lab.kite_bulwark import KITE_BULWARK
from game.config.bosses.lab.lamprey_coil import LAMPREY_COIL
from game.config.bosses.lab.lattice_node import LATTICE_NODE
from game.config.bosses.lab.leviathan_spine import LEVIATHAN_SPINE
from game.config.bosses.lab.mantis_lancer import MANTIS_LANCER
from game.config.bosses.lab.monolith_array import MONOLITH_ARRAY
from game.config.bosses.lab.mortar_raft import MORTAR_RAFT
from game.config.bosses.lab.moth_lantern import MOTH_LANTERN
from game.config.bosses.lab.orbital_foundry import ORBITAL_FOUNDRY
from game.config.bosses.lab.prism_gate import PRISM_GATE
from game.config.bosses.lab.rocket_interceptor import ROCKET_INTERCEPTOR
from game.config.bosses.lab.rotor_bastion import ROTOR_BASTION
from game.config.bosses.lab.seaplane_leviathan import SEAPLANE_LEVIATHAN
from game.config.bosses.lab.siege_crawler import SIEGE_CRAWLER
from game.config.bosses.lab.sky_arsenal import SKY_ARSENAL
from game.config.bosses.lab.sky_carrier import SKY_CARRIER
from game.config.bosses.lab.skyport_hub import SKYPORT_HUB
from game.config.bosses.lab.star_engine import STAR_ENGINE
from game.config.bosses.lab.star_fort import STAR_FORT
from game.config.bosses.lab.stratoliner_colossus import STRATOLINER_COLOSSUS
from game.config.bosses.lab.swing_wing_titan import SWING_WING_TITAN
from game.config.bosses.lab.throne_of_storms import THRONE_OF_STORMS
from game.config.bosses.lab.tiltrotor_behemoth import TILTROTOR_BEHEMOTH
from game.config.bosses.lab.tri_wing_hydra import TRI_WING_HYDRA
from game.config.bosses.lab.twin_boom_lancer import TWIN_BOOM_LANCER
from game.config.bosses.lab.twin_hammerhead import TWIN_HAMMERHEAD
from game.config.bosses.lab.twin_pylon import TWIN_PYLON
from game.config.bosses.lab.windmill_ram import WINDMILL_RAM
from game.config.bosses.lab.zeppelin_citadel import ZEPPELIN_CITADEL
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

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

from core.entities.boss import Boss
from core.entities.enemy import EnemySpawnArea
from core.systems.boss_fights import BossKindDefinition

# A boss design is a config record (`game/config/record.py`), typed as Any there.
BossDesign = Any
# __pragma__ ("noskip")


class BossKind:
    """A kind of boss a game offers (BOSS-07): a name, and how one boss of it comes in."""

    def __init__(self, item_id: str, name: str, spawn: Callable[[EnemySpawnArea], Boss]) -> None:
        self.id = item_id
        self.name = name
        self.spawn = spawn


# The boss designs, mini and final boss of 1-1, then of 1-2... (BOSS-01), then the ten of World 2
# (WLD-2-24), the ten of World 3 (WLD-3-19) and the ten of World 4 (WLD-4-21) in the same order.
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
    # The Lab bosses (specs/bosses/lab/), in the dev viewer only: no level brings them in.
    CARAPACE_DRUM,
    TRI_WING_HYDRA,
    TWIN_HAMMERHEAD,
    HIVE_CARRIER,
    MOTH_LANTERN,
    LEVIATHAN_SPINE,
    MANTIS_LANCER,
    SIEGE_CRAWLER,
    LAMPREY_COIL,
    CRESCENT_HALO,
    PRISM_GATE,
    ORBITAL_FOUNDRY,
    BASTION_CUBE,
    TWIN_PYLON,
    ARROW_LANCE,
    CATHEDRAL_ENGINE,
    LATTICE_NODE,
    FOLDING_CITADEL,
    MONOLITH_ARRAY,
    STAR_ENGINE,
    GALE_CORVETTE,
    SKY_CARRIER,
    BELL_KEEP,
    CLOUD_DREADNOUGHT,
    ROTOR_BASTION,
    ZEPPELIN_CITADEL,
    WINDMILL_RAM,
    SKY_ARSENAL,
    KITE_BULWARK,
    THRONE_OF_STORMS,
    CONDOR_LIFTER,
    STRATOLINER_COLOSSUS,
    AEGIS_WING,
    SEAPLANE_LEVIATHAN,
    TWIN_BOOM_LANCER,
    SWING_WING_TITAN,
    CANARD_GUNSHIP,
    TILTROTOR_BEHEMOTH,
    ROCKET_INTERCEPTOR,
    AERIAL_ARK,
    ANVIL_BARGE,
    FLOATING_DAM,
    IRON_LIGHTHOUSE,
    SKYPORT_HUB,
    DRILL_FORT,
    AQUEDUCT_LEVIATHAN,
    BUNKER_SAUCER,
    CLOCKWORK_CITADEL,
    MORTAR_RAFT,
    STAR_FORT,
]


def _spawner(own: BossDesign) -> Callable[[EnemySpawnArea], Boss]:
    """How one boss of `own` comes in: a world boss from its design, at the area's top."""

    def spawn(area: EnemySpawnArea) -> Boss:
        return WorldBoss(own, area)

    return spawn


def _boss_kind(design: BossDesign) -> BossKind:
    """Return the boss kind of a design, its lasers in its own colour (BOSS-32)."""
    own = with_own_lasers(design)
    return BossKind(design.id, design.stats["name"], _spawner(own))


def _all_kinds() -> list[BossKindDefinition]:
    kinds: list[BossKindDefinition] = [_boss_kind(design) for design in BOSS_DESIGNS]
    return kinds


# One boss kind per design, its lasers in its own colour.
BOSS_KINDS = _all_kinds()
