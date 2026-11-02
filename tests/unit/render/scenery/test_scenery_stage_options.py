# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/scenery_stage_options.py`: what a scenery stage is made of."""

from helpers.render_looks import make_look
from helpers.sample_level import sample_level

from core.content.game_definition import LogicalScreen
from render.scenery.atmosphere_of import AtmosphereOptions
from render.scenery.scenery_look import PlayfieldCameraLook
from render.scenery.scenery_stage_options import SceneryStageConfig, SceneryStageOptions


def _config() -> SceneryStageConfig:
    return SceneryStageConfig(320, 4, 40, 15, 900, 4000, (60, 120), 50, 2, 30)


def test_the_stage_config_keeps_each_setting_under_its_own_name() -> None:
    config = _config()
    assert (config.chunk_length, config.cell, config.margin) == (320, 4, 40)
    assert (config.cloud_clearance, config.sun_distance, config.far_clip) == (15, 900, 4000)
    assert config.prop_reach == (60, 120)
    assert config.prop_step == 50
    # D-216 and D-212: the camera's near clip and how far a tree can be seen.
    assert config.near_clip == 2
    assert config.tree_reach == 30


def test_the_stage_options_hold_their_parts_and_have_no_debug_atmosphere_by_default() -> None:
    screen = LogicalScreen(600, 800)
    camera = PlayfieldCameraLook(30, 50, 120, 2)
    level = sample_level()
    look = make_look()
    models = {"block": "block-model"}

    def kit(_scene: object, _context: object) -> str:
        return "kit"

    config = _config()
    options = SceneryStageOptions(screen, camera, level, look, models, kit, config)
    assert options.screen is screen
    assert options.camera is camera
    assert options.level is level
    assert options.look is look
    assert options.prop_models is models
    assert options.kit is kit
    assert options.config is config
    assert options.atmosphere is None


def test_dev_opt_04_the_stage_options_carry_the_debug_atmosphere_choices() -> None:
    choices = AtmosphereOptions("night", weather=False)
    options = SceneryStageOptions(
        LogicalScreen(600, 800),
        PlayfieldCameraLook(30, 50, 120, 2),
        sample_level(),
        make_look(),
        {},
        lambda _scene, _context: None,
        _config(),
        choices,
    )
    assert options.atmosphere is choices
    assert options.atmosphere.weather is False
