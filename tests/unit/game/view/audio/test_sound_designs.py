"""Unit tests of `src/game/view/audio/sound_designs.py`."""

from audio.audio_types import SoundDesign
from game.view.audio.sound_designs import (
    BLAST_HUGE,
    BLAST_LARGE,
    BLAST_SMALL,
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
from game.view.audio.sound_recipes import env, tone


def test_p12_r10_priorities_put_the_player_top_and_enemy_shots_lowest():
    assert PRIORITY["enemyShot"] == min(PRIORITY.values())
    assert PRIORITY["top"] == max(PRIORITY.values())
    assert PRIORITY["player"] > PRIORITY["weapon"] > PRIORITY["enemy"]


def test_sound_builds_a_design_and_flattens_its_layers():
    a = tone("sine", 100, 1, env(0.1, 0.1), {})
    b = tone("noise", 1, 1, env(0.1, 0.1), {})
    design = sound("cue", 3, 0.5, [a, [b]], {"positional": True, "loop": True, "hold": 1.5})
    assert isinstance(design, SoundDesign)
    assert design.name == "cue"
    assert design.layers == [a, b]
    assert (design.gain, design.priority, design.hold) == (0.5, 3, 1.5)
    assert design.positional is True and design.loop is True


def test_sound_defaults_its_hold_and_optional_flags():
    design = sound("cue", 1, 1, [], {})
    assert design.hold == 0
    assert design.positional is None and design.loop is None


def test_p12_r09_the_player_gun_is_a_positional_quiet_burst():
    gun = PLAYER_WEAPONS["fire:bullet"]
    assert gun.name == "gun-shot"
    assert gun.positional is True
    assert gun.gain < PLAYER_WEAPONS["fire:missile"].gain
    assert len(gun.layers) == 12


def test_p12_r09_the_laser_hum_loops_until_stopped():
    assert PLAYER_WEAPONS["beam:laser"].loop is True
    assert PLAYER_WEAPONS["beam:laser"].gain < PLAYER_WEAPONS["beam-start:laser"].gain


def test_p12_r09_every_group_is_in_the_merged_sound_table():
    groups = [PLAYER_WEAPONS, ENEMY_WEAPONS, HITS, DESTRUCTION, PLAYER, MENUS]
    keys = [key for group in groups for key in group]
    assert len(keys) == len(set(keys))
    assert set(SOUND_DESIGNS) == set(keys)
    assert SOUND_DESIGNS["enemy-bullet"] is ENEMY_WEAPONS["enemy-bullet"]


def test_p12_r10_enemy_shots_are_the_lowest_priority_sounds():
    assert ENEMY_WEAPONS["enemy-bullet"].priority == PRIORITY["enemyShot"]
    assert ENEMY_WEAPONS["enemy-missile"].priority == PRIORITY["enemyShot"]
    assert ENEMY_WEAPONS["laser-warning"].priority == PRIORITY["enemy"]
    assert ENEMY_WEAPONS["laser-fire"].priority == PRIORITY["enemy"]


def test_p12_r09_explosion_sizes_grow_from_small_to_huge():
    assert BLAST_SMALL.seconds < BLAST_LARGE.seconds < BLAST_HUGE.seconds
    assert BLAST_SMALL.debris < BLAST_LARGE.debris < BLAST_HUGE.debris
    assert BLAST_SMALL.tail == 0 < BLAST_LARGE.tail < BLAST_HUGE.tail
    assert BLAST_HUGE.thump < BLAST_SMALL.thump


def test_p12_r09_the_blast_cues_name_their_explosions():
    assert DESTRUCTION["blast-large"].name == "explosion-large"
    assert DESTRUCTION["blast-small"].name == "explosion-small"
    assert DESTRUCTION["blast-large"].layers
    assert DESTRUCTION["blast-small"].layers
