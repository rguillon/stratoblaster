"""Where all audio goes (P12-R05): a music bus and a sound
effect bus, each with its volume, into a master limiter so the output never clips. Browsers only
start audio after a user gesture, so the context is created by `unlock`, called on the first key
press, tap, click or gamepad button: nothing is heard before, and no autoplay warning is shown.
Without Web Audio, or if it fails, everything stays silent and nothing throws.

The context comes from `create_context` (`new AudioContext()` in the browser), never a global.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_bindings import AudioMix
from audio.audio_types import xorshift
from config.audio import AudioLimiter

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Gain ramps on the buses last this long, so a volume change does not click.
BUS_RAMP_SECONDS = 0.03
# The reverb impulse's seed: the same noise on every run (no Math.random).
REVERB_SEED = 0x2545F491


class AudioBuses:
    """The music and sound effect buses (P12-R05)."""

    def __init__(self, context: Any, music: Any, sfx: Any, reverb: Any | None = None) -> None:
        self.context = context
        self.music = music
        # The music reverb's input: it comes out on the music bus. None when not asked for.
        self.reverb = reverb
        self.sfx = sfx


class AudioOutputOptions:
    """Settings of an `AudioOutput`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        create_context: Any | None,
        mix: AudioMix,
        peak_db: float,
        limiter: AudioLimiter,
        reverb_seconds: float | None = None,
    ) -> None:
        # Creates the context; None without Web Audio.
        self.create_context = create_context
        # Level of each bus at full volume, so loud sounds stay within reach of the music.
        self.mix = mix
        # `master_peak`: the limiter's threshold, in dBFS.
        self.peak_db = peak_db
        self.limiter = limiter
        # Length of the music reverb's tail in seconds; no reverb when None.
        self.reverb_seconds = reverb_seconds


def volume_gain(step: float, steps: float) -> float:
    """Bus gain of a volume `step` out of `steps`: (step / steps)^2, 0 silent (P12-R04)."""
    if not (steps > 0):
        return 0
    share = min(1, max(0, step / steps))
    return share * share


def reverb_impulse(context: Any, seconds: float) -> Any:
    """A stereo reverb impulse: decaying noise, the same on every run (no `Math.random`)."""
    length = max(1, math.floor(context.sampleRate * seconds + 0.5))
    buffer = context.createBuffer(2, length, context.sampleRate)
    seed = REVERB_SEED
    for channel in range(2):
        data = buffer.getChannelData(channel)
        for i in range(length):
            seed = xorshift(seed)
            noise = (seed / 0xFFFFFFFF) * 2 - 1
            data[i] = noise * (1 - i / length) ** 3
    return buffer


class AudioOutput:
    """The audio output (see the module doc)."""

    def __init__(self, options: AudioOutputOptions) -> None:
        self.options = options
        self._buses: AudioBuses | None = None
        self._failed = False
        self._music = 1.0
        self._sfx = 1.0

    @property
    def buses(self) -> AudioBuses | None:
        """The buses, once the context exists."""
        return self._buses

    @property
    def state(self) -> str:
        """The context's state: `none` before it is created (or without Web Audio)."""
        if self._buses is None:
            return "none"
        state: str = self._buses.context.state
        return state

    def unlock(self) -> AudioBuses | None:
        """Creates (or resumes) the context, after a user gesture. Returns the buses, if any."""
        if self._buses is None and not self._failed:
            self._buses = self._create()
        if self._buses is not None and self._buses.context.state == "suspended":
            _quietly(self._buses.context.resume())
        return self._buses

    def set_hidden(self, hidden: bool) -> None:
        """Silences everything while the page is hidden (P12-R11), and brings it back."""
        if self._buses is None:
            return
        context = self._buses.context
        if context.state == "closed":
            return
        _quietly(context.suspend() if hidden else context.resume())

    def set_volumes(self, music: float, sfx: float) -> None:
        """Sets the bus gains from 0..1 volume gains (see `volume_gain`)."""
        self._music = music
        self._sfx = sfx
        buses = self._buses
        if buses is None:
            return
        now = buses.context.currentTime
        _ramp(buses.music.gain, music * self.options.mix.music, now)
        _ramp(buses.sfx.gain, sfx * self.options.mix.sfx, now)

    def _create(self) -> AudioBuses | None:
        options = self.options
        if options.create_context is None:
            return None
        try:
            context = options.create_context()
            master = context.createDynamicsCompressor()
            master.threshold.value = options.peak_db
            master.knee.value = options.limiter.knee_db
            master.ratio.value = options.limiter.ratio
            master.attack.value = options.limiter.attack_seconds
            master.release.value = options.limiter.release_seconds
            master.connect(context.destination)
            music = context.createGain()
            sfx = context.createGain()
            music.gain.value = self._music * options.mix.music
            sfx.gain.value = self._sfx * options.mix.sfx
            music.connect(master)
            sfx.connect(master)
            reverb = self._reverb(context, music)
            if reverb is not None:
                return AudioBuses(context, music, sfx, reverb)
            return AudioBuses(context, music, sfx)
        except:  # noqa: E722
            self._failed = True
            return None

    def _reverb(self, context: Any, music: Any) -> Any | None:
        """A convolver into the music bus, so the music volume applies to its tail too."""
        seconds = self.options.reverb_seconds
        if seconds is None:
            return None
        reverb = context.createConvolver()
        reverb.buffer = reverb_impulse(context, seconds)
        reverb.connect(music)
        return reverb


def _ramp(param: Any, value: float, now: float) -> None:
    param.cancelScheduledValues(now)
    param.setValueAtTime(param.value, now)
    param.linearRampToValueAtTime(value, now + BUS_RAMP_SECONDS)


def _quietly(promise: Any) -> None:
    """Audio promises that fail are not errors of the game."""
    promise.catch(lambda error: None)
