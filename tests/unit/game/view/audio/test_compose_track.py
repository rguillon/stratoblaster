"""Unit tests of `src/game/view/audio/compose_track.py`."""

import math

import pytest

import game.view.audio.compose_track as compose_track_module
from core.math.rng import create_rng
from game.view.audio.compose_track import (
    LEVEL_ENERGIES,
    SHIFT_BAR,
    Section,
    TrackRequest,
    chord,
    compose_track,
    energies,
    section_count,
    sections,
    seed_of,
    tempo_of,
)
from game.view.audio.music_styles import (
    BEATS_PER_BAR,
    MENU_STYLE,
    SECTION_BARS,
    WORLD_STYLES,
)


@pytest.fixture
def char_codes(monkeypatch):
    """`charCodeAt` is JavaScript only: CPython reads the code of the character instead."""
    monkeypatch.setattr(compose_track_module, "char_code_at", lambda text, i: ord(text[i]))


def request(world=1, boss=False, seed=5, track_id="level-1-1") -> TrackRequest:
    return TrackRequest(track_id, WORLD_STYLES[world], seed, boss)


def at(value: float):
    return lambda: value


def test_track_request_stores_its_fields():
    r = request(world=2, boss=True, seed=9, track_id="boss-2")
    assert (r.id, r.seed, r.boss) == ("boss-2", 9, True)
    assert r.style is WORLD_STYLES[2]


def test_p12_r06_seed_of_is_fnv1a_and_tells_texts_apart(char_codes):
    assert seed_of("") == 0x811C9DC5
    assert seed_of("level-1-1") == seed_of("level-1-1")
    assert seed_of("level-1-1") != seed_of("level-1-2")
    assert 0 <= seed_of("boss-3") < 2**32


def test_chord_is_a_triad_of_scale_steps():
    scale = [0, 2, 3, 5, 7, 8, 10]
    assert chord(scale, 0) == [0, 3, 7]
    assert chord(scale, 4) == [7, 10, 14]


@pytest.mark.parametrize("bpm", [60, 120, 128, 133])
def test_p12_r06_section_count_lasts_at_least_a_minute(bpm):
    count = section_count(bpm)
    seconds = count * SECTION_BARS * BEATS_PER_BAR * 60 / bpm
    assert seconds >= 60
    assert (count - 1) * SECTION_BARS * BEATS_PER_BAR * 60 / bpm < 60


def test_p12_r06_tempo_stays_in_the_style_range():
    style = WORLD_STYLES[1]
    assert tempo_of(request(), at(0.0)) == style.tempo[0]
    assert tempo_of(request(), at(0.999)) == style.tempo[1]


def test_p12_r07_boss_tempo_is_boosted_above_the_level_tempo():
    style = WORLD_STYLES[1]
    low = tempo_of(request(boss=True), at(0.0))
    high = tempo_of(request(boss=True), at(0.999))
    assert low >= style.tempo[1] + style.boss_boost[0]
    assert high <= style.tempo[1] + style.boss_boost[1] + 1
    assert high > low


def test_p12_r07_boss_energies_are_full_with_one_breath_before_the_end():
    shape = energies(request(boss=True), 5, create_rng(1))
    assert shape == [2, 2, 2, 1, 2]


def test_p12_r06_level_energies_follow_the_level_shape():
    shape = energies(request(), 6, at(0.0))
    assert any(shape == [s[i % len(s)] for i in range(6)] for s in LEVEL_ENERGIES)


def test_p12_r06_menu_style_uses_its_own_energy_shape():
    menu = TrackRequest("menu", MENU_STYLE, 1, False)
    assert energies(menu, 4, at(0.0)) == [1, 2, 1, 2]


def test_p12_r06_sections_repeat_their_themes_in_track_order():
    listed = sections(request(), 6, create_rng(5))
    assert len(listed) == 6
    assert all(isinstance(s, Section) for s in listed)
    assert len({tuple(s.progression) for s in listed}) <= 3


def test_p12_r06_compose_track_is_deterministic_for_a_seed(char_codes):
    a = compose_track(request(seed=11))
    b = compose_track(request(seed=11))
    assert [(n.beat, n.pitch, n.instrument) for n in a.notes] == [
        (n.beat, n.pitch, n.instrument) for n in b.notes
    ]


def test_p12_r06_compose_track_changes_with_the_seed(char_codes):
    a = compose_track(request(seed=11))
    b = compose_track(request(seed=12))
    assert [n.pitch for n in a.notes] != [n.pitch for n in b.notes]


def test_p12_r06_compose_track_is_a_looping_track_of_whole_sections(char_codes):
    track = compose_track(request(seed=3, track_id="level-1-3"))
    assert track.id == "level-1-3"
    assert track.loop is True
    sections_count = track.beats / (SECTION_BARS * BEATS_PER_BAR)
    assert sections_count == int(sections_count)
    assert sections_count >= math.ceil(60 * track.bpm / 60 / BEATS_PER_BAR / SECTION_BARS)
    assert WORLD_STYLES[1].tempo[0] <= track.bpm <= WORLD_STYLES[1].tempo[1]


def test_p12_r06_compose_track_notes_are_sorted_by_beat(char_codes):
    track = compose_track(request(seed=21))
    beats = [n.beat for n in track.notes]
    assert beats == sorted(beats)
    assert all(0 <= n.velocity <= 1 for n in track.notes)


def test_p12_r07_boss_track_is_faster_and_plays_the_boss_parts(char_codes):
    track = compose_track(request(boss=True, seed=4, track_id="boss-1"))
    assert track.bpm >= WORLD_STYLES[1].tempo[1] + WORLD_STYLES[1].boss_boost[0]
    instruments = {n.instrument for n in track.notes}
    assert "stab" in instruments
    assert "riser" in instruments


def test_p12_r06_menu_track_has_no_boss_stabs(char_codes):
    track = compose_track(TrackRequest("menu", MENU_STYLE, 2, False))
    assert "stab" not in {n.instrument for n in track.notes}


def test_shift_bar_is_inside_the_section():
    assert 0 <= SHIFT_BAR < SECTION_BARS
