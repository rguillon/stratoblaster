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
    {"id": TREE_IDS.oak, "weight": 4, "footprint": 3.5, "scale": [1.1, 1.7]},
    {"id": TREE_IDS.pine, "weight": 3, "footprint": 3, "scale": [1.1, 1.7]},
    {"id": TREE_IDS.birch, "weight": 2, "footprint": 3, "scale": [1.1, 1.6]},
    {"id": TREE_IDS.poplar, "weight": 1.5, "footprint": 2, "scale": [1.1, 1.5]},
    {"id": TREE_IDS.bush, "weight": 1.5, "footprint": 2, "scale": [1, 1.6]},
    # A few copper beeches, so the woods are not all one green.
    {"id": TREE_IDS.copper, "weight": 0.4, "footprint": 3.5, "scale": [1.1, 1.6]},
]

# D-212: the trees drawn as imposters (see `render/scenery/imposters.py`): 4 headings (a tree
# turned is another tree), 128-pixel frames 13 model units across, centred 5 up (the middle of a
# tree seen from the playfield camera).
TREE_IMPOSTERS = record({"headings": 4, "framePx": 128, "frameSize": 13, "centre": 5})

# D-212: the woods, about 300 units apart, over 0.45 of the noise at a section's full tree density,
# with ragged edges.
FORESTS = record({"frequency": 1 / 300, "threshold": 0.45, "edge": 0.08})

# D-212: trees tried per cell of 50 units, in a wood: about one per 20 square units.
TREES_PER_CELL = 120
