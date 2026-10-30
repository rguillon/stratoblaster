"""The lightning of a storm (phase 9, P09-R05): the flashes drawn from the level's seed and, for
some strikes, a bolt drawn in the clouds while its flashes last, added over what is behind it. The
flash itself lights the scene through the atmosphere (`flashed`), not here. It is only a look:
nothing in the simulation reads it.

Ported from `render/scenery/lightning-layer.ts`.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng
from core.scenery.lightning import LightningSchedule
from render.babylon import (
    apply_vertex_data,
    babylon_constant,
    color3,
    dispose_node,
    is_enabled,
    new_mesh,
    new_standard_material,
    set_enabled,
    vertex_data_of,
)
from render.scenery.cloud_layers import BELOW_CLOUDS_GROUP

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from core.scenery.atmosphere import Atmosphere  # noqa: E402
from core.scenery.lightning import Bolt, Strike  # noqa: E402
from render.scenery.playfield_framing import GroundWindow  # noqa: E402

Point = tuple[float, float]
__pragma__("noskip")


class BoltLook:
    """How a bolt is drawn in the clouds (P09-R05): a pale violet-white zigzag with a few forks."""

    color = (0.86, 0.86, 1)
    # Length of the main bolt, and of its forks, as shares of the view's width. (`length_`: a
    # class attribute named `length` would clash with the function's own length.)
    length_ = 0.55
    fork = 0.22
    forks = 2
    # Pieces of the main bolt, their widest sideways jag (world units), and the line's width.
    pieces = 12
    jag = 14
    width = 1.4
    # Draw order among the see-through meshes above the ground: before the weather.
    alpha_index = 3


BOLT_LOOK = BoltLook


def _hypot(a: float, b: float) -> float:
    """`Math.hypot(a, b)`: JavaScript's rounding, not `math.hypot`."""
    __pragma__("js", "{}", "return Math.hypot(a, b);")
    return 0


def _zigzag(random: Any, start: Point, length: float, angle: float, pieces: int) -> list[Point]:
    """A jagged line of `pieces` from `start`, `length` long, heading `angle` (radians from +X)."""
    n = pieces
    step = length / n
    dx = math.cos(angle)
    dz = math.sin(angle)
    points: list[Point] = [start]
    for i in range(1, n + 1):
        jag = (random() - 0.5) * 2 * BOLT_LOOK.jag * (0.3 if i == n else 1)
        points.append(
            (
                start[0] + dx * step * i - dz * jag,
                start[1] + dz * step * i + dx * jag,
            )
        )
    return points


def _ribbons(lines: list[list[Point]], width: float) -> Any:
    """Flat ribbons along `lines`, `width` wide, in the XZ plane."""
    positions: list[float] = []
    indices: list[int] = []
    for line in lines:
        for i in range(1, len(line)):
            a = line[i - 1]
            b = line[i]
            length = _hypot(b[0] - a[0], b[1] - a[1])
            if length == 0:
                length = 1
            nx = (-(b[1] - a[1]) / length) * width
            nz = ((b[0] - a[0]) / length) * width
            v = len(positions) // 3
            positions.extend([a[0] - nx, 0, a[1] - nz, a[0] + nx, 0, a[1] + nz])
            positions.extend([b[0] + nx, 0, b[1] + nz, b[0] - nx, 0, b[1] - nz])
            indices.extend([v, v + 1, v + 2, v, v + 2, v + 3])
    return vertex_data_of(positions, indices)


def bolt_lines(seed: float, span: float) -> list[list[Point]]:
    """The lines of the bolt of seed `seed`, across a view `span` wide, from its centre."""
    random = create_rng(int(seed))
    angle = random() * math.pi * 2
    main = _zigzag(random, (0, 0), span * BOLT_LOOK.length_, angle, BOLT_LOOK.pieces)
    forks: list[list[Point]] = []
    for _ in range(BOLT_LOOK.forks):
        origin = main[1 + math.floor(random() * (len(main) - 2))]
        turn = angle + (-1 if random() < 0.5 else 1) * (0.4 + random() * 0.6)  # noqa: PLR2004
        forks.append(_zigzag(random, origin, span * BOLT_LOOK.fork, turn, BOLT_LOOK.pieces // 2))
    out = [main]
    out.extend(forks)
    return out


class LightningLayer:
    """The lightning of a storm: the flashes from the level's seed, and the bolts drawn in the
    clouds while they last."""

    def __init__(self, scene: Any, seed: int, place: tuple[GroundWindow, float]) -> None:
        """`place`: the ground window the bolts are drawn in, and the altitude of the clouds."""
        self._scene = scene
        self.schedule = LightningSchedule(seed)
        self._place = place
        material = new_standard_material("lightning-bolt", scene)
        material.disableLighting = True
        material.emissiveColor = color3(BOLT_LOOK.color[0], BOLT_LOOK.color[1], BOLT_LOOK.color[2])
        material.alphaMode = babylon_constant("ALPHA_ADD")
        material.backFaceCulling = False
        material.disableDepthWrite = True
        self._material = material
        self._bolt: Any = None
        self._strike: Strike | None = None
        self._flash = 0.0

    @property
    def flash(self) -> float:
        """The flash (0..1) on the last frame, before the storm's lightning strength."""
        return self._flash

    @property
    def bolt_shown(self) -> bool:
        """Whether a bolt was drawn on the last frame."""
        return self._bolt is not None and is_enabled(self._bolt)

    def update(self, atmosphere: Atmosphere, time: float, z: float) -> float:
        """The flash at `time` for `atmosphere`'s lightning; the bolt is drawn near `z`."""
        strength = atmosphere.lightning
        self._flash = self.schedule.flash_at(time) if strength > 0 else 0
        strike = self.schedule.strike_at(time) if self._flash > 0 else None
        if strike is not None and strike.bolt is not None and strike is not self._strike:
            self._build(strike.bolt, z)
        self._strike = strike
        shown = strike is not None and strike.bolt is not None
        if self._bolt is not None:
            set_enabled(self._bolt, shown)
        if shown:
            self._material.alpha = min(1, self._flash * strength)
        return self._flash

    def _build(self, bolt: Bolt, z: float) -> None:
        ground_window, altitude = self._place
        span = ground_window.half_width * 2
        if self._bolt is not None:
            dispose_node(self._bolt)
        mesh = new_mesh("lightning-bolt", self._scene)
        apply_vertex_data(_ribbons(bolt_lines(bolt.seed, span), BOLT_LOOK.width), mesh)
        mesh.material = self._material
        mesh.isPickable = False
        mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1
        mesh.alphaIndex = BOLT_LOOK.alpha_index
        mesh.position.set(
            (bolt.x - 0.5) * span,
            altitude,
            z + ground_window.z_near + bolt.z * (ground_window.z_far - ground_window.z_near),
        )
        self._bolt = mesh
