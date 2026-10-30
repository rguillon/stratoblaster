"""Seeded noise and its fractal sums (`core.math.noise`)."""

import pytest

from core.math.noise import OctaveOptions, create_noise2d, fbm, hash_2d, ridged, smoothstep

SAMPLES = [(x * 0.37 - 3.1, y * 0.53 + 0.4) for x in range(12) for y in range(12)]


def test_noise_is_the_same_for_the_same_seed() -> None:
    a = create_noise2d(7)
    b = create_noise2d(7)
    assert all(a(x, y) == b(x, y) for x, y in SAMPLES)


def test_noise_differs_between_seeds() -> None:
    a = create_noise2d(7)
    b = create_noise2d(8)
    assert any(a(x, y) != b(x, y) for x, y in SAMPLES)


def test_noise_stays_within_minus_one_and_one() -> None:
    noise = create_noise2d(3)
    assert all(-1 <= noise(x, y) <= 1 for x, y in SAMPLES)


def test_noise_is_zero_on_the_lattice() -> None:
    noise = create_noise2d(3)
    assert noise(3.0, 5.0) == pytest.approx(0.0)
    assert noise(-2.0, 0.0) == pytest.approx(0.0)


def test_p14_noise_tiles_with_its_period() -> None:
    noise = create_noise2d(5, period=8)
    for x, y in SAMPLES:
        assert noise(x + 8, y) == pytest.approx(noise(x, y))
        assert noise(x, y + 8) == pytest.approx(noise(x, y))


def test_noise_period_wraps_negative_coordinates() -> None:
    noise = create_noise2d(5, period=8)
    assert noise(-2.3, 1.7) == pytest.approx(noise(5.7, 1.7))


def test_noise_period_below_one_is_clamped_to_one() -> None:
    noise = create_noise2d(5, period=0.5)
    assert noise(1.25, 2.5) == pytest.approx(noise(2.25, 2.5))


def test_fbm_with_one_octave_is_the_noise_itself() -> None:
    noise = create_noise2d(11)
    options = OctaveOptions(octaves=1, lacunarity=2, gain=0.5)
    assert fbm(noise, 1.3, 2.6, options) == pytest.approx(noise(1.3, 2.6))


def test_fbm_sums_the_octaves_and_normalises_them() -> None:
    noise = create_noise2d(11)
    options = OctaveOptions(octaves=3, lacunarity=2, gain=0.5)
    expected = (noise(1.3, 2.6) + 0.5 * noise(2.6, 5.2) + 0.25 * noise(5.2, 10.4)) / 1.75
    assert fbm(noise, 1.3, 2.6, options) == pytest.approx(expected)


def test_fbm_without_octaves_is_zero() -> None:
    options = OctaveOptions(octaves=0, lacunarity=2, gain=0.5)
    assert fbm(create_noise2d(1), 1.0, 1.0, options) == 0.0


def test_fbm_stays_within_the_noise_range() -> None:
    noise = create_noise2d(2)
    options = OctaveOptions(octaves=4, lacunarity=2, gain=0.5)
    assert all(-1 <= fbm(noise, x, y, options) <= 1 for x, y in SAMPLES)


def test_ridged_of_a_flat_zero_noise_is_one() -> None:
    options = OctaveOptions(octaves=3, lacunarity=2, gain=0.5)
    assert ridged(lambda x, y: 0.0, 1.0, 1.0, options) == pytest.approx(1.0)


def test_ridged_of_a_flat_noise_at_one_is_zero() -> None:
    options = OctaveOptions(octaves=3, lacunarity=2, gain=0.5)
    assert ridged(lambda x, y: 1.0, 1.0, 1.0, options) == pytest.approx(0.0)


def test_ridged_without_octaves_is_zero() -> None:
    options = OctaveOptions(octaves=0, lacunarity=2, gain=0.5)
    assert ridged(lambda x, y: 0.0, 1.0, 1.0, options) == 0.0


def test_ridged_stays_within_zero_and_one() -> None:
    noise = create_noise2d(4)
    options = OctaveOptions(octaves=4, lacunarity=2, gain=0.5)
    assert all(0 <= ridged(noise, x, y, options) <= 1 for x, y in SAMPLES)


def test_smoothstep_clamps_and_eases() -> None:
    assert smoothstep(0, 1, -1) == 0.0
    assert smoothstep(0, 1, 2) == 1.0
    assert smoothstep(0, 1, 0.5) == pytest.approx(0.5)
    assert smoothstep(0, 2, 0.5) == pytest.approx(0.15625)


def test_smoothstep_with_equal_edges_is_a_step() -> None:
    assert smoothstep(1, 1, 0.5) == 0.0
    assert smoothstep(1, 1, 1.5) == 1.0


def test_hash_2d_is_in_zero_one_and_repeatable() -> None:
    values = [hash_2d(x, y, 42) for x in range(-5, 5) for y in range(-5, 5)]
    assert all(0 <= v < 1 for v in values)
    assert hash_2d(3, -4, 42) == hash_2d(3, -4, 42)


def test_hash_2d_depends_on_the_seed_and_the_coordinates() -> None:
    assert hash_2d(1, 2, 0) != hash_2d(1, 2, 1)
    assert hash_2d(1, 2, 0) != hash_2d(2, 1, 0)
