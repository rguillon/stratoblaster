"""Colours of the props (P04-R04)

Weathered concrete and dark metal, with small neon accents (GD-60/61), and grey dead wood.
Gamma-space RGB, 0..1.
"""

from game.config.record import record

PROP_COLORS = record(
    {
        "concrete": [0.46, 0.44, 0.41],
        "concreteDark": [0.31, 0.3, 0.29],
        "rust": [0.4, 0.23, 0.15],
        "metal": [0.34, 0.36, 0.4],
        "metalDark": [0.17, 0.18, 0.21],
        "roof": [0.24, 0.24, 0.26],
        "white": [0.8, 0.8, 0.78],
        "glass": [0.07, 0.1, 0.14],
        "wood": [0.3, 0.25, 0.2],
        "bark": [0.27, 0.2, 0.14],
        "leaf": [0.22, 0.4, 0.15],
        "leafDark": [0.13, 0.27, 0.12],
        "leafLight": [0.36, 0.52, 0.2],
        "glassBlue": [0.1, 0.17, 0.26],
        "brick": [0.42, 0.26, 0.2],
        "containerBlue": [0.14, 0.27, 0.45],
        "containerGreen": [0.2, 0.36, 0.24],
        "containerRed": [0.5, 0.17, 0.14],
        # Paints of the bus and the tanker's cab (D-213).
        "carOrange": [0.78, 0.42, 0.1],
        "carTeal": [0.1, 0.4, 0.42],
        # More city facades (phase 4 review).
        "sand": [0.55, 0.48, 0.38],
        "glassGreen": [0.09, 0.2, 0.19],
        "glassDark": [0.05, 0.06, 0.09],
        # Desert homes (phase 6): rammed earth, solar panels, thatch, dry leaves.
        "adobe": [0.74, 0.62, 0.47],
        "adobeDark": [0.56, 0.45, 0.33],
        "adobeRoof": [0.64, 0.55, 0.43],
        "solar": [0.07, 0.11, 0.24],
        "thatch": [0.52, 0.42, 0.26],
        "dryLeaf": [0.46, 0.43, 0.25],
        # Farms of World 1's green land (reviewer, 2026-10-26): pale panelled walls, dark roofs.
        "farmWall": [0.66, 0.64, 0.6],
        "farmRoof": [0.2, 0.21, 0.25],
        # World 2 (phase 8): ice, snowy pines and pale frosted wood, painted metal of the harbours
        # and mines, insulated panels.
        "ice": [0.8, 0.89, 0.95],
        "silver": [0.62, 0.65, 0.7],
        "signalOrange": [0.85, 0.42, 0.12],
        "mineYellow": [0.72, 0.56, 0.14],
        "ore": [0.27, 0.25, 0.24],
        "panel": [0.5, 0.56, 0.63],
        # World 3 (phase 9): dark wet soil and red-brown mud, moss, the canopy's greens (deep, mid,
        # sunlit, yellowish and blue-green, so packed crowns read as separate trees), grey-green
        # mossy stone and old paving, red dirt, rusty and dark metal, reeds, lily pads, white water.
        "mud": [0.38, 0.24, 0.15],
        "moss": [0.26, 0.37, 0.14],
        "mossDark": [0.15, 0.24, 0.1],
        "canopy": [0.15, 0.34, 0.12],
        "paving": [0.51, 0.48, 0.41],
        "corrugated": [0.4, 0.36, 0.31],
        "rustDark": [0.3, 0.17, 0.11],
        "foam": [0.87, 0.91, 0.91],
        # World 4 (phase 10): soot black and basalt, grey ash (lighter on the roofs it covers),
        # charred wood, rust red and sulphur yellow mineral stains, dark industrial iron, dark
        # slag, hardy yellow-green grass, the steaming water of the hot springs and the pale steam
        # itself.
        "soot": [0.07, 0.07, 0.075],
        "steam": [0.8, 0.82, 0.83],
        # World 3's homes (reviewer's rework, 2026-10-27): pale rendered walls, warm brick, red
        # tile and dark slate roofs.
        "render": [0.76, 0.73, 0.66],
    }
)

# Self-lit accents.
PROP_LIGHTS = record(
    {
        "cyan": [0, 0.94, 1],
        "pink": [1, 0.16, 0.53],
        "yellow": [0.99, 0.85, 0.1],
        "red": [1, 0.12, 0.1],
        "window": [1, 0.72, 0.38],
        # Dimmer window and trim colours for the city, where hundreds of them glow at once.
        "windowDim": [0.5, 0.36, 0.2],
        "cyanDim": [0, 0.42, 0.48],
        "pinkDim": [0.5, 0.1, 0.3],
        "whiteDim": [0.42, 0.42, 0.4],
        "yellowDim": [0.45, 0.38, 0.08],
        # World 3 (phase 9): the bio-labs' toxic green, and the enemy's violet neon in the ruins.
        "toxicDim": [0.2, 0.48, 0.08],
        "violet": [0.62, 0.2, 1],
        # World 4 (phase 10): molten metal, the furnaces' glowing mouths, lava and glowing slag
        # (dimmer, as there is a lot of it), and the enemy's orange neon in the foundries and the
        # war factory.
        "molten": [1, 0.7, 0.22],
        "lava": [0.95, 0.3, 0.05],
    }
)
