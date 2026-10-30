"""Unit tests of `src/render/scenery/procedural_textures.py`."""

import json
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import patch_babylon
from helpers.render_looks import BLACK, GREY, WHITE, make_look, texture

from render.scenery import procedural_textures
from render.scenery.procedural_textures import (
    TextureJob,
    build_ground_texture,
    build_noise_texture,
    build_water_normal_map,
    crack_lines,
    equalize,
    has_texture,
    keep_texture,
    scenery_texture_jobs,
    texture_pixels,
    tileable_fbm,
)

SIZE = 8


@pytest.fixture(autouse=True)
def _js(monkeypatch: pytest.MonkeyPatch) -> None:
    """The JavaScript `Map` of the kept textures and its JSON keys, as plain Python."""
    patch_babylon(monkeypatch, procedural_textures)
    monkeypatch.setattr(procedural_textures, "_kept", {})
    monkeypatch.setattr(procedural_textures, "_map_has", lambda c, k: k in c)
    monkeypatch.setattr(procedural_textures, "_map_get", lambda c, k: c[k])
    monkeypatch.setattr(procedural_textures, "_map_set", lambda c, k, v: c.__setitem__(k, v))
    monkeypatch.setattr(procedural_textures, "_map_delete", lambda c, k: c.pop(k))
    monkeypatch.setattr(procedural_textures, "_map_size", len)
    monkeypatch.setattr(procedural_textures, "_map_first_key", lambda c: next(iter(c)))
    # JSON.stringify writes an object's own fields: `vars` does the same for the look records.
    monkeypatch.setattr(procedural_textures, "_json_of", lambda v: json.dumps(v, default=vars))


def _rgba(pixels: Any, index: int) -> list[int]:
    return list(pixels[index * 4 : index * 4 + 4])


def test_fractal_noise_is_repeatable_and_stays_in_range() -> None:
    first = tileable_fbm(SIZE, 4, 3, 11)
    second = tileable_fbm(SIZE, 4, 3, 11)
    assert list(first) == list(second)
    assert all(-1 <= v <= 1 for v in first)
    assert list(tileable_fbm(SIZE, 4, 3, 12)) != list(first)


def test_fractal_noise_with_no_octave_is_empty_zero() -> None:
    assert set(tileable_fbm(SIZE, 4, 0, 1)) == {0}


def test_an_octave_whose_period_is_too_long_is_skipped() -> None:
    # Octave 0 has period 300 (over the table size): nothing is summed.
    assert set(tileable_fbm(SIZE, 300, 2, 1)) == {0}


def test_equalize_keeps_the_order_and_spreads_the_values_evenly() -> None:
    out = equalize([5.0, 1.0, 3.0, 2.0])
    assert list(out) == pytest.approx([1.0, 0.0, 2 / 3, 1 / 3])


def test_equalize_keeps_equal_values_in_their_order() -> None:
    # The 0 is the lowest; the two 1s take the next ranks in their order.
    assert list(equalize([1.0, 1.0, 0.0])) == pytest.approx([0.5, 1.0, 0.0])


def test_crack_lines_are_one_or_zero_and_some_cells_crack() -> None:
    lines = crack_lines(16, 4, 3)
    assert set(lines) <= {0, 1}
    assert 1 in set(lines)


def test_a_ground_texture_is_opaque_rgba_of_its_colours() -> None:
    look = texture(colors=(BLACK, GREY, WHITE), frequency=4, octaves=2)
    pixels = build_ground_texture(SIZE, look, 5)
    assert len(pixels) == SIZE * SIZE * 4
    assert all(pixels[i] == 255 for i in range(3, len(pixels), 4))
    # Every colour lies between the dark and the light ones.
    assert all(0 <= pixels[i] <= 255 for i in range(len(pixels)))


def test_speckles_take_the_speckle_colour() -> None:
    look = texture(speckle=1, speckle_color=(1.0, 0.0, 0.0))
    pixels = build_ground_texture(SIZE, look, 5)
    assert all(_rgba(pixels, i)[:3] == [255, 0, 0] for i in range(SIZE * SIZE))


def test_strata_and_cracks_change_the_texture() -> None:
    plain = build_ground_texture(SIZE, texture(frequency=4), 5)
    stratified = build_ground_texture(SIZE, texture(frequency=4, strata=1), 5)
    cracked = build_ground_texture(SIZE, texture(frequency=4, cracks=1), 5)
    assert list(stratified) != list(plain)
    assert list(cracked) != list(plain)


def test_a_noise_texture_holds_fine_and_coarse_noise_in_red_and_green() -> None:
    pixels = build_noise_texture(SIZE, 4, 9)
    reds = [pixels[i] for i in range(0, len(pixels), 4)]
    greens = [pixels[i] for i in range(1, len(pixels), 4)]
    assert min(reds) == 0 and max(reds) == 255
    assert min(greens) == 0 and max(greens) == 255
    assert all(pixels[i] == 0 for i in range(2, len(pixels), 4))


def test_a_flat_water_map_points_straight_up() -> None:
    options = SimpleNamespace(frequency=4, octaves=2, strength=0)
    pixels = build_water_normal_map(SIZE, options, 1)
    # The normal (0, 0, 1) encoded as (0.5, 0.5, 1) in RGB.
    assert _rgba(pixels, 0) == [128, 128, 255, 255]
    assert _rgba(pixels, SIZE * SIZE - 1) == [128, 128, 255, 255]


def test_a_water_map_tilts_its_normals_against_the_slope() -> None:
    options = SimpleNamespace(frequency=4, octaves=3, strength=8)
    pixels = build_water_normal_map(SIZE, options, 1)
    assert any(_rgba(pixels, i)[:2] != [128, 128] for i in range(SIZE * SIZE))


def test_each_job_is_made_by_its_own_generator() -> None:
    ground = texture_pixels(TextureJob("ground", [SIZE, texture(), 3]))
    noise = texture_pixels(TextureJob("noise", [SIZE, 4, 3]))
    water = texture_pixels(
        TextureJob("water", [SIZE, SimpleNamespace(frequency=4, octaves=2, strength=1), 3])
    )
    for pixels in (ground, noise, water):
        assert len(pixels) == SIZE * SIZE * 4


def test_the_jobs_of_a_level_are_its_ground_layers_noise_and_waves() -> None:
    look = make_look()
    jobs = scenery_texture_jobs(look, 100)
    names = [job.name for job in jobs]
    assert names.count("ground") == 7
    assert names.count("noise") == 2
    assert names.count("water") == 1


def test_a_level_with_lava_has_no_wave_texture() -> None:
    look = make_look()
    look.sea.lava = object()
    assert [j.name for j in scenery_texture_jobs(look, 100)].count("water") == 0


def test_a_kept_texture_is_found_again() -> None:
    job = TextureJob("noise", [SIZE, 4, 2])
    assert has_texture(job) is False
    keep_texture(job, "pixels")
    assert has_texture(job) is True
    assert procedural_textures._kept_pixels("noise", [SIZE, 4, 2], lambda: "new") == "pixels"


def test_building_a_kept_texture_again_reuses_its_pixels() -> None:
    calls: list[int] = []

    def build() -> str:
        calls.append(1)
        return "made"

    procedural_textures._kept_pixels("noise", [1], build)
    procedural_textures._kept_pixels("noise", [1], build)
    assert calls == [1]


def test_the_oldest_kept_texture_goes_when_the_cache_is_full(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(procedural_textures, "KEPT_TEXTURES", 2)
    for seed in (1, 2, 3):
        procedural_textures._kept_pixels("noise", [seed], lambda seed=seed: seed)
    assert not has_texture(TextureJob("noise", [1]))
    assert has_texture(TextureJob("noise", [2]))
    assert has_texture(TextureJob("noise", [3]))
