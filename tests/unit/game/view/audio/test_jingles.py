"""Unit tests of `src/game/view/audio/jingles.py`."""

from game.view.audio.instruments import DRUM_PITCH
from game.view.audio.jingles import CHECKPOINT, COMPLETE, JINGLES, OVER, jingle, line


def test_p12_r07_line_builds_notes_from_beat_length_pitch_triples():
    notes = line("lead-saw", [[0, 0.5, 72], [1, 2, 60]], 0.9)
    assert [(n.beat, n.beats, n.pitch, n.velocity, n.instrument) for n in notes] == [
        (0, 0.5, 72, 0.9, "lead-saw"),
        (1, 2, 60, 0.9, "lead-saw"),
    ]


def test_p12_r07_jingle_is_a_track_played_once_with_sorted_notes():
    notes = line("bell", [[2, 1, 80], [0, 1, 79]], 1)
    track = jingle("jingle-test", 100, 4, notes)
    assert track.id == "jingle-test"
    assert track.bpm == 100
    assert track.beats == 4
    assert track.loop is False
    assert [n.beat for n in track.notes] == [0, 2]


def test_p12_r07_the_three_jingles_are_played_once():
    assert set(JINGLES) == {"complete", "over", "checkpoint"}
    for track in JINGLES.values():
        assert track.loop is False
        beats = [n.beat for n in track.notes]
        assert beats == sorted(beats)


def test_p12_r07_level_complete_is_a_rising_fanfare_with_a_tom_roll():
    assert JINGLES["complete"] is COMPLETE
    assert COMPLETE.id == "jingle-complete"
    assert COMPLETE.bpm == 132
    assert COMPLETE.beats == 8
    tom_pitches = [n.pitch for n in COMPLETE.notes if n.instrument == "tom"]
    assert tom_pitches == [DRUM_PITCH + 12, DRUM_PITCH + 7, DRUM_PITCH + 3]
    lead = [n.pitch for n in COMPLETE.notes if n.instrument == "lead-saw"]
    assert lead[0] < lead[-1]


def test_p12_r07_game_over_falls_slowly_on_brass():
    assert JINGLES["over"] is OVER
    assert OVER.bpm == 84
    lead = [n.pitch for n in OVER.notes if n.instrument == "lead-brass"]
    assert lead == sorted(lead, reverse=True)


def test_p12_r07_checkpoint_is_a_short_bell_chime():
    assert JINGLES["checkpoint"] is CHECKPOINT
    assert CHECKPOINT.beats == 3
    assert {n.instrument for n in CHECKPOINT.notes} == {"bell"}
    assert [n.pitch for n in CHECKPOINT.notes] == [79, 84, 88]
