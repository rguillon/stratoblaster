# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/view/audio/sound_designs.py`."""

from audio.audio_types import SoundDesign
from game.view.audio.game_audio import MIX
from game.view.audio.instruments import INSTRUMENTS
from game.view.audio.sound_designs import (
    DESTRUCTION,
    ENEMY_WEAPONS,
    HITS,
    MENUS,
    PLAYER,
    PLAYER_WEAPONS,
    PRIORITY,
    SOUND_DESIGNS,
    sound,
)

# The samples are normalised to -1 dBFS (AUD-SFX-06).
SAMPLE_PEAK = 10 ** (-1 / 20)
# The loudest sound effect is at most this much (+6 dB) over the loudest instrument.
LOUDEST_SFX = 2


def test_aud_sfx_05_priorities_put_the_player_top_and_enemy_shots_lowest() -> None:
    assert PRIORITY["enemyShot"] == min(PRIORITY.values())
    assert PRIORITY["top"] == max(PRIORITY.values())
    assert PRIORITY["player"] > PRIORITY["weapon"] > PRIORITY["enemy"]


def test_aud_engine_01_sound_builds_a_design_playing_the_sample_of_its_name() -> None:
    design = sound("cue", 3, 0.5, 1.5, {"positional": True, "loop": True})
    assert isinstance(design, SoundDesign)
    assert (design.name, design.samples) == ("cue", ["cue"])
    assert (design.gain, design.priority, design.seconds) == (0.5, 3, 1.5)
    assert design.positional is True
    assert design.loop is True


def test_aud_sfx_09_a_sound_can_name_several_samples() -> None:
    design = sound("cue", 1, 1, 1, {"samples": ["a", "b"]})
    assert design.samples == ["a", "b"]


def test_aud_sfx_09_the_small_and_large_explosions_have_three_variants_each() -> None:
    for cue, name in [("blast-small", "explosion-small"), ("blast-large", "explosion-large")]:
        design = DESTRUCTION[cue]
        assert design.name == name
        assert design.samples == [name + "-1", name + "-2", name + "-3"]
    others = [d for cue, d in SOUND_DESIGNS.items() if cue not in ("blast-small", "blast-large")]
    assert all(len(d.samples) == 1 for d in others)


def test_sound_defaults_its_optional_flags() -> None:
    design = sound("cue", 1, 1, 0.2, {})
    assert design.positional is None
    assert design.loop is None


def test_aud_sfx_02_the_player_gun_is_a_positional_quiet_short_shot() -> None:
    """Also AUD-SFX-06 (the guns mixed quiet) and AUD-ENGINE-08 (panned by position)."""
    gun = PLAYER_WEAPONS["fire:bullet"]
    assert gun.name == "gun-shot"
    assert gun.positional is True
    assert gun.gain < PLAYER_WEAPONS["fire:missile"].gain
    # 8 volleys a second: the shot is over before the next but one.
    assert gun.seconds <= 0.25


def test_aud_sfx_01_the_laser_hum_loops_until_stopped() -> None:
    assert PLAYER_WEAPONS["beam:laser"].loop is True
    assert PLAYER_WEAPONS["beam:laser"].gain < PLAYER_WEAPONS["beam-start:laser"].gain


def test_aud_sfx_01_only_the_laser_hum_loops() -> None:
    assert [cue for cue, design in SOUND_DESIGNS.items() if design.loop] == ["beam:laser"]


def test_aud_sfx_01_every_group_is_in_the_merged_sound_table() -> None:
    groups = [PLAYER_WEAPONS, ENEMY_WEAPONS, HITS, DESTRUCTION, PLAYER, MENUS]
    keys = [key for group in groups for key in group]
    assert len(keys) == len(set(keys))
    assert set(SOUND_DESIGNS) == set(keys)
    assert SOUND_DESIGNS["enemy-bullet"] is ENEMY_WEAPONS["enemy-bullet"]


def test_aud_sfx_01_every_event_has_its_own_sound_and_sample() -> None:
    names = [design.name for design in SOUND_DESIGNS.values()]
    assert len(names) == len(set(names))
    assert len(names) == 30
    samples = [sample for design in SOUND_DESIGNS.values() for sample in design.samples]
    assert len(samples) == len(set(samples)) == 34
    for cue, design in SOUND_DESIGNS.items():
        assert design.samples
        assert all(sample.startswith(design.name) for sample in design.samples), cue
        assert design.seconds > 0, cue
        assert 0 < design.gain <= 1, cue


def test_aud_sfx_05_enemy_shots_are_the_lowest_priority_sounds() -> None:
    assert ENEMY_WEAPONS["enemy-bullet"].priority == PRIORITY["enemyShot"]
    assert ENEMY_WEAPONS["enemy-missile"].priority == PRIORITY["enemyShot"]
    assert ENEMY_WEAPONS["laser-warning"].priority == PRIORITY["enemy"]
    assert ENEMY_WEAPONS["laser-fire"].priority == PRIORITY["enemy"]


def test_aud_sfx_05_the_players_and_the_bombs_sounds_outrank_every_enemy_shot() -> None:
    enemy = max(design.priority for design in ENEMY_WEAPONS.values())
    for cue in ["player-hit", "bomb", "life-lost", "extra-life", "weapon-switch", "weapon-up"]:
        design = SOUND_DESIGNS[cue]
        assert design.priority > enemy, cue


def test_aud_sfx_04_the_blast_cues_name_their_explosions_and_grow_with_their_size() -> None:
    assert DESTRUCTION["blast-small"].name == "explosion-small"
    assert DESTRUCTION["blast-large"].name == "explosion-large"
    assert DESTRUCTION["blast-small"].seconds < DESTRUCTION["blast-large"].seconds
    assert DESTRUCTION["blast-large"].seconds < DESTRUCTION["boss-destroyed"].seconds


def test_aud_sfx_06_the_guns_and_the_hum_are_mixed_under_the_hits_and_explosions() -> None:
    quiet = [PLAYER_WEAPONS["fire:bullet"].gain, PLAYER_WEAPONS["beam:laser"].gain]
    loud = [HITS["hit"].gain, DESTRUCTION["blast-small"].gain, DESTRUCTION["blast-large"].gain]
    assert max(quiet) < min(loud)


def test_aud_sfx_06_the_loudest_sound_is_within_6_db_of_the_loudest_instrument() -> None:
    sfx = max(design.gain for design in SOUND_DESIGNS.values()) * SAMPLE_PEAK * MIX.sfx
    music = (
        max(
            instrument.gain * sum(layer.gain for layer in instrument.layers)
            for instrument in INSTRUMENTS.values()
        )
        * MIX.music
    )
    assert sfx <= LOUDEST_SFX * music


def test_aud_sfx_01_the_menu_sounds_are_short_and_play_at_top_priority() -> None:
    for cue, design in MENUS.items():
        assert design.priority == PRIORITY["top"], cue
        assert design.loop is None, cue
    assert max(MENUS[cue].seconds for cue in ["menu-move", "menu-confirm", "menu-back"]) < 0.1


def test_aud_sfx_10_the_blasts_and_the_parts_are_varied_at_random_and_nothing_else_is() -> None:
    varied = {cue for cue, design in SOUND_DESIGNS.items() if design.jitter is not None}
    assert varied == {"blast-small", "blast-large", "part-destroyed"}
    for cue in varied:
        jitter = SOUND_DESIGNS[cue].jitter
        assert 0 < jitter.pitch < 0.5
        assert 0 < jitter.gain < 1
        # Late by less than a blast of a boss dying is apart (BossDeath.every, 0.25 s).
        assert 0 < jitter.delay < 0.25
