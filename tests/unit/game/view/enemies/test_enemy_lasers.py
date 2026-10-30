"""Unit tests of `src/game/view/enemies/enemy_lasers.py`."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from core.math.color import fold_into_family
from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY
from game.view.enemies import enemy_lasers as el


def test_p14_r02_a_laser_colour_is_its_boss_neon_folded_into_the_shots_family():
    color = el.color_of("scorpion")
    assert len(color) == 3
    # The folded colour keeps the neon's brightness, but moves its hue into the shots' family.
    neon = BOSS_LOOK.neon["scorpion"]
    assert max(color) == pytest.approx(max(neon), abs=1e-6)


def test_a_style_without_a_boss_neon_takes_the_laser_look_colour(monkeypatch):
    monkeypatch.setitem(BOSS_LOOK.neon, "bare-style", None)
    folded = fold_into_family(el.LOOK.color, READABILITY.families.enemyShot)
    assert el.color_of("bare-style") == pytest.approx(folded)


def test_p10_r07_contrast_warning_is_a_white_core_then_the_colour_then_dark_edges():
    color = [0.5, 0.0, 1.0]
    t = ENEMY_LOOK.contrast.warningCore
    warning = el.contrast_warning(color)
    assert len(warning) == 4
    # The core is lifted towards white by warningCore.
    assert warning[0] == pytest.approx([0.5 + 0.5 * t, t, 1.0])
    assert warning[1] == pytest.approx(color)
    assert warning[2] == pytest.approx([0.25, 0, 0.5])
    assert warning[3] == pytest.approx([0, 0, 0])


def test_sync_warnings_shows_one_line_per_warning_and_blinks_its_width(monkeypatch):
    monkeypatch.setattr(el.LOOK.warning, "blinkHz", 1.0, raising=False)
    meshes = [MagicMock() for _ in range(2)]
    pool = MagicMock()
    pool.show.return_value = meshes
    warnings = [
        SimpleNamespace(x=1.0, y=2.0, heading=0.5, length=10.0),
        SimpleNamespace(x=3.0, y=4.0, heading=0.0, length=5.0),
    ]
    # At a time when the blink is on (sin > 0), the lines are drawn at full width.
    el.sync_warnings(pool, warnings, time=0.25, width=2.0)
    pool.show.assert_called_once_with(2)
    meshes[0].position.set.assert_called_once_with(1.0, 2.0, -0.8)
    meshes[0].rotation.z = -0.5
    meshes[0].scaling.set.assert_called_once_with(2.0, 10.0, 1)
    meshes[1].scaling.set.assert_called_once_with(2.0, 5.0, 1)


def test_sync_warnings_draws_the_lines_at_half_width_while_the_blink_is_off(monkeypatch):
    monkeypatch.setattr(el.LOOK.warning, "blinkHz", 1.0, raising=False)
    mesh = MagicMock()
    pool = MagicMock()
    pool.show.return_value = [mesh]
    el.sync_warnings(pool, [SimpleNamespace(x=0, y=0, heading=0, length=4)], time=0.75, width=2.0)
    mesh.scaling.set.assert_called_once_with(1.0, 4, 1)


def test_sync_warnings_leaves_spare_pooled_lines_alone():
    mesh = MagicMock()
    pool = MagicMock()
    pool.show.return_value = [mesh]
    el.sync_warnings(pool, [], time=0.0, width=1.0)
    mesh.position.set.assert_not_called()
    mesh.scaling.set.assert_not_called()


def test_the_readability_families_used_for_lasers_exist():
    assert "enemyShot" in READABILITY.families
