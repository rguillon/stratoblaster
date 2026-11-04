# Copyright (c) 2026 Renaud Guillon
"""Data the audio engine plays (AUD-ENGINE-13).

Synth voices, instruments, sound designs and tracks. A game describes its music and sounds with
these; the engine turns them into Web Audio nodes.

Optional fields are `None` when absent. Attribute `from` is `from_`.
"""

from core.math.bits import u32, ushr, xor

# `math.inf` does not compile in Transcrypt (see D-170): Infinity is built this way.
INFINITY = float("Infinity")


def is_finite(value: float) -> bool:
    """`Number.isFinite`: false for Infinity and NaN.

    NaN never equals itself, and Infinity minus Infinity is NaN.
    """
    return value - value == 0


def xorshift(seed: int) -> int:
    """One step of the xorshift32 the audio uses for its noise (`seed ^= seed << 13`, ...).

    On unsigned 32-bit values. The same bits, so the noise sounds the same.
    """
    seed = xor(seed, u32(seed * 8192))
    seed = xor(seed, ushr(seed, 17))
    return xor(seed, u32(seed * 32))


class Envelope:
    """Gain envelope of a voice, in seconds; `sustain` is a share (0..1) of the peak."""

    def __init__(self, attack: float, decay: float, sustain: float, release: float) -> None:
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release


class FilterSpec:
    """A filter on a voice. Its cut-off may start higher and glide down (a "pluck", a "zap")."""

    def __init__(
        self,
        filter_type: str,
        frequency: float,
        q: float | None = None,
        from_: float | None = None,
        sweep_seconds: float | None = None,
    ) -> None:
        # `type`: lowpass, highpass or bandpass.
        self.type = filter_type
        self.frequency = frequency
        self.q = q
        # Cut-off at the start, gliding to `frequency` over `sweep_seconds`.
        self.from_ = from_
        self.sweep_seconds = sweep_seconds


class ToneLayer:
    """One oscillator (or noise) of a voice.

    For an instrument, `pitch` is a ratio of the note's frequency (1 = the note, 0.5 an octave
    down); for a sound effect it is in Hz. Noise ignores it, unless it glides (it then sets the
    noise's playback rate).
    """

    def __init__(
        self,
        wave: str,
        gain: float,
        pitch: float,
        glide_to: float | None,
        glide_seconds: float | None,
        detune_cents: float | None,
        envelope: Envelope,
        filter_spec: FilterSpec | None,
        delay: float | None,
    ) -> None:
        self.wave = wave
        self.gain = gain
        self.pitch = pitch
        # Pitch reached after `glide_seconds` (same unit): sweeps, kicks, lasers.
        self.glide_to = glide_to
        self.glide_seconds = glide_seconds
        self.detune_cents = detune_cents
        self.envelope = envelope
        self.filter = filter_spec
        # Seconds after the voice starts (layers in sequence, e.g. a two-note chime).
        self.delay = delay


class Instrument:
    """A music instrument: the layers every note plays, and its level in the mix."""

    def __init__(
        self,
        layers: list[ToneLayer],
        gain: float,
        echo: float | None = None,
        reverb: float | None = None,
    ) -> None:
        self.layers = layers
        self.gain = gain
        # Share of it sent to the track's tempo-synced echo (0..1), and to the music reverb.
        self.echo = echo
        self.reverb = reverb


class MusicEffects:
    """The music's effects: a tempo-synced echo per track and a shared reverb."""

    def __init__(self, echo_beats: float, echo_feedback: float, reverb_seconds: float) -> None:
        # Echo delay, in beats (0.75: a dotted eighth).
        self.echo_beats = echo_beats
        # Share of each echo fed back into the next one.
        self.echo_feedback = echo_feedback
        # Reverb tail, in seconds.
        self.reverb_seconds = reverb_seconds


class SoundDesign:
    """A sound effect (AUD-SFX-01): a recorded sample and how it is mixed."""

    def __init__(
        self,
        name: str,
        sample: str,
        gain: float,
        priority: float,
        seconds: float,
        positional: bool | None = None,
        loop: bool | None = None,
    ) -> None:
        # Its name, as the e2e test API lists it (DEV-API-02).
        self.name = name
        # The sample it plays (`sfx/<sample>.ogg`, with an `.mp3` fallback), AUD-ENGINE-01.
        self.sample = sample
        # Level in the sound effect mix (the sample's peak is -1 dBFS).
        self.gain = gain
        # When the voices are all taken, a sound replaces one of lower or equal priority
        # (AUD-SFX-05).
        self.priority = priority
        # Length of the sample in seconds, for the voice limits (AUD-ENGINE-07).
        self.seconds = seconds
        # Panned left or right with its x on the playfield.
        self.positional = positional
        # Plays until stopped (a laser hum).
        self.loop = loop


class Note:
    """One note of a track: when, how long (in beats), which MIDI pitch, how hard, on what."""

    def __init__(
        self, beat: float, beats: float, pitch: float, velocity: float, instrument: str
    ) -> None:
        self.beat = beat
        self.beats = beats
        self.pitch = pitch
        # 0..1.
        self.velocity = velocity
        self.instrument = instrument


class Track:
    """A piece of generated music (AUD-MUSIC-01)."""

    def __init__(
        self, track_id: str, bpm: float, beats: float, notes: list[Note], loop: bool
    ) -> None:
        # Its id, as the e2e test API reports it, e.g. `level-2-3`, `boss-2`, `menu`.
        self.id = track_id
        self.bpm = bpm
        # Length in beats; a looping track starts again after it.
        self.beats = beats
        # Sorted by `beat`.
        self.notes = notes
        self.loop = loop


def beat_seconds(bpm: float) -> float:
    """Seconds of one beat at `bpm`."""
    return 60 / bpm


def track_seconds(track: Track) -> float:
    """Length of a track in seconds."""
    return track.beats * beat_seconds(track.bpm)


def midi_to_hz(pitch: float) -> float:
    """Frequency in Hz of a MIDI pitch (69 = A4 = 440 Hz)."""
    return 440 * 2 ** ((pitch - 69) / 12)


def sound_seconds(sound: SoundDesign) -> float:
    """Seconds a sound effect lasts (Infinity for a looping one)."""
    return INFINITY if sound.loop else sound.seconds
