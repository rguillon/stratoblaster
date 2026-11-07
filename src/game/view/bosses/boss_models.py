# Copyright (c) 2026 Renaud Guillon
"""One model per boss, keyed by its model key (the boss kind id, BOSS-01, BOSS-47)."""

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.breakwater_model import build_breakwater
from game.view.bosses.dust_devil_model import build_dust_devil
from game.view.bosses.gull_mothership_model import build_gull_mothership
from game.view.bosses.lab.aegis_wing_model import build_aegis_wing
from game.view.bosses.lab.aerial_ark_model import build_aerial_ark
from game.view.bosses.lab.anvil_barge_model import build_anvil_barge
from game.view.bosses.lab.aqueduct_leviathan_model import build_aqueduct_leviathan
from game.view.bosses.lab.arrow_lance_model import build_arrow_lance
from game.view.bosses.lab.bastion_cube_model import build_bastion_cube
from game.view.bosses.lab.bell_keep_model import build_bell_keep
from game.view.bosses.lab.bunker_saucer_model import build_bunker_saucer
from game.view.bosses.lab.canard_gunship_model import build_canard_gunship
from game.view.bosses.lab.carapace_drum_model import build_carapace_drum
from game.view.bosses.lab.cathedral_engine_model import build_cathedral_engine
from game.view.bosses.lab.clockwork_citadel_model import build_clockwork_citadel
from game.view.bosses.lab.cloud_dreadnought_model import build_cloud_dreadnought
from game.view.bosses.lab.condor_lifter_model import build_condor_lifter
from game.view.bosses.lab.crescent_halo_model import build_crescent_halo
from game.view.bosses.lab.drill_fort_model import build_drill_fort
from game.view.bosses.lab.floating_dam_model import build_floating_dam
from game.view.bosses.lab.folding_citadel_model import build_folding_citadel
from game.view.bosses.lab.gale_corvette_model import build_gale_corvette
from game.view.bosses.lab.hive_carrier_model import build_hive_carrier
from game.view.bosses.lab.iron_lighthouse_model import build_iron_lighthouse
from game.view.bosses.lab.kite_bulwark_model import build_kite_bulwark
from game.view.bosses.lab.lamprey_coil_model import build_lamprey_coil
from game.view.bosses.lab.lattice_node_model import build_lattice_node
from game.view.bosses.lab.leviathan_spine_model import build_leviathan_spine
from game.view.bosses.lab.mantis_lancer_model import build_mantis_lancer
from game.view.bosses.lab.monolith_array_model import build_monolith_array
from game.view.bosses.lab.mortar_raft_model import build_mortar_raft
from game.view.bosses.lab.moth_lantern_model import build_moth_lantern
from game.view.bosses.lab.orbital_foundry_model import build_orbital_foundry
from game.view.bosses.lab.prism_gate_model import build_prism_gate
from game.view.bosses.lab.rocket_interceptor_model import build_rocket_interceptor
from game.view.bosses.lab.rotor_bastion_model import build_rotor_bastion
from game.view.bosses.lab.seaplane_leviathan_model import build_seaplane_leviathan
from game.view.bosses.lab.siege_crawler_model import build_siege_crawler
from game.view.bosses.lab.sky_arsenal_model import build_sky_arsenal
from game.view.bosses.lab.sky_carrier_model import build_sky_carrier
from game.view.bosses.lab.skyport_hub_model import build_skyport_hub
from game.view.bosses.lab.star_engine_model import build_star_engine
from game.view.bosses.lab.star_fort_model import build_star_fort
from game.view.bosses.lab.stratoliner_colossus_model import build_stratoliner_colossus
from game.view.bosses.lab.swing_wing_titan_model import build_swing_wing_titan
from game.view.bosses.lab.throne_of_storms_model import build_throne_of_storms
from game.view.bosses.lab.tiltrotor_behemoth_model import build_tiltrotor_behemoth
from game.view.bosses.lab.tri_wing_hydra_model import build_tri_wing_hydra
from game.view.bosses.lab.twin_boom_lancer_model import build_twin_boom_lancer
from game.view.bosses.lab.twin_hammerhead_model import build_twin_hammerhead
from game.view.bosses.lab.twin_pylon_model import build_twin_pylon
from game.view.bosses.lab.windmill_ram_model import build_windmill_ram
from game.view.bosses.lab.zeppelin_citadel_model import build_zeppelin_citadel
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
    # The Lab bosses (specs/bosses/lab/).
    "carapace-drum": build_carapace_drum,
    "tri-wing-hydra": build_tri_wing_hydra,
    "twin-hammerhead": build_twin_hammerhead,
    "hive-carrier": build_hive_carrier,
    "moth-lantern": build_moth_lantern,
    "leviathan-spine": build_leviathan_spine,
    "mantis-lancer": build_mantis_lancer,
    "siege-crawler": build_siege_crawler,
    "lamprey-coil": build_lamprey_coil,
    "crescent-halo": build_crescent_halo,
    "prism-gate": build_prism_gate,
    "orbital-foundry": build_orbital_foundry,
    "bastion-cube": build_bastion_cube,
    "twin-pylon": build_twin_pylon,
    "arrow-lance": build_arrow_lance,
    "cathedral-engine": build_cathedral_engine,
    "lattice-node": build_lattice_node,
    "folding-citadel": build_folding_citadel,
    "monolith-array": build_monolith_array,
    "star-engine": build_star_engine,
    "gale-corvette": build_gale_corvette,
    "sky-carrier": build_sky_carrier,
    "bell-keep": build_bell_keep,
    "cloud-dreadnought": build_cloud_dreadnought,
    "rotor-bastion": build_rotor_bastion,
    "zeppelin-citadel": build_zeppelin_citadel,
    "windmill-ram": build_windmill_ram,
    "sky-arsenal": build_sky_arsenal,
    "kite-bulwark": build_kite_bulwark,
    "throne-of-storms": build_throne_of_storms,
    "condor-lifter": build_condor_lifter,
    "stratoliner-colossus": build_stratoliner_colossus,
    "aegis-wing": build_aegis_wing,
    "seaplane-leviathan": build_seaplane_leviathan,
    "twin-boom-lancer": build_twin_boom_lancer,
    "swing-wing-titan": build_swing_wing_titan,
    "canard-gunship": build_canard_gunship,
    "tiltrotor-behemoth": build_tiltrotor_behemoth,
    "rocket-interceptor": build_rocket_interceptor,
    "aerial-ark": build_aerial_ark,
    "anvil-barge": build_anvil_barge,
    "floating-dam": build_floating_dam,
    "iron-lighthouse": build_iron_lighthouse,
    "skyport-hub": build_skyport_hub,
    "drill-fort": build_drill_fort,
    "aqueduct-leviathan": build_aqueduct_leviathan,
    "bunker-saucer": build_bunker_saucer,
    "clockwork-citadel": build_clockwork_citadel,
    "mortar-raft": build_mortar_raft,
    "star-fort": build_star_fort,
}
