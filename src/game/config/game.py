# Copyright (c) 2026 Renaud Guillon
"""Game-specific identity values (ENG-143)."""

from game.config.record import record

GAME_CONFIG = record({
    "id": "stratoblaster",
    # The game's name (UI-TITLE-02).
    "title": "Stratoblaster",
    # Logical resolution (GAME-SCREEN-01): landscape 16:9, a full HD screen at x1.5 (D-249).
    "screen": {"width": 1280, "height": 720},
    # The playfield window (D-252, D-263): the level is drawn and played in a 540 x 720 (3:4)
    # window in the middle of the screen, between the HUD's 370 px side columns (UI-HUD-01);
    # nothing of the level is drawn outside it.
    "playfield": {"width": 540, "height": 720, "left": 370},
})
