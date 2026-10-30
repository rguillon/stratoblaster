"""Unit tests of `src/config/shot_viewer.py`."""

from config.shot_viewer import SHOT_VIEWER_CONFIG


def test_p03_r10_the_shots_page_runs_at_the_game_rate() -> None:
    assert SHOT_VIEWER_CONFIG.step_hz == 60
    assert SHOT_VIEWER_CONFIG.max_steps_per_frame >= 1


def test_p03_r10_the_clear_colour_is_an_opaque_rgba() -> None:
    assert len(SHOT_VIEWER_CONFIG.clear_color) == 4
    assert SHOT_VIEWER_CONFIG.clear_color[3] == 1


def test_p03_r10_there_are_six_targets_each_with_an_anchor() -> None:
    targets = SHOT_VIEWER_CONFIG.targets
    assert len(targets.anchors) == 6
    assert all(0 < anchor.x < 480 for anchor in targets.anchors)
    assert targets.max_health > 0
    assert targets.respawn_seconds > 0
    assert targets.ring.thickness > 0
    assert targets.health_bar.width > 0


def test_p03_r10_the_grid_and_the_guides_are_faint_reference_lines() -> None:
    assert SHOT_VIEWER_CONFIG.grid.cell > 0
    assert SHOT_VIEWER_CONFIG.guides.length_ > 0
    assert SHOT_VIEWER_CONFIG.damage_rate_window > 0
