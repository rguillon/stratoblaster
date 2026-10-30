"""Colour helpers (`core.math.color`, phase 14)."""

import pytest

from core.math.color import (
    contrast_ratio,
    fold_into_family,
    hue_saturation,
    in_family,
    relative_luminance,
    srgb_byte_to_linear,
)

RED_FAMILY = {"from": 330.0, "to": 30.0, "minSaturation": 0.2}
GREEN_FAMILY = {"from": 90.0, "to": 150.0, "minSaturation": 0.2}


def test_relative_luminance_weights_the_channels() -> None:
    assert relative_luminance([1, 1, 1]) == pytest.approx(1.0)
    assert relative_luminance([0, 0, 0]) == pytest.approx(0.0)
    assert relative_luminance([0, 1, 0]) == pytest.approx(0.7152)


def test_p14_srgb_byte_to_linear_uses_the_linear_segment_near_black() -> None:
    assert srgb_byte_to_linear(0) == pytest.approx(0.0)
    # 10 / 255 is below the sRGB threshold, so the linear segment applies.
    assert srgb_byte_to_linear(10) == pytest.approx((10 / 255) / 12.92)


def test_p14_srgb_byte_to_linear_uses_the_power_curve_elsewhere() -> None:
    assert srgb_byte_to_linear(255) == pytest.approx(1.0)
    assert srgb_byte_to_linear(128) == pytest.approx(0.2158605, rel=1e-5)


def test_contrast_ratio_spans_one_to_twenty_one() -> None:
    assert contrast_ratio(1.0, 0.0) == pytest.approx(21.0)
    assert contrast_ratio(0.0, 0.0) == pytest.approx(1.0)
    assert contrast_ratio(0.5, 0.5) == pytest.approx(1.0)


def test_contrast_ratio_does_not_depend_on_argument_order() -> None:
    assert contrast_ratio(0.2, 0.7) == pytest.approx(contrast_ratio(0.7, 0.2))


@pytest.mark.parametrize(
    ("color", "hue"),
    [
        ((1, 0, 0), 0.0),
        ((0, 1, 0), 120.0),
        ((0, 0, 1), 240.0),
        ((1, 1, 0), 60.0),
        ((1, 0, 1), 300.0),
        ((1, 0.5, 0), 30.0),
        # Red tilted towards blue wraps around to just below 360.
        ((1, 0, 0.5), 330.0),
    ],
)
def test_hue_saturation_gives_the_hue_in_degrees(color: tuple[float, ...], hue: float) -> None:
    got_hue, saturation = hue_saturation(color)
    assert got_hue == pytest.approx(hue)
    assert saturation == pytest.approx(1.0)


def test_hue_saturation_of_a_grey_is_zero() -> None:
    assert hue_saturation((0.4, 0.4, 0.4)) == (0.0, 0.0)
    assert hue_saturation((0, 0, 0)) == (0.0, 0.0)


def test_hue_saturation_of_a_pale_colour_is_partly_saturated() -> None:
    hue, saturation = hue_saturation((1.0, 0.5, 0.5))
    assert hue == pytest.approx(0.0)
    assert saturation == pytest.approx(0.5)


def test_p14_in_family_checks_the_hue_range_and_saturation() -> None:
    assert in_family((1, 0, 0), RED_FAMILY)
    assert in_family((1, 0, 0.2), RED_FAMILY)
    assert not in_family((0, 1, 0), RED_FAMILY)
    assert not in_family((0.5, 0.5, 0.5), RED_FAMILY)


def test_p14_in_family_needs_the_minimal_saturation() -> None:
    pale_red = (1.0, 0.95, 0.95)  # Saturation 0.05, below the family's 0.2.
    assert not in_family(pale_red, RED_FAMILY)


def test_p14_r02_fold_into_family_moves_the_hue_into_the_family() -> None:
    folded = fold_into_family((0, 1, 1), GREEN_FAMILY)  # Cyan: hue 180, outside.
    hue, _ = hue_saturation(folded)
    assert in_family(folded, GREEN_FAMILY)
    # Hue 180 is half way along the whole wheel, so half way along the family.
    assert hue == pytest.approx(90 + 0.5 * 60)


def test_p14_r02_fold_into_family_keeps_brightness_and_saturation() -> None:
    colour = (0.8, 0.2, 0.5)
    folded = fold_into_family(colour, GREEN_FAMILY)
    assert max(folded) == pytest.approx(max(colour))
    assert min(folded) == pytest.approx(min(colour))


def test_p14_r02_fold_into_family_leaves_greys_alone() -> None:
    grey = (0.3, 0.3, 0.3)
    assert fold_into_family(grey, GREEN_FAMILY) is grey


def test_p14_r02_fold_into_family_maps_the_hue_start_to_the_family_start() -> None:
    folded = fold_into_family((1, 0, 0), GREEN_FAMILY)
    assert hue_saturation(folded)[0] == pytest.approx(90.0)
