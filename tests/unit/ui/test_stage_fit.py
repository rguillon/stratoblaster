# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/stage_fit.py`."""

from helpers.dom import FakeDocument

from core.content.game_definition import LogicalScreen
from ui.stage_fit import apply_stage_fit, fit_stage, phone_layout, render_ratio

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
