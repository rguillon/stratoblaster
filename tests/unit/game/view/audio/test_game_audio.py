# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/audio/game_audio.py`."""

from typing import Any

import pytest

import game.view.audio.compose_track as compose_track_module
from audio.audio_bindings import MusicRequest
from audio.audio_types import Track
from game.view.audio import game_audio
from game.view.audio.jingles import JINGLES
from game.view.audio.music_styles import WORLD_STYLES


@pytest.fixture(autouse=True)
def fresh_cache(monkeypatch: Any) -> None:
    """Each test composes its own tracks: the cache of made tracks starts empty."""
    monkeypatch.setattr(game_audio, "made", {})
    # JavaScript-only helpers: CPython reads the level id and the characters itself.
    monkeypatch.setattr(game_audio, "world_of", lambda level_id: int(level_id.split("-")[0]))
    monkeypatch.setattr(compose_track_module, "char_code_at", lambda text, index: ord(text[index]))


def test_aud_music_11_the_menu_request_gives_the_menu_track() -> None:
    track = game_audio.game_music(MusicRequest("menu", None, None))
    assert isinstance(track, Track)
    assert track.id == "menu"
    assert track.loop is True


def test_aud_music_02_a_level_request_gives_that_levels_own_track() -> None:
    """Also WLD-2-28: level 2-3 plays World 2's style."""
    track = game_audio.game_music(MusicRequest("level", "2-3", None))
    assert track.id == "level-2-3"
    assert track.loop is True
    assert track.bpm >= WORLD_STYLES[2].tempo[0]


def test_aud_music_07_a_boss_request_gives_the_worlds_boss_track() -> None:
    """Also WLD-3-21: World 3's boss track."""
    track = game_audio.game_music(MusicRequest("boss", "3-1", None))
    assert track.id == "boss-3"
    assert track.bpm > WORLD_STYLES[3].tempo[1]


def test_aud_music_01_tracks_are_composed_once_and_kept() -> None:
    first = game_audio.game_music(MusicRequest("level", "1-1", None))
    second = game_audio.game_music(MusicRequest("level", "1-1", None))
    assert first is second


def test_aud_music_10_a_jingle_request_gives_the_named_jingle() -> None:
    assert game_audio.game_music(MusicRequest("jingle", None, "over")) is JINGLES["over"]


def test_aud_music_10_an_unknown_jingle_or_kind_is_silence() -> None:
    assert game_audio.game_music(MusicRequest("jingle", None, "nope")) is None
    assert game_audio.game_music(MusicRequest("jingle", None, None)) is None
    assert game_audio.game_music(MusicRequest("silence", None, None)) is None


def test_a_world_without_a_style_is_silence() -> None:
    assert game_audio.game_music(MusicRequest("level", "9-1", None)) is None
    assert game_audio.game_music(MusicRequest("boss", "9-1", None)) is None


def test_aud_engine_13_the_bindings_take_the_music_instruments_sounds_and_mix() -> None:
    bindings = game_audio.GAME_AUDIO
    assert bindings.music is game_audio.game_music
    assert bindings.large_blast_radius == game_audio.LARGE_BLAST_RADIUS
    assert bindings.mix is game_audio.MIX
    assert bindings.effects is game_audio.EFFECTS
    assert "bomb" in bindings.sounds
    assert "kick" in bindings.instruments


def test_aud_engine_02_the_buses_are_mixed_at_their_set_levels() -> None:
    """Also AUD-ENGINE-06: the echo the instruments send to."""
    assert game_audio.MIX.music == 0.8
    assert game_audio.MIX.sfx == 1
    assert game_audio.EFFECTS.echo_beats == 0.75
