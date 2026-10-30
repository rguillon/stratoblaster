"""Mixing limits of the sound effects (P12-R10), ported from `audio/voice-pool.ts`: at most
`max_voices` at once; when they are all taken, a new sound replaces the oldest one of lower or
equal priority (or is dropped); the same sound started again within `retrigger_seconds` is not
played twice. Pure: time is given.
"""


class PoolVoice:
    """A sound effect voice the pool counts."""

    def __init__(self, voice_id: int, name: str, priority: float, start: float, end: float) -> None:
        self.id = voice_id
        self.name = name
        self.priority = priority
        self.start = start
        # When it is over (Infinity for a looping sound, until released).
        self.end = end


class PoolDecision:
    """What the pool decided for a sound: play it (in place of `evicted`), or not (`play` false;
    `retrigger` says it was started again too soon)."""

    def __init__(
        self, play: bool, voice_id: int, evicted: PoolVoice | None, retrigger: bool
    ) -> None:
        self.play = play
        self.id = voice_id
        self.evicted = evicted
        self.retrigger = retrigger


class VoicePool:
    """The voice limits (see the module doc)."""

    def __init__(self, max_voices: float, retrigger_seconds: float) -> None:
        self._max_voices = max_voices
        self._retrigger_seconds = retrigger_seconds
        self._voices: list[PoolVoice] = []
        # The last start of each name: parallel lists (Transcrypt dictionaries are not used).
        self._last_names: list[str] = []
        self._last_starts: list[float] = []
        self._next_id = 1

    @property
    def voices(self) -> list[PoolVoice]:
        """The voices playing at the last request."""
        return self._voices

    def request(self, name: str, priority: float, now: float, seconds: float) -> PoolDecision:
        """Asks to play `name` at `now` for `seconds`."""
        self._expire(now)
        last = self._last_start(name)
        if last is not None and now - last < self._retrigger_seconds:
            return PoolDecision(False, 0, None, True)
        evicted: PoolVoice | None = None
        if len(self._voices) >= self._max_voices:
            evicted = self._victim(priority)
            if evicted is None:
                return PoolDecision(False, 0, None, False)
            self._voices.pop(self._index_of(evicted.id))
        voice = PoolVoice(self._next_id, name, priority, now, now + seconds)
        self._next_id += 1
        self._voices.append(voice)
        self._set_last_start(name, now)
        return PoolDecision(True, voice.id, evicted, False)

    def release(self, voice_id: int) -> None:
        """A voice stopped early (a looping sound let go, or every sound stopped)."""
        index = self._index_of(voice_id)
        if index >= 0:
            self._voices.pop(index)

    def clear(self) -> None:
        """Forgets every voice (the game paused: they were all stopped, P12-R11)."""
        self._voices = []
        self._last_names = []
        self._last_starts = []

    def _index_of(self, voice_id: int) -> int:
        for i in range(len(self._voices)):
            if self._voices[i].id == voice_id:
                return i
        return -1

    def _last_start(self, name: str) -> float | None:
        for i in range(len(self._last_names)):
            if self._last_names[i] == name:
                return self._last_starts[i]
        return None

    def _set_last_start(self, name: str, now: float) -> None:
        for i in range(len(self._last_names)):
            if self._last_names[i] == name:
                self._last_starts[i] = now
                return
        self._last_names.append(name)
        self._last_starts.append(now)

    def _expire(self, now: float) -> None:
        i = len(self._voices) - 1
        while i >= 0:
            if self._voices[i].end <= now:
                self._voices.pop(i)
            i -= 1

    def _victim(self, priority: float) -> PoolVoice | None:
        """The oldest voice whose priority is not above `priority`."""
        oldest: PoolVoice | None = None
        for voice in self._voices:
            if voice.priority <= priority and (oldest is None or voice.start < oldest.start):
                oldest = voice
        return oldest
