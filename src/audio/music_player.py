"""Plays the generated music (P12-R05..R08, P12-R11), ported from `audio/music-player.ts`: one
track at a time, cross-fading into the next or fading out, plus one-shot jingles over it. Notes
are scheduled ahead on the audio clock by `update`, so the music keeps time when frames are slow.
Pausing keeps each track's position; resuming goes on from there.

`bus` is a function returning the `MusicBus` once the context exists (None before), as in the
TypeScript. Seconds into each paused track are kept in parallel lists (a Map keyed by slot).
"""

from org.transcrypt.stubs.browser import __pragma__

from audio.audio_types import INFINITY, Instrument, MusicEffects, Track, midi_to_hz
from audio.sequencer import Sequencer
from audio.synth import Voice, VoiceOptions, play_voice
from audio.track_mixer import MusicBus, TrackMixer

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class MusicTimings:
    """Timings of a `MusicPlayer` (`config/audio.py`)."""

    def __init__(self, lookahead_seconds: float, pause_fade_seconds: float) -> None:
        self.lookahead_seconds = lookahead_seconds
        # How fast the notes still sounding go quiet when the game pauses.
        self.pause_fade_seconds = pause_fade_seconds


class Slot:
    """A track playing (or fading out), on its own mixer into the music bus."""

    def __init__(self, track: Track, fade: float) -> None:
        self.track = track
        self.sequencer = Sequencer(track)
        self.mixer: TrackMixer | None = None
        # Audio time of the track's start; None until the context exists.
        self.anchor: float | None = None
        self.voices: list[Voice] = []
        # Fades to this level (1 in, 0 out) over `fade` seconds once it starts.
        self.target = 1.0
        self.fade = fade
        # Audio time it is over (faded out), if it is fading out.
        self.until: float | None = None


def _all_ended(voices: list[Voice], now: float) -> bool:
    """Whether every voice is over (`end <= now`, false for NaN as in the TypeScript)."""
    return all([voice.end <= now for voice in voices])


class MusicPlayer:
    """The music player (see the module doc)."""

    def __init__(
        self,
        bus: Any,
        instruments: dict[str, Instrument],
        timings: MusicTimings,
        effects: MusicEffects | None = None,
    ) -> None:
        self._bus = bus
        self._instruments = instruments
        self._timings = timings
        # The tracks' echo and reverb; dry when None.
        self._effects = effects
        self._current: Slot | None = None
        self._others: list[Slot] = []
        self._paused = False
        # Seconds into each track where it was paused: parallel lists.
        self._paused_slots: list[Slot] = []
        self._paused_at: list[float] = []

    @property
    def track(self) -> Track | None:
        """The track playing (not a jingle), if any."""
        return self._current.track if self._current is not None else None

    @property
    def position(self) -> float:
        """Seconds into the current track, counting loops (0 before the context exists)."""
        slot = self._current
        if slot is None:
            return 0
        index = self._paused_index(slot)
        if index >= 0:
            return self._paused_at[index]
        bus = self._bus()
        if bus is not None and slot.anchor is not None:
            current: float = bus.context.currentTime
            return current - slot.anchor
        return 0

    def play(self, track: Track | None, fade: float) -> None:
        """Plays `track` from its start, cross-fading from the current one over `fade` seconds;
        None fades the music out."""
        previous = self._current
        if previous is not None:
            self._fade_out(previous, fade)
        self._current = self._slot(track, fade) if track is not None else None

    def jingle(self, track: Track) -> None:
        """Plays `track` once over the music (a jingle)."""
        self._others.append(self._slot(track, 0))

    def pause(self) -> None:
        """Pauses the music where it is (P12-R11): the notes sounding stop."""
        if self._paused:
            return
        self._paused = True
        bus = self._bus()
        for slot in self._slots():
            if bus is None or slot.anchor is None:
                continue
            now = bus.context.currentTime
            at = now - slot.anchor
            self._set_paused_at(slot, at)
            slot.sequencer.seek(at)
            for voice in slot.voices:
                voice.stop(now, self._timings.pause_fade_seconds)
            slot.voices = []

    def resume(self) -> None:
        """Goes on from where the music was paused."""
        if not self._paused:
            return
        self._paused = False
        bus = self._bus()
        now = bus.context.currentTime if bus is not None else 0
        for i in range(len(self._paused_slots)):
            self._paused_slots[i].anchor = now - self._paused_at[i]
        self._paused_slots = []
        self._paused_at = []

    def stop(self) -> None:
        """Stops everything at once."""
        bus = self._bus()
        now = bus.context.currentTime if bus is not None else 0
        for slot in self._slots():
            self._silence(slot, now)
        self._current = None
        self._others = []
        self._paused_slots = []
        self._paused_at = []

    def update(self) -> None:
        """Schedules the notes due within the lookahead, and drops the tracks that are over."""
        bus = self._bus()
        if bus is None or self._paused:
            return
        now = bus.context.currentTime
        for slot in self._slots():
            self._schedule(slot, bus, now)
        self._others = [slot for slot in self._others if not self._over(slot, now)]

    def _slots(self) -> list[Slot]:
        slots: list[Slot] = []
        if self._current is not None:
            slots.append(self._current)
        slots.extend(self._others)
        return slots

    def _slot(self, track: Track, fade: float) -> Slot:
        return Slot(track, fade)

    def _paused_index(self, slot: Slot) -> int:
        for i in range(len(self._paused_slots)):
            if self._paused_slots[i] is slot:
                return i
        return -1

    def _set_paused_at(self, slot: Slot, at: float) -> None:
        index = self._paused_index(slot)
        if index >= 0:
            self._paused_at[index] = at
        else:
            self._paused_slots.append(slot)
            self._paused_at.append(at)

    def _fade_out(self, slot: Slot, fade: float) -> None:
        slot.target = 0
        slot.fade = fade
        self._others.append(slot)
        bus = self._bus()
        if bus is None or slot.mixer is None:
            slot.until = -INFINITY
            return
        now = bus.context.currentTime
        slot.until = now + fade
        slot.mixer.fade_to(0, now, max(0.01, fade))

    def _schedule(self, slot: Slot, bus: MusicBus, now: float) -> None:
        """Starts the slot on the bus if needed, then schedules its notes up to the lookahead."""
        # A track fading out goes on playing until it is silent; one never started stays so.
        if slot.until is not None and slot.mixer is None:
            return
        if slot.mixer is None or slot.anchor is None:
            self._start(slot, bus, now)
        mixer = slot.mixer
        anchor = slot.anchor
        if mixer is None or anchor is None:
            return
        slot.voices = [voice for voice in slot.voices if voice.end > now]
        lookahead = now + self._timings.lookahead_seconds - anchor
        for scheduled in slot.sequencer.advance(lookahead):
            note = scheduled.note
            start = anchor + scheduled.at
            instrument = self._playable(slot, note.instrument, start)
            if instrument is None:
                continue
            options = VoiceOptions(
                max(now, start),
                midi_to_hz(note.pitch),
                scheduled.seconds,
                note.velocity * instrument.gain,
            )
            destination = mixer.input(note.instrument, instrument)
            slot.voices.append(play_voice(bus.context, destination, instrument.layers, options))

    def _playable(self, slot: Slot, name: str, start: float) -> Instrument | None:
        """The instrument of a note, unless it is unknown or starts once the fade-out is over."""
        if slot.until is not None and start >= slot.until:
            return None
        return self._instruments.get(name)

    def _start(self, slot: Slot, bus: MusicBus, now: float) -> None:
        mixer = TrackMixer(bus, self._effects, slot.track.bpm)
        mixer.fade_in(now, slot.fade)
        slot.mixer = mixer
        slot.anchor = now

    def _over(self, slot: Slot, now: float) -> bool:
        """A slot is over once faded out, or once a jingle has played all its notes."""
        if slot.until is not None and now >= slot.until:
            self._silence(slot, now)
            return True
        return slot.sequencer.done and _all_ended(slot.voices, now)

    def _silence(self, slot: Slot, now: float) -> None:
        for voice in slot.voices:
            voice.stop(now, self._timings.pause_fade_seconds)
        slot.voices = []
        if slot.mixer is not None:
            slot.mixer.disconnect()
