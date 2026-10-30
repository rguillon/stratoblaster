"""GD-43: the enemies' shots in playfield space (bullets, missiles, lasers)

Bullets are thin instances of a template per layer (as the blasts, D-034): one draw call however
many bullets are flying.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
__pragma__("noskip")

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.readability import READABILITY  # noqa: E402
from game.view.enemies.enemy_lasers import EnemyLasers  # noqa: E402
from game.view.enemies.enemy_materials import enemy_materials, mesh_of  # noqa: E402
from game.view.shot_geometry import (  # noqa: E402
    build_glow_disc,
    build_swirl,
)
from game.view.shots.shot_meshes import (  # noqa: E402
    additive_template,
    blended_template,
)
from render.babylon import (  # noqa: E402
    babylon_constant,
    new_transform_node,
    node_name,
)
from render.geometry.solids import SolidBuilder  # noqa: E402
from render.node_adopter import ON_TOP_ALPHA_INDEX  # noqa: E402
from render.node_pool import NodePool  # noqa: E402
from render.outline import set_outline  # noqa: E402

LOOK = ENEMY_LOOK
# Draw order of the bullets: after every other see-through mesh of the playfield, the missiles'
# flames and the lasers (`ON_TOP_ALPHA_INDEX`) included (P14-R05).
ON_TOP = ON_TOP_ALPHA_INDEX + 1


def _object_keys(obj: Any) -> list[str]:
    """`Object.keys(obj)`."""
    __pragma__("skip")
    return list(obj.keys())
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.keys(obj);")
    return []


def _float32_array(length: int) -> Any:
    """A zero-filled `Float32Array` of `length` values."""
    __pragma__("skip")
    return [0.0] * length
    __pragma__("noskip")
    __pragma__("js", "{}", "return new Float32Array(length);")
    return None


def _ceil_log2(n: int) -> int:
    """`Math.ceil(Math.log2(n))`."""
    __pragma__("skip")
    return math.ceil(math.log2(n)) if n > 0 else 0
    __pragma__("noskip")
    __pragma__("js", "{}", "return Math.ceil(Math.log2(n));")
    return 0


# The bullet styles of the look (`LOOK.bullets.styles`), in order.
STYLES = _object_keys(LOOK.bullets.styles)


def disc_alphas(segments: int, fade: list[float]) -> list[float]:
    """Opacity of each vertex of a bullet's disc: its centre, then each ring's."""
    out: list[float] = []
    for ring, alpha in enumerate(fade):
        count = 1 if ring == 0 else segments
        out.extend([alpha for _ in range(count)])
    return out


class BulletLayer:
    """One layer of the bullets of one colour, drawn as thin instances of a template: one draw call
    however many bullets are flying."""

    def __init__(self, mesh: Any, z: float, order: int) -> None:
        self.mesh = mesh
        self.z = z
        # A first buffer of 16 instances, one of them (a zero matrix, drawn nowhere) and the mesh
        # hidden: a thin-instanced mesh from the start, so its shader with thin instances is
        # compiled before play (P13-R04), not on the frame of the first shot. (Babylon counts a
        # mesh as thin-instanced only while it has instances.)
        self.matrices = _float32_array(16 * 16)
        mesh.thinInstanceSetBuffer("matrix", self.matrices, 16, False)
        mesh.thinInstanceCount = 1
        mesh.setEnabled(False)
        # P14-R05: over everything else on the playfield (blasts, player shots, models), in layer
        # order; never culled: instances spread anywhere.
        mesh.alphaIndex = ON_TOP + order
        mesh.alwaysSelectAsActiveMesh = True
        if mesh.material:
            mesh.material.depthFunction = babylon_constant("ALWAYS")

    def show(self, spots: list[list[float]]) -> None:
        """Draws one thin instance per spot `[x, y, radius, angle]`."""
        n = len(spots)
        self.mesh.setEnabled(n > 0)
        if n == 0:
            return
        grow = n > len(self.matrices) / 16
        if grow:
            self.matrices = _float32_array(max(16, 2 ** _ceil_log2(n)) * 16)
        for i, spot in enumerate(spots):
            x = spot[0]
            y = spot[1]
            radius = spot[2]
            angle = spot[3]
            c = math.cos(angle) * radius
            s = math.sin(angle) * radius
            self.matrices.set([c, s, 0, 0, -s, c, 0, 0, 0, 0, 1, 0, x, y, self.z, 1], i * 16)
        if grow:
            self.mesh.thinInstanceSetBuffer("matrix", self.matrices, 16, False)
        # Before the update, as the blasts (Babylon uploads only `thinInstanceCount` matrices).
        self.mesh.thinInstanceCount = n
        if not grow:
            self.mesh.thinInstanceBufferUpdated("matrix")

    def dispose(self) -> None:
        if self.mesh.material:
            self.mesh.material.dispose()
        self.mesh.dispose()


def contrast_spark(name: str, scene: Any) -> Any:
    """The white spark of a bullet in the contrast style (P10-R07). It has no dark rim any more
    (reviewer, 2026-10-30, D-194)."""
    segments = LOOK.bullets.segments
    spark = LOOK.contrast.spark
    return additive_template(name + "-spark", build_glow_disc(segments, spark.colors), scene)


def halo_scale(age: float) -> float:
    """Size of a bullet's aura, relative to the bullet, flickering as it flies."""
    halo = LOOK.bullets.halo
    scale: float = halo.size * (1 + halo.flicker * math.sin(2 * math.pi * halo.flickerHz * age))
    return scale


def core_scale(age: float) -> float:
    """Size of a bullet's core, relative to the bullet, `age` seconds after it was fired."""
    core = LOOK.bullets.core
    scale: float = core.size * (1 + core.pulse.amount * math.sin(2 * math.pi * core.pulse.hz * age))
    return scale


def drawn_radius(b: Any) -> float:
    """A bullet's drawn radius: never under half `minEnemyBulletSize` (P14-R05); its hitbox is
    kept."""
    radius: float = max(b.radius * LOOK.bullets.scale, READABILITY.minEnemyBulletSize / 2)
    return radius


def body_placement(b: Any, r: float) -> list[float]:
    """The body is drawn at the bullet's radius."""
    return [r, 0]


def halo_placement(b: Any, r: float) -> list[float]:
    """The aura breathes with the bullet's age."""
    return [r * halo_scale(b.age), 0]


def core_placement(b: Any, r: float) -> list[float]:
    """The core pulses with the bullet's age."""
    return [r * core_scale(b.age), 0]


def fixed_placement(factor: float) -> Any:
    """A layer drawn at a fixed factor of the bullet's radius."""

    def place(b: Any, r: float) -> list[float]:
        return [r * factor, 0]

    return place


def swirl_placement(swirl: Any) -> Any:
    """A swirl grows with its size and turns with the bullet's heading and age."""

    def place(b: Any, r: float) -> list[float]:
        return [r * swirl.size, b.heading * 3 + swirl.spinRadPerSec * b.age]

    return place


def swirl_layer(name: str, scene: Any, swirl: Any, i: int, colors: Any) -> list[Any]:
    """One swirl of plasma, spinning with its bullet."""
    color = colors.swirls[i]
    if color == None:  # noqa: E711
        color = colors.halo
    mesh = additive_template(
        name + "-swirl-" + str(i),
        build_swirl(LOOK.bullets.swirlSegments, color, swirl),
        scene,
    )
    return [mesh, swirl_placement(swirl)]


def bullet_layers(style: str, scene: Any, contrast: bool) -> list[list[Any]]:
    """A ball of plasma (GD-43), back to front: a faint flickering aura, a solid body, two curled
    swirls of brighter plasma spinning opposite ways, and a pulsing white-hot core. In the
    contrast style (P10-R07), a white spark over the core."""
    segments = LOOK.bullets.segments
    fade = LOOK.bullets.fade
    colors = LOOK.bullets.styles[style]
    name = "enemy-bullet-" + style
    body = build_glow_disc(segments, colors.body)
    layers: list[list[Any]] = [
        [
            additive_template(name + "-halo", build_glow_disc(segments, colors.halo), scene),
            halo_placement,
        ],
        [blended_template(name, body, disc_alphas(segments, fade), scene), body_placement],
    ]
    for i, swirl in enumerate(LOOK.bullets.swirls):
        layers.append(swirl_layer(name, scene, swirl, i, colors))
    layers.append(
        [
            additive_template(name + "-core", build_glow_disc(segments, colors.core), scene),
            core_placement,
        ]
    )
    if contrast:
        spark = LOOK.contrast.spark
        layers.append([contrast_spark(name, scene), fixed_placement(spark.size)])
    # Back to front, towards the camera (-Z).
    out: list[list[Any]] = []
    for order, entry in enumerate(layers):
        out.append([BulletLayer(entry[0], -1 - 0.05 * order, order), entry[1]])
    return out


def bullet_pools(scene: Any, contrast: bool) -> dict[str, list[list[Any]]]:
    """One set of plasma layers per bullet colour (GD-43)."""
    pools: dict[str, list[list[Any]]] = {}
    for style in STYLES:
        pools[style] = bullet_layers(style, scene, contrast)
    return pools


def warm_bullets(pools: dict[str, list[list[Any]]], on: bool) -> None:
    """Shows one bullet in each layer of each colour (`on`), or hides them all: the loading draws
    them, so the shaders of the layers (some only drawn with their instances) compile before play
    (P13-R04), not on the frame of the first shot of each colour."""
    spot = [[0, 0, 0, 0]] if on else []
    for style in STYLES:
        for entry in pools[style]:
            entry[0].show(spot)


def sync_bullets(pools: dict[str, list[list[Any]]], bullets: list[Any]) -> None:
    """Draws every bullet in its colour's layers."""
    for style in STYLES:
        layers = pools[style]
        own = [b for b in bullets if (b.style if b.style in pools else STYLES[0]) == style]
        for entry in layers:
            layer = entry[0]
            place = entry[1]
            spots: list[list[float]] = []
            for b in own:
                placed = place(b, drawn_radius(b))
                spots.append([b.x, b.y, placed[0], placed[1]])
            layer.show(spots)


def build_missile(scene: Any, flame: Any, i: int) -> Any:
    """A small dark missile pointing +Y with an orange tip and a flame behind it, and (P14-R05) a
    rim glow in the enemy shots' colour, so it shows over blasts and bright ground."""
    look = LOOK.missile
    root = new_transform_node("enemy-missile-" + str(i), scene)
    body = SolidBuilder().cylinder(
        look.radius,
        look.length,
        6,
        LOOK.hull.panel,
        Placement([0, -look.length / 2, 0]),
    )
    tip = SolidBuilder().cylinder(
        look.radius,
        3,
        6,
        look.tip,
        Placement([0, look.length / 2, 0]),
        0,
    )
    mats = enemy_materials(scene)
    hull = mesh_of(node_name(root) + "-body", body.geometry, mats.hull, scene)
    hull.parent = root
    set_outline(hull, look.tip)
    mesh_of(node_name(root) + "-tip", tip.geometry, mats.neon, scene).parent = root
    glow = flame.clone(node_name(root) + "-flame")
    glow.parent = root
    glow.setEnabled(True)
    w = look.flameSize[0]
    h = look.flameSize[1]
    glow.position.set(0, -look.length / 2 - h * 0.6, 0.5)
    glow.scaling.set(w, h, 1)
    return root


def sync_missiles(pool: Any, missiles: list[Any]) -> None:
    """Places each missile's node on its shot."""
    shown = pool.show(len(missiles))
    for i, node in enumerate(shown):
        if i >= len(missiles):
            continue
        m = missiles[i]
        node.position.set(m.x, m.y, -0.5)
        node.rotation.z = -m.heading


class ShotRendererHandle:
    """The enemy shot renderer: its `sync`, `dispose`, and
    `warm(on)` (one bullet shown in each colour's layers, or none: see `warm_bullets`)."""

    def __init__(self, sync: Any, dispose: Any, warm: Any) -> None:
        self.sync = sync
        self.dispose = dispose
        self.warm = warm


def create_enemy_shot_renderer(scene: Any) -> ShotRendererHandle:
    """The enemies' shots of one scene: bullets, missiles, and lasers (contrast look, P10-R07,
    used in every level since P14-R05)."""
    contrast = True
    bullets = bullet_pools(scene, contrast)
    flame = additive_template("enemy-missile-flame", build_glow_disc(8, LOOK.missile.flame), scene)
    # P14-R05: over the player's shots and the blasts, under the bullets (its clones too).
    flame.alphaIndex = ON_TOP_ALPHA_INDEX
    missiles = NodePool(lambda i: build_missile(scene, flame, i))
    lasers = EnemyLasers(scene, contrast)
    clock = [0.0]

    def sync(frame: Any) -> None:
        clock[0] += frame.dt_seconds
        sync_bullets(bullets, frame.bullets)
        sync_missiles(missiles, frame.missiles)
        lasers.sync(frame.lasers, clock[0])

    def dispose() -> None:
        for style in STYLES:
            for entry in bullets[style]:
                entry[0].dispose()
        lasers.dispose()
        missiles.dispose()
        flame.dispose()

    def warm(on: bool) -> None:
        warm_bullets(bullets, on)

    return ShotRendererHandle(sync, dispose, warm)
