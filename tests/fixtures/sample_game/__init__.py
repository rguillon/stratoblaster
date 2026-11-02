# Copyright (c) 2026 Renaud Guillon
"""A minimal sample game for the engine's unit tests (ENG-145).

`SAMPLE_GAME` is a `GameDefinition`

of its own, with one enemy kind, one weapon and one tiny level; its look values are in `look`.
The engine tests read a game's numbers from here, never from `src/game/`.
"""

from fixtures.sample_game.game import SAMPLE_GAME, make_sample_game
from fixtures.sample_game.look import PLAYFIELD_CAMERA, WINDOW_ATLAS
from fixtures.sample_game.record import record

__all__ = ["PLAYFIELD_CAMERA", "SAMPLE_GAME", "WINDOW_ATLAS", "make_sample_game", "record"]
