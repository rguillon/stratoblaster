# Copyright (c) 2026 Renaud Guillon
"""The frost on the 2-1 bosses (MB-FLOE-BREAKER-05, FB-NARWHAL-05).

World 2 theme: dark metal with neon, plus frost, ice and snow. Logical pixels, nose +Z, Y up. Pale
vertex colours on the hull's top faces.
"""

from game.config.record import record

# Frost shades: snow caps and frosted panels.
FROST = record({
    # Snow and ice crust on top faces.
    "snow": [0.75, 0.82, 0.9],
    # A frosted panel: hull metal under a thin rime.
    "panel": [0.42, 0.48, 0.56],
})
