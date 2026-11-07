# Copyright (c) 2026 Renaud Guillon
"""Look of the bosses (specs/bosses/).

Their neon colours (BOSS-50), the white flash of a part when hit, the smoke of a part under half
its health (BOSS-17); a destroyed part leaves nothing (BOSS-18, D-225). Linear RGB 0..1, sizes in
logical pixels, times in seconds.
"""

from game.config.record import record

BOSS_LOOK = record({
    # Neon colour of each boss (BOSS-50; its file's lights requirement), by boss kind id.
    "neon": {
        "reef-warden": [0.1, 0.9, 1],  # MB-REEF-WARDEN-04
        "storm-petrel": [1, 0.1, 0.85],  # FB-STORM-PETREL-04
        "breakwater": [1, 0.5, 0.05],  # MB-BREAKWATER-04
        "gull-mothership": [0.2, 1, 0.35],  # FB-GULL-MOTHERSHIP-04
        "dust-devil": [1, 0.75, 0.15],  # MB-DUST-DEVIL-04
        "mesa-fortress": [1, 0.1, 0.12],  # FB-MESA-FORTRESS-04
        "scorpion": [1, 0.9, 0.1],  # MB-SCORPION-05
        "refinery-titan": [1, 0.45, 0.05],  # FB-REFINERY-TITAN-04
        "sentinel": [0.15, 0.4, 1],  # MB-SENTINEL-04
        "overlord": [0.65, 0.2, 1],  # FB-OVERLORD-04
        # World 2.
        "floe-breaker": [0.1, 0.85, 1],  # MB-FLOE-BREAKER-04
        "narwhal": [0.05, 0.95, 0.75],  # FB-NARWHAL-04
        "fjord-lynx": [0.55, 0.95, 1],  # MB-FJORD-LYNX-04
        "harbour-kraken": [1, 0.5, 0.08],  # FB-HARBOUR-KRAKEN-04
        "snow-owl": [0.85, 0.92, 1],  # MB-SNOW-OWL-04
        "aurora-station": [0.3, 1, 0.55],  # FB-AURORA-STATION-04
        "avalanche": [1, 0.85, 0.1],  # MB-AVALANCHE-04
        "glacier-colossus": [1, 0.35, 0.08],  # FB-GLACIER-COLOSSUS-04
        "ice-queen": [0.55, 0.65, 1],  # MB-ICE-QUEEN-04
        "boreal-citadel": [0.35, 1, 0.6],  # FB-BOREAL-CITADEL-05
        # World 3.
        "mangrove-croc": [0.25, 1, 0.3],  # MB-MANGROVE-CROC-06
        "river-leviathan": [0.05, 0.9, 0.8],  # FB-RIVER-LEVIATHAN-07
        "toucan": [1, 0.7, 0.1],  # MB-TOUCAN-06
        "canopy-spider": [1, 0.12, 0.15],  # FB-CANOPY-SPIDER-06
        "stone-idol": [0.95, 0.2, 1],  # MB-STONE-IDOL-05
        "sky-temple": [1, 0.8, 0.2],  # FB-SKY-TEMPLE-06
        "mosquito": [1, 0.3, 0.7],  # MB-MOSQUITO-06
        # D-231: on the green side (was lime, 0.6), as its hull is overgrown with moss.
        "dam-breaker": [0.3, 1, 0.1],  # FB-DAM-BREAKER-05
        "jaguar": [1, 0.6, 0.05],  # MB-JAGUAR-05
        "verdant-crown": [0.1, 1, 0.45],  # FB-VERDANT-CROWN-06
        # World 4.
        "cinder-crab": [1, 0.45, 0.05],  # MB-CINDER-CRAB-05
        # FB-STEAM-DREADNOUGHT-06 (laser: FB-STEAM-DREADNOUGHT-13).
        "steam-dreadnought": [1, 0.08, 0.1],
        "ash-wraith": [0.55, 0.95, 1],  # MB-ASH-WRAITH-05
        "geyser-rig": [1, 0.88, 0.1],  # FB-GEYSER-RIG-06
        # MB-MAGMA-SALAMANDER-05 (laser: MB-MAGMA-SALAMANDER-15).
        "magma-salamander": [1, 0.62, 0.08],
        # FB-OBSIDIAN-GOLEM-06 (laser: FB-OBSIDIAN-GOLEM-14).
        "obsidian-golem": [1, 0.32, 0.04],
        "furnace-drake": [1, 0.22, 0.05],  # MB-FURNACE-DRAKE-05
        # FB-FOUNDRY-ARK-07 (laser: FB-FOUNDRY-ARK-14).
        "foundry-ark": [1, 0.55, 0.12],
        "ember-herald": [1, 0.78, 0.22],  # MB-EMBER-HERALD-04
        # FB-CALDERA-THRONE-06 (laser: FB-CALDERA-THRONE-12).
        "caldera-throne": [0.95, 0.05, 0.22],
        # The Lab bosses (specs/bosses/lab/).
        "carapace-drum": [0.2, 1, 0.8],  # MB-CARAPACE-DRUM-04
        "tri-wing-hydra": [0.6, 1, 0.1],  # FB-TRI-WING-HYDRA-04
        "twin-hammerhead": [1, 0.3, 0.1],  # MB-TWIN-HAMMERHEAD-04
        "hive-carrier": [1, 0.8, 0.05],  # FB-HIVE-CARRIER-04
        "moth-lantern": [0.85, 0.5, 1],  # MB-MOTH-LANTERN-04
        "leviathan-spine": [0.05, 0.6, 1],  # FB-LEVIATHAN-SPINE-04
        "mantis-lancer": [0.3, 1, 0.3],  # MB-MANTIS-LANCER-04
        "siege-crawler": [1, 0.15, 0.1],  # FB-SIEGE-CRAWLER-04
        "lamprey-coil": [1, 0.2, 0.6],  # MB-LAMPREY-COIL-04
        "crescent-halo": [1, 0.95, 0.6],  # FB-CRESCENT-HALO-04
        "prism-gate": [0.4, 0.85, 1],  # MB-PRISM-GATE-04
        "orbital-foundry": [1, 0.55, 0.2],  # FB-ORBITAL-FOUNDRY-04
        "bastion-cube": [1, 0.35, 0.35],  # MB-BASTION-CUBE-04
        "twin-pylon": [0.3, 0.5, 1],  # FB-TWIN-PYLON-04
        "arrow-lance": [1, 1, 0.2],  # MB-ARROW-LANCE-04
        "cathedral-engine": [0.75, 0.3, 1],  # FB-CATHEDRAL-ENGINE-04
        "lattice-node": [0.2, 1, 0.55],  # MB-LATTICE-NODE-04
        "folding-citadel": [1, 0.6, 0.1],  # FB-FOLDING-CITADEL-04
        "monolith-array": [0.1, 1, 1],  # MB-MONOLITH-ARRAY-04
        "star-engine": [1, 0.1, 0.35],  # FB-STAR-ENGINE-04
        "gale-corvette": [0.5, 0.9, 1],  # MB-GALE-CORVETTE-04
        "sky-carrier": [1, 0.45, 0.1],  # FB-SKY-CARRIER-04
        "bell-keep": [1, 0.85, 0.4],  # MB-BELL-KEEP-04
        "cloud-dreadnought": [1, 0.1, 0.2],  # FB-CLOUD-DREADNOUGHT-04
        "rotor-bastion": [0.3, 1, 0.6],  # MB-ROTOR-BASTION-04
        "zeppelin-citadel": [0.6, 0.4, 1],  # FB-ZEPPELIN-CITADEL-04
        "windmill-ram": [1, 0.7, 0],  # MB-WINDMILL-RAM-04
        "sky-arsenal": [0.2, 0.7, 1],  # FB-SKY-ARSENAL-04
        "kite-bulwark": [0.9, 1, 0.3],  # MB-KITE-BULWARK-04
        "throne-of-storms": [1, 0.3, 0.8],  # FB-THRONE-OF-STORMS-04
        "condor-lifter": [0.4, 1, 0.9],  # MB-CONDOR-LIFTER-04
        "stratoliner-colossus": [1, 0.65, 0.3],  # FB-STRATOLINER-COLOSSUS-04
        "aegis-wing": [0.6, 0.6, 1],  # MB-AEGIS-WING-04
        "seaplane-leviathan": [0.1, 0.8, 1],  # FB-SEAPLANE-LEVIATHAN-04
        "twin-boom-lancer": [1, 0.85, 0.2],  # MB-TWIN-BOOM-LANCER-04
        "swing-wing-titan": [1, 0.25, 0.55],  # FB-SWING-WING-TITAN-04
        "canard-gunship": [0.5, 1, 0.2],  # MB-CANARD-GUNSHIP-04
        "tiltrotor-behemoth": [0.9, 0.4, 1],  # FB-TILTROTOR-BEHEMOTH-04
        "rocket-interceptor": [1, 0.45, 0.2],  # MB-ROCKET-INTERCEPTOR-04
        "aerial-ark": [1, 0.95, 0.95],  # FB-AERIAL-ARK-04
        "anvil-barge": [1, 0.5, 0.25],  # MB-ANVIL-BARGE-04
        "floating-dam": [0.2, 0.8, 1],  # FB-FLOATING-DAM-04
        "iron-lighthouse": [1, 0.95, 0.5],  # MB-IRON-LIGHTHOUSE-04
        "skyport-hub": [0.3, 1, 0.8],  # FB-SKYPORT-HUB-04
        "drill-fort": [1, 0.75, 0.1],  # MB-DRILL-FORT-04
        "aqueduct-leviathan": [0.5, 0.7, 1],  # FB-AQUEDUCT-LEVIATHAN-04
        "bunker-saucer": [0.9, 0.3, 0.3],  # MB-BUNKER-SAUCER-04
        "clockwork-citadel": [1, 0.85, 0.55],  # FB-CLOCKWORK-CITADEL-04
        "mortar-raft": [0.6, 1, 0.4],  # MB-MORTAR-RAFT-04
        "star-fort": [1, 0.35, 0.6],  # FB-STAR-FORT-04
    },
    # Its charge lights strobe this many times a second while it holds its fire (BOSS-22).
    "stageStrobeHz": 6,
    # While it is angry, they flicker this many times a second, down to `dim` (BOSS-27; phase 7
    # review).
    "rageFlicker": {"hz": 14, "dim": 0.35},
    # A part flashes this colour for `seconds` after a hit (about one frame and a bit, BOSS-17).
    "flash": {"color": [1, 1, 1], "seconds": 0.05},
    # Under `below` of its health a part smokes: `puffs` grey discs `size` times its radius,
    # rising by `rise` and drifting back by `drift` over `seconds`, then starting again.
    "smoke": {
        "below": 0.5,
        "puffs": 3,
        "size": 0.45,
        "rise": 6,
        "drift": 16,
        "seconds": 1.1,
        "color": [0.16, 0.15, 0.15],
        "alpha": 0.55,
    },
    # A boss's transformation (BOSS-43, D-224, D-254), in shares of its length: its armour
    # strains (shudders `shudder` px, strobing `strobeHz`) until `burst`, then bursts off in
    # pieces that are gone by `burstEnd`, thrown `throw` px out, rising
    # `lift` px and falling `fall` px, tumbling `spin` radians. Its hidden weapons swing up on
    # their hinges from `swing[0]` to `swing[1]`, rising from `sink` of their radius down, then
    # slide their barrels out from `slide[0]` to `slide[1]`, overshooting by `overshoot` (a
    # back-out ease). A piece that moves rather than bursting
    # (D-230) strains as armour does, then moves into its new pose from `move[0]` to `move[1]`.
    "reveal": {
        "burst": 0.15,
        "burstEnd": 0.6,
        "shudder": 0.8,
        "strobeHz": 9,
        "throw": 45,
        "lift": 28,
        "fall": 60,
        "spin": 7,
        "swing": [0.4, 0.75],
        "slide": [0.7, 1.0],
        "move": [0.15, 0.6],
        "sink": 0.9,
        "overshoot": 1.7,
    },
    # The armour a boss sheds (BOSS-43, D-254): a region drawn without its own pieces cracks into
    # at most `chunks` plates (`bossChunks` a boss), `plate` px thick at the top of its armour;
    # surfaces within about `hold` px of each other hold together (BOSS-52).
    "armour": {"chunks": 12, "bossChunks": 24, "hold": 1.2, "plate": 2.5},
    # The dark metal frame a shed region leaves (BOSS-44, `boss_frame.py`): a `floor` where the
    # armour was, `lift` px over its lowest point; `metal` ribs `ribWidth` wide and `ribHeight`
    # high, `ribGap` px apart (sampled every `step` px against the floor, at least `least` px
    # long), one in `seamEvery` with a neon seam on top; `pipe` pipes along the longest ribs.
    "frame": {
        "floor": [0.035, 0.037, 0.045],
        "metal": [0.1, 0.105, 0.12],
        "pipe": [0.09, 0.09, 0.11],
        "lift": 0.6,
        "ribWidth": 1.6,
        "ribHeight": 2.2,
        "ribGap": 9,
        "step": 1.5,
        "least": 3,
        "pipeRadius": 0.9,
        "spokes": 12,
        "seamEvery": 3,
    },
})
