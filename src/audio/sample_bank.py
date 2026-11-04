# Copyright (c) 2026 Renaud Guillon
"""The sound effect samples (AUD-ENGINE-01): fetched at start-up, decoded once the context exists.

Browsers only let a context start after a user gesture (AUD-ENGINE-03), so the files are fetched
at once (`fetch_sample(name)` returns a promise of the file's bytes) and decoded when the context
is created. A sample that is not ready, or that failed to load or decode, is just not there: its
sound is silent and nothing throws (AUD-ENGINE-04).
"""

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class SampleBank:
    """The samples by name (see the module doc)."""

    def __init__(self, fetch_sample: Any | None, names: list[str]) -> None:
        self._fetch = fetch_sample
        self._names = names
        self._started = False
        # The bytes that arrived and are not decoded yet, and the decoded samples, by name.
        self._bytes: dict[str, Any] = {}
        self._buffers: dict[str, Any] = {}
        self._context: Any | None = None

    def prefetch(self) -> None:
        """Start fetching every sample, once."""
        fetch = self._fetch
        if self._started or fetch is None:
            return
        self._started = True
        for name in self._names:
            self._fetch_one(fetch, name)

    def decode_with(self, context: Any) -> None:
        """Decode the samples with `context`, now or as they arrive."""
        self._context = context
        for name in self._names:
            if self._bytes.get(name) is not None:
                self._decode(context, name)

    def get(self, name: str) -> Any | None:
        """Return the decoded sample `name`, or None while it is not ready (or failed)."""
        return self._buffers.get(name)

    @property
    def ready(self) -> int:
        """How many samples are decoded."""
        return len(self._buffers)

    def _fetch_one(self, fetch: Any, name: str) -> None:
        def arrived(data: Any) -> None:
            self._bytes[name] = data
            context = self._context
            if context is not None:
                self._decode(context, name)

        _quietly(fetch(name).then(arrived))

    def _decode(self, context: Any, name: str) -> None:
        data = self._bytes.pop(name)

        def decoded(buffer: Any) -> None:
            self._buffers[name] = buffer

        _quietly(context.decodeAudioData(data).then(decoded))


def _quietly(promise: Any) -> None:
    """Swallow a failure: a sample that fails to load only leaves its sound silent."""
    promise.catch(lambda _error: None)
