# Copyright (c) 2026 Renaud Guillon
"""Player ship look (GFX-ART-04, GFX-SHIP-04; darksynth, GFX-ART-03)."""

from game.config.record import record

# Logical pixels per model unit when the player ships are drawn on the playfield (GFX-SHIP-07).
PLAYER_SHIP_SCALE = 7

# Player ship look (GFX-SHIP-04: satin grey/blue metal in three shades, blue light behind each
# reactor). Linear RGB, 0..1. D-327: rougher than the mirror metal it was (0.25), so the light rolls
# smoothly over the hull instead of breaking into hard white spots.
SHIP_LOOK = record({
    "hull": {"albedo": [0.6, 0.66, 0.76], "metallic": 0.8, "roughness": 0.42},
    # Steel for the shoulders' fittings, canards and spinners: a step darker than the hull.
    "hullMid": {"albedo": [0.4, 0.45, 0.54], "metallic": 0.85, "roughness": 0.45},
    # Gunmetal for the tails, flaps and fins: the darkest shade.
    "hullDark": {"albedo": [0.2, 0.23, 0.29], "metallic": 0.85, "roughness": 0.5},
    "accent": {"albedo": [0.16, 0.3, 0.6], "metallic": 0.75, "roughness": 0.4},
    "canopy": {
        "albedo": [0.03, 0.08, 0.18],
        "metallic": 0.3,
        "roughness": 0.05,
        "emissive": [0, 0.06, 0.12],
    },
    "trim": {"albedo": [0.24, 0.28, 0.36], "metallic": 0.85, "roughness": 0.3},
    "nozzle": {"albedo": [0.18, 0.2, 0.24], "metallic": 1, "roughness": 0.45},
    # The inside of the intakes, matte black (D-347, owner: "make the back of the reactor intake
    # mat black"): no metal, fully rough, so it takes no highlight.
    "intakeBlack": {"albedo": [0.012, 0.012, 0.015], "metallic": 0, "roughness": 1},
    # The canopy's tinted glass (D-354): see-through, the cockpit showing under it, with the sky's
    # reflections over it.
    "glass": {"albedo": [0.02, 0.07, 0.14], "metallic": 0.2, "roughness": 0.06, "alpha": 0.45},
    "reactorCore": {"emissive": [0.35, 0.75, 1]},
    # GFX-SHIP-09 (D-335, owner: "remove the highlight as an outter layer for the player's ship,
    # instead make it look like it's the extremities of the wings and cockpit that are glowing"):
    # the self-lit cyan of the wings' and canards' leading edges and of the canopy's frame, in
    # place of the edge trim round the ship; it blooms in the glow layer.
    "edgeGlow": {"emissive": [0.25, 0.85, 1]},
    "reactorExhaust": {"emissive": [0.1, 0.45, 1], "alpha": 0.45},
    # Hot inner flame, shorter and whiter than the exhaust cone around it.
    "reactorFlame": {"emissive": [0.55, 0.85, 1], "alpha": 0.75},
    # Plasma puffs flowing down the exhaust.
    "reactorPlasma": {"emissive": [0.3, 0.7, 1], "alpha": 0.6},
})

# Reactor flame animation (GFX-SHIP-06). Lengths are relative to the exhaust cone; frequencies in
# Hz.
REACTOR_FLAME = record({
    # Flicker amplitude (+- fraction) of the flame length, width and brightness.
    "lengthFlicker": 0.14,
    "widthFlicker": 0.06,
    "brightnessFlicker": 0.2,
    # Mixed sine frequencies: incommensurate so the flicker never looks periodic.
    "flickerHz": [5.3, 11.7, 19.1],
    # Inner flame size, relative to the exhaust cone.
    "coreLength": 0.6,
    "coreWidth": 0.55,
    "puffCount": 3,
    # Exhaust lengths travelled per second by a plasma puff.
    "puffSpeed": 1.8,
    # Puff diameter relative to the nacelle radius, at the nozzle.
    "puffSize": 1.1,
})
