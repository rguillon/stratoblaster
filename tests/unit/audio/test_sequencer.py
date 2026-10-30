"""Unit tests of `src/audio/sequencer.py`."""

import pytest

from audio.audio_types import Note, Track
from audio.sequencer import Sequencer


def make_track(loop: bool) -> Track:
    # 120 bpm: one beat is 0.5 s. Four beats in all, notes on beats 0, 1 and 3.
    notes = [Note(0, 1, 60, 1, "a"), Note(1, 1, 62, 1, "a"), Note(3, 1, 64, 1, "a")]
    return Track("t", 120, 4, notes, loop)


def test_p12_r05_notes_are_handed_out_once_as_the_position_moves_on() -> None:
    seq = Sequencer(make_track(loop=False))
    first = seq.advance(0.6)
    assert [s.at for s in first] == [0.0, 0.5]
    assert [s.seconds for s in first] == [0.5, 0.5]
    assert seq.advance(0.6) == []
    later = seq.advance(2.0)
    assert [s.at for s in later] == [1.5]


def test_p12_r05_a_note_starting_exactly_at_the_limit_waits_for_the_next_call() -> None:
    seq = Sequencer(make_track(loop=False))
    assert [s.note.pitch for s in seq.advance(0.5)] == [60]


def test_p12_r05_a_track_that_does_not_loop_is_done_after_its_length() -> None:
    seq = Sequencer(make_track(loop=False))
    assert seq.done is False
    seq.advance(100)
    assert seq.position == pytest.approx(2.0)
    assert seq.done is True


def test_p12_r05_a_looping_track_starts_again_and_counts_its_loops() -> None:
    seq = Sequencer(make_track(loop=True))
    handed = seq.advance(4.5)
    times = [s.at for s in handed]
    assert times == pytest.approx([0.0, 0.5, 1.5, 2.0, 2.5, 3.5, 4.0])
    assert seq.done is False


def test_p12_r11_seeking_back_hands_out_the_notes_again() -> None:
    seq = Sequencer(make_track(loop=False))
    seq.advance(10)
    seq.seek(0.9)  # the note on beat 1 (0.5 s) is behind it; the one on beat 3 (1.5 s) is next
    assert [s.at for s in seq.advance(10)] == [1.5]


def test_p12_r11_seeking_into_a_loop_skips_the_notes_before_the_seek_point() -> None:
    seq = Sequencer(make_track(loop=True))
    seq.seek(4.6)  # second loop (2 s each), 0.6 s into it: the note at 1.5 s of it is next
    assert [s.at for s in seq.advance(6.0)] == pytest.approx([5.5])


def test_p12_r11_seeking_negative_time_starts_from_the_top() -> None:
    seq = Sequencer(make_track(loop=False))
    seq.seek(-3)
    assert seq.position == 0
    assert [s.at for s in seq.advance(0.1)] == [0.0]


def test_p12_r05_an_empty_track_hands_out_nothing() -> None:
    seq = Sequencer(Track("silence", 120, 4, [], True))
    assert seq.advance(10) == []
    assert seq.position == 10
