# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/render/scenery/procedural_textures.py` (GFX-TERRAIN-07, PERF-11)."""

import json
import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers.render_fakes import patch_babylon
from helpers.render_looks import BLACK, GREY, WHITE, make_look, texture

from core.math.noise import hash_2d
from render.scenery import procedural_textures
from render.scenery.procedural_textures import (
    STONE_LIGHT_X,
    STONE_LIGHT_Y,
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

# The JavaScript `Map` and JSON helpers as the module defines them, taken before the fixture below
# replaces them, with the placeholder CPython returns after their `__pragma__("js")` body.
JS_HELPERS: list[tuple[Any, tuple[Any, ...], Any]] = [
    (procedural_textures._new_map, (), None),
    (procedural_textures._map_has, ({}, "k"), False),
    (procedural_textures._map_get, ({}, "k"), None),
    (procedural_textures._map_set, ({}, "k", 1), None),
    (procedural_textures._map_delete, ({}, "k"), None),
    (procedural_textures._map_size, ({},), 0),
    (procedural_textures._map_first_key, ({},), ""),
    (procedural_textures._json_of, ([1, 2],), ""),
]


@pytest.fixture(autouse=True)
def _js(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace the JavaScript `Map` of the kept textures and its JSON keys with plain Python."""
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


def test_stones_change_the_texture_and_cut_dark_joints_into_it() -> None:
    """GFX-TERRAIN-07: a rock face of stones, each a shade of its own, dark joints between."""
    size = 32
    colors = ((0.4, 0.4, 0.4), GREY, WHITE)
    plain = build_ground_texture(size, texture(colors=colors, frequency=4), 5)
    stony = build_ground_texture(size, texture(colors=colors, frequency=4, stones=1), 5)
    assert list(stony) != list(plain)
    # The joints: the darkest pixels of the stony texture are darker than the dark colour, which
    # is as dark as the plain one gets.
    darkest = min(sum(_rgba(stony, i)[:3]) for i in range(size * size))
    assert darkest < min(sum(_rgba(plain, i)[:3]) for i in range(size * size))
    assert darkest < 3 * 0.4 * 255
    # The same look and seed give the same stones.
    again = build_ground_texture(size, texture(colors=colors, frequency=4, stones=1), 5)
    assert list(again) == list(stony)


def test_jittered_cells_give_a_number_a_gap_and_a_lit_side_per_pixel() -> None:
    cells = procedural_textures.jittered_cells(16, 4, 3, 0.75, 1.5)
    assert len(cells) == 16 * 16 * 3
    for i in range(16 * 16):
        assert 0 <= cells[i * 3] < 1
        assert cells[i * 3 + 1] >= 0
        assert -1 - 1e-6 <= cells[i * 3 + 2] <= 1 + 1e-6


def _reference_cells(
    size: int, cells: float, seed: int, jitter: float, aspect: float
) -> list[float]:
    """D-413: `jittered_cells` as it was, each point worked out for every pixel that looks at it."""
    n = max(2, math.floor(cells + 0.5))
    m = max(2, math.floor(cells * aspect + 0.5))

    def point(i: int, j: int) -> list[float]:
        wi = ((i % n) + n) % n
        wj = ((j % m) + m) % m
        return [
            i + 0.5 + (hash_2d(wi, wj, seed) - 0.5) * jitter,
            j + 0.5 + (hash_2d(wi, wj, seed + 1) - 0.5) * jitter,
            hash_2d(wi, wj, seed + 2),
        ]

    out = [0.0] * (size * size * 3)
    for y in range(size):
        for x in range(size):
            u = (x / size) * n
            v = (y / size) * m
            nearest = 1e9
            second = 1e9
            own = 0.0
            lit = 0.0
            for j in range(math.floor(v) - 1, math.floor(v) + 2):
                for i in range(math.floor(u) - 1, math.floor(u) + 2):
                    p = point(i, j)
                    d = math.hypot(u - p[0], v - p[1])
                    if d < nearest:
                        second = nearest
                        nearest = d
                        own = p[2]
                        light = (u - p[0]) * STONE_LIGHT_X + (v - p[1]) * STONE_LIGHT_Y
                        lit = light / (d or 1)
                    elif d < second:
                        second = d
            k = (y * size + x) * 3
            out[k] = own
            out[k + 1] = second - nearest
            out[k + 2] = lit
    return out


@pytest.mark.parametrize(
    ("size", "cells", "seed", "jitter", "aspect"),
    [(24, 4, 3, 0.75, 1.5), (32, 5.5, 91, 1, 1), (16, 2.2, 7, 0.4, 0.6)],
)
def test_d413_jittered_cells_match_the_points_worked_out_per_pixel(
    size: int, cells: float, seed: int, jitter: float, aspect: float
) -> None:
    """PERF-03: the grid's points worked out once give the same cells."""
    made = procedural_textures.jittered_cells(size, cells, seed, jitter, aspect)
    assert list(made) == _reference_cells(size, cells, seed, jitter, aspect)


def test_a_noise_texture_holds_fine_and_coarse_noise_in_red_and_green() -> None:
    pixels = build_noise_texture(SIZE, 4, 9)
    reds = [pixels[i] for i in range(0, len(pixels), 4)]
    greens = [pixels[i] for i in range(1, len(pixels), 4)]
    assert min(reds) == 0
    assert max(reds) == 255
    assert min(greens) == 0
    assert max(greens) == 255
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


@pytest.mark.parametrize(("helper", "args", "placeholder"), JS_HELPERS)
def test_the_map_and_json_helpers_are_javascript_only(
    helper: Any, args: tuple[Any, ...], placeholder: Any
) -> None:
    """The kept textures' `Map` and their JSON keys exist in the browser only.

    CPython runs the placeholder return after each `__pragma__("js")` body.
    """
    assert helper(*args) == placeholder
