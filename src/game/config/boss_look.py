"""Look of the bosses (P07)

Their neon colours (GD-61), the white flash of a part when hit, the smoke of a part under half its
health (P07-R01); a destroyed part leaves nothing (D-225). Linear RGB 0..1, sizes in logical pixels,
times in seconds.
"""

from game.config.record import record

BOSS_LOOK = record(
    {
        # Neon colour of each boss (P07-R05), by boss kind id.
        "neon": {
            "reef-warden": [0.1, 0.9, 1],
            "storm-petrel": [1, 0.1, 0.85],
            "breakwater": [1, 0.5, 0.05],
            "gull-mothership": [0.2, 1, 0.35],
            "dust-devil": [1, 0.75, 0.15],
            "mesa-fortress": [1, 0.1, 0.12],
            "scorpion": [1, 0.9, 0.1],
            "refinery-titan": [1, 0.45, 0.05],
            "sentinel": [0.15, 0.4, 1],
            "overlord": [0.65, 0.2, 1],
            # World 2 (P08-R10).
            "floe-breaker": [0.1, 0.85, 1],
            "narwhal": [0.05, 0.95, 0.75],
            "fjord-lynx": [0.55, 0.95, 1],
            "harbour-kraken": [1, 0.5, 0.08],
            "snow-owl": [0.85, 0.92, 1],
            "aurora-station": [0.3, 1, 0.55],
            "avalanche": [1, 0.85, 0.1],
            "glacier-colossus": [1, 0.35, 0.08],
            "ice-queen": [0.55, 0.65, 1],
            "boreal-citadel": [0.35, 1, 0.6],
            # World 3 (P09-R09).
            "mangrove-croc": [0.25, 1, 0.3],
            "river-leviathan": [0.05, 0.9, 0.8],
            "toucan": [1, 0.7, 0.1],
            "canopy-spider": [1, 0.12, 0.15],
            "stone-idol": [0.95, 0.2, 1],
            "sky-temple": [1, 0.8, 0.2],
            "mosquito": [1, 0.3, 0.7],
            # D-231: on the green side (was lime, 0.6), as its hull is overgrown with moss.
            "dam-breaker": [0.3, 1, 0.1],
            "jaguar": [1, 0.6, 0.05],
            "verdant-crown": [0.1, 1, 0.45],
            # World 4 (P10-R11).
            "cinder-crab": [1, 0.45, 0.05],
            "steam-dreadnought": [1, 0.08, 0.1],
            "ash-wraith": [0.55, 0.95, 1],
            "geyser-rig": [1, 0.88, 0.1],
            "magma-salamander": [1, 0.62, 0.08],
            "obsidian-golem": [1, 0.32, 0.04],
            "furnace-drake": [1, 0.22, 0.05],
            "foundry-ark": [1, 0.55, 0.12],
            "ember-herald": [1, 0.78, 0.22],
            "caldera-throne": [0.95, 0.05, 0.22],
        },
        # Its charge lights strobe this many times a second while it holds its fire (P07-R04).
        "stageStrobeHz": 6,
        # While it is angry, they flicker this many times a second, down to `dim` (phase 7 review).
        "rageFlicker": {"hz": 14, "dim": 0.35},
        # A part flashes this colour for `seconds` after a hit (about one frame and a bit).
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
        # A boss's transformation (docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md,
        # D-224), in shares of its length: its armour strains (shudders `shudder` px, strobing
        # `strobeHz`) until `burst`, then bursts off in chunks that are gone by `burstEnd`, thrown
        # `throw` px out, rising `lift` px and falling `fall` px, tumbling `spin` radians. Its
        # hidden weapons swing up on their hinges from `swing[0]` to `swing[1]`, rising from `sink`
        # of their radius down, then slide their barrels out from `slide[0]` to `slide[1]`,
        # overshooting by `overshoot` (a back-out ease). A piece that moves rather than bursting
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
        # How armour is cut out of a boss's body: faces cut down to `cut` px first, at most
        # `chunks` chunks a region and `bossChunks` a boss; surfaces within about `hold` px hold
        # together (D-227).
        "armour": {"cut": 6, "chunks": 12, "bossChunks": 24, "hold": 1.2},
        # The dark metal frame a shed region leaves (`boss_frame.py`): a `floor` where the armour
        # was, `lift` px over its lowest point; `metal` ribs `ribWidth` wide and `ribHeight` high,
        # `ribGap` px apart (sampled every `step` px against the floor, at least `least` px long),
        # one in `seamEvery` with a neon seam on top; `pipe` pipes along the longest ribs.
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
            # Pylons holding up the pieces over it (D-227): `pylonShare` of the piece's radius
            # wide, between `pylonLeast` and `pylonMost` px.
            "pylonShare": 0.7,
            "pylonLeast": 3,
            "pylonMost": 10,
        },
    }
)
