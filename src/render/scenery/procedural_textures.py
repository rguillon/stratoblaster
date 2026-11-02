# Copyright (c) 2026 Renaud Guillon
"""Generated textures of a scenery level (GFX-TERRAIN-07, GFX-WATER-03, PERF-11): fractal noise.

Ground, noise and water normal maps as RGBA8 pixels, pure functions of their arguments, made here or
in the worker, and kept for reuse.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.noise import create_noise2d, hash_2d
from render.babylon import float32_array, uint8_array

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

# __pragma__ ("noskip")


# Largest lattice period the noise supports (its permutation table size).
MAX_PERIOD = 256

# How many generated textures are kept for reuse (PERF-11).
KEPT_TEXTURES = 48

# Noise cycles across the terrain blending and cloud noise textures (the scenery kit's).
NOISE_FREQUENCY = 8

# Crack cells across the texture per noise cycle, and the cracks' width (in cells).
CRACK_CELLS = 0.5
CRACK_WIDTH = 0.08
# Stones (GFX-TERRAIN-07): cells of a jittered grid across the texture per noise cycle, the width
# of the joints between them and of the bevel lit at their edges (in cells, as a share of the gap
# between the two nearest cells), how far the stones' own shades spread over the colour range, how
# much the bevel lights or shadows an edge, how dark the joints are, and where the light comes from
# (in texture space).
STONE_CELLS = 0.85
STONE_JOINT = 0.07
STONE_BEVEL = 0.25
STONE_SHADE = 0.6
STONE_BEVEL_LIGHT = 0.3
STONE_JOINT_DARK = 0.55
STONE_LIGHT_X = -0.6
STONE_LIGHT_Y = -0.8
# How far the stones' points move from their grid (0..1; less than the cracks' full jitter, so no
# two points lie almost together and cut a sliver), how much wider than high the stones are (slabs
# along the strata), how much the noise wobbles the joints, how strong the grain inside a stone is,
# and the fractures: thinner cracks of a finer grid (`STONE_FRACTURES` times the cells) that split
# some stones, their width (in cells) and how dark they are.
STONE_JITTER = 0.75
STONE_ASPECT = 1.6
STONE_WOBBLE = 0.08
STONE_GRAIN = 0.7
STONE_FRACTURES = 2.3
STONE_FRACTURE_WIDTH = 0.04
STONE_FRACTURE_DARK = 0.3

# How far the ground noise spreads from the base colour towards the dark and light ones.
GROUND_CONTRAST = 1.2


class TextureJob:
    """A texture to generate: its `name` ('ground', 'noise' or 'water').

    Its `args` (PERF-14: made in a worker).
    """

    def __init__(self, name: str, args: Sequence[Any]) -> None:
        self.name = name
        self.args = args


def _new_map() -> Any:
    """Return an empty JavaScript `Map`."""
    __pragma__("js", "{}", "return new Map();")
    return None


def _map_has(cache: Any, key: str) -> bool:
    __pragma__("js", "{}", "return cache.has(key);")
    return False


def _map_get(cache: Any, key: str) -> Any:
    __pragma__("js", "{}", "return cache.get(key);")
    return None


def _map_set(cache: Any, key: str, value: Any) -> None:
    __pragma__("js", "{}", "cache.set(key, value);")


def _map_delete(cache: Any, key: str) -> None:
    __pragma__("js", "{}", "cache.delete(key);")


def _map_size(cache: Any) -> int:
    __pragma__("js", "{}", "return cache.size;")
    return 0


def _map_first_key(cache: Any) -> str:
    __pragma__("js", "{}", "return cache.keys().next().value;")
    return ""


def _json_of(value: Any) -> str:
    """`JSON.stringify(value)`."""
    __pragma__("js", "{}", "return JSON.stringify(value);")
    return ""


def _hypot2(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return math.hypot(a, b)  # Only reached outside Transcrypt (CPython).


def _hypot3(a: float, b: float, c: float) -> float:
    """`Math.hypot(a, b, c)`."""
    __pragma__("js", "{}", "return Math.hypot(a, b, c);")
    return math.hypot(a, b, c)  # Only reached outside Transcrypt (CPython).


_kept: Any = _new_map()


def _key_of(job: TextureJob) -> str:
    return job.name + ":" + _json_of(job.args)


def _stable_sort(items: list[Any], compare: Callable[[Any, Any], float]) -> list[Any]:
    """Return a stable merge sort with a comparator.

    Transcrypt's `sort` is unstable and takes none.
    """
    n = len(items)
    if n < 2:
        return list(items)
    middle = n // 2
    left = _stable_sort(items[0:middle], compare)
    right = _stable_sort(items[middle:n], compare)
    out: list[Any] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if compare(right[j], left[i]) < 0:
            out.append(right[j])
            j += 1
        else:
            out.append(left[i])
            i += 1
    while i < len(left):
        out.append(left[i])
        i += 1
    while j < len(right):
        out.append(right[j])
        j += 1
    return out


def texture_pixels(job: TextureJob) -> Any:
    """Return the pixels of `job`, generated now (not kept): what a worker runs."""
    if job.name == "ground":
        return _ground_pixels(job.args[0], job.args[1], job.args[2])
    if job.name == "noise":
        return _noise_pixels(job.args[0], job.args[1], job.args[2])
    return _water_pixels(job.args[0], job.args[1], job.args[2])


def has_texture(job: TextureJob) -> bool:
    """Whether the pixels of `job` are kept already."""
    return _map_has(_kept, _key_of(job))


def keep_texture(job: TextureJob, pixels: Any) -> None:
    """Keep `pixels` as those of `job` (made in a worker), for the next build of that texture."""
    _kept_pixels(job.name, job.args, lambda: pixels)


def scenery_texture_jobs(look: Any, seed: int) -> list[TextureJob]:
    """Return every texture the scenery kit generates for a level with `look` and `seed`.

    The kit is made by `createSceneryKit`; the textures are its ground layers, its noise, its clouds
    and (without lava) its waves.
    """
    t = look.terrain
    layers = [
        [t.low, 1],
        [t.ground, 2],
        [t.steep, 3],
        [t.high, 4],
        [t.lush, 8],
        [t.paved, 9],
        [t.sand, 10],
    ]
    jobs: list[TextureJob] = [
        TextureJob("ground", [t.textureSize, pair[0], seed + pair[1]]) for pair in layers
    ]
    jobs.append(TextureJob("noise", [t.textureSize, NOISE_FREQUENCY, seed + 5]))
    jobs.append(TextureJob("noise", [t.textureSize, NOISE_FREQUENCY / 2, seed + 7]))
    sea = look.sea
    if sea.lava == None:
        jobs.append(TextureJob("water", [sea.normalMap.size, sea.normalMap, seed + 6]))
    return jobs


def _kept_pixels(name: str, args: Sequence[Any], build: Callable[[], Any]) -> Any:
    """Return the pixels `build` makes for `args`, made once and kept.

    The most recent KEPT_TEXTURES are kept, so starting a level again, or another level with the
    same look, does not generate them again (PERF-11). The textures are pure functions of their
    arguments; callers must not change them.
    """
    key = name + ":" + _json_of(args)
    if _map_has(_kept, key):
        pixels = _map_get(_kept, key)
        _map_delete(_kept, key)
    else:
        pixels = build()
        if _map_size(_kept) >= KEPT_TEXTURES:
            _map_delete(_kept, _map_first_key(_kept))
    _map_set(_kept, key, pixels)
    return pixels


def tileable_fbm(size: int, frequency: float, octaves: float, seed: int) -> Any:
    """Return fractal noise on a `size` x `size` grid that tiles seamlessly.

    Octave `k` has `frequency` x 2^k cycles across the grid, each with its own wrapping lattice.
    Values are in [-1, 1].
    """
    values = float32_array(size * size)
    total = 0.0
    for k in range(math.floor(octaves)):
        period = math.floor(frequency * 2**k + 0.5)
        if period < 1 or period > MAX_PERIOD:
            break
        noise = create_noise2d(seed + k, period)
        amplitude = 0.5**k
        total += amplitude
        for y in range(size):
            for x in range(size):
                i = y * size + x
                values[i] = values[i] + amplitude * noise((x / size) * period, (y / size) * period)
    if total > 0:
        out = float32_array(size * size)
        for i in range(size * size):
            out[i] = values[i] / total
        return out
    return values


def equalize(values: Any) -> Any:
    """Ranks of `values` scaled to [0, 1].

    The same order, but evenly spread (histogram equalised).
    """
    indices = list(range(len(values)))
    order = _stable_sort(indices, lambda a, b: values[a] - values[b])
    out = float32_array(len(values))
    last = max(1, len(values) - 1)
    for rank in range(len(order)):
        out[order[rank]] = rank / last
    return out


def _byte(v: float) -> int:
    return math.floor(min(1, max(0, v)) * 255 + 0.5)


def _mix_rgb(a: Sequence[float], b: Sequence[float], t: float) -> list[float]:
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t]


def _ground_color(look: Any, n: float) -> list[float]:
    """Colour of a ground texture for a noise value `n` in [0, 1]."""
    dark = look.colors[0]
    base = look.colors[1]
    light = look.colors[2]
    if n < 0.5:
        return _mix_rgb(dark, base, n * 2)
    return _mix_rgb(base, light, (n - 0.5) * 2)


def jittered_cells(size: int, cells: float, seed: int, jitter: float = 1, aspect: float = 1) -> Any:
    """Return the cells of a jittered grid of `cells` x `cells` points over a tiling texture.

    `size` x `size` pixels, three values each in a row: the nearest point's own number (0..1, a
    hash), the gap between the distances to the nearest and the second nearest points (0 on the
    edge between their cells, in cells), and how much the pixel faces the light from its nearest
    point (-1..1). The points move up to `jitter` (0..1) of a cell from their grid; the cells are
    `aspect` times wider than high.
    """
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

    out = float32_array(size * size * 3)
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
                    d = _hypot2(u - p[0], v - p[1])
                    if d < nearest:
                        second = nearest
                        nearest = d
                        own = p[2]
                        lit = ((u - p[0]) * STONE_LIGHT_X + (v - p[1]) * STONE_LIGHT_Y) / (d or 1)
                    elif d < second:
                        second = d
            k = (y * size + x) * 3
            out[k] = own
            out[k + 1] = second - nearest
            out[k + 2] = lit
    return out


def crack_lines(size: int, cells: float, seed: int) -> Any:
    """Crack lines over a `size` x `size` texture that tiles (phase 8: lake ice).

    The edges between the cells of a jittered grid of `cells` x `cells` points, 1 on a crack and 0
    elsewhere.
    """
    grid = jittered_cells(size, cells, seed)
    lines = float32_array(size * size)
    for i in range(size * size):
        lines[i] = 1 if grid[i * 3 + 1] < CRACK_WIDTH else 0
    return lines


def build_ground_texture(size: int, look: Any, seed: int) -> Any:
    """RGBA8 pixels of a tiling ground texture (GFX-TERRAIN-07)."""
    return _kept_pixels("ground", [size, look, seed], lambda: _ground_pixels(size, look, seed))


def _ground_pixels(size: int, look: Any, seed: int) -> Any:
    noise = _map_f32(
        tileable_fbm(size, look.frequency, look.octaves, seed),
        lambda v: min(1, max(0, 0.5 + v * GROUND_CONTRAST)),
    )
    bands = tileable_fbm(size, look.frequency / 2, 2, seed + 50)
    cracks = crack_lines(size, look.frequency * CRACK_CELLS, seed + 70) if look.cracks else None
    crack_strength = look.cracks if look.cracks != None else 0
    stones = look.stones if look.stones != None else 0
    grid = None
    fractures = None
    if stones:
        cells = look.frequency * STONE_CELLS
        grid = jittered_cells(size, cells, seed + 90, STONE_JITTER, STONE_ASPECT)
        fractures = jittered_cells(size, cells * STONE_FRACTURES, seed + 110, STONE_JITTER)
    pixels = uint8_array(size * size * 4)
    for y in range(size):
        for x in range(size):
            i = y * size + x
            # Strata: bands along X whose phase wanders with a second noise; a whole number of
            # bands across the texture keeps it tiling.
            band = math.sin(((y / size) * look.frequency * 2 + bands[i]) * math.pi * 2)
            crack = (cracks[i] if cracks is not None else 0) * crack_strength
            n = (noise[i] * (1 - look.strata) + look.strata * (band * 0.5 + 0.5)) * (1 - crack)
            dark = 1.0
            if grid is not None and fractures is not None:
                # Stones: each cell a flat shade of its own with the noise's grain over it, its
                # edges lit on the side facing the light and shadowed on the other, a dark joint
                # between the cells (its line wobbling with the noise) and thin fractures splitting
                # some stones.
                stone = 0.5 + (grid[i * 3] - 0.5) * STONE_SHADE + (n - 0.5) * STONE_GRAIN
                gap = grid[i * 3 + 1] + (noise[i] - 0.5) * STONE_WOBBLE
                edge = 1 - min(1, max(0, gap) / STONE_BEVEL)
                stone += grid[i * 3 + 2] * edge * STONE_BEVEL_LIGHT
                n = n + (stone - n) * stones
                joint = max(0, 1 - max(0, gap) / STONE_JOINT)
                split = max(0, 1 - fractures[i * 3 + 1] / STONE_FRACTURE_WIDTH)
                dark = 1 - stones * max(STONE_JOINT_DARK * joint, STONE_FRACTURE_DARK * split)
            speck = hash_2d(x, y, seed) < look.speckle
            rgb = look.speckleColor if speck else _ground_color(look, n)
            pixels.set(
                [_byte(rgb[0] * dark), _byte(rgb[1] * dark), _byte(rgb[2] * dark), 255], i * 4
            )
    return pixels


def _map_f32(values: Any, fn: Callable[[float], float]) -> Any:
    """`values.map(fn)` on a Float32Array: a new Float32Array."""
    out = float32_array(len(values))
    for i in range(len(values)):
        out[i] = fn(values[i])
    return out


def build_noise_texture(size: int, frequency: float, seed: int) -> Any:
    """Return the RGBA8 pixels of a tiling noise texture.

    R fine noise (`frequency` cycles), G coarse noise (a quarter of it), both evenly spread over [0,
    1].
    """
    return _kept_pixels(
        "noise", [size, frequency, seed], lambda: _noise_pixels(size, frequency, seed)
    )


def _noise_pixels(size: int, frequency: float, seed: int) -> Any:
    fine = equalize(tileable_fbm(size, frequency, 4, seed))
    coarse = equalize(tileable_fbm(size, max(1, frequency / 4), 3, seed + 10))
    pixels = uint8_array(size * size * 4)
    for i in range(size * size):
        pixels.set([_byte(fine[i]), _byte(coarse[i]), 0, 255], i * 4)
    return pixels


def build_water_normal_map(size: int, options: Any, seed: int) -> Any:
    """RGBA8 pixels of a tiling normal map of small waves (GFX-WATER-03).

    The slope of a fractal height map, `strength` times steeper, encoded as tangent-space normals.
    `options` has `frequency`, `octaves` and `strength`.
    """
    return _kept_pixels("water", [size, options, seed], lambda: _water_pixels(size, options, seed))


def _water_pixels(size: int, options: Any, seed: int) -> Any:
    heights = tileable_fbm(size, options.frequency, options.octaves, seed)

    def at(x: int, y: int) -> float:
        value: float = heights[((y + size) % size) * size + ((x + size) % size)]
        return value

    pixels = uint8_array(size * size * 4)
    for y in range(size):
        for x in range(size):
            dx = (at(x + 1, y) - at(x - 1, y)) * options.strength
            dy = (at(x, y + 1) - at(x, y - 1)) * options.strength
            length = _hypot3(dx, dy, 1)
            n = [-dx / length, -dy / length, 1 / length]
            pixels.set(
                [_byte(n[0] * 0.5 + 0.5), _byte(n[1] * 0.5 + 0.5), _byte(n[2] * 0.5 + 0.5), 255],
                (y * size + x) * 4,
            )
    return pixels
