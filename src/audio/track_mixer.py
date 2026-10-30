"""The mixer of one playing track (P12-R06): an input per
instrument into the track's fader, with sends to its tempo-synced echo (a dotted eighth by
default) and to the shared music reverb, so a track fades in and out with its echoes and reverb.
Web Audio nodes are untyped attribute access on the context the game gives in.
"""

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_types import Instrument, MusicEffects, beat_seconds

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


SILENT = 0.0001


class MusicBus:
    """Where the music goes, once the audio context exists."""

    def __init__(self, context: Any, music: Any, reverb: Any | None = None) -> None:
        self.context = context
        self.music = music
        # The music reverb's input, if there is one.
        self.reverb = reverb


def _fade_param(param: Any, value: float, now: float, seconds: float) -> None:
    """Fades `param` from where it is to `value` over `seconds` from `now`."""
    param.cancelScheduledValues(now)
    param.setValueAtTime(max(SILENT, param.value), now)
    param.exponentialRampToValueAtTime(max(SILENT, value), now + max(0.01, seconds))


class TrackMixer:
    """The mixer of one playing track (see the module doc)."""

    def __init__(self, bus: MusicBus, effects: MusicEffects | None, bpm: float) -> None:
        self._bus = bus
        self._effects = effects
        self._bpm = bpm
        context = bus.context
        # The track's fader, into the music bus.
        self.output = context.createGain()
        self.output.connect(bus.music)
        self._reverb: Any | None = None
        if bus.reverb is not None and effects is not None:
            self._reverb = context.createGain()
            self._reverb.connect(bus.reverb)
        self._echo: Any | None = None
        # The instrument inputs: parallel lists, by name.
        self._input_names: list[str] = []
        self._input_nodes: list[Any] = []

    def fade_to(self, level: float, now: float, seconds: float) -> None:
        """Fades the track (and its effects) to `level` over `seconds`; at once when 0."""
        for param in self._faders():
            if seconds > 0:
                _fade_param(param, level, now, seconds)
            else:
                param.setValueAtTime(level, now)

    def fade_in(self, now: float, seconds: float) -> None:
        """Starts silent, then fades in over `seconds` (at once when 0)."""
        if seconds <= 0:
            self.fade_to(1, now, 0)
            return
        for param in self._faders():
            param.setValueAtTime(SILENT, now)
        self.fade_to(1, now, seconds)

    def input(self, name: str, instrument: Instrument) -> Any:
        """Where the notes of `instrument` go: its own gain, with its echo and reverb sends."""
        for i in range(len(self._input_names)):
            if self._input_names[i] == name:
                return self._input_nodes[i]
        context = self._bus.context
        node = context.createGain()
        node.connect(self.output)
        if instrument.echo and self._effects is not None:
            self._send(node, self._echo_input(), instrument.echo)
        if instrument.reverb and self._reverb is not None:
            self._send(node, self._reverb, instrument.reverb)
        self._input_names.append(name)
        self._input_nodes.append(node)
        return node

    def disconnect(self) -> None:
        """Cuts the track off the music bus."""
        self.output.disconnect()
        if self._reverb is not None:
            self._reverb.disconnect()
        if self._echo is not None:
            self._echo.disconnect()

    def _faders(self) -> list[Any]:
        if self._reverb is not None:
            return [self.output.gain, self._reverb.gain]
        return [self.output.gain]

    def _send(self, source: Any, to: Any, amount: float) -> None:
        send = self._bus.context.createGain()
        send.gain.value = amount
        source.connect(send)
        send.connect(to)

    def _echo_input(self) -> Any:
        """The echo: a delay of `echo_beats` at the track's tempo, fed back, into the fader."""
        if self._echo is not None:
            return self._echo
        context = self._bus.context
        effects = self._effects
        echo_beats = effects.echo_beats if effects is not None else 0.75
        seconds = echo_beats * beat_seconds(self._bpm)
        node = context.createGain()
        delay = context.createDelay(max(1, seconds))
        delay.delayTime.value = seconds
        feedback = context.createGain()
        feedback.gain.value = effects.echo_feedback if effects is not None else 0.3
        node.connect(delay)
        delay.connect(feedback)
        feedback.connect(delay)
        delay.connect(self.output)
        self._echo = node
        return node
