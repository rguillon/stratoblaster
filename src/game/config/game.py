"""Game-specific identity values (ENG-143), ported from `config/game.ts`."""

from game.config.record import record

GAME_CONFIG = record(
    {
        "id": "stratoblaster",
        "title": "Stratoblaster",
        # Logical resolution (GD-02).
        "screen": {"width": 480, "height": 640},
    }
)
