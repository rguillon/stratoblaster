"""The sculpted ground of a level (P04-R01): every section is a fractal relief, optionally
flattened (plateau), carved (canyon) or dropped under the sea (coast), and neighbouring sections
blend smoothly over `level.transition`. Before Z = 0 and after the end, the ground continues as
the first and last sections. Pure and deterministic for a given seed. Ported from
`core/scenery/height-field.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402

from core.scenery.scenery_level import (  # noqa: E402
    Lakes,
    Meander,
    PlacedSection,
    SceneryLevel,
    TerrainSection,
)

__pragma__("noskip")

from core.math.noise import (  # noqa: E402
    NOISE_SLOPE,
    OctaveOptions,
    create_noise2d,
    fbm,
    ridged,
    smoothstep,
)
from core.scenery.ice_sculpt import LakeField, crevasse_depth  # noqa: E402
from core.scenery.scenery_level import Surface, layout_sections  # noqa: E402

INFINITY = float("Infinity")

# Octave falloff of every relief: each octave has twice the frequency and half the height.
OCTAVE_LACUNARITY = 2
OCTAVE_GAIN = 0.5
# Share of `max_height` below it where the squashing of peaks starts.
PEAK_KNEE = 0.25
# Cycles per world unit of the small relief left on flattened ground and canyon floors.
DETAIL_FREQUENCY = 1 / 60
# How much irregular wobble (as a share of the amplitude) is added to the sine of a meander.
MEANDER_WOBBLE = 0.35
# Dunes: share of a crest-to-crest cycle taken by the windward slope (the rest is the steep lee
# side), the scale (in wavelengths) of the noise bending the crest lines and varying their height,
# and the lowest crest height (as a share of `height`).
DUNE_WINDWARD = 0.78
DUNE_NOISE_SCALE = 3
DUNE_LOWEST_CREST = 0.45
# Rounding left out when telling whether a channel can reach somewhere.
SLACK = 1e-9


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def _or_one(value: float) -> float:
    """`value || 1` of JavaScript: 1 when `value` is zero (or not a number)."""
    return value if value else 1


def _surface_share(sections: Sequence[PlacedSection], index: int, key: str) -> float:
    """The share of ground cover `key` of the section at `index` (0 when it has none)."""
    if index >= len(sections):
        return 0
    surface = sections[index].section.surface
    if surface is None:
        return 0
    if key == "lush":
        share = surface.lush
    elif key == "paved":
        share = surface.paved
    else:
        share = surface.sandy
    return share if share is not None else 0


def _max_of(values: Sequence[float]) -> float:
    """`Math.max(...values)`: -Infinity for no values."""
    high = -INFINITY
    for v in values:
        high = max(high, v)
    return high


class Steepness:
    """How steep the relief of a section can be (most height change per unit along X or Z), and
    the heights it stays between."""

    def __init__(self, slope: float, low: float, high: float) -> None:
        self.slope = slope
        self.low = low
        self.high = high


def _smooth_only(section: TerrainSection) -> bool:
    """Whether `section`'s ground is its relief alone, smooth (no ridges)."""
    return (
        section.relief.style == "smooth"
        and section.dunes is None
        and section.crevasses is None
        and section.lakes is None
        and section.flatten is None
        and section.shore is None
    )


def _octaves_steepness(octaves: int) -> float:
    """How much steeper than one octave `octaves` octaves of `fbm` can be."""
    total_sum = 0.0
    total = 0.0
    for k in range(octaves):
        total_sum += math.pow(OCTAVE_GAIN * OCTAVE_LACUNARITY, k)
        total += math.pow(OCTAVE_GAIN, k)
    return total_sum / total if total > 0 else 0


def _section_steepness(placed: PlacedSection, transition: float) -> Steepness | None:
    """The steepness of a placed section, if it is smooth enough to tell (see `Steepness`)."""
    section = placed.section
    if not _smooth_only(section) or placed.end - placed.start < transition:
        return None
    relief = section.relief
    amplitude = abs(relief.amplitude)
    slope = amplitude * relief.frequency * NOISE_SLOPE * _octaves_steepness(relief.octaves)
    # Squashed peaks (`soft_cap`) are no steeper, and stay above the start of the squash.
    max_height = relief.max_height
    squash = INFINITY if max_height is None else max_height - _or_one(abs(max_height) * PEAK_KNEE)
    return Steepness(
        slope,
        min(relief.base - amplitude, squash),
        relief.base + amplitude,
    )


def soft_cap(h: float, max_height: float) -> float:
    """`h`, squashed smoothly so it never exceeds `max_height`."""
    knee = _or_one(abs(max_height) * PEAK_KNEE)
    start = max_height - knee
    return h if h <= start else start + knee * math.tanh((h - start) / knee)


def terrain_ceiling(level: SceneryLevel) -> float:
    """A height the ground of `level` never exceeds, whatever the seed: the top of each section's
    relief (or its peak cap), of its flattened band and of its sea bed. Carving only lowers the
    ground, and blending stays between the heights of the blended sections."""
    tops: list[float] = []
    for section in level.sections:
        relief = section.relief
        dunes = section.dunes
        top = relief.base + abs(relief.amplitude) + (abs(dunes.height) if dunes is not None else 0)
        candidates: list[float] = [
            top if relief.max_height is None else min(top, relief.max_height)
        ]
        flatten = section.flatten
        if flatten is not None:
            candidates.append(flatten.height + abs(flatten.roughness))
        shore = section.shore
        if shore is not None:
            candidates.append(shore.seabed)
        # A lake may raise ground lower than its level up to it (crevasses only cut).
        lakes = section.lakes
        if lakes is not None:
            candidates.append(lakes.level)
        tops.append(_max_of(candidates))
    return _max_of(tops)


class HeightField:
    """The ground of a level, as a height for every (x, z)."""

    def __init__(self, level: SceneryLevel, seed: int | None = None) -> None:
        seed_value = level.seed if seed is None else seed
        self.sections: list[PlacedSection] = layout_sections(level)
        """The sections, placed along Z."""
        self.length_ = self.sections[len(self.sections) - 1].end if self.sections else 0
        """Length of the level along Z."""
        self.ceiling = terrain_ceiling(level)
        """The ground never rises above this height (see `terrain_ceiling`)."""
        self._relief = create_noise2d(seed_value)
        self._detail = create_noise2d(seed_value + 1)
        self._wobble = create_noise2d(seed_value + 2)
        self._dunes = create_noise2d(seed_value + 3)
        self._ice = create_noise2d(seed_value + 4)
        self._seed = seed_value
        self._transition = max(0, level.transition)
        # Each section's octaves, made once.
        self._octaves: list[OctaveOptions] = [
            OctaveOptions(placed.section.relief.octaves, OCTAVE_LACUNARITY, OCTAVE_GAIN)
            for placed in self.sections
        ]
        # The lakes of each section that has some, each square's lake worked out once.
        self._lake_fields: list[LakeField | None] = [None for _ in self.sections]
        self._steepness: list[Steepness | None] = [
            _section_steepness(placed, self._transition) for placed in self.sections
        ]

    def steepness(self, x: float, z: float, reach: float) -> float:
        """At least the most the ground changes per unit along X or along Z within `reach` of
        (`x`, `z`), or Infinity when that cannot be told. Known for smooth reliefs away from their
        channels, blends included."""
        half = self._transition / 2
        first = self.section_index_at(z - reach - half)
        last = self.section_index_at(z + reach + half)
        slope = 0.0
        blend = 0.0
        for i in range(first, last + 1):
            own = self._steepness[i] if i < len(self._steepness) else None
            if own is None or not self._clear_of_channel(i, x, z, reach):
                return INFINITY
            slope = max(slope, own.slope)
            # Blending into the next section changes the height along Z by up to their difference.
            nxt = self._steepness[i + 1] if i < last and i + 1 < len(self._steepness) else None
            if nxt is not None and half > 0:
                apart = max(own.high, nxt.high) - min(own.low, nxt.low)
                blend = max(blend, (1.5 / self._transition) * apart)
        return slope + blend

    def _clear_of_channel(self, i: int, x: float, z: float, reach: float) -> bool:
        """Whether section `i`'s channel, if any, stays out of reach of (`x`, `z`)."""
        channel = self.sections[i].section.channel if i < len(self.sections) else None
        if channel is None:
            return True
        path = channel.path
        # How far the channel's middle line can move over `reach` along Z, its wobble included.
        turn = (
            abs(path.amplitude) * (2 * math.pi + MEANDER_WOBBLE * NOISE_SLOPE)
        ) / path.wavelength
        away = abs(x - self.path_x(path, z)) - reach * (1 + turn)
        return away > channel.half_width + channel.wall + SLACK

    def section_index_at(self, z: float) -> int:
        """Index of the section under `z` (the first or last one outside the level)."""
        sections = self.sections
        for i in range(len(sections)):
            if z < sections[i].end:
                return i
        return len(sections) - 1

    def section_at(self, z: float) -> PlacedSection:
        """The section under `z`."""
        index = self.section_index_at(z)
        if index < 0 or index >= len(self.sections):
            raise ValueError("A height field needs a section")
        return self.sections[index]

    def height(self, x: float, z: float) -> float:
        """Ground height at (`x`, `z`)."""
        return self._blend(z, lambda i: self._section_height(i, x, z))

    def surface(self, z: float) -> Surface:
        """Ground cover at `z`, blended between sections like the height."""
        return Surface(
            self._blend(z, lambda i: _surface_share(self.sections, i, "lush")),
            self._blend(z, lambda i: _surface_share(self.sections, i, "paved")),
            self._blend(z, lambda i: _surface_share(self.sections, i, "sandy")),
        )

    def _blend(self, z: float, value: Callable[[int], float]) -> float:
        """`value` of the section under `z`, blended with its neighbour near their boundary."""
        i = self.section_index_at(z)
        here = value(i)
        half = self._transition / 2
        if i >= len(self.sections) or half == 0:
            return here
        placed = self.sections[i]
        if i < len(self.sections) - 1 and z > placed.end - half:
            return _lerp(here, value(i + 1), smoothstep(placed.end - half, placed.end + half, z))
        if i > 0 and z < placed.start + half:
            return _lerp(
                value(i - 1), here, smoothstep(placed.start - half, placed.start + half, z)
            )
        return here

    def slope(self, x: float, z: float, step: float = 1) -> float:
        """Steepness at (`x`, `z`): height change per unit of horizontal distance."""
        dx = (self.height(x + step, z) - self.height(x - step, z)) / (2 * step)
        dz = (self.height(x, z + step) - self.height(x, z - step)) / (2 * step)
        return math.hypot(dx, dz)

    def path_x(self, path: Meander, z: float) -> float:
        """X of a meander line at `z`."""
        phase = (2 * math.pi * z) / path.wavelength
        wobble = self._wobble(z / path.wavelength, path.x / path.wavelength)
        return path.x + path.amplitude * (math.sin(phase) + MEANDER_WOBBLE * wobble)

    def _section_height(self, index: int, x: float, z: float) -> float:
        if index >= len(self.sections):
            return 0
        section = self.sections[index].section
        h = self._relief_height(index, x, z) + self._dune_height(section, x, z)
        if section.crevasses is not None:
            h -= crevasse_depth(section.crevasses, self._ice, x, z)
        if section.lakes is not None:
            h = self._lake_field(index, section.lakes).apply(x, z, h)
        h = self._flatten(section, x, z, h)
        h = self._carve(section, x, z, h)
        return self._shore(section, x, z, h)

    def _lake_field(self, index: int, lakes: Lakes) -> LakeField:
        field = self._lake_fields[index]
        if field is None:
            field = LakeField(lakes, self._seed)
            self._lake_fields[index] = field
        return field

    def _relief_height(self, index: int, x: float, z: float) -> float:
        relief = self.sections[index].section.relief
        options = self._octaves[index]
        f = relief.frequency
        if relief.style == "ridged":
            h = relief.base + relief.amplitude * ridged(self._relief, x * f, z * f, options)
        else:
            h = relief.base + relief.amplitude * fbm(self._relief, x * f, z * f, options)
        return h if relief.max_height is None else soft_cap(h, relief.max_height)

    def _dune_height(self, section: TerrainSection, x: float, z: float) -> float:
        """Height of the dunes over the relief at (`x`, `z`): 0 in the troughs, up to `height`."""
        dunes = section.dunes
        if dunes is None:
            return 0
        angle = (dunes.angle_deg * math.pi) / 180
        scale = dunes.wavelength * DUNE_NOISE_SCALE
        bend = self._dunes(x / scale, z / scale)
        across = (x * math.sin(angle) + z * math.cos(angle)) / dunes.wavelength
        phase = across + dunes.warp * bend
        t = phase - math.floor(phase)
        # Long windward rise, then a short steep drop on the lee side, both eased at the crest.
        if t < DUNE_WINDWARD:
            shape = smoothstep(0, DUNE_WINDWARD, t)
        else:
            shape = 1 - smoothstep(DUNE_WINDWARD, 1, t)
        crest = _lerp(
            DUNE_LOWEST_CREST,
            1,
            self._dunes(z / scale + 17, x / scale + 31) * 0.5 + 0.5,
        )
        return dunes.height * shape * crest

    def _detail_noise(self, x: float, z: float) -> float:
        return self._detail(x * DETAIL_FREQUENCY, z * DETAIL_FREQUENCY)

    def _flatten(self, section: TerrainSection, x: float, z: float, h: float) -> float:
        flatten = section.flatten
        if flatten is None:
            return h
        d = abs(x - self.path_x(flatten.path, z))
        flat = flatten.height + flatten.roughness * self._detail_noise(x, z)
        return _lerp(flat, h, smoothstep(flatten.half_width, flatten.half_width + flatten.edge, d))

    def _carve(self, section: TerrainSection, x: float, z: float, h: float) -> float:
        channel = section.channel
        if channel is None:
            return h
        d = abs(x - self.path_x(channel.path, z))
        floor = min(h, channel.floor + self._detail_noise(x, z))
        return _lerp(floor, h, smoothstep(channel.half_width, channel.half_width + channel.wall, d))

    def _shore(self, section: TerrainSection, x: float, z: float, h: float) -> float:
        shore = section.shore
        if shore is None:
            return h
        inland = shore.land_side * (x - self.path_x(shore.path, z))
        return _lerp(shore.seabed, h, smoothstep(-shore.width / 2, shore.width / 2, inland))
