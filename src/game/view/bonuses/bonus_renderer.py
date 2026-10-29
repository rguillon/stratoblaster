"""The bonuses (phase 6 review, P11-R07), ported from `bonuses/bonus-renderer.ts`, in playfield
space: each one a badge of its kind swinging from side to side over a pulsing halo, and a ring
flashing out where the ship picks one up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from core.systems.bonus_world import Bonus  # noqa: E402
from render.game_view import BonusRenderer  # noqa: E402

__pragma__("noskip")

from game.config.bonus_look import BONUS_LOOK as LOOK  # noqa: E402
from game.view.bonuses.bonus_geometry import (  # noqa: E402
    build_bomb_badge,
    build_bonus_badge,
    build_life_badge,
)
from game.view.shot_geometry import build_glow_disc  # noqa: E402
from game.view.shots.shot_meshes import additive_template  # noqa: E402
from render.babylon import (  # noqa: E402
    apply_vertex_data,
    color3,
    color3_black,
    new_mesh,
    new_standard_material,
    node_name,
    vertex_data_of,
)
from render.node_pool import NodePool  # noqa: E402

KINDS = ["weapon", "life", "bomb"]


def _bonus_renderer(sync: Any, dispose: Any) -> Any:
    """A `BonusRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def _badge_colors(
    frame: list[float], face: list[float], chevrons: list[float], inset: float
) -> Any:
    """The colours of a weapon badge with its inset (`{ ...colors, inset }`), as a JS object."""
    __pragma__(
        "js",
        "{}",
        "return {frame: frame, face: face, chevrons: chevrons, inset: inset};",
    )
    return None


class Flash:
    """A pickup flash in progress."""

    def __init__(self, x: float, y: float, age: float) -> None:
        self.x = x
        self.y = y
        self.age = age


class KindPools:
    """The badges and halos of one kind of bonus."""

    def __init__(self, badges: NodePool, halos: NodePool) -> None:
        self.badges = badges
        self.halos = halos


def opaque_template(name: str, geo: Any, scene: Any) -> Any:
    """A disabled template showing its vertex colours, unlit and opaque (so it glows, GD-61)."""
    mesh = new_mesh(name, scene)
    data = vertex_data_of(geo.positions, geo.indices, None, geo.colors)
    apply_vertex_data(data, mesh)
    material = new_standard_material(name, scene)
    material.emissiveColor = color3(1, 1, 1)
    material.diffuseColor = color3_black()
    material.specularColor = color3_black()
    material.disableLighting = True
    # Both sides show as it spins.
    material.backFaceCulling = False
    mesh.material = material
    mesh.isPickable = False
    mesh.setEnabled(False)
    return mesh


def ring(segments: int, color: list[float]) -> Any:
    """A thin ring at the rim of a disc, black (nothing, added on) inside and out."""
    rings: list[list[float]] = [[0, 0, 0] for _ in range(6)]
    rings.append([0.4, 0.4, 0.4])
    rings.append(color)
    rings.append([0, 0, 0])
    return build_glow_disc(segments, rings)


def pool(template: Any) -> NodePool:
    """A pool of clones of `template`, each enabled."""

    def make(i: int) -> Any:
        mesh = template.clone(node_name(template) + "-" + str(i))
        mesh.setEnabled(True)
        return mesh

    return NodePool(make)


def sync_flashes(rings: NodePool, flashes: list[Flash], picked: list[Any], dt: float) -> None:
    """Ages the `flashes` by `dt`, starts one where each of `picked` was, draws them as rings."""
    size = LOOK.size
    depth = LOOK.depth
    flash = LOOK.flash
    for f in flashes:
        f.age += dt
    for p in picked:
        flashes.append(Flash(p.x, p.y, 0))
    live = [f for f in flashes if f.age < flash.life]
    while len(flashes) > 0:
        flashes.pop()
    for f in live:
        flashes.append(f)
    for i, mesh in enumerate(rings.show(len(flashes))):
        f = flashes[i]
        if not f:
            continue
        t = f.age / flash.life
        radius = size * flash.size * math.sqrt(max(t, 0.05))
        mesh.position.set(f.x, f.y, depth - 0.5)
        mesh.scaling.set(radius, radius, 1)
        mesh.visibility = 1 - t


def kind_templates(scene: Any) -> dict[str, list[Any]]:
    """The badge and halo templates of each bonus kind (P11-R07)."""
    halo = LOOK.halo
    life = LOOK.life
    bomb = LOOK.bomb

    def glow(name: str, rings: Any) -> Any:
        return additive_template(name, build_glow_disc(halo.segments, rings), scene)

    weapon_badge = opaque_template(
        "bonus-badge",
        build_bonus_badge(_badge_colors(LOOK.frame, LOOK.face, LOOK.chevrons, LOOK.frameInset)),
        scene,
    )
    weapon_halo = glow("bonus-halo", halo.colors)
    life_heart = opaque_template("bonus-heart", build_life_badge(life), scene)
    life_halo = glow("bonus-glow-life", life.halo)
    bomb_sphere = opaque_template("bonus-sphere", build_bomb_badge(bomb), scene)
    bomb_halo = glow("bonus-glow-bomb", bomb.halo)
    return {
        "weapon": [weapon_badge, weapon_halo],
        "life": [life_heart, life_halo],
        "bomb": [bomb_sphere, bomb_halo],
    }


def sync_kind(kind_pools: KindPools, bonuses: list[Bonus]) -> None:
    """Draws `bonuses` (all of one kind) as swinging badges over pulsing halos."""
    size = LOOK.size
    depth = LOOK.depth
    halo = LOOK.halo
    for i, mesh in enumerate(kind_pools.badges.show(len(bonuses))):
        bonus = bonuses[i]
        if not bonus:
            continue
        mesh.position.set(bonus.x, bonus.y, depth)
        mesh.scaling.setAll(size)
        swing = LOOK.swing
        mesh.rotation.y = swing.amplitude * math.sin(2 * math.pi * swing.hz * bonus.age)
    for i, mesh in enumerate(kind_pools.halos.show(len(bonuses))):
        bonus = bonuses[i]
        if not bonus:
            continue
        pulse = 1 + halo.pulse * math.sin(2 * math.pi * halo.pulseHz * bonus.age)
        mesh.position.set(bonus.x, bonus.y, depth + 0.5)
        mesh.scaling.set(size * halo.size * pulse, size * halo.size * pulse, 1)


def create_bonus_renderer(scene: Any) -> BonusRenderer:
    """The bonuses and their pickup flashes, drawn in `scene` (phase 6 review, P11-R07)."""
    flash = LOOK.flash
    by_kind = kind_templates(scene)
    flash_template = additive_template("bonus-flash", ring(flash.segments, flash.color), scene)
    pools = [KindPools(pool(by_kind[kind][0]), pool(by_kind[kind][1])) for kind in KINDS]
    rings = pool(flash_template)
    flashes: list[Flash] = []

    def sync(frame: Any) -> None:
        for i, kind in enumerate(KINDS):
            kind_pools = pools[i]
            if kind_pools:
                sync_kind(kind_pools, [b for b in frame.bonuses if b.kind == kind])
        sync_flashes(rings, flashes, frame.picked, frame.dtSeconds)

    def dispose() -> None:
        for p in pools:
            p.badges.dispose()
            p.halos.dispose()
        rings.dispose()
        for kind in KINDS:
            for t in by_kind[kind]:
                t.dispose()
        flash_template.dispose()

    renderer: BonusRenderer = _bonus_renderer(sync, dispose)
    return renderer
