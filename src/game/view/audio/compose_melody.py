"""The melody of generated music (P12-R06): a two-bar motif
(a rhythm, and a walk on the scale that lands on chord tones), repeated and varied over a section.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.math.rng import Random  # noqa: E402

__pragma__("noskip")

from audio.audio_types import Note  # noqa: E402
from core.math.rng import pick  # noqa: E402
from game.view.audio.compose_parts import BarContext, note  # noqa: E402
from game.view.audio.music_styles import BEATS_PER_BAR, MusicStyle  # noqa: E402


class MotifNote:
    """One note of a motif: when (eighths into its two bars), how long, and a scale step."""

    def __init__(self, step: int, length: int, degree: int) -> None:
        self.step = step
        self.length_ = length
        # Scale steps above the chord's root.
        self.degree = degree


# A two-bar melodic idea, repeated and varied over a section (a type: typing is skipped).
__pragma__("skip")
Motif = list[MotifNote]
__pragma__("noskip")

# Rhythms of a two-bar motif: [eighth, length in eighths] pairs.
RHYTHMS = [
    [[0, 2], [2, 2], [4, 1], [5, 3], [8, 2], [10, 2], [12, 4]],
    [[0, 3], [3, 1], [4, 2], [6, 2], [8, 3], [11, 1], [12, 2], [14, 2]],
    [[0, 1], [1, 1], [2, 2], [4, 4], [8, 1], [9, 1], [10, 2], [12, 4]],
    [[0, 4], [4, 2], [6, 2], [8, 6], [14, 2]],
    [[1, 1], [2, 2], [4, 1], [5, 1], [6, 2], [9, 1], [10, 2], [12, 3]],
    [[0, 2], [3, 2], [6, 2], [8, 2], [11, 2], [14, 2]],
]

# Chord tones (scale steps above the chord's root) a motif lands on.
CHORD_STEPS = [0, 2, 4, 7]


def make_motif(random: Random) -> Motif:
    """A motif for a section (P12-R06): one of the rhythms, its pitches a walk on the scale that
    starts and ends on chord tones, so every level gets its own melody."""
    rhythm = pick(random, RHYTHMS)
    degree = pick(random, CHORD_STEPS)
    motif: Motif = []
    for i, (step, length) in enumerate(rhythm):
        if i > 0:
            strong = step % 4 == 0
            if strong:
                degree = nearest_chord_step(degree + pick(random, [-2, -1, 1, 2]))
            else:
                degree = degree + pick(random, [-2, -1, 1, 1, 2])
            degree = max(-3, min(9, degree))
        motif.append(MotifNote(step, length, degree))
    return motif


def nearest_chord_step(degree: int) -> int:
    """The chord step nearest to `degree` (ties keep the earlier candidate)."""
    best = 0
    candidates = [-7, -5, -3]
    candidates.extend(CHORD_STEPS)
    candidates.append(9)
    for step in candidates:
        if abs(step - degree) < abs(best - degree):
            best = step
    return best


def motif_bars(
    style: MusicStyle,
    motif: Motif,
    bar: BarContext,
    chord_degree: int,
    shift: int,
) -> list[Note]:
    """Plays two bars of a motif from `bar`, on the chord of the bar (its scale step
    `chord_degree`), `shift` scale steps up for a variation."""
    if bar.energy == 0:
        return []
    eighth = BEATS_PER_BAR / 8
    octave = 12 * style.octaves.lead
    notes: list[Note] = []
    for m in motif:
        index = chord_degree + m.degree + shift
        pitch = scale_pitch(bar.scale, index) + octave
        notes.append(
            note(
                style.instruments.lead,
                bar.beat + m.step * eighth,
                m.length_ * eighth * 0.92,
                pitch,
                0.8,
            )
        )
    return notes


def scale_pitch(scale: list[int], index: int) -> int:
    """The pitch of scale step `index` (any integer: it wraps by octaves)."""
    size = len(scale)
    if size == 0:
        return 0
    octave = index // size
    return scale[index - octave * size] + 12 * octave
