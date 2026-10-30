"""Randomly generated roads and paths of a level (P04-R07) Main roads wind along the whole level.
Where the ground is under
`min_height` (the sea) or steeper than `max_slope`, a main road turns off the screen before it and
comes back from the side after it, so no road ever starts or ends on screen (beyond X =
±`offscreen_x`). Paths branch off the main roads at random intervals, widen where they meet them,
and run across to past the screen edge; a path that cannot reach it on buildable ground is dropped.
Buildings stand only along roads, in slots every `slot_spacing` on both sides. The streets of the
runout, past the level's end, are laid apart (`add_runout`). Pure and deterministic for a given
seed.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

from core.math.rng import Random  # noqa: E402
from core.scenery.districts import District  # noqa: E402
from core.scenery.height_field import HeightField  # noqa: E402
from core.scenery.scenery_level import RoadRules, TileRules  # noqa: E402
from core.scenery.street_links import Block  # noqa: E402

__pragma__("noskip")

from core.math.noise import create_noise2d  # noqa: E402
from core.math.rng import create_rng, random_in  # noqa: E402
from core.scenery.districts import ZRange, find_districts, laid_districts  # noqa: E402
from core.scenery.lanes import lanes_of, main_road_width, with_width  # noqa: E402
from core.scenery.road_paths import PathGround, lay_paths  # noqa: E402
from core.scenery.road_segments import SegmentIndex, add_slots  # noqa: E402
from core.scenery.road_types import Road, RoadPoint, RoadSlot, RoadSnapshot  # noqa: E402
from core.scenery.street_grid import street_runs  # noqa: E402
from core.scenery.street_runs import Point  # noqa: E402

INFINITY = float("Infinity")

# Irregular wobble of a main road, as a share of its meander amplitude.
WOBBLE = 0.3
# When a road cannot leave the screen from its end, it tries again this many points earlier…
RETREAT_POINTS = 4
# …at most this many times, then the piece is dropped.
MAX_RETREATS = 40
# Rounding left out when a slope is known to be under the steepest a road takes.
SLOPE_SLACK = 1e-9
# World units of road generated before the start and after the end of a level.
LEVEL_MARGIN = 3000
# …but a street grid the level starts in only begins this far before it (reviewer, 2026-10-28): the
# camera sees the ground from Z = 0 at the start, and street grids are the costliest roads to lay.
# The winding roads and paths still begin `LEVEL_MARGIN` before (they cost little).
STREETS_BEFORE = 400
SQRT2 = math.sqrt(2)


def _any_road(_road: Road) -> bool:
    """Accepts every road."""
    return True


def _other_than(except_road: Road) -> Callable[[Road], bool]:
    """Accepts every road but `except_road`."""

    def accept(road: Road) -> bool:
        return road is not except_road

    return accept


def _heading(points: Sequence[Point], i: int) -> float:
    """Heading of the segment ending at `points[i]`, in radians from +Z, positive towards +X."""
    a = points[max(0, i - 1)] if len(points) > 0 else None
    b = points[i] if 0 <= i < len(points) else None
    if a is not None and b is not None:
        return math.atan2(b.x - a.x, b.z - a.z)
    return 0


class Follow:
    """A main road to follow at a distance, on one side (`noCrossings`)."""

    def __init__(self, line: Sequence[Point], side: float, width: float, gap: float) -> None:
        self.line = line
        self.side = side
        """-1: on its left (-X), 1: on its right."""
        self.width = width
        self.gap = gap


class RoadNetworkOptions:
    """What a `RoadNetwork` starts from, besides its ground and rules."""

    def __init__(
        self,
        made: RoadSnapshot | None = None,
        runout_from: float | None = None,
        streets_from: float | None = None,
    ) -> None:
        self.made = made
        """The roads made before (e.g. in a worker, P13-R03): taken as they are, not generated."""
        self.runout_from = runout_from
        """Where the level's runout starts, if it has one: its streets are laid by `add_runout`."""
        self.streets_from = streets_from
        """The street grids start no lower than this (the winding roads keep out of them below
        too)."""


class RoadNetwork:
    """Randomly generated roads and paths of a level (see the module doc)."""

    def __init__(
        self,
        field: HeightField,
        rules: RoadRules,
        seed: int,
        span: ZRange,
        options: RoadNetworkOptions | None = None,
    ) -> None:
        """`span`: Z range covered by the main roads; their ends there are out of view."""
        opts = options if options is not None else RoadNetworkOptions()
        self.field = field
        self.rules = rules
        self.range = span
        self._roads: list[Road] = []
        self.slots: list[RoadSlot] = []
        """The building slots (not kept by `snapshot`: only placing the buildings needs them)."""
        self.blocks: list[Block] = []
        """The blocks between the streets of the districts (phase 4 review)."""
        self.setback = rules.setback
        """Gap between road edges and building footprints."""
        self.offscreen_x = rules.offscreen_x
        """Roads start and end beyond X = ±offscreen_x, out of view."""
        self.runout_from = opts.runout_from
        """Where the runout starts, if its streets are laid apart (see `add_runout`)."""
        self._segments = SegmentIndex()
        self._seed = seed
        self._streets_from = opts.streets_from if opts.streets_from is not None else -INFINITY
        self._districts: list[District] = find_districts(field.sections, span)
        before, after = laid_districts(self._districts, opts.streets_from, opts.runout_from)
        self._runout: list[District] = after
        self._runout_laid = False
        self._laying: float | None = None
        if opts.made is not None:
            self._restore(opts.made)
            return
        random = create_rng(seed + 4)
        # Without crossings, the streets come first: the winding roads and the paths keep clear.
        if rules.no_crossings is not None:
            self._add_streets(before, create_rng(seed + 5), None)
        previous: Follow | None = None
        for i in range(rules.main_roads):
            width = main_road_width(rules, i)
            line = self._main_line(random, width, previous)
            self._laying = width / 2 if rules.no_crossings is not None else None
            self._add_main_pieces(line, width)
            self._laying = None
            previous = self._follow(line, previous, width)
        ground = PathGround(
            rules,
            span,
            lambda x, z: self._open(x, z),  # noqa: PLW0108 (Transcrypt binds methods: keep the lambda)
            lambda x, z, which: self._segments.nearest(x, z, which),  # noqa: PLW0108
            lambda points: self._add_road("cross", points),  # noqa: PLW0108
        )
        lay_paths(ground, random, [road for road in self._roads if road.kind == "main"])
        if rules.no_crossings is None:
            self._add_streets(before, create_rng(seed + 5), None)
        for road in self._roads:
            self._slots(road)

    def _slots(self, road: Road) -> None:
        """Building slots along `road`; none along the streets on tiles (P15-R08: blocks)."""
        if road.kind == "street" and self.rules.tiles is not None:
            return
        add_slots(road, self.rules.slot_spacing, self.slots)

    @property
    def tiles(self) -> TileRules | None:
        """The grid of tiles of the districts, if they are laid on one (phase 15)."""
        return self.rules.tiles

    @property
    def runout_laid(self) -> bool:
        """Whether the runout's streets are laid (see `add_runout`)."""
        return self._runout_laid

    @property
    def roads(self) -> list[Road]:
        """The roads, the runout's last once laid (a new list then: the old one stays as it was)."""
        return self._roads

    def add_runout(self, made: RoadSnapshot | None = None) -> RoadSnapshot:
        """Lays the streets of the runout (reviewer, 2026-10-28: after the rest, so the level is
        ready sooner), or takes those `made` before (e.g. in a worker), and returns what it added:
        its roads, blocks and slots. Their columns start on the last row laid before the runout.
        Once only: afterwards, it adds nothing."""
        if self._runout_laid:
            return RoadSnapshot([], [], [])
        self._runout_laid = True
        kept = self._roads
        self._roads = list(kept)
        blocks_before = len(self.blocks)
        slots_before = len(self.slots)
        from_ = self.runout_from if self.runout_from is not None else INFINITY

        # A column may end where it starts, on the row laid before (but not where that row was cut).
        def joins(p: Any) -> bool:
            return self._street_ends(p) or (p.z <= from_ and self.edge_distance(p.x, p.z) < 0)

        if made is not None:
            for road in made.roads:
                self._index(road)
            self.blocks.extend(made.blocks)
            self.slots.extend(made.slots)
        else:
            self._add_streets(self._runout, create_rng(self._seed + 6), joins)
        added = self._roads[len(kept) :]
        # The same list when there is nothing more.
        if len(added) == 0:
            self._roads = kept
        elif made is None:
            for road in added:
                self._slots(road)
        return RoadSnapshot(
            added,
            self.blocks[blocks_before:],
            self.slots[slots_before:],
        )

    def _follow(
        self, line: Sequence[Point], previous: Follow | None, width: float
    ) -> Follow | None:
        """How the next main road follows `line` without crossing it (`noCrossings`): on the side
        of the screen the first main road leaves free, at least `gap` from its edge."""
        no_crossings = self.rules.no_crossings
        if no_crossings is None:
            return None
        total = 0.0
        for p in line:
            total += p.x
        mean = total / max(1, len(line))
        side = previous.side if previous is not None else -1 if mean >= 0 else 1
        return Follow(line, side, width, no_crossings.gap)

    def edge_distance(self, x: float, z: float, except_road: Road | None = None) -> float:
        """Distance from (`x`, `z`) to the edge of the nearest road other than `except_road`
        (negative on a road), or Infinity when no road is within about `BUCKET` units."""
        which = _any_road if except_road is None else _other_than(except_road)
        return self._segments.nearest(x, z, which).distance

    def clear_of(self, x: float, z: float, clearance: float) -> bool:
        """Whether (`x`, `z`) is at least `clearance` from every road edge: `edge_distance(x, z) >=
        clearance`, faster (reviewer, 2026-10-28: the props ask this a lot)."""
        return self._segments.clear_of(x, z, clearance)

    def buildable(self, x: float, z: float) -> bool:
        """Whether a road can be built at (`x`, `z`)."""
        min_height = self.rules.min_height
        max_slope = self.rules.max_slope
        step = self.rules.step
        if not (self.field.height(x, z) >= min_height):
            return False
        # Reviewer, 2026-10-28: where the ground cannot be that steep, the slope is not measured
        # (it is at most √2 times the most it changes along each axis).
        if SQRT2 * self.field.steepness(x, z, step) < max_slope - SLOPE_SLACK:
            return True
        return self.field.slope(x, z, step) <= max_slope

    def _offscreen(self, p: Point) -> bool:
        """Whether `p` is off the screen, or at the ends of the generated range (out of view)."""
        return (
            abs(p.x) >= self.rules.offscreen_x
            or p.z <= self.range.z_min
            or p.z >= self.range.z_max - self.rules.step
        )

    def _street_ends(self, p: Point) -> bool:
        """Whether a street may end at `p`: off the screen, or where the street grids start."""
        return self._offscreen(p) or p.z <= self._streets_from

    def _main_line(self, random: Random, width: float, previous: Follow | None) -> list[Point]:
        """A main road's centre line: on its own, or following the previous one (`noCrossings`)."""
        meander = self.rules.meander
        spread = self.rules.spread
        step = self.rules.step
        x0 = random_in(random, -spread, spread)
        amplitude = random_in(random, meander.amplitude[0], meander.amplitude[1])
        wavelength = random_in(random, meander.wavelength[0], meander.wavelength[1])
        phase = random() * math.pi * 2
        wobble = create_noise2d(math.floor(random() * 1000000000))
        points: list[Point] = []
        z = self.range.z_min
        k = 0
        while z <= self.range.z_max:
            wave = math.sin((2 * math.pi * z) / wavelength + phase) + WOBBLE * wobble(
                z / wavelength, 0.5
            )
            followed = (
                previous.line[k] if (previous is not None and k < len(previous.line)) else None
            )
            if previous is not None and followed is not None:
                # From `gap` to `gap + 2 × amplitude` beside the edge of the road it follows.
                side = previous.side
                gap = previous.gap
                apart = gap + (previous.width + width) / 2
                points.append(
                    Point(
                        followed.x + side * (apart + amplitude * (1 + wave / (1 + WOBBLE))),
                        z,
                    )
                )
            else:
                points.append(Point(x0 + amplitude * wave, z))
            z += step
            k += 1
        return points

    def _add_main_pieces(self, line: Sequence[Point], width: float) -> None:
        """Lays the buildable runs of a main road line, each made to start and end off the screen:
        an end on screen gets a turn that leaves the screen sideways (tried earlier and earlier
        along the run when the ground does not allow it there)."""
        run: list[Point] = []
        # Each piece is laid at once, so the next ones keep clear of it (`noCrossings`).
        for p in line:
            if self._open(p.x, p.z):
                run.append(p)
            else:
                self._close_run(run, width)
                run = []
        self._close_run(run, width)

    def _close_run(self, run: Sequence[Point], width: float) -> None:
        piece = self._leave_at_both_ends(run) if len(run) >= self.rules.min_run else None
        if piece is not None:
            self._add_road("main", with_width(piece, width))

    def _leave_at_both_ends(self, run: Sequence[Point]) -> list[Point] | None:
        end = self._leave(run)
        if end is None:
            return None
        reversed_end = self._leave(list(reversed(end)))
        if reversed_end is None:
            return None
        return list(reversed(reversed_end))

    def _leave(self, run: Sequence[Point]) -> list[Point] | None:
        """`run`, cut back if needed and ended by a turn that leaves the screen."""
        if len(run) == 0 or self._offscreen(run[len(run) - 1]):
            return list(run)
        for attempt in range(MAX_RETREATS + 1):
            i = len(run) - 1 - attempt * RETREAT_POINTS
            from_ = run[i] if 0 <= i < len(run) else None
            if from_ is None or i + 1 < self.rules.min_run:
                return None
            exit_points = self._exit_turn(from_, _heading(run, i))
            if exit_points is not None:
                result = list(run[0 : i + 1])
                result.extend(exit_points)
                return result
        return None

    def _exit_turn(self, from_: Point, start: float) -> list[Point] | None:
        """Points turning from `from_` (heading `start`) towards the nearest side of the screen,
        then on until off the screen; the other side is tried when that one is not buildable."""
        nearest = 1 if from_.x >= 0 else -1
        first = self._turn_towards(from_, start, nearest)
        if first is not None:
            return first
        return self._turn_towards(from_, start, -nearest)

    def _turn_towards(self, from_: Point, start: float, side: int) -> list[Point] | None:
        turn_rate = self.rules.turn_rate
        step = self.rules.step
        offscreen_x = self.rules.offscreen_x
        # The side's heading (±90°), taken a whole turn from where it is nearest the start heading,
        # so the road turns the short way.
        side90 = (side * math.pi) / 2
        target = side90 + 2 * math.pi * math.floor((start - side90) / (2 * math.pi) + 0.5)
        max_points = math.ceil((4 * offscreen_x) / step)
        points: list[Point] = []
        x = from_.x
        z = from_.z
        h = start
        for _ in range(max_points):
            h += max(-turn_rate, min(turn_rate, target - h))
            x += math.sin(h) * step
            z += math.cos(h) * step
            if not self._open(x, z):
                return None
            points.append(Point(x, z))
            if side * x >= offscreen_x:
                return points
        return None

    def _add_streets(
        self,
        districts: Sequence[District],
        random: Random,
        out_of_view: Callable[[Any], bool] | None,
    ) -> None:
        """The straight streets of `districts` (phase 4 review, see `street_runs`), as `street`
        roads of the main road width, or wider avenues and boulevards. A street may end on a node
        `out_of_view` accepts (by default, out of view: see `_street_ends`)."""
        if out_of_view is None:

            def default_out_of_view(p: Any) -> bool:
                return self._street_ends(p)

            out_of_view = default_out_of_view
        for district in districts:
            runs, blocks = street_runs(
                district,
                self.rules,
                random,
                lambda x, z: self.buildable(x, z),  # noqa: PLW0108
                out_of_view,
            )
            self.blocks.extend(blocks)
            for run in runs:
                self._add_road("street", with_width(run.points, run.width))

    def _open(self, x: float, z: float) -> bool:
        """Whether winding roads and paths may go at (`x`, `z`): buildable, out of the districts,
        and clear of the other roads while a main road is laid without crossings."""
        if self._in_district(z):
            return False
        if not self.buildable(x, z):
            return False
        laying = self._laying
        if laying is None:
            return True
        no_crossings = self.rules.no_crossings
        gap = no_crossings.gap if no_crossings is not None else 0
        return self.clear_of(x, z, laying + gap)

    def _in_district(self, z: float) -> bool:
        return any(z >= d.z_min and z <= d.z_max for d in self._districts)

    def snapshot(self) -> RoadSnapshot:
        """What this network made (P13-R03): its roads, blocks and slots."""
        return RoadSnapshot(list(self._roads), list(self.blocks), list(self.slots))

    def _restore(self, made: RoadSnapshot) -> None:
        """The roads made before, indexed as they were when made (in order), with their blocks
        and slots."""
        for road in made.roads:
            self._index(road)
        self.blocks.extend(made.blocks)
        self.slots.extend(made.slots)

    def _add_road(self, kind: str, points: Sequence[RoadPoint]) -> None:
        if kind == "cross":
            width = self.rules.cross_width
        else:
            width = points[0].width if len(points) > 0 else 0
        tiles = self.rules.tiles
        # Phase 15: a street on tiles has as many lanes each way as it is tiles wide.
        if kind == "street" and tiles is not None:
            lanes = min(4, max(1, math.floor(width / tiles.size + 0.5)))
        else:
            lanes = lanes_of(self.rules, width)
        self._index(Road(len(self._roads), kind, width, lanes, points))

    def _index(self, road: Road) -> None:
        self._roads.append(road)
        self._segments.add(road)


def level_roads(
    field: HeightField,
    rules: RoadRules,
    seed: int,
    options: RoadNetworkOptions | None = None,
) -> RoadNetwork:
    """The roads of a whole level, a little beyond both ends (the camera sees past them). The
    `streets_from` of `options` is ignored: the street grids start `STREETS_BEFORE` before Z = 0."""
    span = ZRange(-LEVEL_MARGIN, field.length_ + LEVEL_MARGIN)
    made = options.made if options is not None else None
    runout_from = options.runout_from if options is not None else None
    return RoadNetwork(
        field,
        rules,
        seed,
        span,
        RoadNetworkOptions(made, runout_from, -STREETS_BEFORE),
    )
