# Copyright (c) 2026 Renaud Guillon
"""One model per boss, keyed by its model key (the boss kind id, BOSS-01, BOSS-47)."""

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.breakwater_model import build_breakwater
from game.view.bosses.dust_devil_model import build_dust_devil
from game.view.bosses.gull_mothership_model import build_gull_mothership
from game.view.bosses.mesa_fortress_model import build_mesa_fortress
from game.view.bosses.overlord_model import build_overlord
from game.view.bosses.reef_warden_model import build_reef_warden
from game.view.bosses.refinery_titan_model import build_refinery_titan
from game.view.bosses.scorpion_model import build_scorpion
from game.view.bosses.sentinel_model import build_sentinel
from game.view.bosses.storm_petrel_model import build_storm_petrel
from game.view.bosses.world_2.aurora_station_model import build_aurora_station
from game.view.bosses.world_2.avalanche_model import build_avalanche
from game.view.bosses.world_2.boreal_citadel_model import build_boreal_citadel
from game.view.bosses.world_2.fjord_lynx_model import build_fjord_lynx
from game.view.bosses.world_2.floe_breaker_model import build_floe_breaker
from game.view.bosses.world_2.glacier_colossus_model import build_glacier_colossus
from game.view.bosses.world_2.harbour_kraken_model import build_harbour_kraken
from game.view.bosses.world_2.ice_queen_model import build_ice_queen
from game.view.bosses.world_2.narwhal_model import build_narwhal
from game.view.bosses.world_2.snow_owl_model import build_snow_owl
from game.view.bosses.world_3.canopy_spider_model import build_canopy_spider
from game.view.bosses.world_3.dam_breaker_model import build_dam_breaker
from game.view.bosses.world_3.jaguar_model import build_jaguar
from game.view.bosses.world_3.mangrove_croc_model import build_mangrove_croc
from game.view.bosses.world_3.mosquito_model import build_mosquito
from game.view.bosses.world_3.river_leviathan_model import build_river_leviathan
from game.view.bosses.world_3.sky_temple_model import build_sky_temple
from game.view.bosses.world_3.stone_idol_model import build_stone_idol
from game.view.bosses.world_3.toucan_model import build_toucan
from game.view.bosses.world_3.verdant_crown_model import build_verdant_crown
from game.view.bosses.world_4.ash_wraith_model import build_ash_wraith
from game.view.bosses.world_4.caldera_throne_model import build_caldera_throne
from game.view.bosses.world_4.cinder_crab_model import build_cinder_crab
from game.view.bosses.world_4.ember_herald_model import build_ember_herald
from game.view.bosses.world_4.foundry_ark_model import build_foundry_ark
from game.view.bosses.world_4.furnace_drake_model import build_furnace_drake
from game.view.bosses.world_4.geyser_rig_model import build_geyser_rig
from game.view.bosses.world_4.magma_salamander_model import build_magma_salamander
from game.view.bosses.world_4.obsidian_golem_model import build_obsidian_golem
from game.view.bosses.world_4.steam_dreadnought_model import build_steam_dreadnought

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

# One model per boss, keyed by its model key (the boss kind id, BOSS-01).
BOSS_MODELS = {
    "reef-warden": build_reef_warden,
    "storm-petrel": build_storm_petrel,
    "breakwater": build_breakwater,
    "gull-mothership": build_gull_mothership,
    "dust-devil": build_dust_devil,
    "mesa-fortress": build_mesa_fortress,
    "scorpion": build_scorpion,
    "refinery-titan": build_refinery_titan,
    "sentinel": build_sentinel,
    "overlord": build_overlord,
    # World 2 (specs/bosses/*/2-*.md).
    "floe-breaker": build_floe_breaker,
    "narwhal": build_narwhal,
    "fjord-lynx": build_fjord_lynx,
    "harbour-kraken": build_harbour_kraken,
    "snow-owl": build_snow_owl,
    "aurora-station": build_aurora_station,
    "avalanche": build_avalanche,
    "glacier-colossus": build_glacier_colossus,
    "ice-queen": build_ice_queen,
    "boreal-citadel": build_boreal_citadel,
    # World 3 (specs/bosses/*/3-*.md).
    "mangrove-croc": build_mangrove_croc,
    "river-leviathan": build_river_leviathan,
    "toucan": build_toucan,
    "canopy-spider": build_canopy_spider,
    "stone-idol": build_stone_idol,
    "sky-temple": build_sky_temple,
    "mosquito": build_mosquito,
    "dam-breaker": build_dam_breaker,
    "jaguar": build_jaguar,
    "verdant-crown": build_verdant_crown,
    # World 4 (specs/bosses/*/4-*.md).
    "cinder-crab": build_cinder_crab,
    "steam-dreadnought": build_steam_dreadnought,
    "ash-wraith": build_ash_wraith,
    "geyser-rig": build_geyser_rig,
    "magma-salamander": build_magma_salamander,
    "obsidian-golem": build_obsidian_golem,
    "furnace-drake": build_furnace_drake,
    "foundry-ark": build_foundry_ark,
    "ember-herald": build_ember_herald,
    "caldera-throne": build_caldera_throne,
}
