"""The laser shots (P03-R02): a bright blue beam per segment, thinner at each lower level, a glow
at its base and where it touches a target, and particles flowing up along it.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from core.systems.beam import BeamSegment  # noqa: E402
from render.game_view import ShotRenderer  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402

__pragma__("noskip")

from core.math.rng import create_rng  # noqa: E402
from game.config.shot_look import SHOT_LOOK  # noqa: E402
from game.view.reactor_flame import flicker  # noqa: E402
from game.view.shot_geometry import build_glow_bar, build_glow_disc  # noqa: E402
from game.view.shots.laser_particles import LaserParticles  # noqa: E402
from game.view.shots.shot_meshes import additive_template  # noqa: E402
from render.node_pool import NodePool  # noqa: E402

LOOK = SHOT_LOOK.laser
# Length used to spread the particles along the beam before it first fires.
INITIAL_LENGTH = 600
DISC_SEGMENTS = 10


def _shot_renderer(sync: Any, dispose: Any) -> Any:
    """A `ShotRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def glow_pool(scene: Any, name: str, geo: ColoredGeometry) -> tuple[Any, NodePool]:
    """A disabled additive template and a pool of its clones."""
    template = additive_template(name, geo, scene)
    pool = NodePool(lambda i: template.clone(name + "-" + str(i)))
    return template, pool


def place_bars(bars: NodePool, beam: list[BeamSegment], wobble: float) -> None:
    """One bar per segment, as wide as the segment's level (times the glow), from y0 to y1."""
    for i, mesh in enumerate(bars.show(len(beam))):
        s = beam[i]
        if not s:
            continue
        mesh.position.set(s.x, s.y0, 0)
        mesh.scaling.set(s.width * LOOK.glowWidth * wobble, max(0, s.y1 - s.y0), 1)


def place_contacts(contacts: NodePool, beam: list[BeamSegment], wobble: float) -> None:
    """A glow at the end of each segment that stops on a target."""
    hits = [s for s in beam if s.hit]
    for i, mesh in enumerate(contacts.show(len(hits))):
        s = hits[i]
        if not s:
            continue
        r = LOOK.contact.radius * wobble * (0.5 + s.width / 16)
        mesh.position.set(s.x, s.y1, -0.5)
        mesh.scaling.set(r, r, 1)


def place_muzzle(muzzle: NodePool, beam: list[BeamSegment], time: float) -> None:
    """A pulsing glow where the beam leaves the ship, bigger for wider (higher level) beams."""
    first = beam[0] if len(beam) > 0 else None
    shown = muzzle.show(1 if first else 0)
    mesh = shown[0] if len(shown) > 0 else None
    if not first or not mesh:
        return
    look = LOOK.muzzle
    pulse = 1 + look.pulse * flicker(time, 1, look.pulseHz)
    r = look.radius * (look.baseScale + first.width / look.widthDivisor) * pulse
    mesh.position.set(first.x, first.y0, -0.6)
    mesh.scaling.set(r, r * look.stretch, 1)


def place_sparks(sparks: NodePool, spots: list[Any]) -> None:
    """Draws the particles as small glowing discs."""
    for i, mesh in enumerate(sparks.show(len(spots))):
        p = spots[i]
        if not p:
            continue
        mesh.position.set(p.x, p.y, -0.2)
        mesh.scaling.set(p.radius, p.radius * 2, 1)


def create_laser_renderer(scene: Any) -> ShotRenderer:
    """The laser shots (P03-R02), drawn in `scene`."""
    bars_template, bars = glow_pool(scene, "laser", build_glow_bar(LOOK.colors))
    contacts_template, contacts = glow_pool(
        scene, "laser-contact", build_glow_disc(DISC_SEGMENTS, LOOK.contact.colors)
    )
    sparks_template, sparks = glow_pool(
        scene, "laser-particle", build_glow_disc(DISC_SEGMENTS, LOOK.particles.colors)
    )
    muzzle_template, muzzle = glow_pool(
        scene, "laser-muzzle", build_glow_disc(LOOK.muzzle.segments, LOOK.muzzle.colors)
    )
    particles = LaserParticles(LOOK.particles, create_rng(LOOK.particles.seed), INITIAL_LENGTH)
    # The beam's clock, in a list so the closure below can advance it.
    clock = [0.0]

    def sync(frame: Any) -> None:
        clock[0] += frame.dt_seconds
        time = clock[0]
        wobble = 1 + LOOK.flicker * flicker(time, 0, [LOOK.flickerHz])
        place_bars(bars, frame.beam, wobble)
        place_contacts(contacts, frame.beam, wobble)
        place_muzzle(muzzle, frame.beam, time)
        place_sparks(sparks, particles.step(frame.beam, frame.dt_seconds))

    def dispose() -> None:
        for pool, template in [
            (bars, bars_template),
            (contacts, contacts_template),
            (muzzle, muzzle_template),
            (sparks, sparks_template),
        ]:
            pool.dispose()
            template.dispose()

    renderer: ShotRenderer = _shot_renderer(sync, dispose)
    return renderer
