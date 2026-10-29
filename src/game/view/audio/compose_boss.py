"""The boss tracks' parts (P12-R07, GD-70 "a more stressful music"), ported from
`audio/compose-boss.ts`: a driving drum machine with pushed kicks and snare rolls, a rolling octave
bass, chord stabs on a 3-3-2 rhythm and a noise riser into every section.
"""

from audio.audio_types import Note  # noqa: E402
from game.view.audio.compose_parts import BarContext, note  # noqa: E402
from game.view.audio.instruments import DRUM_PITCH  # noqa: E402
from game.view.audio.music_styles import (  # noqa: E402
    BEATS_PER_BAR,
    FULL_ENERGY,
    OCTAVE,
    MusicStyle,
)

# Every other bar of four ends on a short roll: this is its position in each four bars.
ROLL_BAR = 3

# The chord's fifth is its third element (a triad).
FIFTH_INDEX = 2

STEPS = 16
STEP = BEATS_PER_BAR / STEPS

# Boss chord progressions (scale degrees, one chord per two bars): tense, around the root, with
# the flat second (phrygian) or the diminished second and major fifth (harmonic minor).
BOSS_PROGRESSIONS = [
    [0, 1, 0, 1],
    [0, 5, 1, 4],
    [0, 0, 5, 4],
    [0, 6, 5, 1],
]

# Four on the floor, pushed by off-beat sixteenths.
KICKS = [0, 4, 7, 8, 12, 14]
SNARES = [4, 12]
# The off-beat eighths: open hats, or toms (World 3).
OFF_BEATS = [2, 6, 10, 14]


def snare_roll(snare: str, bar: BarContext, count: int) -> list[Note]:
    """A snare roll over the last `count` sixteenths of the bar, growing louder."""
    return [
        note(
            snare, bar.beat + (STEPS - count + i) * STEP, STEP, DRUM_PITCH, 0.35 + (0.6 * i) / count
        )
        for i in range(count)
    ]


def roll_length(bar: BarContext) -> int:
    """Every other bar of four ends on a short roll; the section's last bar rolls for half a bar."""
    if bar.fill:
        return 8
    return 4 if (bar.beat / BEATS_PER_BAR) % 4 == ROLL_BAR else 0


def boss_drum_bar(style: MusicStyle, bar: BarContext) -> list[Note]:
    """One bar of boss drums: sixteenth hats, pushed kicks, the backbeat and snare rolls."""
    kick = style.instruments.kick
    snare = style.instruments.snare
    hat = style.instruments.hat
    perc = style.instruments.perc
    roll = roll_length(bar)
    notes = [note(kick, bar.beat + i * STEP, STEP, DRUM_PITCH, 1) for i in KICKS]
    for i in SNARES:
        if i < STEPS - roll:
            notes.append(note(snare, bar.beat + i * STEP, 0.5, DRUM_PITCH, 0.95))
    for i in range(STEPS):
        if i not in OFF_BEATS:
            notes.append(
                note(hat, bar.beat + i * STEP, STEP, DRUM_PITCH, 0.85 if i % 4 == 0 else 0.55)
            )
    for i in OFF_BEATS:
        notes.append(note(perc, bar.beat + i * STEP, STEP * 2, DRUM_PITCH, 0.7))
    notes.extend(snare_roll(snare, bar, roll))
    return notes


def boss_bass_bar(style: MusicStyle, bar: BarContext) -> list[Note]:
    """One bar of boss bass: rolling sixteenths jumping between the root and its octave."""
    root = bar.chord[0] if len(bar.chord) > 0 else 36
    return [
        note(
            style.instruments.bass,
            bar.beat + s * STEP,
            STEP * 0.85,
            root + OCTAVE if s % 2 else root,
            0.75 if s % 4 else 1,
        )
        for s in range(STEPS)
    ]


# The stabs' steps: 3-3-2, twice a bar.
STAB_STEPS = [0, 3, 6, 8, 11, 14]


def stab_bar(bar: BarContext) -> list[Note]:
    """Chord stabs (root, fifth, octave, an octave over the bass) on a restless 3-3-2 rhythm."""
    if bar.energy < FULL_ENERGY:
        return []
    root = bar.chord[0] if len(bar.chord) > 0 else 36
    fifth = bar.chord[FIFTH_INDEX] if len(bar.chord) > FIFTH_INDEX else root + 7
    voicing = [root + OCTAVE, fifth + OCTAVE, root + 2 * OCTAVE]
    notes: list[Note] = []
    for s in STAB_STEPS:
        for pitch in voicing:
            notes.append(
                note("stab", bar.beat + s * STEP, STEP * 1.5, pitch, 0.85 if s % 8 == 0 else 0.65)
            )
    return notes


def riser_bar(bar: BarContext) -> list[Note]:
    """A rising noise sweep over a section's last bar, into the next section."""
    return [note("riser", bar.beat, BEATS_PER_BAR, DRUM_PITCH, 0.8)] if bar.fill else []
