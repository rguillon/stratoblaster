"""Plays one voice's layers into a destination (P12-R05), ported from `audio/synth.ts`: each layer
is an oscillator or looped noise, through its filter and envelope. The Web Audio context is passed
in (a fake one in the tests); nothing here reads a browser global.

Gain values ramp from and to 0.0001 instead of 0, which exponential ramps cannot reach.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_types import INFINITY, ToneLayer, is_finite, xorshift

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Seconds of white noise, looped by the noise layers.
NOISE_SECONDS = 1
# Gain values ramp from and to this instead of 0, which exponential ramps cannot reach.
SILENT = 0.0001
# Sources stop a little after their release, so nothing clicks.
STOP_MARGIN = 0.02
# The noise seed: a fixed sequence (no Math.random), so the noise sounds the same on every run.
NOISE_SEED = 0x9E3779B9

# One noise buffer per context (a WeakMap in the TypeScript): parallel lists, as Transcrypt has
# no object-keyed dictionaries.
_noise_contexts = []  # type: list[Any]
_noise_buffers = []  # type: list[Any]


class VoiceOptions:
    """How one voice is played."""

    def __init__(self, when: float, note_hz: float | None, hold: float, gain: float) -> None:
        # Audio time it starts at.
        self.when = when
        # The note's frequency for an instrument (layer pitches are ratios); None for a sound.
        self.note_hz = note_hz
        # Seconds the layers hold before their release; Infinity until `Voice.stop`.
        self.hold = hold
        # Gain on every layer (velocity times mix level).
        self.gain = gain


class _Part:
    """A layer's source and its gain, as the voice keeps them."""

    def __init__(self, source: Any, gain: Any) -> None:
        self.source = source
        self.gain = gain


class Voice:
    """A voice playing (or scheduled)."""

    def __init__(self, end: float, parts: list[_Part]) -> None:
        # Audio time it is over (Infinity while a looping voice holds).
        self.end = end
        self._parts = parts

    def stop(self, at: float, fade: float) -> None:
        """Fades it out over `fade` seconds from `at`, then stops it."""
        for part in self._parts:
            part.gain.gain.cancelScheduledValues(at)
            part.gain.gain.setTargetAtTime(SILENT, at, max(0.001, fade / 4))
            try:  # noqa: SIM105 (Transcrypt has no contextlib)
                part.source.stop(at + fade + STOP_MARGIN)
            except:  # noqa: E722 (a Web Audio call that throws must not stop the game, as in the TypeScript)
                # Already stopped earlier than that: nothing to do.
                pass


def noise_buffer(ctx: Any) -> Any:
    """One second of white noise per context, made once."""
    for i in range(len(_noise_contexts)):
        if _noise_contexts[i] is ctx:
            return _noise_buffers[i]
    length = math.floor(ctx.sampleRate * NOISE_SECONDS + 0.5)
    buffer = ctx.createBuffer(1, length, ctx.sampleRate)
    data = buffer.getChannelData(0)
    seed = NOISE_SEED
    for i in range(len(data)):
        seed = xorshift(seed)
        data[i] = (seed / 0xFFFFFFFF) * 2 - 1
    _noise_contexts.append(ctx)
    _noise_buffers.append(buffer)
    return buffer


def _source(ctx: Any, layer: ToneLayer, start: float, base: float) -> Any:
    """The layer's source: an oscillator at its pitch (gliding), or looped noise."""
    pitch = layer.pitch * base
    glide = layer.glide_to * base if layer.glide_to is not None else None
    seconds = layer.glide_seconds if layer.glide_seconds is not None else 0
    if layer.wave == "noise":
        noise = ctx.createBufferSource()
        noise.buffer = noise_buffer(ctx)
        noise.loop = True
        if glide is not None and pitch > 0:
            noise.playbackRate.setValueAtTime(1, start)
            noise.playbackRate.exponentialRampToValueAtTime(
                max(SILENT, glide / pitch), start + seconds
            )
        return noise
    osc = ctx.createOscillator()
    osc.type = layer.wave
    osc.frequency.setValueAtTime(pitch, start)
    if glide is not None:
        osc.frequency.exponentialRampToValueAtTime(max(1, glide), start + seconds)
    if layer.detune_cents:
        osc.detune.setValueAtTime(layer.detune_cents, start)
    return osc


def _layer_filter(ctx: Any, layer: ToneLayer, start: float) -> Any:
    """The layer's filter, its cut-off gliding from `from` to `frequency`; None without one."""
    spec = layer.filter
    if spec is None:
        return None
    node = ctx.createBiquadFilter()
    node.type = spec.type
    node.Q.setValueAtTime(spec.q if spec.q is not None else 1, start)
    node.frequency.setValueAtTime(spec.from_ if spec.from_ is not None else spec.frequency, start)
    if spec.from_ is not None:
        sweep = spec.sweep_seconds if spec.sweep_seconds is not None else 0.1
        node.frequency.exponentialRampToValueAtTime(spec.frequency, start + sweep)
    return node


def _envelope(param: Any, layer: ToneLayer, start: float, peak: float, hold: float) -> float:
    """Shapes `param` with the layer's envelope; returns when its release ends (Infinity if
    held)."""
    envelope = layer.envelope
    level = max(SILENT, peak * envelope.sustain)
    param.setValueAtTime(SILENT, start)
    param.linearRampToValueAtTime(peak, start + envelope.attack)
    param.linearRampToValueAtTime(level, start + envelope.attack + envelope.decay)
    if not is_finite(hold):
        return INFINITY
    release_at = start + max(hold, envelope.attack + envelope.decay)
    param.setValueAtTime(level, release_at)
    param.linearRampToValueAtTime(SILENT, release_at + envelope.release)
    return release_at + envelope.release


def play_voice(ctx: Any, destination: Any, layers: list[ToneLayer], options: VoiceOptions) -> Voice:
    """Plays the `layers` of one voice into `destination` (P12-R05). Returns a handle to stop it
    early."""
    parts: list[_Part] = []
    end = 0.0
    for layer in layers:
        start = options.when + (layer.delay if layer.delay is not None else 0)
        note_hz = options.note_hz if options.note_hz is not None else 1
        src = _source(ctx, layer, start, note_hz)
        gain = ctx.createGain()
        shaped = _layer_filter(ctx, layer, start)
        if shaped is not None:
            src.connect(shaped).connect(gain)
        else:
            src.connect(gain)
        gain.connect(destination)
        over = _envelope(gain.gain, layer, start, layer.gain * options.gain, options.hold)
        src.start(start)
        if is_finite(over):
            src.stop(over + STOP_MARGIN)
        end = max(end, over)
        parts.append(_Part(src, gain))
    return Voice(end, parts)
