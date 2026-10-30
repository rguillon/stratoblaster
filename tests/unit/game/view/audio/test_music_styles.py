"""Unit tests of `src/game/view/audio/music_styles.py`."""

import pytest

from game.view.audio.compose_parts import BASS_STEPS, DRUM_STEPS, PATTERNS
from game.view.audio.music_styles import (
    BEATS_PER_BAR,
    FULL_ENERGY,
    MENU_STYLE,
    MUSIC_LOOP_MIN_SECONDS,
    OCTAVE,
    SCALES,
    SECTION_BARS,
    WORLD_STYLES,
    MusicStyle,
    Octaves,
    StyleInstruments,
)


@pytest.mark.parametrize("name", list(SCALES))
def test_p12_r06_scales_are_seven_notes_inside_an_octave(name):
    steps = SCALES[name]
    assert len(steps) == 7
    assert steps[0] == 0
    assert steps == sorted(steps)
    assert steps[-1] < OCTAVE


def test_p12_r06_the_four_worlds_have_a_style_each():
    assert set(WORLD_STYLES) == {1, 2, 3, 4}
    for style in WORLD_STYLES.values():
        assert isinstance(style, MusicStyle)
        assert style.tempo[0] < style.tempo[1]
        assert style.drums in PATTERNS
        assert style.bass in BASS_STEPS
        assert all(len(p) == 4 for p in style.progressions)
        assert style.roots and style.scales


def test_p12_r07_boss_tracks_are_faster_than_the_levels():
    for style in WORLD_STYLES.values():
        assert style.boss_boost[0] <= style.boss_boost[1]


def test_p12_r08_menu_theme_is_slower_than_every_level():
    slowest_level = min(style.tempo[0] for style in WORLD_STYLES.values())
    assert MENU_STYLE.tempo[0] < slowest_level
    assert MENU_STYLE.energies == [[1, 2, 1, 2, 2]]


def test_p12_r06_timing_constants():
    assert BEATS_PER_BAR == 4
    assert SECTION_BARS == 8
    assert FULL_ENERGY == 2
    assert MUSIC_LOOP_MIN_SECONDS == 60
    assert OCTAVE == 12
    assert DRUM_STEPS == 16


def test_style_instruments_and_octaves_store_their_fields():
    inst = StyleInstruments("k", "s", "h", "p", "b", "pad", "arp", "lead")
    assert (inst.kick, inst.snare, inst.hat, inst.perc) == ("k", "s", "h", "p")
    assert (inst.bass, inst.pad, inst.arp, inst.lead) == ("b", "pad", "arp", "lead")
    octaves = Octaves(1, 2, 3)
    assert (octaves.pad, octaves.arp, octaves.lead) == (1, 2, 3)
