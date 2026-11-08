# Copyright (c) 2026 Renaud Guillon
"""The laser shots (GFX-SHOT-03, GFX-SHOT-04): a bright blue beam per segment.

Each beam is thinner at each lower level, with a glow at its base and where it touches a target, and
particles flowing up along it.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng
from game.config.shot_look import SHOT_LOOK
from game.view.reactor_flame import flicker
from game.view.shot_geometry import bar_alphas, build_glow_bar, build_glow_disc, build_glow_ramp
from game.view.shots.laser_particles import LaserParticles
from game.view.shots.shot_meshes import additive_template, blended_template
from render.node_pool import NodePool

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.systems.beam import BeamSegment
from render.game_view import ShotRenderer
from render.geometry.gradient_shapes import ColoredGeometry

# __pragma__ ("noskip")


LOOK = SHOT_LOOK.laser
# Length used to spread the particles along the beam before it first fires.
INITIAL_LENGTH = 600
DISC_SEGMENTS = 10
# The blended core sits just behind the additive glow, so the glow is drawn over it.
CORE_DEPTH = 0.05


def _shot_renderer(sync: Any, dispose: Any) -> Any:
    """Return a `ShotRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def core_pool(scene: Any, name: str, ramp: bool) -> tuple[Any, NodePool]:
    """Return a disabled blended template of the beam's core (a bar, or its `ramp`) and a pool."""
    # Its colours stay; a ramp fades in by its alpha alone (black would darken it on the way).
    geo = build_glow_bar(LOOK.core.colors)
    template = blended_template(name, geo, bar_alphas(LOOK.core.alphas, ramp), scene)
    pool = NodePool(lambda i: template.clone(name + "-" + str(i)))
    return template, pool


def glow_pool(scene: Any, name: str, geo: ColoredGeometry) -> tuple[Any, NodePool]:
    """Return a disabled additive template and a pool of its clones."""
    template = additive_template(name, geo, scene)
    pool = NodePool(lambda i: template.clone(name + "-" + str(i)))
    return template, pool


def drawn_width(width: float) -> float:
    """Return the width a beam of hit width `width` is drawn with (GFX-SHOT-03).

    `widthBonus` wider than its hit width.
    """
    bonus: float = LOOK.widthBonus
    return width + bonus


def bar_spans(beam: list[BeamSegment]) -> list[list[float]]:
    """Return `[x, y0, y1, width, ramp]` of each bar of `beam` (GFX-SHOT-03).

    One bar per segment, from y0 to y1. The first segment, leaving the ship, starts with a ramp
    `fadeIn` long (`ramp` 1) so the beam fades in rather than starting square; its bar goes on from
    the ramp's top.
    """
    spans: list[list[float]] = []
    for i, s in enumerate(beam):
        if not s:
            continue
        width = drawn_width(s.width)
        start = s.y0
        if i == 0:
            top = min(s.y1, s.y0 + LOOK.fadeIn)
            spans.append([s.x, s.y0, top, width, 1])
            start = top
        if s.y1 > start:
            spans.append([s.x, start, s.y1, width, 0])
    return spans


def place_bars(
    bars: NodePool, ramps: NodePool, beam: list[BeamSegment], scale: float, depth: float
) -> None:
    """Draw the bars and the ramp of `beam`, `scale` times their drawn width, at `depth`."""
    spans = bar_spans(beam)
    plain = [span for span in spans if span[4] == 0]
    sloped = [span for span in spans if span[4] == 1]
    for pool, chosen in [(bars, plain), (ramps, sloped)]:
        for i, mesh in enumerate(pool.show(len(chosen))):
            span = chosen[i]
            mesh.position.set(span[0], span[1], depth)
            mesh.scaling.set(span[3] * scale, max(0, span[2] - span[1]), 1)


def place_contacts(contacts: NodePool, beam: list[BeamSegment], wobble: float) -> None:
    """Place a glow at the end of each segment that stops on a target (GFX-FX-01)."""
    hits = [s for s in beam if s.hit]
    for i, mesh in enumerate(contacts.show(len(hits))):
        s = hits[i]
        r = LOOK.contact.radius * wobble * (0.5 + drawn_width(s.width) / 16)
        mesh.position.set(s.x, s.y1, -0.5)
        mesh.scaling.set(r, r, 1)


def place_muzzle(muzzle: NodePool, beam: list[BeamSegment], time: float) -> None:
    """Place a pulsing glow where the beam leaves the ship.

    It is bigger for wider (higher level) beams.
    """
    first = beam[0] if len(beam) > 0 else None
    shown = muzzle.show(1 if first else 0)
    mesh = shown[0] if len(shown) > 0 else None
    if not first or not mesh:
        return
    look = LOOK.muzzle
    pulse = 1 + look.pulse * flicker(time, 1, look.pulseHz)
    r = look.radius * (look.baseScale + drawn_width(first.width) / look.widthDivisor) * pulse
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
    """Return the laser shots (GFX-SHOT-03), drawn in `scene`."""
    bars_template, bars = glow_pool(scene, "laser", build_glow_bar(LOOK.colors))
    ramps_template, ramps = glow_pool(scene, "laser-ramp", build_glow_ramp(LOOK.colors))
    cores_template, cores = core_pool(scene, "laser-core", False)
    core_ramps_template, core_ramps = core_pool(scene, "laser-core-ramp", True)
    contacts_template, contacts = glow_pool(
        scene, "laser-contact", build_glow_disc(DISC_SEGMENTS, LOOK.contact.colors)
    )
    sparks_template, sparks = glow_pool(
        scene, "laser-particle", build_glow_disc(DISC_SEGMENTS, LOOK.particles.colors)
    )
    muzzle_template, muzzle = glow_pool(
        scene, "laser-muzzle", build_glow_disc(LOOK.muzzle.segments, LOOK.muzzle.colors)
    )
    particles = LaserParticles(
        LOOK.particles, create_rng(LOOK.particles.seed), INITIAL_LENGTH, LOOK.widthBonus
    )
    # The beam's clock, in a list so the closure below can advance it.
    clock = [0.0]

    def sync(frame: Any) -> None:
        clock[0] += frame.dt_seconds
        time = clock[0]
        wobble = 1 + LOOK.flicker * flicker(time, 0, [LOOK.flickerHz])
        place_bars(cores, core_ramps, frame.beam, wobble, CORE_DEPTH)
        place_bars(bars, ramps, frame.beam, LOOK.glowWidth * wobble, 0)
        place_contacts(contacts, frame.beam, wobble)
        place_muzzle(muzzle, frame.beam, time)
        place_sparks(sparks, particles.step(frame.beam, frame.dt_seconds))

    def dispose() -> None:
        for pool, template in [
            (bars, bars_template),
            (ramps, ramps_template),
            (cores, cores_template),
            (core_ramps, core_ramps_template),
            (contacts, contacts_template),
            (muzzle, muzzle_template),
            (sparks, sparks_template),
        ]:
            pool.dispose()
            template.dispose()

    renderer: ShotRenderer = _shot_renderer(sync, dispose)
    return renderer
