# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/audio/sample_bank.py`."""

from typing import Any

from helpers.audio_fakes import FakeContext, FakePromise

from audio.sample_bank import SampleBank


class Fetches:
    """`fetch_sample`: records the names asked for and hands out promises the test settles."""

    def __init__(self) -> None:
        self.promises: dict[str, FakePromise] = {}

    def __call__(self, name: str) -> FakePromise:
        self.promises[name] = FakePromise()
        return self.promises[name]


def test_aud_engine_01_the_files_are_fetched_once_at_start_up() -> None:
    fetch = Fetches()
    bank = SampleBank(fetch, ["hit", "bomb"])
    bank.prefetch()
    bank.prefetch()
    assert list(fetch.promises) == ["hit", "bomb"]
    assert bank.ready == 0
    assert bank.get("hit") is None


def test_aud_engine_01_a_sample_is_decoded_when_the_context_exists_and_its_bytes_are_there() -> (
    None
):
    fetch = Fetches()
    context = FakeContext()
    bank = SampleBank(fetch, ["hit", "bomb"])
    bank.prefetch()
    fetch.promises["hit"].resolve("hit-bytes")
    assert context.decodes == []  # no context yet: nothing is decoded
    bank.decode_with(context)
    assert [d.data for d in context.decodes] == ["hit-bytes"]
    context.decodes[0].resolve("hit-buffer")
    assert bank.get("hit") == "hit-buffer"
    assert bank.ready == 1


def test_aud_engine_01_a_sample_arriving_after_the_context_is_decoded_at_once() -> None:
    fetch = Fetches()
    context = FakeContext()
    bank = SampleBank(fetch, ["hit"])
    bank.prefetch()
    bank.decode_with(context)
    assert context.decodes == []
    fetch.promises["hit"].resolve("late-bytes")
    assert [d.data for d in context.decodes] == ["late-bytes"]
    context.decodes[0].resolve("buffer")
    assert bank.get("hit") == "buffer"


def test_aud_engine_01_a_sample_is_decoded_once_even_if_the_context_is_set_again() -> None:
    fetch = Fetches()
    context = FakeContext()
    bank = SampleBank(fetch, ["hit"])
    bank.prefetch()
    fetch.promises["hit"].resolve("bytes")
    bank.decode_with(context)
    bank.decode_with(context)
    assert len(context.decodes) == 1


def test_aud_engine_04_a_file_that_fails_to_load_or_decode_is_just_missing() -> None:
    fetch = Fetches()
    context = FakeContext()
    bank = SampleBank(fetch, ["hit", "bomb"])
    bank.prefetch()
    bank.decode_with(context)
    fetch.promises["hit"].reject("404")
    fetch.promises["bomb"].resolve("garbage")
    context.decodes[0].reject("bad data")
    assert bank.get("hit") is None
    assert bank.get("bomb") is None
    assert bank.ready == 0
    # The handlers that swallow the errors were given to both promises.
    assert fetch.promises["hit"].caught
    assert context.decodes[0].caught


def test_aud_engine_04_without_a_fetch_function_every_sample_is_missing() -> None:
    bank: Any = SampleBank(None, ["hit"])
    bank.prefetch()
    bank.decode_with(FakeContext())
    assert bank.get("hit") is None
