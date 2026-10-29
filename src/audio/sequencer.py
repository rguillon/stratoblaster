"""Walks a track's notes ahead of time (P12-R05), ported from `audio/sequencer.ts`: each call
hands out the notes that start before a given point of the track, once each, looping at the
track's end. Pure: the player turns track time into audio time, so the music keeps time when
frames are slow, and pausing is only a matter of where it stands.
"""

import math

from audio.audio_types import Note, Track, beat_seconds, track_seconds


class ScheduledNote:
    """A note to play, with its time in seconds since the track started (counting loops)."""

    def __init__(self, note: Note, at: float, seconds: float) -> None:
        self.note = note
        self.at = at
        self.seconds = seconds


class Sequencer:
    """Hands out a track's notes as its position moves on (see the module doc)."""

    def __init__(self, track: Track) -> None:
        self.track = track
        # Seconds into the track (counting loops) up to which the notes were handed out.
        self._position = 0.0
        # Index of the next note in the track, and the loop it is in.
        self._index = 0
        self._loop = 0
        self._beat = beat_seconds(track.bpm)
        self._length = track_seconds(track)

    @property
    def position(self) -> float:
        """Seconds into the track (counting loops) handed out so far."""
        return self._position

    @property
    def done(self) -> bool:
        """Whether a track that does not loop has handed out all its notes."""
        return not self.track.loop and self._position >= self._length

    def advance(self, until: float) -> list[ScheduledNote]:
        """The notes starting before `until` seconds into the track that were not handed out yet."""
        out: list[ScheduledNote] = []
        if until <= self._position or self._length <= 0:
            return out
        notes = self.track.notes
        loop = self.track.loop
        while len(notes) > 0:
            if self._index >= len(notes):
                if not loop:
                    break
                self._index = 0
                self._loop += 1
                continue
            note = notes[self._index]
            at = self._loop * self._length + note.beat * self._beat
            if at >= until:
                break
            out.append(ScheduledNote(note, at, note.beats * self._beat))
            self._index += 1
        self._position = until if loop else min(until, self._length)
        return out

    def seek(self, seconds: float) -> None:
        """Goes back (or on) to `seconds` into the track: the notes from there are handed out
        again. Used when the game pauses, as the notes scheduled ahead are cancelled (P12-R11).
        """
        time = max(0, seconds)
        length = self._length
        self._loop = math.floor(time / length) if length > 0 and self.track.loop else 0
        in_loop = time - self._loop * length
        index = len(self.track.notes)
        for i, note in enumerate(self.track.notes):
            if note.beat * self._beat >= in_loop:
                index = i
                break
        self._index = index
        self._position = time
