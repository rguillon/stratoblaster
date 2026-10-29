"""Look of the bosses (P07), ported from `config/boss-look.ts`.

Their neon colours (GD-61), the white flash of a part when hit, the smoke of a part under half its
health, and the stump left by a destroyed part (P07-R01). Linear RGB 0..1, sizes in logical pixels,
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
            "dam-breaker": [0.6, 1, 0.1],
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
        # A destroyed part's wound (P16-R05): torn plating in `char`, its organ dimmed to `organ`,
        # and sparks flickering on `sparkChance` of frames.
        "stump": {
            "char": [0.05, 0.04, 0.035],
            "organ": [0.06, 0.012, 0.018],
            "spark": [1, 0.55, 0.15],
            "sparkChance": 0.35,
        },
    }
)
