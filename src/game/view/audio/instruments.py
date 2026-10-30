"""The instruments of the generated music (P12-R06..R08, GD-70): darksynth (reviewer, 2026-10-26),
all synthesised from oscillators and
noise through filters and envelopes. An 80s drum machine (punchy kicks, big gated snares, synth
toms), pumping and rolling saw basses, detuned saw pads, plucked arpeggios and leads sent to the
track's echo, and the music reverb. Drums play at `DRUM_PITCH` (toms higher or lower for fills);
their layers' pitches are ratios of it.

Partial layer objects are plain dicts with snake_case keys
(`glide_to`, `detune_cents`, `filter`, ...); absent keys take the defaults.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from audio.audio_types import Envelope, FilterSpec, Instrument, ToneLayer  # noqa: E402
from game.view.audio.sound_recipes import flatten_layers  # noqa: E402

# The MIDI pitch drum notes are played at (their layers' pitches are ratios of it).
DRUM_PITCH = 36


def env(attack: float, decay: float, sustain: float, release: float) -> Envelope:
    """A gain envelope."""
    return Envelope(attack, decay, sustain, release)


def layer(wave: str, gain: float, rest: dict[str, Any]) -> ToneLayer:
    """One layer: pitch 1, a short plucked envelope, then `rest` overrides."""
    return ToneLayer(
        wave,
        gain,
        rest.get("pitch", 1),
        rest.get("glide_to"),
        rest.get("glide_seconds"),
        rest.get("detune_cents"),
        rest.get("envelope", env(0.002, 0.12, 0, 0.05)),
        rest.get("filter"),
        rest.get("delay"),
    )


def saws(cents: list[float], gain: float, rest: dict[str, Any]) -> list[ToneLayer]:
    """Saws detuned by `cents`: the classic analog "supersaw"."""
    layers: list[ToneLayer] = []
    for detune in cents:
        options: dict[str, Any] = {"detune_cents": detune}
        for key, value in rest.items():
            options[key] = value
        layers.append(layer("sawtooth", gain, options))
    return layers


def _instrument(gain: float, layers: list[Any], rest: dict[str, Any]) -> Instrument:
    """An instrument from its gain, layers (or lists of layers) and optional `echo` and `reverb`
    shares."""
    return Instrument(flatten_layers(layers), gain, rest.get("echo"), rest.get("reverb"))


def _drums() -> dict[str, Instrument]:
    return {
        "kick": _instrument(
            0.95,
            [
                layer(
                    "sine",
                    1,
                    {
                        "pitch": 2.6,
                        "glide_to": 0.75,
                        "glide_seconds": 0.09,
                        "envelope": env(0.001, 0.3, 0, 0.05),
                    },
                ),
                layer(
                    "noise",
                    0.2,
                    {
                        "envelope": env(0.001, 0.01, 0, 0.01),
                        "filter": FilterSpec("highpass", 3000, None, None, None),
                    },
                ),
            ],
            {},
        ),
        "kick-heavy": _instrument(
            1,
            [
                layer(
                    "sine",
                    1,
                    {
                        "pitch": 2,
                        "glide_to": 0.6,
                        "glide_seconds": 0.16,
                        "envelope": env(0.002, 0.42, 0, 0.08),
                    },
                ),
                layer(
                    "square",
                    0.14,
                    {
                        "pitch": 1.2,
                        "glide_to": 0.6,
                        "glide_seconds": 0.08,
                        "envelope": env(0.001, 0.06, 0, 0.02),
                        "filter": FilterSpec("lowpass", 600, None, None, None),
                    },
                ),
            ],
            {},
        ),
        # The big 80s snare: noise held at half its peak for the note, then cut (the "gate").
        "snare-gated": _instrument(
            0.6,
            [
                layer(
                    "noise",
                    0.9,
                    {
                        "envelope": env(0.001, 0.05, 0.45, 0.025),
                        "filter": FilterSpec("bandpass", 1900, 0.6, None, None),
                    },
                ),
                layer(
                    "triangle",
                    0.6,
                    {
                        "pitch": 5.2,
                        "glide_to": 4,
                        "glide_seconds": 0.06,
                        "envelope": env(0.001, 0.1, 0, 0.03),
                    },
                ),
            ],
            {"reverb": 0.45},
        ),
        "hat": _instrument(
            0.2,
            [
                layer(
                    "noise",
                    1,
                    {
                        "envelope": env(0.001, 0.03, 0, 0.02),
                        "filter": FilterSpec("highpass", 8500, None, None, None),
                    },
                ),
            ],
            {},
        ),
        "open-hat": _instrument(
            0.15,
            [
                layer(
                    "noise",
                    1,
                    {
                        "envelope": env(0.001, 0.2, 0.1, 0.08),
                        "filter": FilterSpec("highpass", 7500, None, None, None),
                    },
                ),
            ],
            {},
        ),
        "shaker": _instrument(
            0.15,
            [
                layer(
                    "noise",
                    1,
                    {
                        "envelope": env(0.012, 0.05, 0, 0.03),
                        "filter": FilterSpec("bandpass", 6500, 1.2, None, None),
                    },
                ),
            ],
            {},
        ),
        # Simmons-style synth toms: a falling sine with a touch of noise, played at several pitches.
        "tom": _instrument(
            0.55,
            [
                layer(
                    "sine",
                    1,
                    {
                        "pitch": 3,
                        "glide_to": 2,
                        "glide_seconds": 0.2,
                        "envelope": env(0.002, 0.32, 0, 0.08),
                    },
                ),
                layer(
                    "noise",
                    0.12,
                    {
                        "envelope": env(0.001, 0.04, 0, 0.02),
                        "filter": FilterSpec("lowpass", 2500, None, None, None),
                    },
                ),
            ],
            {"reverb": 0.35},
        ),
    }


def _basses() -> dict[str, Instrument]:
    return {
        # Outrun: the pumping octave saw bass.
        "bass-saw": _instrument(
            0.42,
            [
                layer(
                    "sawtooth",
                    0.7,
                    {
                        "envelope": env(0.004, 0.16, 0.45, 0.04),
                        "filter": FilterSpec("lowpass", 650, 5, 2600, 0.12),
                    },
                ),
                layer("square", 0.45, {"pitch": 0.5, "envelope": env(0.004, 0.2, 0.6, 0.04)}),
            ],
            {},
        ),
        # Dreamwave: a round, plucked saw over a sine sub.
        "bass-dream": _instrument(
            0.45,
            [
                layer(
                    "sawtooth",
                    0.55,
                    {
                        "envelope": env(0.005, 0.2, 0.55, 0.06),
                        "filter": FilterSpec("lowpass", 480, 4, 1800, 0.12),
                    },
                ),
                layer("sine", 0.6, {"pitch": 0.5, "envelope": env(0.005, 0.22, 0.75, 0.06)}),
            ],
            {},
        ),
        # A plucked square bass for syncopated lines.
        "bass-pluck": _instrument(
            0.45,
            [
                layer(
                    "square",
                    0.6,
                    {
                        "envelope": env(0.003, 0.16, 0.2, 0.06),
                        "filter": FilterSpec("lowpass", 450, 6, 2000, 0.09),
                    },
                ),
                layer("sine", 0.6, {"pitch": 0.5, "envelope": env(0.003, 0.2, 0.3, 0.06)}),
            ],
            {},
        ),
        # Darksynth: detuned saws and a square, growling through a resonant filter, over a sub.
        "bass-heavy": _instrument(
            0.4,
            [
                saws(
                    [-16, 16],
                    0.55,
                    {
                        "envelope": env(0.004, 0.18, 0.6, 0.05),
                        "filter": FilterSpec("lowpass", 620, 6, 2200, 0.09),
                    },
                ),
                layer(
                    "square",
                    0.3,
                    {
                        "detune_cents": 7,
                        "envelope": env(0.004, 0.18, 0.5, 0.05),
                        "filter": FilterSpec("lowpass", 900, 2, None, None),
                    },
                ),
                layer("sine", 0.7, {"pitch": 0.5, "envelope": env(0.004, 0.2, 0.8, 0.05)}),
            ],
            {},
        ),
    }


def _pads() -> dict[str, Instrument]:
    return {
        "pad-warm": _instrument(
            0.1,
            saws(
                [-12, 0, 12],
                0.5,
                {
                    "envelope": env(0.35, 0.6, 0.75, 0.8),
                    "filter": FilterSpec("lowpass", 1700, 0.8, None, None),
                },
            ),
            {"reverb": 0.5},
        ),
        "pad-dream": _instrument(
            0.1,
            [
                saws(
                    [-9, 9],
                    0.5,
                    {
                        "envelope": env(0.7, 0.8, 0.8, 1.2),
                        "filter": FilterSpec("lowpass", 1200, 0.7, None, None),
                    },
                ),
                layer("triangle", 0.5, {"pitch": 2, "envelope": env(0.9, 0.8, 0.7, 1.4)}),
            ],
            {"reverb": 0.6},
        ),
        "pad-dark": _instrument(
            0.11,
            saws(
                [-14, 0, 14],
                0.5,
                {
                    "envelope": env(0.45, 0.8, 0.7, 0.9),
                    "filter": FilterSpec("lowpass", 800, 1.4, None, None),
                },
            ),
            {"reverb": 0.5},
        ),
    }


def _arps() -> dict[str, Instrument]:
    return {
        "arp-pluck": _instrument(
            0.13,
            [
                layer(
                    "sawtooth",
                    0.7,
                    {
                        "envelope": env(0.002, 0.13, 0.1, 0.07),
                        "filter": FilterSpec("lowpass", 1300, 4, 5000, 0.09),
                    },
                ),
            ],
            {"echo": 0.4, "reverb": 0.2},
        ),
        "arp-square": _instrument(
            0.13,
            [
                layer(
                    "square",
                    0.6,
                    {
                        "envelope": env(0.002, 0.12, 0.1, 0.06),
                        "filter": FilterSpec("lowpass", 1500, 3, 4200, 0.08),
                    },
                ),
            ],
            {"echo": 0.4, "reverb": 0.2},
        ),
        # A glassy FM-style bell arpeggio (dreamwave).
        "arp-glass": _instrument(
            0.12,
            [
                layer("sine", 0.8, {"envelope": env(0.002, 0.3, 0.1, 0.4)}),
                layer("sine", 0.25, {"pitch": 3, "envelope": env(0.002, 0.12, 0, 0.2)}),
            ],
            {"echo": 0.45, "reverb": 0.4},
        ),
    }


def _leads() -> dict[str, Instrument]:
    return {
        "lead-square": _instrument(
            0.14,
            [
                layer(
                    "square",
                    0.55,
                    {
                        "envelope": env(0.01, 0.2, 0.65, 0.15),
                        "filter": FilterSpec("lowpass", 2800, 1, None, None),
                    },
                ),
                layer(
                    "sawtooth",
                    0.35,
                    {
                        "detune_cents": 8,
                        "envelope": env(0.01, 0.2, 0.65, 0.15),
                        "filter": FilterSpec("lowpass", 2800, 1, None, None),
                    },
                ),
            ],
            {"echo": 0.3, "reverb": 0.3},
        ),
        # The supersaw lead.
        "lead-saw": _instrument(
            0.13,
            saws(
                [-14, 0, 14],
                0.45,
                {
                    "envelope": env(0.02, 0.25, 0.7, 0.2),
                    "filter": FilterSpec("lowpass", 3200, 1, None, None),
                },
            ),
            {"echo": 0.3, "reverb": 0.35},
        ),
        # An FM-style electric bell (DX7 style, dreamwave).
        "bell": _instrument(
            0.13,
            [
                layer("sine", 0.8, {"envelope": env(0.002, 0.8, 0.1, 1.2)}),
                layer("sine", 0.3, {"pitch": 2.76, "envelope": env(0.002, 0.4, 0, 0.6)}),
                layer("sine", 0.15, {"pitch": 5.4, "envelope": env(0.002, 0.2, 0, 0.3)}),
            ],
            {"echo": 0.35, "reverb": 0.45},
        ),
        # Analog brass (darksynth).
        "lead-brass": _instrument(
            0.14,
            saws(
                [-6, 6],
                0.6,
                {
                    "envelope": env(0.04, 0.25, 0.6, 0.2),
                    "filter": FilterSpec("lowpass", 1400, 2, 400, 0.12),
                },
            ),
            {"echo": 0.2, "reverb": 0.3},
        ),
    }


def _boss() -> dict[str, Instrument]:
    return {
        # A short, bright supersaw chord stab (boss tracks).
        "stab": _instrument(
            0.075,
            saws(
                [-12, 0, 12],
                0.5,
                {
                    "envelope": env(0.002, 0.14, 0.15, 0.05),
                    "filter": FilterSpec("lowpass", 1400, 3, 5500, 0.1),
                },
            ),
            {"echo": 0.15, "reverb": 0.25},
        ),
        # A noise sweep rising over a bar into the next section.
        "riser": _instrument(
            0.12,
            [
                layer(
                    "noise",
                    1,
                    {
                        "envelope": env(1.3, 0.1, 0.9, 0.05),
                        "filter": FilterSpec("bandpass", 7000, 1.5, 300, 1.4),
                    },
                ),
            ],
            {"reverb": 0.4},
        ),
    }


def _all_instruments() -> dict[str, Instrument]:
    instruments: dict[str, Instrument] = {}
    for group in [_drums(), _basses(), _pads(), _arps(), _leads(), _boss()]:
        for key, value in group.items():
            instruments[key] = value
    return instruments


# Every instrument the game's tracks name.
INSTRUMENTS = _all_instruments()
