"""Trees of the green land (D-212): their ids, how they are placed, how their imposters are baked
and how they gather in woods."""

from game.config.record import record

TREE_IDS = record(
    {
        "pine": "tree-pine",
        "oak": "tree-oak",
        "poplar": "tree-poplar",
        "birch": "tree-birch",
        "copper": "tree-copper",
        "bush": "tree-bush",
    }
)

# The trees as the placement picks them: weight, radius of ground (at their largest), scales.
TREE_KINDS = [
    {"id": TREE_IDS.oak, "weight": 4, "footprint": 4.5, "scale": [1.4, 2.1]},
    {"id": TREE_IDS.pine, "weight": 3, "footprint": 4, "scale": [1.4, 2.1]},
    {"id": TREE_IDS.birch, "weight": 2, "footprint": 4, "scale": [1.4, 2]},
    {"id": TREE_IDS.poplar, "weight": 1.5, "footprint": 2.5, "scale": [1.4, 1.9]},
    {"id": TREE_IDS.bush, "weight": 1.5, "footprint": 2.5, "scale": [1.3, 2]},
    # A few copper beeches, so the woods are not all one green.
    {"id": TREE_IDS.copper, "weight": 0.4, "footprint": 4.5, "scale": [1.4, 2]},
]

# D-212: the trees drawn as imposters (see `render/scenery/imposters.py`): 4 headings (a tree
# turned is another tree), 256-pixel frames (their leaves are small) 13 model units across, centred
# 5 up (the middle of a tree seen from the playfield camera), shaded hard (soft, they looked like
# plastic).
TREE_IMPOSTERS = record(
    {"headings": 4, "framePx": 256, "frameSize": 13, "centre": 5, "ambient": 0.6}
)

# D-212: woods almost everywhere on the grass (the noise is over 0.27 on about 93 % of the ground),
# clearings about 300 units apart, ragged edges.
FORESTS = record({"frequency": 1 / 300, "threshold": 0.27, "edge": 0.06})

# D-212: trees tried per cell of 50 units, in a wood: about one per 35 square units (fewer, bigger
# trees: each costs its checks as the ground scrolls in).
TREES_PER_CELL = 70
