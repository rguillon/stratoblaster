"""Unit tests of `src/core/math/pixel_contrast.py`."""

import pytest

from core.math.pixel_contrast import (
    PixelBox,
    Pixels,
    ReadabilityReport,
    box_contrast,
    brightest_but,
    luminance_at,
)

BLACK = [0, 0, 0, 255]

WHITE = [255, 255, 255, 255]


def _image(width: int, height: int, pixels: list[list[int]]) -> Pixels:
    data: list[int] = []
    for pixel in pixels:
        data.extend(pixel)
    return Pixels(width, height, data)


def test_luminance_of_black_and_white() -> None:
    image = _image(1, 1, [BLACK])
    assert luminance_at(image, 0, 0) == pytest.approx(0.0)
    assert luminance_at(_image(1, 1, [WHITE]), 0, 0) == pytest.approx(1.0)


def test_luminance_reads_the_pixel_at_the_given_coordinates() -> None:
    image = _image(2, 2, [BLACK, WHITE, WHITE, BLACK])
    assert luminance_at(image, 1, 0) == pytest.approx(1.0)
    assert luminance_at(image, 0, 1) == pytest.approx(1.0)
    assert luminance_at(image, 0, 0) == pytest.approx(0.0)


def test_luminance_of_missing_data_is_black() -> None:
    image = Pixels(1, 1, [])
    assert luminance_at(image, 0, 0) == pytest.approx(0.0)


def test_p14_r08_box_contrast_of_white_on_black_is_twenty_one() -> None:
    frame = _image(2, 1, [WHITE, WHITE])
    background = _image(2, 1, [BLACK, BLACK])
    assert box_contrast(frame, background, PixelBox(0.5, 0, 0.5)) == pytest.approx(21.0)


def test_p14_r08_box_contrast_is_one_when_the_box_is_off_the_image() -> None:
    image = _image(2, 1, [WHITE, WHITE])
    assert box_contrast(image, image, PixelBox(50, 50, 2)) == pytest.approx(1.0)


def test_box_contrast_uses_the_median_of_the_background() -> None:
    frame = _image(3, 1, [WHITE, WHITE, WHITE])
    # Background luminances 0, 0, 1: the median is 0 (the middle one once sorted).
    background = _image(3, 1, [BLACK, BLACK, WHITE])
    assert box_contrast(frame, background, PixelBox(1, 0, 1)) == pytest.approx(21.0)
    # The median of an all-white background is 1: no contrast on white.
    all_white = _image(3, 1, [WHITE, WHITE, WHITE])
    assert box_contrast(frame, all_white, PixelBox(1, 0, 1)) == pytest.approx(1.0)


def test_box_contrast_with_an_empty_background_uses_black() -> None:
    frame = _image(1, 1, [WHITE])
    empty = Pixels(0, 0, [])
    assert box_contrast(frame, empty, PixelBox(0, 0, 0)) == pytest.approx(21.0)


def test_box_rounds_halves_up_like_javascript() -> None:
    # A box centred on x = 0.5 with no radius covers pixel 1 (Math.round(0.5) is 1).
    frame = _image(3, 1, [BLACK, WHITE, BLACK])
    background = _image(3, 1, [BLACK, BLACK, BLACK])
    assert box_contrast(frame, background, PixelBox(0.5, 0, 0)) == pytest.approx(21.0)


def test_brightest_but_zero_share_is_the_brightest_pixel() -> None:
    image = _image(4, 1, [[0, 0, 0, 255], [64, 64, 64, 255], [128, 128, 128, 255], WHITE])
    assert brightest_but(image, 0) == pytest.approx(1.0)


def test_brightest_but_full_share_is_the_darkest_pixel() -> None:
    image = _image(4, 1, [[0, 0, 0, 255], [64, 64, 64, 255], [128, 128, 128, 255], WHITE])
    assert brightest_but(image, 1) == pytest.approx(0.0)


def test_brightest_but_picks_the_quantile() -> None:
    grey = [[v, v, v, 255] for v in (0, 64, 128, 255)]
    image = _image(4, 1, grey)
    middle = brightest_but(image, 0.5)
    assert 0 < middle < 1
    assert middle == pytest.approx(luminance_at(image, 1, 0))


def test_brightest_but_of_an_empty_image_is_zero() -> None:
    assert brightest_but(Pixels(0, 0, []), 0.5) == 0.0


def test_readability_report_keeps_its_fields() -> None:
    report = ReadabilityReport(1.0, None, 2.5, None, 0.3)
    assert report.player == 1.0
    assert report.enemy is None
    assert report.enemy_bullet == 2.5
    assert report.player_shot is None
    assert report.background_luminance == 0.3
