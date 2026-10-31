"""Trees of the green land (D-212) and dead trees of the desert (D-214): their ids, how they are
placed, how their imposters are baked and how they gather in woods."""

from game.config.record import record

TREE_IDS = record(
    {
        "pine": "tree-pine",
        "oak": "tree-oak",
        "poplar": "tree-poplar",
        "birch": "tree-birch",
        "copper": "tree-copper",
        "bush": "tree-bush",
        # D-214: the dead trees of the desert.
        "deadOak": "tree-dead-oak",
        "deadPine": "tree-dead-pine",
        "snag": "tree-snag",
        "deadBush": "tree-dead-bush",
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
    # D-214: the dead trees, where a section lists them (`DEAD_TREES`).
    {"id": TREE_IDS.deadOak, "weight": 3, "footprint": 4, "scale": [1.6, 2.4]},
    {"id": TREE_IDS.deadPine, "weight": 1.5, "footprint": 2.5, "scale": [1.4, 2]},
    {"id": TREE_IDS.snag, "weight": 1.5, "footprint": 2.5, "scale": [1.4, 2]},
    {"id": TREE_IDS.deadBush, "weight": 3, "footprint": 2.5, "scale": [1.3, 2]},
]

# D-214: the trees a section lists: the living ones (the green land) and the dead ones (the
# desert).
LIVE_TREES = [
    TREE_IDS.oak,
    TREE_IDS.pine,
    TREE_IDS.birch,
    TREE_IDS.poplar,
    TREE_IDS.bush,
    TREE_IDS.copper,
]
DEAD_TREES = [TREE_IDS.deadOak, TREE_IDS.deadPine, TREE_IDS.snag, TREE_IDS.deadBush]

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

# D-214: the dead woods of the desert: sparse (about one tree in seven of a green wood's), in
# patches over about a fifth of the ground (the woods' noise over about 0.6), and dead trees
# standing alone between them, one or two per 50-unit cell.
DESERT_WOODS = record({"cover": 0.55, "keep": 0.15, "scatter": 0.01})
# D-214: on bare ground (a dry lake bed), no woods, only a dead tree here and there.
LONE_DEAD_TREES = record({"cover": 0, "keep": 0, "scatter": 0.004})
