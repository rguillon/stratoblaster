"""Plays the sound effects (P12-R09, P12-R10): each through the
`VoicePool`'s limits, panned with its position, on the sound effect bus. Without a context the
pool still decides, so the game's logic (and the e2e test API) does not depend on audio being
available.
"""

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_types import INFINITY, SoundDesign, sound_seconds
from audio.synth import Voice, VoiceOptions, play_voice
from audio.voice_pool import VoicePool

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class SfxBus:
    """Where the sound effects go, once the audio context exists."""

    def __init__(self, context: Any, sfx: Any) -> None:
        self.context = context
        self.sfx = sfx


class SfxSettings:
    """Mixing settings of an `SfxPlayer` (`config/audio.py`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        max_voices: float,
        retrigger_seconds: float,
        retrigger_boost: float,
        pan_max: float,
        stop_fade_seconds: float,
    ) -> None:
        self.max_voices = max_voices
        self.retrigger_seconds = retrigger_seconds
        # A sound started again within `retrigger_seconds` is made this much louder instead.
        self.retrigger_boost = retrigger_boost
        # Pan of a sound at the playfield's edges (-pan_max left, +pan_max right).
        self.pan_max = pan_max
        # How fast a sound fades when stopped early.
        self.stop_fade_seconds = stop_fade_seconds


def pan_at(x: float, width: float, pan_max: float) -> float:
    """Pan of a sound at `x` on a playfield `width` wide: -`pan_max` at the left edge, 0 in the
    middle."""
    if not (width > 0):
        return 0
    share = min(1, max(0, x / width))
    return (share * 2 - 1) * pan_max


class _Playing:
    """A sound playing, with its voice once the context exists."""

    def __init__(self, voice_id: int, voice: Voice | None, gain: Any | None) -> None:
        self.id = voice_id
        self.voice = voice
        self.gain = gain


class SfxPlayer:
    """The sound effects player (see the module doc)."""

    def __init__(self, bus: Any, clock: Any, settings: SfxSettings) -> None:
        self._bus = bus
        self._clock = clock
        self._settings = settings
        self._pool = VoicePool(settings.max_voices, settings.retrigger_seconds)
        self._playing: list[_Playing] = []
        # Looping sounds playing, by name: parallel lists.
        self._loop_names: list[str] = []
        self._loop_ids: list[int] = []

    @property
    def voices(self) -> int:
        """Voices counted by the pool."""
        return len(self._pool.voices)

    def play(self, sound: SoundDesign, pan: float = 0) -> bool:
        """Plays `sound`, panned to `pan` (-1..1) when it is positional. Returns whether it plays
        (the pool may drop it)."""
        if sound.loop and self._loop_index(sound.name) >= 0:
            return False
        decision = self._pool.request(
            sound.name, sound.priority, self._clock(), sound_seconds(sound)
        )
        if not decision.play:
            if decision.retrigger:
                self._boost(sound.name)
            return False
        if decision.evicted is not None:
            self._stop_voice(decision.evicted.id)
        self._forget_ended()
        voice, gain = self._start(sound, pan)
        self._playing.append(_Playing(decision.id, voice, gain))
        if sound.loop:
            self._loop_names.append(sound.name)
            self._loop_ids.append(decision.id)
        return True

    def stop_loop(self, name: str) -> None:
        """Stops the looping sound `name` (the laser is let go)."""
        index = self._loop_index(name)
        if index < 0:
            return
        voice_id = self._loop_ids[index]
        self._loop_names.pop(index)
        self._loop_ids.pop(index)
        self._stop_voice(voice_id)

    def looping(self, name: str) -> bool:
        """Whether the looping sound `name` plays."""
        return self._loop_index(name) >= 0

    def stop_all(self) -> None:
        """Stops every sound (the game pauses, P12-R11)."""
        for voice_id in [playing.id for playing in self._playing]:
            self._stop_voice(voice_id)
        self._loop_names = []
        self._loop_ids = []
        self._pool.clear()

    def _loop_index(self, name: str) -> int:
        for i in range(len(self._loop_names)):
            if self._loop_names[i] == name:
                return i
        return -1

    def _find_playing(self, voice_id: int) -> _Playing | None:
        for playing in self._playing:
            if playing.id == voice_id:
                return playing
        return None

    def _start(self, sound: SoundDesign, pan: float) -> tuple[Voice | None, Any | None]:
        bus = self._bus()
        if bus is None:
            return None, None
        context = bus.context
        gain = context.createGain()
        gain.gain.value = 1
        out = gain
        if sound.positional and pan != 0:
            panner = context.createStereoPanner()
            panner.pan.value = max(-1, min(1, pan))
            gain.connect(panner)
            out = panner
        out.connect(bus.sfx)
        hold = INFINITY if sound.loop else sound.hold
        options = VoiceOptions(context.currentTime, None, hold, sound.gain)
        voice = play_voice(context, gain, sound.layers, options)
        return voice, gain

    def _boost(self, name: str) -> None:
        """The same sound again too soon: the one playing gets a little louder instead
        (P12-R10)."""
        voices = self._pool.voices
        voice = None
        i = len(voices) - 1
        while i >= 0:
            if voices[i].name == name:
                voice = voices[i]
                break
            i -= 1
        playing = self._find_playing(voice.id) if voice is not None else None
        gain = playing.gain if playing is not None else None
        bus = self._bus()
        if gain is None or bus is None:
            return
        boosted = min(
            self._settings.retrigger_boost**2,
            gain.gain.value * self._settings.retrigger_boost,
        )
        gain.gain.setValueAtTime(boosted, bus.context.currentTime)

    def _forget_ended(self) -> None:
        """Forgets the sounds that are over (the pool let them go)."""
        alive = [voice.id for voice in self._pool.voices]
        self._playing = [playing for playing in self._playing if playing.id in alive]

    def _stop_voice(self, voice_id: int) -> None:
        playing = self._find_playing(voice_id)
        self._playing = [p for p in self._playing if p.id != voice_id]
        keep = [i for i in range(len(self._loop_ids)) if self._loop_ids[i] != voice_id]
        self._loop_names = [self._loop_names[i] for i in keep]
        self._loop_ids = [self._loop_ids[i] for i in keep]
        self._pool.release(voice_id)
        bus = self._bus()
        if playing is not None and playing.voice is not None and bus is not None:
            playing.voice.stop(bus.context.currentTime, self._settings.stop_fade_seconds)
