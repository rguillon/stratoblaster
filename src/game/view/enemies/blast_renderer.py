"""GD-62: explosions where enemies and missiles were destroyed, in playfield space, ported from
`enemies/blast-renderer.ts`. Each layer (smoke, shock rings, fireballs, debris, embers) is one mesh
of thin instances, so a big blast costs no more draw calls than a small one."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

type Rgb = list[float]
# The table of the blast layers: each disc, whether it is added on, and its depth.
type LayerTable = dict[str, tuple[Callable[[], Any], bool, float]]
__pragma__("noskip")

from core.math.rng import create_rng  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.blast_particles import BLAST_LAYERS, BlastParticles  # noqa: E402
from game.view.shot_geometry import build_glow_disc  # noqa: E402
from render.babylon import (  # noqa: E402
    apply_vertex_data,
    babylon_constant,
    color3,
    color3_black,
    new_mesh,
    new_standard_material,
    vertex_data_of,
)

LOOK = ENEMY_LOOK.blasts


def _object_with_colors(geo: Any, colors: list[float]) -> Any:
    """`{ ...geo, colors }`: a copy of a coloured geometry with other colours."""
    __pragma__("js", "{}", "return Object.assign({}, geo, {colors: colors});")
    return None


def _float32_array(length: int) -> Any:
    """A zero-filled `Float32Array` of `length` values."""
    __pragma__("js", "{}", "return new Float32Array(length);")
    return None


def _ceil_log2(n: int) -> int:
    """`Math.ceil(Math.log2(n))`."""
    __pragma__("js", "{}", "return Math.ceil(Math.log2(n));")
    return 0


def soft(segments: int) -> Any:
    """A soft white disc, fading to its rim."""
    return build_glow_disc(
        segments,
        [[1, 1, 1], [0.85, 0.85, 0.85], [0.4, 0.4, 0.4], [0, 0, 0]],
    )


def ring(segments: int) -> Any:
    """A thin white ring at the rim of a disc, black (nothing, added on) inside and out."""
    colors: list[Rgb] = [[0, 0, 0] for _ in range(7)]
    colors.extend([[0.5, 0.5, 0.5], [1, 1, 1], [0, 0, 0]])
    return build_glow_disc(segments, colors)


def puff(segments: int) -> Any:
    """A soft disc for smoke: white, its opacity fading to the rim."""
    geo = soft(segments)
    colors: list[float] = []
    for i in range(0, len(geo.colors), 4):
        colors.extend([1, 1, 1, geo.colors[i] or 0])
    return _object_with_colors(geo, colors)


# Each layer: its disc (a function), whether it is added on (fire) or laid over (smoke), and its
# depth.
LAYERS = {  # type: LayerTable
    "smoke": (lambda: puff(LOOK.smoke.segments), False, -2.8),
    "rings": (lambda: ring(LOOK.ring.segments), False, -3),
    "fireballs": (lambda: puff(LOOK.fireball.segments), False, -3.2),
    "debris": (lambda: soft(LOOK.debris.segments), True, -3.4),
    "embers": (lambda: soft(LOOK.debris.segments), True, -3.5),
}


class LayerMesh:
    """One mesh drawing a whole layer as thin instances, tinted one by one."""

    def __init__(self, name: str, geo: Any, add: bool, z: float, order: int, scene: Any) -> None:
        self.z = z
        self.matrices = _float32_array(0)
        self.colors = _float32_array(0)
        self.mesh = new_mesh(name, scene)
        data = vertex_data_of(geo.positions, geo.indices, None, geo.colors)
        apply_vertex_data(data, self.mesh)
        material = new_standard_material(name, scene)
        material.emissiveColor = color3(1, 1, 1)
        material.diffuseColor = color3_black()
        material.specularColor = color3_black()
        material.disableLighting = True
        material.backFaceCulling = False
        material.alphaMode = babylon_constant("ALPHA_ADD" if add else "ALPHA_COMBINE")
        # Below 1, so the material goes through the blended pass.
        material.alpha = 0.999
        material.disableDepthWrite = True
        self.mesh.material = material
        self.mesh.hasVertexAlpha = not add
        self.mesh.isPickable = False
        # Drawn in layer order (smoke under fire), and never culled: instances spread anywhere.
        self.mesh.alphaIndex = order
        self.mesh.alwaysSelectAsActiveMesh = True
        self.mesh.setEnabled(False)

    def show(self, spots: list[Any]) -> None:
        """Draws one thin instance per spot, tinted by the spot's colour."""
        n = len(spots)
        self.mesh.setEnabled(n > 0)
        if n == 0:
            return
        grow = n > len(self.colors) / 4
        if grow:
            capacity = max(16, 2 ** _ceil_log2(n))
            self.matrices = _float32_array(capacity * 16)
            self.colors = _float32_array(capacity * 4)
        for i, s in enumerate(spots):
            m = i * 16
            self.matrices.set(
                [s.radius, 0, 0, 0, 0, s.radius, 0, 0, 0, 0, 1, 0, s.x, s.y, self.z, 1],
                m,
            )
            self.colors.set([s.r, s.g, s.b, s.a], i * 4)
        if grow:
            self.mesh.thinInstanceSetBuffer("matrix", self.matrices, 16, False)
            self.mesh.thinInstanceSetBuffer("color", self.colors, 4, False)
        # Before the update: Babylon uploads only the first `thinInstanceCount` matrices, and new
        # instances would show for a frame where older ones were, in their new colours (phase 6
        # review: stray glows when an enemy blew up).
        self.mesh.thinInstanceCount = n
        if not grow:
            self.mesh.thinInstanceBufferUpdated("matrix")
            self.mesh.thinInstanceBufferUpdated("color")

    def dispose(self) -> None:
        if self.mesh.material:
            self.mesh.material.dispose()
        self.mesh.dispose()


class BlastRendererHandle:
    """The blast renderer (`BlastRenderer` in the TypeScript): its `sync` and `dispose`."""

    def __init__(self, sync: Any, dispose: Any) -> None:
        self.sync = sync
        self.dispose = dispose


def create_blast_renderer(scene: Any) -> BlastRendererHandle:
    """GD-62: explosions where enemies and missiles were destroyed, in playfield space."""
    layers: list[list[Any]] = []
    for order, layer in enumerate(BLAST_LAYERS):
        geo_of, add, z = LAYERS[layer]
        layers.append([layer, LayerMesh("blast-" + layer, geo_of(), add, z, order, scene)])
    particles = BlastParticles(create_rng(LOOK.seed))

    def sync(blasts: list[Any], dt: float) -> None:
        for blast in blasts:
            particles.emit(blast)
        spots = particles.step(dt)
        # In front of the ships (towards the camera, -Z).
        for entry in layers:
            entry[1].show(spots[entry[0]])

    def dispose() -> None:
        for entry in layers:
            entry[1].dispose()

    return BlastRendererHandle(sync, dispose)
