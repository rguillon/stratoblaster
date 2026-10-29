"""Composes a whole looping track (P12-R06..R08), ported from `audio/compose-track.ts`: a key, a
tempo and sections picked from the style by a seeded generator, each section's bars made of
drums, bass, pad, arpeggio and melody. Pure: the same request always gives the same notes.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.math.rng import Random  # noqa: E402
from game.view.audio.compose_melody import Motif  # noqa: E402

__pragma__("noskip")

from audio.audio_types import Note, Track  # noqa: E402
from core.math.bits import imul, u32, xor  # noqa: E402
from core.math.rng import create_rng, pick, random_in  # noqa: E402
from game.view.audio.compose_boss import (  # noqa: E402
    BOSS_PROGRESSIONS,
    boss_bass_bar,
    boss_drum_bar,
    riser_bar,
    stab_bar,
)
from game.view.audio.compose_melody import make_motif, motif_bars, scale_pitch  # noqa: E402
from game.view.audio.compose_parts import (  # noqa: E402
    BarContext,
    arp_bar,
    arp_shape,
    bass_bar,
    bass_steps,
    concat,
    drum_bar,
    pad_bar,
    sort_by_beat,
)
from game.view.audio.music_styles import (  # noqa: E402
    BEATS_PER_BAR,
    MUSIC_LOOP_MIN_SECONDS,
    SECTION_BARS,
    MusicStyle,
)


class TrackRequest:
    """What to compose: a level's track, its world's boss track, or the menu theme."""

    def __init__(self, track_id: str, style: MusicStyle, seed: int, boss: bool) -> None:
        # Its id, as the track reports it (`level-2-3`, `boss-2`, `menu`).
        self.id = track_id
        self.style = style
        # Seeds the choices: the same seed always gives the same track (P12-R06).
        self.seed = seed
        # Faster and more intense (P12-R07).
        self.boss = boss


def char_code_at(text: str, index: int) -> int:
    """`text.charCodeAt(index)`."""
    __pragma__("js", "{}", "return text.charCodeAt(index);")
    return 0


def seed_of(text: str) -> int:
    """A seed from a text (FNV-1a), so a level's id picks its music."""
    hash_ = 0x811C9DC5
    for i in range(len(text)):
        hash_ = xor(hash_, char_code_at(text, i))
        hash_ = imul(hash_, 0x01000193)
    return u32(hash_)


class Section:
    """One section of a track: its chords, its melody and how intense it is."""

    def __init__(self, progression: list[int], motif: Motif, energy: int) -> None:
        self.progression = progression
        self.motif = motif
        self.energy = energy


def tempo_of(request: TrackRequest, random: Random) -> int:
    """The tempo of a track: in its style's range, or 20–30 BPM above it for a boss (P12-R07)."""
    tempo = request.style.tempo
    if request.boss:
        return math.floor(
            tempo[1]
            + random_in(random, request.style.boss_boost[0], request.style.boss_boost[1])
            + 0.5
        )
    return math.floor(random_in(random, tempo[0], tempo[1] + 1) - 0.5 + 0.5)


def section_count(bpm: int) -> int:
    """Whole sections, enough for the track to last at least `music_loop_min` (P12-R06)."""
    bars = (MUSIC_LOOP_MIN_SECONDS * bpm) / 60 / BEATS_PER_BAR
    return math.ceil(bars / SECTION_BARS)


# The bar of a section whose melody is shifted up a step (a variation).
SHIFT_BAR = 6

# A level's energy shapes: it drives from the start and swells to full sections (no bare
# breakdown: energetic synthwave, reviewer 2026-10-26).
LEVEL_ENERGIES = [
    [1, 2, 2, 1, 2],
    [2, 1, 2, 1, 2],
    [1, 2, 1, 2, 2],
]


def energies(request: TrackRequest, count: int, random: Random) -> list[int]:
    """The energy of each section: the level's shape; a boss fight is intense all along, with one
    breath."""
    if request.boss:
        return [1 if i == count - 2 else 2 for i in range(count)]
    shape = pick(
        random, request.style.energies if request.style.energies is not None else LEVEL_ENERGIES
    )
    return [shape[i % len(shape)] for i in range(count)]


def sections(request: TrackRequest, count: int, random: Random) -> list[Section]:
    """Two or three different sections (verse, chorus, bridge), repeated in the track's order."""
    progressions = BOSS_PROGRESSIONS if request.boss else request.style.progressions
    themes: list[tuple[list[int], Motif]] = []
    for i in range(min(3, len(progressions))):
        index = (math.floor(random() * len(progressions)) + i) % len(progressions)
        themes.append((progressions[index], make_motif(random)))
    order = pick(random, [[0, 1, 0, 2, 1], [0, 0, 1, 2, 1], [0, 1, 2, 1, 0]])
    result: list[Section] = []
    for i, energy in enumerate(energies(request, count, random)):
        theme_index = order[i % len(order)] % len(themes)
        progression, motif = themes[theme_index]
        result.append(Section(progression, motif, energy))
    return result


def chord(scale: list[int], degree: int) -> list[int]:
    """The chord of scale step `degree`: a triad in the bass register."""
    return [scale_pitch(scale, degree + third) for third in [0, 2, 4]]


def rhythm_bar(
    request: TrackRequest, bar: BarContext, random: Random, bass: list[int]
) -> list[Note]:
    """The drums and bass of a bar: the style's, or the boss's driving ones with chord stabs."""
    style = request.style
    if request.boss:
        return concat([boss_drum_bar(style, bar), boss_bass_bar(style, bar), stab_bar(bar)])
    return concat([drum_bar(style, bar, random), bass_bar(style, bar, bass)])


class TrackParts:
    """The choices a track's sections share: its scale, the random generator, bass and arp."""

    def __init__(self, scale: list[int], random: Random, bass: list[int], arp: list[int]) -> None:
        self.scale = scale
        self.random = random
        self.bass = bass
        self.arp = arp


def section_notes(
    request: TrackRequest,
    section: Section,
    start: int,
    parts: TrackParts,
) -> list[Note]:
    """The notes of one section, bar by bar."""
    style = request.style
    scale = parts.scale
    notes: list[Note] = []
    for b in range(SECTION_BARS):
        degree = section.progression[math.floor(b / 2) % len(section.progression)]
        bar = BarContext(
            (start + b) * BEATS_PER_BAR,
            chord(scale, degree),
            scale,
            section.energy,
            b == SECTION_BARS - 1,
        )
        notes.extend(rhythm_bar(request, bar, parts.random, parts.bass))
        notes.extend(pad_bar(style, bar))
        notes.extend(arp_bar(style, bar, parts.arp))
        notes.extend(riser_bar(bar))
        if b % 2 == 0:
            notes.extend(motif_bars(style, section.motif, bar, degree, 1 if b == SHIFT_BAR else 0))
    return notes


def compose_track(request: TrackRequest) -> Track:
    """Composes a looping track (P12-R06..R08): a key, a tempo and sections picked from the style
    by a seeded generator, each section's bars made of drums, bass, pad, arpeggio and melody.
    Pure: the same request always gives the same notes."""
    random = create_rng(request.seed)
    style = request.style
    bpm = tempo_of(request, random)
    steps = style.boss_scale if request.boss else pick(random, style.scales)
    root = pick(random, style.roots)
    scale = [root + s for s in steps]
    parts = TrackParts(scale, random, bass_steps(style, random), arp_shape(random))
    listed = sections(request, section_count(bpm), random)
    notes: list[Note] = []
    for i, section in enumerate(listed):
        notes.extend(section_notes(request, section, i * SECTION_BARS, parts))
    notes = sort_by_beat(notes)
    return Track(
        request.id,
        bpm,
        len(listed) * SECTION_BARS * BEATS_PER_BAR,
        notes,
        True,
    )
