"""Scales, styles and the drum, bass and tempo choices of the generated music (P12-R06, P12-R08),
ported from `audio/music-styles.ts`. A world's style says its key, tempo, chords and rhythm.
"""

# Scales, as semitones above their root.
SCALES = {
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "harmonicMinor": [0, 2, 3, 5, 7, 8, 11],
}


class StyleInstruments:
    """The instrument of each part (keys of `INSTRUMENTS`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        kick: str,
        snare: str,
        hat: str,
        perc: str,
        bass: str,
        pad: str,
        arp: str,
        lead: str,
    ) -> None:
        self.kick = kick
        self.snare = snare
        self.hat = hat
        # The off-beat open hat, or the tribal toms.
        self.perc = perc
        self.bass = bass
        self.pad = pad
        self.arp = arp
        self.lead = lead


class Octaves:
    """Octaves above the bass the pad, arpeggio and lead play at."""

    def __init__(self, pad: int, arp: int, lead: int) -> None:
        self.pad = pad
        self.arp = arp
        self.lead = lead


class MusicStyle:
    """A world's musical style (P12-R06): its levels share it but differ in key, tempo, chords,
    melody and rhythm. `drums` is one of four, `bass` one of three (see the TypeScript)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        tempo: list[int],
        boss_boost: list[int],
        scales: list[list[int]],
        boss_scale: list[int],
        roots: list[int],
        progressions: list[list[int]],
        instruments: StyleInstruments,
        drums: str,
        bass: str,
        arp_rate: int,
        energies: list[list[int]] | None,
        octaves: Octaves,
    ) -> None:
        # BPM range of its level tracks.
        self.tempo = tempo
        # Its boss track is this many BPM faster than its fastest level track.
        self.boss_boost = boss_boost
        self.scales = scales
        # The boss track's scale: darker and tenser (its chords: `BOSS_PROGRESSIONS`).
        self.boss_scale = boss_scale
        # MIDI pitches the keys' roots are picked from (bass register).
        self.roots = roots
        # Chord progressions: scale degrees (0 = the root's chord), one chord per two bars.
        self.progressions = progressions
        self.instruments = instruments
        # How the drums go: four, backbeat, tribal or heavy.
        self.drums = drums
        # How the bass goes: eighths, syncopated or rolling.
        self.bass = bass
        # Arpeggio notes per beat.
        self.arp_rate = arp_rate
        # Energy shapes its tracks pick from (0 a breakdown … 2 full), one value per 8-bar
        # section; the composer's own when None.
        self.energies = energies
        self.octaves = octaves


def _world(  # noqa: PLR0917 (positional: a table of styles)
    tempo: list[int],
    scales: list[list[int]],
    boss_scale: list[int],
    roots: list[int],
    progressions: list[list[int]],
    instruments: StyleInstruments,
    drums: str,
    bass: str,
    octaves: Octaves,
) -> MusicStyle:
    """A level style: boss boost 20–30 BPM, four-note arpeggios (the shared defaults)."""
    return MusicStyle(
        tempo,
        [20, 30],
        scales,
        boss_scale,
        roots,
        progressions,
        instruments,
        drums,
        bass,
        4,
        None,
        octaves,
    )


# The four worlds' styles (P12-R06, tempo ranges from the phase's tunables), all energetic
# darksynth (reviewer, 2026-10-26): minor and phrygian keys, heavy kicks, growling basses, dark
# pads. World 1 (desert and sea) the outrun drive (four on the floor, pumping bass, supersaw
# lead); World 2 (Frozen North) cold, with glassy bells on a driving beat; World 3 (Jungle) on
# toms and shakers; World 4 (Volcanic Lands) the heaviest.
WORLD_STYLES = {
    1: _world(
        [128, 140],
        [SCALES["minor"], SCALES["harmonicMinor"], SCALES["phrygian"]],
        SCALES["harmonicMinor"],
        [38, 40, 41, 43, 45],
        [[0, 4, 5, 3], [5, 3, 0, 4], [0, 6, 3, 0], [0, 5, 2, 6], [5, 4, 3, 4]],
        StyleInstruments(
            "kick-heavy",
            "snare-gated",
            "hat",
            "open-hat",
            "bass-heavy",
            "pad-dark",
            "arp-pluck",
            "lead-saw",
        ),
        "four",
        "eighths",
        Octaves(2, 3, 2),
    ),
    2: _world(
        [112, 124],
        [SCALES["minor"], SCALES["harmonicMinor"], SCALES["phrygian"]],
        SCALES["harmonicMinor"],
        [36, 38, 39, 41, 43],
        [[0, 5, 2, 6], [0, 3, 0, 4], [5, 6, 0, 0], [0, 2, 5, 4], [3, 0, 6, 4]],
        StyleInstruments(
            "kick-heavy",
            "snare-gated",
            "hat",
            "open-hat",
            "bass-dream",
            "pad-dream",
            "arp-glass",
            "bell",
        ),
        "backbeat",
        "eighths",
        Octaves(2, 3, 2),
    ),
    3: _world(
        [120, 132],
        [SCALES["phrygian"], SCALES["minor"], SCALES["harmonicMinor"]],
        SCALES["phrygian"],
        [38, 40, 41, 43, 45],
        [[0, 6, 5, 6], [0, 3, 6, 4], [0, 0, 5, 6], [3, 4, 0, 0], [0, 5, 3, 4]],
        StyleInstruments(
            "kick-heavy",
            "snare-gated",
            "shaker",
            "tom",
            "bass-pluck",
            "pad-dark",
            "arp-square",
            "lead-square",
        ),
        "tribal",
        "syncopated",
        Octaves(2, 2, 2),
    ),
    4: _world(
        [104, 116],
        [SCALES["phrygian"], SCALES["harmonicMinor"], SCALES["minor"]],
        SCALES["phrygian"],
        [33, 34, 36, 38, 40],
        [[0, 1, 0, 6], [0, 5, 1, 0], [0, 3, 1, 4], [0, 0, 5, 1], [5, 1, 0, 6]],
        StyleInstruments(
            "kick-heavy",
            "snare-gated",
            "hat",
            "open-hat",
            "bass-heavy",
            "pad-dark",
            "arp-pluck",
            "lead-brass",
        ),
        "heavy",
        "rolling",
        Octaves(2, 2, 2),
    ),
}

# The menu theme's style (P12-R08, synthwave reviews): mid-tempo darksynth in a minor key, with
# the classic i–VI–III–VII chords, a backbeat, a pumping octave bass, a plucked arpeggio and a
# supersaw lead; slower than every level.
MENU_STYLE = MusicStyle(
    [100, 100],
    [0, 0],
    [SCALES["minor"]],
    SCALES["minor"],
    [40],
    [[0, 5, 2, 6], [0, 5, 3, 4], [5, 3, 0, 6]],
    StyleInstruments(
        "kick-heavy",
        "snare-gated",
        "hat",
        "open-hat",
        "bass-heavy",
        "pad-dark",
        "arp-pluck",
        "lead-saw",
    ),
    "backbeat",
    "eighths",
    4,
    # Never a bare breakdown: the menus always have a full track (synthwave review).
    [[1, 2, 1, 2, 2]],
    Octaves(2, 3, 2),
)

# `music_loop_min`: a track lasts at least this long before it repeats.
MUSIC_LOOP_MIN_SECONDS = 60

# Bars of a section: tracks are made of whole sections.
SECTION_BARS = 8

# Beats in a bar (4/4).
BEATS_PER_BAR = 4

# The energy of a full section (0 a breakdown, 1 a build, 2 full).
FULL_ENERGY = 2

# Semitones in an octave.
OCTAVE = 12
