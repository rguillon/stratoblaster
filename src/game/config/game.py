"""Game-specific identity values (ENG-143)"""

from game.config.record import record

GAME_CONFIG = record(
    {
        "id": "stratoblaster",
        "title": "Stratoblaster",
        # Logical resolution (GD-02).
        "screen": {"width": 480, "height": 640},
    }
)
