# Copyright (c) 2026 Renaud Guillon
"""Game-specific identity values (ENG-143)."""

from game.config.record import record

GAME_CONFIG = record({
    "id": "stratoblaster",
    # The game's name (UI-TITLE-02).
    "title": "Stratoblaster",
    # Logical resolution (GAME-SCREEN-01): landscape 16:9, a full HD screen at x1.5 (D-249).
    "screen": {"width": 1280, "height": 720},
})
