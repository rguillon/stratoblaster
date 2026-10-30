"""The game's short fanfares (P12-R07): "level complete",
"game over" and "checkpoint reached", each a track played once.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")

__pragma__("noskip")

from audio.audio_types import Note, Track  # noqa: E402
from game.view.audio.compose_parts import concat, note, sort_by_beat  # noqa: E402
from game.view.audio.instruments import DRUM_PITCH  # noqa: E402


def line(instrument: str, notes: list[list[float]], velocity: float) -> list[Note]:
    """Notes of `instrument` from [beat, beats, pitch] triples, at one velocity."""
    return [note(instrument, beat, beats, pitch, velocity) for beat, beats, pitch in notes]


def jingle(track_id: str, bpm: float, beats: float, notes: list[Note]) -> Track:
    """A short fanfare played once (P12-R07): its notes sorted by beat, not looping."""
    return Track(track_id, bpm, beats, sort_by_beat(notes[:]), False)


# "Level complete": a rising major synthwave fanfare, a supersaw over a tom fill.
COMPLETE = jingle(
    "jingle-complete",
    132,
    8,
    concat(
        [
            line(
                "lead-saw",
                [
                    [0, 0.5, 72],
                    [0.5, 0.5, 76],
                    [1, 0.5, 79],
                    [1.5, 1.5, 84],
                    [3.5, 0.5, 83],
                    [4, 3, 84],
                ],
                0.9,
            ),
            line(
                "pad-warm",
                [
                    [0, 3.5, 60],
                    [0, 3.5, 64],
                    [0, 3.5, 67],
                    [3.5, 4, 65],
                    [3.5, 4, 69],
                    [3.5, 4, 72],
                ],
                0.8,
            ),
            line("bass-saw", [[0, 3, 48], [3.5, 4, 53]], 0.9),
            line(
                "tom",
                [
                    [3, 0.25, DRUM_PITCH + 12],
                    [3.25, 0.25, DRUM_PITCH + 7],
                    [3.5, 0.25, DRUM_PITCH + 3],
                ],
                0.8,
            ),
            line("snare-gated", [[4, 0.5, DRUM_PITCH]], 0.9),
            line("kick", [[4, 0.5, DRUM_PITCH]], 1),
        ]
    ),
)

# "Game over": a slow, falling darksynth line on analog brass.
OVER = jingle(
    "jingle-over",
    84,
    8,
    concat(
        [
            line("lead-brass", [[0, 1, 67], [1, 1, 66], [2, 1, 65], [3, 4, 64]], 0.85),
            line(
                "pad-dark",
                [
                    [0, 3, 52],
                    [0, 3, 55],
                    [0, 3, 60],
                    [3, 4.5, 48],
                    [3, 4.5, 51],
                    [3, 4.5, 55],
                ],
                0.8,
            ),
            line("bass-heavy", [[0, 7, 36]], 0.8),
        ]
    ),
)

# "Checkpoint reached": a short bright FM bell chime over the music, with its echo.
CHECKPOINT = jingle(
    "jingle-checkpoint",
    120,
    3,
    line("bell", [[0, 0.5, 79], [0.5, 0.5, 84], [1, 1.5, 88]], 1),
)

# The game's three jingles.
JINGLES = {
    "complete": COMPLETE,
    "over": OVER,
    "checkpoint": CHECKPOINT,
}
