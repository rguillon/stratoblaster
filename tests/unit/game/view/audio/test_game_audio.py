"""Unit tests of `src/game/view/audio/game_audio.py`."""

import pytest

import game.view.audio.compose_track as compose_track_module
from audio.audio_bindings import MusicRequest
from audio.audio_types import Track
from game.view.audio import game_audio
from game.view.audio.jingles import JINGLES
from game.view.audio.music_styles import WORLD_STYLES


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch):
    """Each test composes its own tracks: the cache of made tracks starts empty."""
    monkeypatch.setattr(game_audio, "made", {})
    # JavaScript-only helpers: CPython reads the level id and the characters itself.
    monkeypatch.setattr(game_audio, "world_of", lambda level_id: int(level_id.split("-")[0]))
    monkeypatch.setattr(compose_track_module, "char_code_at", lambda text, index: ord(text[index]))


def test_p12_r06_the_menu_request_gives_the_menu_track():
    track = game_audio.game_music(MusicRequest("menu", None, None))
    assert isinstance(track, Track)
    assert track.id == "menu"
    assert track.loop is True


def test_p12_r06_a_level_request_gives_that_levels_own_track():
    track = game_audio.game_music(MusicRequest("level", "2-3", None))
    assert track.id == "level-2-3"
    assert track.loop is True
    assert track.bpm >= WORLD_STYLES[2].tempo[0]


def test_p12_r07_a_boss_request_gives_the_worlds_boss_track():
    track = game_audio.game_music(MusicRequest("boss", "3-1", None))
    assert track.id == "boss-3"
    assert track.bpm > WORLD_STYLES[3].tempo[1]


def test_p12_r06_tracks_are_composed_once_and_kept():
    first = game_audio.game_music(MusicRequest("level", "1-1", None))
    second = game_audio.game_music(MusicRequest("level", "1-1", None))
    assert first is second


def test_p12_r07_a_jingle_request_gives_the_named_jingle():
    assert game_audio.game_music(MusicRequest("jingle", None, "over")) is JINGLES["over"]


def test_p12_r07_an_unknown_jingle_or_kind_is_silence():
    assert game_audio.game_music(MusicRequest("jingle", None, "nope")) is None
    assert game_audio.game_music(MusicRequest("jingle", None, None)) is None
    assert game_audio.game_music(MusicRequest("silence", None, None)) is None


def test_a_world_without_a_style_is_silence():
    assert game_audio.game_music(MusicRequest("level", "9-1", None)) is None
    assert game_audio.game_music(MusicRequest("boss", "9-1", None)) is None


def test_p12_r05_the_bindings_take_the_music_instruments_sounds_and_mix():
    bindings = game_audio.GAME_AUDIO
    assert bindings.music is game_audio.game_music
    assert bindings.large_blast_radius == game_audio.LARGE_BLAST_RADIUS
    assert bindings.mix is game_audio.MIX
    assert bindings.effects is game_audio.EFFECTS
    assert "bomb" in bindings.sounds
    assert "kick" in bindings.instruments


def test_p12_r10_the_buses_are_mixed_at_their_set_levels():
    assert game_audio.MIX.music == 0.8
    assert game_audio.MIX.sfx == 1
    assert game_audio.EFFECTS.echo_beats == 0.75
