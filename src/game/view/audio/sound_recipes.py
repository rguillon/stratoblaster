"""The building blocks of the game's sound effects (P12-R09), ported from
`audio/sound-recipes.ts`: envelopes, tones and recipes.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from audio.audio_types import Envelope, FilterSpec, ToneLayer  # noqa: E402


class MinigunBurst:
    """The rounds of a minigun burst and the seconds between them (`MINIGUN`)."""

    def __init__(self, rounds: int, gap: float) -> None:
        self.rounds = rounds
        self.gap = gap


# Rounds in a minigun burst, and the seconds between them (about 48 rounds a second).
MINIGUN = MinigunBurst(6, 0.021)


class ExplosionSize:
    """How big an explosion is (reviewer, 2026-10-26: more realistic)."""

    def __init__(self, seconds: float, body: float, thump: float, tail: float, debris: int) -> None:
        # How long its body lasts, in seconds.
        self.seconds = seconds
        # Cut-off its body starts from, closing down to a rumble (Hz).
        self.body = body
        # Pitch of its sub-bass thump, falling by half (Hz).
        self.thump = thump
        # A low rumble rolling on after it, in seconds (0: none).
        self.tail = tail
        # Bits of debris crackling after it.
        self.debris = debris


def flatten_layers(items: list[Any]) -> list[ToneLayer]:
    """The layers of `items`, where an item is a layer or a list of layers (a recipe such as
    `explosion(...)`). Transcrypt drops the `*` spread in a list literal, so recipes are
    flattened here instead."""
    layers: list[ToneLayer] = []
    for item in items:
        if isinstance(item, ToneLayer):
            layers.append(item)
        else:
            layers.extend(item)
    return layers


def env(attack: float, decay: float, sustain: float = 0, release: float = 0.03) -> Envelope:
    """A gain envelope; sustain 0 and a 0.03 s release by default."""
    return Envelope(attack, decay, sustain, release)


def tone(
    wave: str,
    pitch: float,
    gain: float,
    envelope: Envelope,
    rest: dict[str, Any],
) -> ToneLayer:
    """One layer of a voice; `rest` holds the optional fields (`delay`, `glide_to`, `filter`,
    ...), absent ones are None."""
    return ToneLayer(
        wave,
        gain,
        rest.get("pitch", pitch),
        rest.get("glide_to"),
        rest.get("glide_seconds"),
        rest.get("detune_cents"),
        rest.get("envelope", envelope),
        rest.get("filter"),
        rest.get("delay"),
    )


def minigun(burst: MinigunBurst) -> list[ToneLayer]:
    """A minigun burst (reviewer, 2026-10-26): rounds `gap` apart, each a gritty crack over a
    short thump. A volley's burst lasts until the next volley (the gun fires 8 a second), so
    holding fire rattles on without a break: BRRRT."""
    layers: list[ToneLayer] = []
    for i in range(burst.rounds):
        delay = i * burst.gap
        accent = 0.75 if i % 2 else 1
        layers.append(
            tone(
                "noise",
                1,
                accent,
                env(0.001, 0.014, 0, 0.004),
                {"delay": delay, "filter": FilterSpec("bandpass", 1700, 0.9, None, None)},
            )
        )
        layers.append(
            tone(
                "square",
                150,
                0.5 * accent,
                env(0.001, 0.016, 0, 0.004),
                {
                    "delay": delay,
                    "glide_to": 65,
                    "glide_seconds": 0.018,
                    "filter": FilterSpec("lowpass", 1200, None, None, None),
                },
            )
        )
    return layers


# Spacing and pitches of the debris crackles: fixed, so a sound is the same each time.
DEBRIS_GAPS = [0.11, 0.07, 0.16, 0.09, 0.13, 0.06, 0.18, 0.1]
DEBRIS_PITCHES = [2400, 1700, 3100, 2000, 2700, 1500, 3500, 2200]


def explosion(size: ExplosionSize, delay: float = 0) -> list[ToneLayer]:
    """A realistic explosion (reviewer, 2026-10-26), layer by layer: a few milliseconds of
    broadband crack (the shock front), a body of noise whose brightness closes fast (the
    fireball), a sub-bass thump, a low rumble rolling on for the big ones, and debris crackling
    after it. Most of its energy is low, so a busy wave does not turn into a hiss. Starts `delay`
    seconds in."""
    seconds = size.seconds
    layers: list[ToneLayer] = [
        tone(
            "noise",
            1,
            0.35,
            env(0.001, 0.012, 0, 0.006),
            {"delay": delay, "filter": FilterSpec("highpass", 1200, None, None, None)},
        ),
        tone(
            "noise",
            1,
            0.8,
            env(0.003, seconds * 0.6, 0, seconds * 0.35),
            {
                "delay": delay,
                "filter": FilterSpec("lowpass", 180, 0.5, size.body, seconds * 0.8),
            },
        ),
        tone(
            "sine",
            size.thump,
            0.9,
            env(0.002, seconds * 0.7, 0, 0.05),
            {
                "delay": delay,
                "glide_to": size.thump * 0.45,
                "glide_seconds": seconds * 0.6,
            },
        ),
    ]
    if size.tail > 0:
        layers.append(
            tone(
                "noise",
                1,
                0.35,
                env(0.04, size.tail, 0, 0.1),
                {"delay": delay, "filter": FilterSpec("lowpass", 260, 0.7, None, None)},
            )
        )
    at = delay + seconds * 0.2
    for i in range(size.debris):
        at += DEBRIS_GAPS[i % len(DEBRIS_GAPS)] * (1 + seconds * 0.5)
        layers.append(
            tone(
                "noise",
                1,
                0.14 * (1 - (0.5 * i) / max(1, size.debris)),
                env(0.001, 0.016, 0, 0.01),
                {
                    "delay": at,
                    "filter": FilterSpec(
                        "bandpass", DEBRIS_PITCHES[i % len(DEBRIS_PITCHES)], 2, None, None
                    ),
                },
            )
        )
    return layers


def chime(wave: str, pitches: list[float], gap: float, gain: float) -> list[ToneLayer]:
    """Notes of a little arpeggio, one after the other."""
    return [
        tone(wave, pitch, gain, env(0.003, 0.12, 0.2, 0.12), {"delay": i * gap})
        for i, pitch in enumerate(pitches)
    ]
