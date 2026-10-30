"""Unit tests of `src/game/view/audio/compose_parts.py`."""

import pytest

from audio.audio_types import Note
from core.math.rng import create_rng
from game.view.audio.compose_parts import (
    ARP_SHAPES,
    BASS_FIFTH_HIGH,
    BASS_FIFTH_LOW,
    BASS_STEPS,
    DRUM_STEPS,
    PATTERNS,
    TOM_FILL,
    BarContext,
    arp_bar,
    arp_shape,
    bass_bar,
    bass_steps,
    concat,
    drum_bar,
    drum_fill,
    note,
    pad_bar,
    sort_by_beat,
)
from game.view.audio.instruments import DRUM_PITCH
from game.view.audio.music_styles import BEATS_PER_BAR, WORLD_STYLES


def bar(energy: int = 2, fill: bool = False, beat: float = 8.0) -> BarContext:
    return BarContext(beat, [36, 39, 43], [36, 38, 39, 41, 43, 45, 46], energy, fill)


def const(value: float):
    """A generator that always gives `value` (no clock, no `random` module)."""
    return lambda: value


def style(world: int = 1):
    return WORLD_STYLES[world]


def test_note_builds_a_note_with_its_instrument():
    n = note("kick", 1.5, 0.25, 36, 0.9)
    assert isinstance(n, Note)
    assert (n.beat, n.beats, n.pitch, n.velocity, n.instrument) == (1.5, 0.25, 36, 0.9, "kick")


def test_concat_keeps_the_order_of_the_groups():
    a = [note("a", 0, 1, 1, 1)]
    b = [note("b", 1, 1, 1, 1), note("c", 2, 1, 1, 1)]
    assert [n.instrument for n in concat([a, b])] == ["a", "b", "c"]
    assert concat([]) == []


def test_sort_by_beat_is_stable_for_equal_beats():
    notes = [
        note("late", 3, 1, 1, 1),
        note("first-at-1", 1, 1, 1, 1),
        note("second-at-1", 1, 1, 1, 1),
        note("early", 0, 1, 1, 1),
    ]
    ordered = sort_by_beat(notes)
    assert [n.instrument for n in ordered] == ["early", "first-at-1", "second-at-1", "late"]
    # The input list is not reordered.
    assert notes[0].instrument == "late"


@pytest.mark.parametrize("size", [0, 1, 2, 3, 5, 8, 13])
def test_sort_by_beat_sorts_any_size(size):
    gen = create_rng(size + 7)
    notes = [note("n", gen() * 10, 1, 1, 1) for _ in range(size)]
    ordered = sort_by_beat(notes)
    assert len(ordered) == size
    assert [n.beat for n in ordered] == sorted(n.beat for n in notes)


def test_p12_r06_drum_bar_at_zero_energy_plays_only_the_kick():
    style_ = style(1)
    notes = drum_bar(style_, bar(energy=0), const(0.5))
    assert notes
    assert {n.instrument for n in notes} == {style_.instruments.kick}
    assert len(notes) == len(PATTERNS[style_.drums].kick)


def test_p12_r06_drum_bar_places_kick_and_snare_on_the_pattern_steps():
    style_ = style(1)
    pattern = PATTERNS[style_.drums]
    step = BEATS_PER_BAR / DRUM_STEPS
    notes = drum_bar(style_, bar(energy=1, beat=4.0), const(0.5))
    kicks = [n.beat for n in notes if n.instrument == style_.instruments.kick]
    snares = [n.beat for n in notes if n.instrument == style_.instruments.snare]
    assert kicks == pytest.approx([4.0 + i * step for i in pattern.kick])
    assert snares == pytest.approx([4.0 + i * step for i in pattern.snare])
    assert all(n.pitch == DRUM_PITCH for n in notes)


def test_p12_r06_full_energy_plays_a_hat_on_every_sixteenth():
    style_ = style(1)
    notes = drum_bar(style_, bar(energy=2), const(0.5))
    hats = [n for n in notes if n.instrument == style_.instruments.hat]
    # Every sixteenth but the open hats' steps (their percussion is another instrument).
    assert len(hats) == DRUM_STEPS - len(PATTERNS[style_.drums].open)


def test_p12_r06_hats_are_sparser_at_low_energy():
    style_ = style(1)
    low = drum_bar(style_, bar(energy=1), const(0.5))
    high = drum_bar(style_, bar(energy=2), const(0.5))
    hats_low = [n for n in low if n.instrument == style_.instruments.hat]
    hats_high = [n for n in high if n.instrument == style_.instruments.hat]
    assert len(hats_low) < len(hats_high)


def test_p12_r06_a_section_end_adds_a_tom_fill():
    style_ = style(1)
    plain = drum_bar(style_, bar(energy=1, fill=False), const(0.5))
    filled = drum_bar(style_, bar(energy=1, fill=True), const(0.5))
    assert not [n for n in plain if n.instrument == "tom"]
    assert [n for n in filled if n.instrument == "tom"]


def test_p12_r06_drum_fill_descends_over_the_last_beats():
    fill_bar = bar(energy=2, fill=True, beat=0)
    notes = drum_fill(fill_bar, const(0))
    assert len(notes) == 6
    assert [n.pitch for n in notes] == [DRUM_PITCH + p for p in TOM_FILL]
    assert all(n.beat >= BEATS_PER_BAR - 1.5 for n in notes)
    assert [n.beat for n in notes] == sorted(n.beat for n in notes)


def test_p12_r06_drum_fill_is_short_at_low_energy():
    counts = {len(drum_fill(bar(energy=1, fill=True), const(r))) for r in (0.0, 0.99)}
    assert counts == {3, 4}


def test_p12_r06_bass_bar_plays_root_then_the_passing_fifth():
    style_ = style(1)
    chord = [36, 39, 43]
    ctx = BarContext(0.0, chord, [36, 38, 39, 41, 43, 45, 46], 1, False)
    steps = list(range(0, 16, 2))
    notes = bass_bar(style_, ctx, steps)
    assert len(notes) == len(steps)
    by_step = {round(n.beat * 4): n.pitch for n in notes}
    # Root on most steps, the fifth between steps 12 and 14.
    assert by_step[0] == 36
    assert by_step[BASS_FIFTH_LOW] == 43
    # Elsewhere the root, or its octave on the pumping eighths (steps 2, 6, 10, 14).
    for s, pitch in by_step.items():
        if not BASS_FIFTH_LOW <= s < BASS_FIFTH_HIGH:
            assert pitch in (36, 48)


def test_p12_r06_bass_bar_pumps_an_octave_on_off_beat_eighths():
    style_ = style(1)  # "eighths" bass
    ctx = BarContext(0.0, [36, 39, 43], [36], 1, False)
    notes = bass_bar(style_, ctx, [2, 4])
    pitches = {round(n.beat * 4): n.pitch for n in notes}
    assert pitches[2] == 36 + 12
    assert pitches[4] == 36


def test_p12_r06_full_energy_bass_plays_rolling_sixteenths():
    ctx = BarContext(0.0, [36, 39, 43], [36], 2, False)
    notes = bass_bar(style(1), ctx, [0])
    assert len(notes) == DRUM_STEPS


def test_bass_bar_falls_back_to_defaults_for_an_empty_chord():
    ctx = BarContext(0.0, [], [36], 1, False)
    notes = bass_bar(style(1), ctx, [0, 8])
    assert {n.pitch for n in notes} <= {36, 36 + 12, 36 + 7}


def test_bass_steps_picks_a_rhythm_of_the_style():
    style_ = style(4)  # "rolling"
    assert bass_steps(style_, const(0.0)) in BASS_STEPS[style_.bass]


def test_p12_r06_pad_bar_holds_each_chord_tone_for_the_bar():
    style_ = style(1)
    ctx = bar(beat=12.0)
    notes = pad_bar(style_, ctx)
    assert [n.pitch for n in notes] == [p + 12 * style_.octaves.pad for p in ctx.chord]
    assert all(n.beat == 12.0 and n.beats == BEATS_PER_BAR for n in notes)


def test_p12_r06_arp_bar_plays_rate_notes_per_beat():
    style_ = style(1)  # arp_rate 4
    notes = arp_bar(style_, bar(energy=1), [0, 1, 2, 3])
    assert len(notes) == BEATS_PER_BAR * style_.arp_rate


def test_p12_r06_arp_bar_is_sixteenths_at_full_energy():
    style_ = style(3)  # arp_rate 4 too
    notes = arp_bar(style_, bar(energy=2), [0])
    assert len(notes) == BEATS_PER_BAR * max(4, style_.arp_rate)
    assert all(n.velocity in (0.9, 0.65) for n in notes)


def test_arp_bar_uses_the_shape_over_two_octaves():
    ctx = BarContext(0.0, [36, 40, 43], [36], 1, False)
    notes = arp_bar(style(1), ctx, [0, 3, 5])
    tones = {n.pitch for n in notes}
    shift = 12 * style(1).octaves.arp
    assert tones <= {36 + shift, 40 + shift, 43 + shift, 48 + shift, 52 + shift, 55 + shift}


def test_arp_shape_is_one_of_the_shapes():
    assert arp_shape(create_rng(3)) in ARP_SHAPES


def test_bar_context_stores_its_fields():
    ctx = BarContext(4.0, [1], [2], 1, True)
    assert (ctx.beat, ctx.chord, ctx.scale, ctx.energy, ctx.fill) == (4.0, [1], [2], 1, True)
