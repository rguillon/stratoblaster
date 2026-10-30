"""The parts of a bar of generated music (P12-R06): drums,
bass, pad and arpeggio, each a list of notes for one bar.

`sort_by_beat` replaces `Array.prototype.sort` with a comparator: Transcrypt's sort
takes none and is not stable, and the order of notes at one beat must stay as composed.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.math.rng import Random  # noqa: E402

__pragma__("noskip")

from audio.audio_types import Note  # noqa: E402
from core.math.rng import pick  # noqa: E402
from game.view.audio.instruments import DRUM_PITCH  # noqa: E402
from game.view.audio.music_styles import (  # noqa: E402
    BEATS_PER_BAR,
    FULL_ENERGY,
    OCTAVE,
    MusicStyle,
)


class BarContext:
    """What a bar is made from: its chord (scale-tone pitches) and how intense the section is."""

    def __init__(
        self, beat: float, chord: list[int], scale: list[int], energy: int, fill: bool
    ) -> None:
        # First beat of the bar.
        self.beat = beat
        # The chord's pitches in the bass register, root first.
        self.chord = chord
        # The scale's pitches over the lead's range, low to high.
        self.scale = scale
        # 0 calm (an intro, a break) … 2 full (a boss fight).
        self.energy = energy
        # Last bar of a section: the drums fill.
        self.fill = fill


def note(instrument: str, beat: float, beats: float, pitch: float, velocity: float) -> Note:
    """A note of `instrument` at `beat` (beats), `beats` long."""
    return Note(beat, beats, pitch, velocity, instrument)


def concat(groups: list[list[Note]]) -> list[Note]:
    """The notes of several lists, one after the other (`[...a, ...b]`: Transcrypt's `+` on lists
    concatenates strings)."""
    notes: list[Note] = []
    for group in groups:
        notes.extend(group)
    return notes


def sort_by_beat(notes: list[Note]) -> list[Note]:
    """The notes sorted by `beat`, stable (equal beats keep their order): a bottom-up merge sort."""
    items = notes[:]
    width = 1
    size = len(items)
    while width < size:
        merged: list[Note] = []
        start = 0
        while start < size:
            middle = min(start + width, size)
            end = min(start + 2 * width, size)
            left = start
            right = middle
            while left < middle and right < end:
                # Take from the right only when strictly earlier: that keeps the sort stable.
                if items[right].beat < items[left].beat:
                    merged.append(items[right])
                    right += 1
                else:
                    merged.append(items[left])
                    left += 1
            while left < middle:
                merged.append(items[left])
                left += 1
            while right < end:
                merged.append(items[right])
                right += 1
            start += 2 * width
        items = merged
        width *= 2
    return items


DRUM_STEPS = 16


# A drum machine pattern: the steps (of 16 per bar) each drum plays at.
class DrumPattern:
    """A drum machine pattern."""

    def __init__(self, kick: list[int], snare: list[int], hat_every: int, open_: list[int]) -> None:
        self.kick = kick
        self.snare = snare
        # Closed hats every this many steps (16ths: 1, eighths: 2), every step when intense.
        self.hat_every = hat_every
        # Open hats (on the off-beats) or, with tribal drums, the extra percussion.
        self.open = open_


# Synthwave drum patterns by feel (synthwave reviews): four on the floor with off-beat open hats
# (outrun), a driving backbeat (dreamwave, the menus), tom-heavy tribal, heavy darksynth.
PATTERNS = {
    "four": DrumPattern([0, 4, 8, 12], [4, 12], 2, [2, 6, 10, 14]),
    "backbeat": DrumPattern([0, 6, 8, 10], [4, 12], 2, [2, 6, 10, 14]),
    "tribal": DrumPattern([0, 6, 10], [4, 12], 1, [3, 7, 11, 15]),
    "heavy": DrumPattern([0, 3, 8, 10, 11], [4, 12], 2, [6, 14]),
}

# Gated snares ring for an eighth, so their gate shows.
SNARE_BEATS = 0.5


def drum_bar(style: MusicStyle, bar: BarContext, random: Random) -> list[Note]:
    """One bar of drums (P12-R06): the style's pattern, hats by energy, a tom fill at section
    ends."""
    kick = style.instruments.kick
    snare = style.instruments.snare
    hat = style.instruments.hat
    perc = style.instruments.perc
    pattern = PATTERNS[style.drums]
    step = BEATS_PER_BAR / DRUM_STEPS
    notes = [note(kick, bar.beat + i * step, step, DRUM_PITCH, 1) for i in pattern.kick]
    if bar.energy == 0:
        return notes
    for i in pattern.snare:
        notes.append(note(snare, bar.beat + i * step, SNARE_BEATS, DRUM_PITCH, 0.9))
    every = 1 if bar.energy >= FULL_ENERGY else pattern.hat_every
    for i in range(0, DRUM_STEPS, every):
        if i in pattern.open and perc != hat:
            continue
        velocity = 0.85 if i % 4 == 0 else 0.5 + random() * 0.2
        notes.append(note(hat, bar.beat + i * step, step, DRUM_PITCH, velocity))
    for i in pattern.open:
        notes.append(note(perc, bar.beat + i * step, step * 2, DRUM_PITCH, 0.6))
    if bar.fill:
        notes.extend(drum_fill(bar, random))
    return notes


# Pitches of a tom fill, high to low (semitones above the drum pitch).
TOM_FILL = [14, 10, 7, 3, 0, -4]


def drum_fill(bar: BarContext, random: Random) -> list[Note]:
    """The end of a section: a descending synth-tom fill over the last beat or two."""
    step = BEATS_PER_BAR / DRUM_STEPS
    count = 6 if bar.energy >= FULL_ENERGY else pick(random, [3, 4])
    fill: list[Note] = []
    for i, pitch in enumerate(TOM_FILL[len(TOM_FILL) - count :]):
        at = bar.beat + (DRUM_STEPS - count + i) * step
        fill.append(note("tom", at, step * 2, DRUM_PITCH + pitch, 0.75))
    return fill


# The chord's fifth is its third element (a triad).
FIFTH_INDEX = 2

# The bass pumps an octave on this step of each four (outrun eighths).
PUMP_STEP = 2

# Bass sixteenths of the passing fifth: 12 and 13 of the bar.
BASS_FIFTH_LOW = 12
BASS_FIFTH_HIGH = 14

# Steps (of 16 per bar) the bass plays at, by feel; a held note lasts until the next one.
BASS_STEPS = {
    "eighths": [[0, 2, 4, 6, 8, 10, 12, 14]],
    "syncopated": [[0, 6, 8, 12], [0, 4, 6, 12], [0, 6, 10, 12]],
    "rolling": [list(range(16))],
}

# Bass steps when intense: rolling sixteenths.
BUSY_BASS = list(range(16))


def bass_bar(style: MusicStyle, bar: BarContext, steps: list[int]) -> list[Note]:
    """One bar of bass: the chord's root, the octave pumping on the off-beat eighths (outrun), a
    passing fifth near the bar's end."""
    root = bar.chord[0] if len(bar.chord) > 0 else 36
    fifth = bar.chord[FIFTH_INDEX] if len(bar.chord) > FIFTH_INDEX else root + 7
    sixteenth = BEATS_PER_BAR / DRUM_STEPS
    hits = BUSY_BASS if bar.energy >= FULL_ENERGY else steps
    notes: list[Note] = []
    for i, s in enumerate(hits):
        following = hits[i + 1] if i + 1 < len(hits) else DRUM_STEPS
        pitch = fifth if (s >= BASS_FIFTH_LOW and s < BASS_FIFTH_HIGH) else root
        if style.bass == "eighths" and s % 4 == PUMP_STEP:
            pitch += OCTAVE
        accent = 1 if s % 4 == 0 else 0.75
        notes.append(
            note(
                style.instruments.bass,
                bar.beat + s * sixteenth,
                (following - s) * sixteenth * 0.9,
                pitch,
                accent,
            )
        )
    return notes


def bass_steps(style: MusicStyle, random: Random) -> list[int]:
    """The bass steps of a track: one rhythm of the style, picked for the level."""
    return pick(random, BASS_STEPS[style.bass])


def pad_bar(style: MusicStyle, bar: BarContext) -> list[Note]:
    """The pad holds the chord over the bar, voiced up `octaves`."""
    shift = 12 * style.octaves.pad
    return [note(style.instruments.pad, bar.beat, BEATS_PER_BAR, p + shift, 0.7) for p in bar.chord]


# Arpeggio shapes: indices into the chord tones, over two octaves.
ARP_SHAPES = [
    [0, 1, 2, 3],
    [0, 2, 1, 3],
    [3, 2, 1, 0],
    [0, 1, 2, 1],
    [0, 2, 3, 5],
    [0, 3, 1, 4],
]


def arp_shape(random: Random) -> list[int]:
    """The arpeggio shape of a track."""
    return pick(random, ARP_SHAPES)


def arp_bar(style: MusicStyle, bar: BarContext, shape: list[int]) -> list[Note]:
    """One bar of arpeggio over the chord, `rate` notes per beat (sixteenths when intense); it
    goes on alone in the breaks, as synthwave breakdowns do."""
    rate = max(4, style.arp_rate) if bar.energy >= FULL_ENERGY else style.arp_rate
    shift = OCTAVE * style.octaves.arp
    tones = bar.chord[:]
    tones.extend([p + OCTAVE for p in bar.chord])
    length = 1 / rate
    notes: list[Note] = []
    for i in range(BEATS_PER_BAR * rate):
        tone = tones[shape[i % len(shape)] % len(tones)]
        velocity = 0.9 if i % rate == 0 else 0.65
        notes.append(
            note(style.instruments.arp, bar.beat + i * length, length * 0.9, tone + shift, velocity)
        )
    return notes
