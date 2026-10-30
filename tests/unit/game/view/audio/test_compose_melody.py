"""Unit tests of `src/game/view/audio/compose_melody.py`."""

import pytest

from core.math.rng import create_rng
from game.view.audio.compose_melody import (
    CHORD_STEPS,
    RHYTHMS,
    MotifNote,
    make_motif,
    motif_bars,
    nearest_chord_step,
    scale_pitch,
)
from game.view.audio.compose_parts import BarContext
from game.view.audio.music_styles import BEATS_PER_BAR, WORLD_STYLES

MAJOR_ISH = [0, 2, 4, 5, 7, 9, 11]


def test_scale_pitch_walks_the_scale_by_octaves():
    assert scale_pitch(MAJOR_ISH, 0) == 0
    assert scale_pitch(MAJOR_ISH, 6) == 11
    assert scale_pitch(MAJOR_ISH, 7) == 12
    assert scale_pitch(MAJOR_ISH, 14) == 24


def test_scale_pitch_wraps_below_zero():
    assert scale_pitch(MAJOR_ISH, -1) == -1
    assert scale_pitch(MAJOR_ISH, -7) == -12


def test_scale_pitch_of_an_empty_scale_is_zero():
    assert scale_pitch([], 5) == 0


@pytest.mark.parametrize(
    ("degree", "expected"),
    [
        (0, 0),
        (1, 0),  # ties keep the earlier candidate
        (3, 2),
        (5, 4),
        (6, 7),
        (9, 9),
        (-6, -7),
        (-4, -5),  # a tie between -5 and -3 keeps -5
        (20, 9),
    ],
)
def test_p12_r06_nearest_chord_step(degree, expected):
    assert nearest_chord_step(degree) == expected


def test_p12_r06_make_motif_has_the_rhythm_and_the_clamped_walk():
    for seed in range(20):
        motif = make_motif(create_rng(seed))
        steps = [[m.step, m.length_] for m in motif]
        assert steps in RHYTHMS
        assert all(-3 <= m.degree <= 9 for m in motif)
        assert motif[0].degree in CHORD_STEPS


def test_p12_r06_make_motif_is_repeatable_for_a_seed():
    a = make_motif(create_rng(42))
    b = make_motif(create_rng(42))
    assert [(m.step, m.length_, m.degree) for m in a] == [(m.step, m.length_, m.degree) for m in b]


def test_motif_note_stores_its_fields():
    m = MotifNote(2, 3, 4)
    assert (m.step, m.length_, m.degree) == (2, 3, 4)


def test_p12_r06_motif_bars_are_silent_without_energy():
    ctx = BarContext(0.0, [36, 39, 43], MAJOR_ISH, 0, False)
    motif = [MotifNote(0, 2, 0)]
    assert motif_bars(WORLD_STYLES[1], motif, ctx, 0, 0) == []


def test_p12_r06_motif_bars_play_each_note_on_the_chord_in_the_lead_register():
    style = WORLD_STYLES[1]
    ctx = BarContext(8.0, [36, 39, 43], MAJOR_ISH, 2, False)
    motif = [MotifNote(0, 2, 0), MotifNote(4, 4, 2)]
    notes = motif_bars(style, motif, ctx, 0, 0)
    assert len(notes) == 2
    octave = 12 * style.octaves.lead
    assert notes[0].pitch == pytest.approx(scale_pitch(MAJOR_ISH, 0) + octave)
    assert notes[1].pitch == pytest.approx(scale_pitch(MAJOR_ISH, 2) + octave)
    eighth = BEATS_PER_BAR / 8
    assert notes[0].beat == pytest.approx(8.0)
    assert notes[1].beat == pytest.approx(8.0 + 4 * eighth)
    assert notes[1].beats == pytest.approx(4 * eighth * 0.92)
    assert all(n.velocity == pytest.approx(0.8) for n in notes)
    assert all(n.instrument == style.instruments.lead for n in notes)


def test_p12_r06_motif_variation_shifts_the_pitches_up_a_step():
    style = WORLD_STYLES[1]
    ctx = BarContext(0.0, [36, 39, 43], MAJOR_ISH, 1, False)
    motif = [MotifNote(0, 2, 0)]
    plain = motif_bars(style, motif, ctx, 0, 0)[0].pitch
    shifted = motif_bars(style, motif, ctx, 0, 1)[0].pitch
    assert shifted - plain == pytest.approx(scale_pitch(MAJOR_ISH, 1) - scale_pitch(MAJOR_ISH, 0))
