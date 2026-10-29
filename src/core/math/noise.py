"""Seeded 2D gradient noise and its fractal sums, ported from `core/math/noise.ts`."""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable  # noqa: E402

Noise2D = Callable[[float, float], float]
__pragma__("noskip")

import math  # noqa: E402

from core.math.bits import imul, ushr, xor  # noqa: E402
from core.math.rng import create_rng  # noqa: E402

TABLE_SIZE = 256
PI = 3.141592653589793
SQRT2 = 1.4142135623730951

# The most a create_noise2d noise changes per unit along either axis (ported constant). Blends of
# four unit gradients, a smootherstep of slope 15/8 and the ramps' own slope, scaled by √2.
NOISE_SLOPE = 9


class OctaveOptions:
    """Octave settings of `fbm` and `ridged`."""

    def __init__(self, octaves: int, lacunarity: float, gain: float) -> None:
        self.octaves = octaves
        """Number of octaves."""
        self.lacunarity = lacunarity
        """Frequency multiplier between octaves (usually 2)."""
        self.gain = gain
        """Amplitude multiplier between octaves (usually 0.5)."""


def _smootherstep(t: float) -> float:
    return t * t * t * (t * (t * 6 - 15) + 10)


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _int_mod(a: int, n: int) -> int:
    """`a % n` for whole numbers, with JavaScript's `%` (Transcrypt's `%` also corrects the sign,
    which is slow here: the noise is evaluated for every texel). Equal to Python's for `a >= 0`."""
    r = 0
    __pragma__("js", "{}", "r = a % n;")
    return r


def _wrap(i: int, period: int) -> int:
    return _int_mod(_int_mod(i, period) + period, period)


def create_noise2d(seed: int, period: int = TABLE_SIZE) -> Noise2D:
    """Seeded 2D gradient noise (Perlin style), values in [-1, 1].

    With a `period`, the lattice wraps every `period` units, so the noise tiles seamlessly on a
    `period` × `period` square (for textures).
    """
    random = create_rng(seed)
    perm = list(range(TABLE_SIZE))
    for i in range(TABLE_SIZE - 1, 0, -1):
        j = math.floor(random() * (i + 1))
        perm[i], perm[j] = perm[j], perm[i]
    angles = [random() * PI * 2 for _ in range(TABLE_SIZE)]
    # Each angle's cosine and sine are worked out once (the same values, every call).
    cos_table = [math.cos(a) for a in angles]
    sin_table = [math.sin(a) for a in angles]
    p = max(1, math.floor(period))

    def gradient(ix: int, iy: int, dx: float, dy: float) -> float:
        h = perm[_int_mod(_wrap(ix, p) + perm[_int_mod(_wrap(iy, p), TABLE_SIZE)], TABLE_SIZE)]
        return cos_table[h] * dx + sin_table[h] * dy

    def noise(x: float, y: float) -> float:
        ix = math.floor(x)
        iy = math.floor(y)
        fx = x - ix
        fy = y - iy
        u = _smootherstep(fx)
        v = _smootherstep(fy)
        bottom = _lerp(gradient(ix, iy, fx, fy), gradient(ix + 1, iy, fx - 1, fy), u)
        top = _lerp(gradient(ix, iy + 1, fx, fy - 1), gradient(ix + 1, iy + 1, fx - 1, fy - 1), u)
        # Gradient noise peaks at about ±0.71 in 2D: scale it to fill [-1, 1].
        value = _lerp(bottom, top, v) * SQRT2
        return -1 if value < -1 else (1 if value > 1 else value)

    return noise


def fbm(noise: Noise2D, x: float, y: float, options: OctaveOptions) -> float:
    """Fractal sum of `noise` octaves, normalised back to [-1, 1]."""
    total_sum = 0.0
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    for _ in range(options.octaves):
        total_sum += noise(x * frequency, y * frequency) * amplitude
        total += amplitude
        amplitude *= options.gain
        frequency *= options.lacunarity
    return total_sum / total if total > 0 else 0.0


def ridged(noise: Noise2D, x: float, y: float, options: OctaveOptions) -> float:
    """Ridged fractal noise in [0, 1]: sharp crests where the noise crosses zero."""
    total_sum = 0.0
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    weight = 1.0
    for _ in range(options.octaves):
        crest = 1 - abs(noise(x * frequency, y * frequency))
        value = crest * crest * weight
        weight = value * 2 if value * 2 < 1 else 1
        total_sum += value * amplitude
        total += amplitude
        amplitude *= options.gain
        frequency *= options.lacunarity
    return total_sum / total if total > 0 else 0.0


def smoothstep(edge0: float, edge1: float, x: float) -> float:
    """0 below `edge0`, 1 above `edge1`, smooth in between."""
    if edge0 == edge1:
        return 0.0 if x < edge0 else 1.0
    t = (x - edge0) / (edge1 - edge0)
    t = 0 if t < 0 else (1 if t > 1 else t)
    return t * t * (3 - 2 * t)


def hash_2d(x: int, y: int, seed: int) -> float:
    """A well-mixed 32-bit hash of integer coordinates and a seed, as a number in [0, 1)."""
    h = xor(xor(imul(int(x), 0x27D4EB2D), imul(int(y), 0x165667B1)), imul(int(seed), 0x9E3779B1))
    h = imul(xor(h, ushr(h, 15)), 0x85EBCA6B)
    h = imul(xor(h, ushr(h, 13)), 0xC2B2AE35)
    return xor(h, ushr(h, 16)) / 4294967296
