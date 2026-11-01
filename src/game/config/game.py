"""Game-specific identity values (ENG-143)"""

from game.config.record import record

GAME_CONFIG = record(
    {
        "id": "stratoblaster",
        # The game's name (UI-TITLE-02).
        "title": "Stratoblaster",
        # Logical resolution (GAME-SCREEN-01).
        "screen": {"width": 480, "height": 640},
    }
)
