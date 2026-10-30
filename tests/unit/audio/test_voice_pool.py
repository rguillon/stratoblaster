"""Unit tests of `src/audio/voice_pool.py`."""

from audio.voice_pool import VoicePool


def test_p12_r10_a_sound_plays_when_a_voice_is_free() -> None:
    pool = VoicePool(2, 0.03)
    decision = pool.request("shot", 1, 0.0, 0.2)
    assert decision.play is True
    assert decision.evicted is None
    assert decision.retrigger is False
    assert [v.name for v in pool.voices] == ["shot"]


def test_p12_r10_the_same_sound_again_too_soon_is_not_played_twice() -> None:
    pool = VoicePool(4, 0.03)
    pool.request("shot", 1, 0.0, 0.2)
    decision = pool.request("shot", 1, 0.01, 0.2)
    assert decision.play is False
    assert decision.retrigger is True
    assert len(pool.voices) == 1


def test_p12_r10_the_same_sound_is_played_again_after_the_retrigger_window() -> None:
    pool = VoicePool(4, 0.03)
    pool.request("shot", 1, 0.0, 0.01)
    assert pool.request("shot", 1, 0.05, 0.2).play is True


def test_p12_r10_a_full_pool_replaces_the_oldest_voice_of_lower_priority() -> None:
    pool = VoicePool(2, 0.0)
    old = pool.request("a", 1, 0.0, 5).id
    pool.request("b", 1, 0.1, 5)
    decision = pool.request("c", 2, 0.2, 1)
    assert decision.play is True
    assert decision.evicted is not None
    assert decision.evicted.id == old
    assert sorted(v.name for v in pool.voices) == ["b", "c"]


def test_p12_r10_a_full_pool_drops_a_sound_when_nothing_is_of_lower_priority() -> None:
    pool = VoicePool(1, 0.0)
    pool.request("boss", 5, 0.0, 5)
    decision = pool.request("tick", 1, 0.1, 1)
    assert decision.play is False
    assert decision.evicted is None
    assert [v.name for v in pool.voices] == ["boss"]


def test_p12_r10_finished_voices_free_their_place() -> None:
    pool = VoicePool(1, 0.0)
    pool.request("a", 1, 0.0, 0.5)
    assert pool.request("b", 1, 1.0, 0.5).evicted is None


def test_p12_r11_a_released_voice_is_forgotten() -> None:
    pool = VoicePool(1, 0.0)
    decision = pool.request("hum", 1, 0.0, float("inf"))
    pool.release(decision.id)
    pool.release(999)
    assert pool.voices == []
    assert pool.request("tick", 1, 0.1, 0.1).play is True


def test_p12_r11_clear_forgets_every_voice_and_the_last_starts() -> None:
    pool = VoicePool(4, 1.0)
    pool.request("shot", 1, 0.0, 5)
    pool.clear()
    assert pool.voices == []
    assert pool.request("shot", 1, 0.1, 0.2).retrigger is False
