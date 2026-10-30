"""Unit tests of `src/game/view/audio/compose_boss.py`."""

import pytest

from game.view.audio.compose_boss import (
    BOSS_PROGRESSIONS,
    KICKS,
    OFF_BEATS,
    STAB_STEPS,
    STEP,
    STEPS,
    boss_bass_bar,
    boss_drum_bar,
    riser_bar,
    roll_length,
    snare_roll,
    stab_bar,
)
from game.view.audio.compose_parts import BarContext
from game.view.audio.instruments import DRUM_PITCH
from game.view.audio.music_styles import BEATS_PER_BAR, OCTAVE, WORLD_STYLES


def bar(energy: int = 2, fill: bool = False, beat: float = 0.0, chord=None) -> BarContext:
    chord = [36, 39, 43] if chord is None else chord
    return BarContext(beat, chord, [36, 38, 39, 41, 43, 45, 46], energy, fill)


def test_p12_r07_boss_progressions_are_four_chords_inside_the_scale():
    assert all(len(p) == 4 for p in BOSS_PROGRESSIONS)
    assert all(0 <= d <= 6 for p in BOSS_PROGRESSIONS for d in p)


def test_p12_r07_roll_length_is_short_every_fourth_bar_and_half_a_bar_at_a_section_end():
    assert roll_length(bar(beat=3 * BEATS_PER_BAR)) == 4
    assert roll_length(bar(beat=0)) == 0
    assert roll_length(bar(beat=7 * BEATS_PER_BAR)) == 4
    assert roll_length(bar(fill=True)) == 8


def test_snare_roll_grows_louder_over_its_sixteenths():
    notes = snare_roll("snare", bar(beat=0.0), 4)
    assert len(notes) == 4
    velocities = [n.velocity for n in notes]
    assert velocities == sorted(velocities)
    assert velocities[0] == pytest.approx(0.35)
    assert velocities[-1] == pytest.approx(0.35 + 0.6 * 3 / 4)
    assert notes[0].beat == pytest.approx((STEPS - 4) * STEP)


def test_p12_r07_boss_drums_push_kicks_and_hit_every_sixteenth_but_the_off_beats():
    notes = boss_drum_bar(WORLD_STYLES[1], bar())
    kick = WORLD_STYLES[1].instruments.kick
    kicks = [n for n in notes if n.instrument == kick]
    assert len(kicks) == len(KICKS)
    hats = [n for n in notes if n.instrument == WORLD_STYLES[1].instruments.hat]
    assert len(hats) == STEPS - len(OFF_BEATS)
    perc = [n for n in notes if n.instrument == WORLD_STYLES[1].instruments.perc]
    assert len(perc) == len(OFF_BEATS)
    assert all(n.pitch == DRUM_PITCH for n in notes)


def test_p12_r07_boss_drums_roll_the_snare_on_a_section_end_and_drop_the_backbeat():
    style = WORLD_STYLES[1]
    snares = [
        n for n in boss_drum_bar(style, bar(fill=True)) if n.instrument == style.instruments.snare
    ]
    # The roll covers the last 8 sixteenths: only the backbeat on step 4 is left before it.
    backbeat = [n for n in snares if n.velocity == pytest.approx(0.95)]
    assert [n.beat for n in backbeat] == [pytest.approx(4 * STEP)]
    assert len(snares) == 1 + 8


def test_p12_r07_boss_bass_jumps_between_root_and_octave():
    style = WORLD_STYLES[1]
    notes = boss_bass_bar(style, bar(chord=[36, 39, 43]))
    assert len(notes) == STEPS
    for i, n in enumerate(notes):
        assert n.pitch == (36 + OCTAVE if i % 2 else 36)
    assert notes[0].velocity == 1
    assert notes[1].velocity == 0.75


def test_p12_r07_boss_bass_falls_back_to_the_default_root_without_a_chord():
    notes = boss_bass_bar(WORLD_STYLES[1], bar(chord=[]))
    assert {n.pitch for n in notes} == {36, 48}


def test_p12_r07_stabs_are_silent_below_full_energy():
    assert stab_bar(bar(energy=1)) == []


def test_p12_r07_stabs_play_a_three_note_voicing_on_the_3_3_2_rhythm():
    notes = stab_bar(bar(energy=2))
    assert len(notes) == len(STAB_STEPS) * 3
    assert {n.instrument for n in notes} == {"stab"}
    assert {n.pitch for n in notes} == {36 + OCTAVE, 43 + OCTAVE, 36 + 2 * OCTAVE}


def test_p12_r07_stabs_fall_back_to_defaults_without_a_chord():
    notes = stab_bar(bar(energy=2, chord=[]))
    assert {n.pitch for n in notes} == {36 + OCTAVE, 36 + 7 + OCTAVE, 36 + 2 * OCTAVE}


def test_p12_r07_riser_sweeps_only_into_the_next_section():
    assert riser_bar(bar(fill=False)) == []
    notes = riser_bar(bar(fill=True))
    assert len(notes) == 1
    assert notes[0].instrument == "riser"
    assert notes[0].beats == BEATS_PER_BAR
