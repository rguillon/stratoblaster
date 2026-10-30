"""Unit tests of `src/audio/audio_bindings.py`."""

from audio.audio_bindings import AudioBindings, AudioMix, MusicRequest


def test_p12_r05_a_music_request_names_a_level_a_boss_or_a_jingle() -> None:
    level = MusicRequest("level", "level-2", None)
    assert (level.kind, level.level_id, level.jingle) == ("level", "level-2", None)
    jingle = MusicRequest("jingle", None, "complete")
    assert jingle.jingle == "complete"
    assert jingle.level_id is None


def test_p12_r05_the_bindings_keep_the_game_s_music_sounds_and_mix() -> None:
    mix = AudioMix(0.6, 1.0)

    def music(request: MusicRequest) -> None:
        return None

    bindings = AudioBindings(music, {}, {}, 40, mix)
    assert bindings.music is music
    assert bindings.large_blast_radius == 40
    assert bindings.mix is mix
    assert bindings.effects is None
