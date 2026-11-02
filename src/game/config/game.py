# Copyright (c) 2026 Renaud Guillon
"""Game-specific identity values (ENG-143)."""

from game.config.record import record

GAME_CONFIG = record({
    "id": "stratoblaster",
    # The game's name (UI-TITLE-02).
    "title": "Stratoblaster",
    # Logical resolution (GAME-SCREEN-01): a 16:9 landscape screen (D-249). The height is the one
    # the game was tuned at, so every vertical size and speed keeps its value; the width is the
    # one that gives 16:9 at that height (640 x 16 / 9 = 1137.8), so a 1920 x 1080 screen is
    # filled without bars.
    "screen": {"width": 1138, "height": 640},
})
