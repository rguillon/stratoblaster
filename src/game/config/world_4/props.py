# Copyright (c) 2026 Renaud Guillon
"""World 4's own rules (WLD-4-12, WLD-4-13).

Its buildings are the city's (`city_props.py`); the volcanic props of the first World 4 were removed
(reviewer, 2026-10-28).
"""

from game.config.record import merge
from game.config.world_3.props import WORLD_3_ROADS

# Roads of World 4: as in World 3 (no crossings, D-046, street grids as wide as the ground that
# shows), and in the city's street grids, wide straight boulevards of 3 lanes each way, 3 x 3 tiles
# (GFX-ROAD-17; a road of size 3, GFX-ROAD-09; reviewer, 2026-10-28; the 4-lane ones dropped,
# 3 x 3 is enough).
WORLD_4_ROADS = merge(WORLD_3_ROADS, {"boulevards": [{"lanes": 3, "width": 18, "share": 0.2}]})
