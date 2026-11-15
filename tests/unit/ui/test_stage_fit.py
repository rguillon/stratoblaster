# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/stage_fit.py`."""

import pytest
from helpers.dom import FakeDocument

from core.content.game_definition import LogicalScreen
from ui.stage_fit import (
    NARROW_SIDES_CLASS,
    StageFit,
    apply_stage_fit,
    fit_stage,
    phone_layout,
    render_ratio,
)

LOGICAL = LogicalScreen(640, 360)


def test_gd02_the_stage_is_the_largest_fit_of_the_logical_aspect_ratio() -> None:
    fit = fit_stage(1000, 1000, LOGICAL)
    assert fit.scale == 1000 / 640
    assert fit.width == 1000
    assert fit.height == 562
    assert fit.left == 0
    assert fit.top == 219


def test_gd02_a_wide_window_fits_by_height_and_is_centred_across() -> None:
    fit = fit_stage(1280, 360, LOGICAL)
    assert fit.scale == 1
    assert fit.width == 640
    assert fit.height == 360
    assert fit.left == 320
    assert fit.top == 0


def test_gd03_a_window_with_no_room_gives_no_scale() -> None:
    fit = fit_stage(0, 0, LOGICAL)
    assert fit.scale == 0
    assert fit.width == 0
    assert fit.height == 0


def test_gd03_applying_the_fit_places_the_stage_and_scales_the_overlay() -> None:
    doc = FakeDocument()
    stage = doc.createElement("div")
    overlay = doc.createElement("div")
    fit = fit_stage(1280, 720, LOGICAL)
    apply_stage_fit(stage, overlay, fit, LOGICAL)
    assert stage.style.width == "1280.0px"
    assert stage.style.height == "720.0px"
    assert stage.style.left == "0.0px"
    assert overlay.style.width == "640px"
    assert overlay.style.height == "360px"
    assert overlay.style.transform == "scale(2.0)"


def test_eng_110_the_render_ratio_caps_the_pixels_drawn_per_logical_pixel() -> None:
    """D-250: a 4K panel (ratio 2, the stage 1280 CSS px wide for 640 logical) draws at 1.5 x."""
    assert render_ratio(2, fit_stage(1280, 720, LOGICAL), 1.5) == 0.75
    # A small window: the device ratio is under the cap, so it stays.
    assert render_ratio(2, fit_stage(320, 180, LOGICAL), 1.5) == 2
    # A stage with no room keeps the device ratio.
    assert render_ratio(2, fit_stage(0, 0, LOGICAL), 1.5) == 2


def test_ui_look_02_a_stage_scaled_under_a_half_lays_the_menus_out_for_a_phone() -> None:
    """D-286: a 390 px wide phone shows the 1280 x 720 stage at 0.3: the overlay gets `phone`."""
    screen = LogicalScreen(1280, 720)
    phone = fit_stage(390, 844, screen)
    desk = fit_stage(800, 600, screen)
    assert phone_layout(phone)
    assert not phone_layout(desk)
    assert not phone_layout(fit_stage(0, 0, screen))
    doc = FakeDocument()
    stage = doc.createElement("div")
    overlay = doc.createElement("div")
    apply_stage_fit(stage, overlay, phone, screen)
    assert overlay.classList.contains("phone")
    apply_stage_fit(stage, overlay, desk, screen)
    assert not overlay.classList.contains("phone")


SCREEN = LogicalScreen(1280, 720)
# The 540 x 720 playfield window in the middle of the 1280 x 720 screen (D-252).
PLAYFIELD = LogicalScreen(540, 720, (370 / 1280, 0, 540 / 1280, 1))


def _window_box(fit: StageFit) -> tuple[float, float, float, float]:
    """Return the playfield window's left, top, width and height in the browser window."""
    left = fit.left + 370 * fit.scale
    return left, fit.top, 540 * fit.scale, 720 * fit.scale


def test_gd02_a_narrow_window_keeps_the_playfield_large_cropping_only_the_side_columns() -> None:
    """Owner: "the display area get small for no good reason when I play with the browser size".

    A 1000 x 900 window showed the playfield at 421 x 562, fitting the whole 16:9 stage; now the
    playfield fills the height, centred, the side columns running past the window's edges.
    """
    fit = fit_stage(1000, 900, SCREEN, PLAYFIELD)
    assert fit.scale == 1.25
    assert fit.width / fit.height == 1280 / 720
    left, top, width, height = _window_box(fit)
    assert (width, height) == (675, 900)
    assert top == 0
    assert left == pytest.approx((1000 - 675) / 2, abs=1)
    assert left >= 0
    assert left + width <= 1000


def test_gd02_a_wide_window_still_shows_the_whole_stage_centred() -> None:
    assert fit_stage(1920, 1080, SCREEN, PLAYFIELD).left == 0
    fit = fit_stage(2560, 720, SCREEN, PLAYFIELD)
    assert fit.scale == 1
    assert fit.left == 640
    assert fit.width == 1280


def test_gd02_the_playfield_never_outgrows_the_window() -> None:
    for view in [(390, 844), (800, 600), (1000, 1400), (1280, 720), (3000, 500)]:
        fit = fit_stage(view[0], view[1], SCREEN, PLAYFIELD)
        left, top, width, height = _window_box(fit)
        # Within the pixel the stage's place is floored to.
        assert left >= -1
        assert top >= 0
        assert left + width <= view[0] + 1
        assert top + height <= view[1] + 1
        assert max(width / view[0], height / view[1]) > 0.99


def test_ui_look_02_a_phone_keeps_its_layout_with_the_larger_playfield() -> None:
    """D-286: the phone layout is measured on the whole stage, as before; the playfield grows."""
    fit = fit_stage(390, 844, SCREEN, PLAYFIELD)
    assert phone_layout(fit)
    assert fit.scale == pytest.approx(390 / 540)
    assert not phone_layout(fit_stage(800, 600, SCREEN, PLAYFIELD))


def test_gd02_the_side_room_is_the_part_of_the_right_column_in_view() -> None:
    """D-329: the touch buttons sit in the right column; how much of it the window shows."""
    assert fit_stage(1920, 1080, SCREEN, PLAYFIELD).side_room == pytest.approx(370)
    # 1000 x 900: the window, 675 px wide, centred; 162 px of column at 1.25 on its right.
    assert fit_stage(1000, 900, SCREEN, PLAYFIELD).side_room == pytest.approx(130, abs=1)
    # A phone: the playfield fills the width, no column in view.
    assert fit_stage(390, 844, SCREEN, PLAYFIELD).side_room == pytest.approx(0, abs=2)
    assert fit_stage(1000, 900, SCREEN).side_room is None


def test_gd02_too_little_side_room_moves_the_touch_buttons_into_the_window() -> None:
    doc = FakeDocument()
    stage = doc.createElement("div")
    overlay = doc.createElement("div")
    apply_stage_fit(stage, overlay, fit_stage(1920, 1080, SCREEN, PLAYFIELD), SCREEN)
    assert overlay.style.getPropertyValue("--side-room") == "370.0px"
    assert not overlay.classList.contains(NARROW_SIDES_CLASS)
    apply_stage_fit(stage, overlay, fit_stage(1000, 900, SCREEN, PLAYFIELD), SCREEN)
    assert overlay.classList.contains(NARROW_SIDES_CLASS)
