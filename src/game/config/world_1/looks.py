"""How the World 1 levels look (P06-R05, R06, R10; reworked at the reviewer's request, 2026-10-26)

One ground for the whole world, from a turquoise sea over green grass and dry earth to the dried
red land of an American desert (reviewer, 2026-10-30, D-200: not sand dunes), and
a time of day per level, later and later: midday over the sea (1-1), early afternoon on the green
coast (1-2), late afternoon in the green country (1-3), sunset over the dry lands (1-4) and dusk
over the deep desert, its towns' lights on (1-5). Every look starts from Level Zero's. Gamma-space
RGB, 0..1.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import merge, record
from game.config.scenery_look import BASE_SCENERY_LOOK, texture

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Desert sand (P06-R06): warm, fine-grained, with dark grains. World 2 starts on it too.
SAND = texture(
    [
        [0.76, 0.6, 0.4],
        [0.81, 0.66, 0.45],
        [0.86, 0.72, 0.5],
    ],
    18,
    {"speckle": 0.025, "speckleColor": [0.52, 0.38, 0.24]},
)

# Dry earth: the ground where the grass turns dry, between the green land and the sand.
DRY_EARTH = texture(
    [
        [0.5, 0.42, 0.3],
        [0.6, 0.51, 0.37],
        [0.68, 0.6, 0.45],
    ],
    12,
    {"speckle": 0.04, "speckleColor": [0.38, 0.38, 0.22]},
)

# Fresh green grass of the islands, the coast and the meadows, with a few yellow tufts.
GRASS = texture(
    [
        [0.22, 0.34, 0.12],
        [0.3, 0.46, 0.16],
        [0.4, 0.55, 0.22],
    ],
    14,
    {"speckle": 0.035, "speckleColor": [0.6, 0.56, 0.28]},
)

# Red-brown desert rock, layered (World 2's slopes).
DESERT_ROCK = texture(
    [
        [0.42, 0.28, 0.2],
        [0.56, 0.38, 0.27],
        [0.66, 0.48, 0.35],
    ],
    8,
    {"strata": 0.45},
)

# Red mesa rock, in strong layers (D-200): the walls of World 1's mesas, buttes and canyons.
MESA_ROCK = texture(
    [
        [0.46, 0.22, 0.13],
        [0.62, 0.32, 0.19],
        [0.74, 0.44, 0.28],
    ],
    8,
    {"strata": 0.6},
)

# The dried land of an American desert (D-200): red-orange dirt, scattered with dark pebbles and
# sage-grey scrub, no sand.
DESERT_DIRT = texture(
    [
        [0.56, 0.34, 0.21],
        [0.67, 0.43, 0.28],
        [0.76, 0.53, 0.36],
    ],
    14,
    {"speckle": 0.045, "speckleColor": [0.36, 0.34, 0.26]},
)

# Dried earth (D-200): the bare ground of the dry levels, warm brown, between the dry grass and the
# red dirt (World 1's other levels keep the olive `DRY_EARTH`).
DRIED_EARTH = texture(
    [
        [0.52, 0.38, 0.26],
        [0.62, 0.47, 0.33],
        [0.7, 0.56, 0.4],
    ],
    12,
    {"speckle": 0.04, "speckleColor": [0.4, 0.33, 0.24]},
)

# A dry lake bed (D-200): pale grey-pink hardpan, cracked into plates, on the low flats.
HARDPAN = texture(
    [
        [0.64, 0.57, 0.53],
        [0.75, 0.68, 0.63],
        [0.85, 0.79, 0.73],
    ],
    10,
    {"cracks": 0.75, "speckle": 0.01, "speckleColor": [0.48, 0.38, 0.28]},
)

# The ground of the whole world: dry earth by default, covered with grass, sand or pavement by
# section (`surface`), so the land fades from green to sand along the levels.
TERRAIN = merge(
    BASE_SCENERY_LOOK.terrain,
    {
        "ground": DRY_EARTH,
        "lush": GRASS,
        "sand": SAND,
        "shore": merge(
            BASE_SCENERY_LOOK.terrain.shore,
            {
                "sand": [0.86, 0.78, 0.6],
                "shallow": [0.1, 0.62, 0.6],
                "deep": [0.02, 0.2, 0.32],
            },
        ),
    },
)

# The dry levels (D-200): dried earth, red dirt where the sections lay their "sandy" cover, cracked
# hardpan on the low flats, red rock on the walls of the mesas, buttes and canyons, a warmer tint.
DRY_TERRAIN = merge(
    TERRAIN,
    {
        "ground": DRIED_EARTH,
        "low": HARDPAN,
        "sand": DESERT_DIRT,
        "steep": MESA_ROCK,
        # No snow on the flat tops of the mesas and buttes (the heights the shader compares are the
        # world's, twice the ground's).
        "highHeight": 1000,
        # Steep ground is bare rock (no dunes whose lee sides must stay covered).
        "steepSlope": [0.55, 0.95],
        "tints": [
            [1.05, 0.98, 0.9],
            [0.9, 0.84, 0.78],
        ],
    },
)


def sky(haze: list[float], horizon: list[float], zenith: list[float], intensity: float) -> Any:
    """The sky script of a look: `haze` at the middle, `horizon` and `zenith` around it."""
    return record(
        {
            "haze": haze,
            "stops": [
                {"at": -1, "color": [0.25, 0.22, 0.2]},
                {"at": 0, "color": horizon},
                {"at": 0.35, "color": haze},
                {"at": 1, "color": zenith},
            ],
            "environmentIntensity": intensity,
        }
    )


def sun(elevation_deg: float, azimuth_deg: float, color: list[float], intensity: float) -> Any:
    """Level Zero's sun, moved to `elevation_deg` and `azimuth_deg`, with its own colour."""
    return merge(
        BASE_SCENERY_LOOK.sun,
        {
            "elevationDeg": elevation_deg,
            "azimuthDeg": azimuth_deg,
            "color": color,
            "intensity": intensity,
        },
    )


def clouds(
    low: float,
    high: float,
    color: list[float] | None = None,
    shade: list[float] | None = None,
) -> Any:
    """The two cloud layers of Level Zero, with another coverage and colour each."""
    first = BASE_SCENERY_LOOK.clouds[0]
    second = BASE_SCENERY_LOOK.clouds[1]
    tint = {"color": color, "shade": shade} if color and shade else {}
    return [
        merge(merge(first, {"coverage": low}), tint),
        merge(merge(second, {"coverage": high}), tint),
    ]


# 1-1: midday, the sun high, over a clear turquoise sea, scattered white clouds.
LEVEL_1_1_LOOK = merge(
    BASE_SCENERY_LOOK,
    {
        "sky": sky([0.7, 0.8, 0.9], [0.86, 0.9, 0.95], [0.22, 0.45, 0.82], 0.7),
        "sun": sun(72, 20, [1, 0.97, 0.92], 1.7),
        "ambient": {"sky": [0.66, 0.76, 0.9], "ground": [0.32, 0.36, 0.3], "intensity": 0.65},
        "terrain": TERRAIN,
        "sea": merge(BASE_SCENERY_LOOK.sea, {"color": [0.02, 0.2, 0.32]}),
        "clouds": clouds(0.35, 0.2),
    },
)

# 1-2: early afternoon on the green coast, a little warmer.
LEVEL_1_2_LOOK = merge(
    LEVEL_1_1_LOOK,
    {
        "sky": sky([0.74, 0.8, 0.86], [0.9, 0.88, 0.84], [0.26, 0.46, 0.78], 0.7),
        "sun": sun(55, 35, [1, 0.93, 0.82], 1.65),
        "ambient": {"sky": [0.66, 0.74, 0.86], "ground": [0.34, 0.36, 0.28], "intensity": 0.62},
        "clouds": clouds(0.3, 0.18),
    },
)

# 1-3: late afternoon in the green country, golden light and longer shadows.
LEVEL_1_3_LOOK = merge(
    LEVEL_1_1_LOOK,
    {
        "sky": sky([0.84, 0.76, 0.64], [0.96, 0.82, 0.6], [0.3, 0.44, 0.74], 0.65),
        "sun": sun(35, 45, [1, 0.85, 0.64], 1.65),
        "ambient": {"sky": [0.68, 0.68, 0.76], "ground": [0.4, 0.34, 0.24], "intensity": 0.6},
        "clouds": clouds(0.22, 0.14, [1, 0.94, 0.84], [0.76, 0.68, 0.68]),
    },
)

# 1-4: sunset over the dry lands: a low orange sun, a magenta haze, long shadows.
LEVEL_1_4_LOOK = merge(
    BASE_SCENERY_LOOK,
    {
        "sky": sky([0.86, 0.56, 0.52], [1, 0.62, 0.36], [0.26, 0.24, 0.52], 0.6),
        "fog": {"start": 1100, "end": 2800},
        "sun": sun(14, 40, [1, 0.64, 0.38], 1.6),
        "ambient": {"sky": [0.66, 0.56, 0.72], "ground": [0.46, 0.32, 0.24], "intensity": 0.7},
        "terrain": DRY_TERRAIN,
        "props": merge(BASE_SCENERY_LOOK.props, {"lightIntensity": 1.15}),
        "clouds": clouds(0.14, 0.1, [1, 0.72, 0.56], [0.62, 0.4, 0.5]),
    },
)

# 1-5: dusk over the deep desert: the sun on the horizon, a violet sky, the town lights on.
LEVEL_1_5_LOOK = merge(
    LEVEL_1_4_LOOK,
    {
        "sky": sky([0.7, 0.48, 0.6], [0.96, 0.5, 0.42], [0.2, 0.16, 0.4], 0.6),
        "fog": {"start": 1000, "end": 2600},
        # Low but still lighting the ground: in a darker dusk the ship was lost over the towns.
        "sun": sun(8, 30, [1, 0.56, 0.4], 1.6),
        "ambient": {"sky": [0.66, 0.58, 0.82], "ground": [0.44, 0.34, 0.34], "intensity": 1},
        "props": merge(BASE_SCENERY_LOOK.props, {"lightIntensity": 1.3}),
        "glow": {"intensity": 0.4, "blurKernelSize": 16},
        "clouds": clouds(0.15, 0.1, [0.9, 0.56, 0.6], [0.46, 0.3, 0.46]),
    },
)
