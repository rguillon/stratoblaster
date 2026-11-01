# Copyright (c) 2026 Renaud Guillon
"""The enemies' lasers: a blinking warning line, then a beam with a flare at its base.

A warning line blinks (GFX-SHOT-16), then the beam is drawn (GFX-SHOT-17), in the colour of their
style (phase 8 review).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.color import fold_into_family
from game.config.boss_look import BOSS_LOOK
from game.config.enemy_look import (
    ENEMY_LOOK,
    laser_palette,
)
from game.config.readability import READABILITY
from game.view.reactor_flame import flicker
from game.view.shot_geometry import (
    build_glow_bar,
    build_glow_disc,
)
from game.view.shots.shot_meshes import additive_template
from render.babylon import node_name
from render.node_adopter import ON_TOP_ALPHA_INDEX
from render.node_pool import NodePool

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Sequence
from typing import Any

from game.config.record import fields_of, record

type Rgb = list[float]
# __pragma__ ("noskip")


LOOK = ENEMY_LOOK.laser


class LaserPools:
    """The warning lines, beams and base flares of the lasers of one colour."""

    def __init__(self, warning: Any, beam: Any, emitter: Any, templates: list[Any]) -> None:
        self.warning = warning
        self.beam = beam
        self.emitter = emitter
        self.templates = templates


def color_of(style: str) -> Sequence[float]:
    """Return the colour of the lasers of `style` (GFX-SHOT-18).

    A boss's neon (BOSS-32), or the Lancer's (phase 8 review), moved into the enemy shots' colour
    family (GFX-READ-06).
    """
    neon = BOSS_LOOK.neon[style]
    color = neon if neon != None else LOOK.color
    return fold_into_family(color, READABILITY.families.enemyShot)


def contrast_warning(color: Sequence[float]) -> list[Rgb]:
    """Return a warning line with a white core, standing out over red grounds (GFX-READ-11)."""
    r = color[0]
    g = color[1]
    b = color[2]
    t = ENEMY_LOOK.contrast.warningCore
    return [
        [r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t],
        [r, g, b],
        [r * 0.5, g * 0.5, b * 0.5],
        [0, 0, 0],
    ]


def with_warning(base: Any, warning: list[Rgb]) -> Any:
    """`{ ...base, warning }`: the palette with another warning colour."""
    __pragma__("skip")
    return record({**fields_of(base), "warning": warning})
    __pragma__("noskip")
    __pragma__("js", "{}", "return Object.assign({}, base, {warning: warning});")
    return None


def pool_of(template: Any) -> Any:
    """Return a pool of clones of `template`, named after it and their index.

    It is a factory: no loop closure.
    """
    return NodePool(lambda i: template.clone(node_name(template) + "-" + str(i)))


def lasers_of(scene: Any, style: str, contrast: bool) -> LaserPools:
    """Return the pools of the lasers of one style (their templates, clones and warning colour)."""
    base = laser_palette(color_of(style))
    palette = with_warning(base, contrast_warning(color_of(style))) if contrast else base

    def name(part: str) -> str:
        return "enemy-laser-" + part + "-" + style

    # Drawn over the models: a beam leaves its emitter's lens, not from under the hull around it.
    templates = [
        additive_template(name("warning"), build_glow_bar(palette.warning), scene, True),
        additive_template(name("beam"), build_glow_bar(palette.beam), scene, True),
        additive_template(
            name("emitter"),
            build_glow_disc(LOOK.flare.segments, palette.emitter),
            scene,
            True,
        ),
    ]
    # GFX-READ-13: over the player's shots and the blasts, under the bullets (their clones too).
    for template in templates:
        template.alphaIndex = ON_TOP_ALPHA_INDEX
    return LaserPools(
        pool_of(templates[0]),
        pool_of(templates[1]),
        pool_of(templates[2]),
        templates,
    )


def sync_warnings(pool: Any, warnings: list[Any], time: float, width: float) -> None:
    """Add the warning lines, blinking: drawn at full or half width.

    A thin blinking line, not taken for a bullet (GFX-READ-12).
    """
    blink = 1 if math.sin(2 * math.pi * LOOK.warning.blinkHz * time) > 0 else 0.5
    shown = pool.show(len(warnings))
    for i, mesh in enumerate(shown):
        if i >= len(warnings):
            continue
        line = warnings[i]
        mesh.position.set(line.x, line.y, -0.8)
        mesh.rotation.z = -line.heading
        mesh.scaling.set(width * blink, line.length, 1)


def sync_beams(pools: LaserPools, beams: list[Any], time: float) -> None:
    """Add the beams, each with a pulsing flare where it leaves, as the player's laser's.

    Bigger for wider beams, and stretched along the beam.
    """
    wobble = 1 + LOOK.beam.flicker * flicker(time, 0, [LOOK.beam.flickerHz])
    shown = pools.beam.show(len(beams))
    for i, mesh in enumerate(shown):
        if i >= len(beams):
            continue
        line = beams[i]
        mesh.position.set(line.x, line.y, -0.9)
        mesh.rotation.z = -line.heading
        mesh.scaling.set(line.spec.width * LOOK.beam.glowWidth * wobble, line.length, 1)
    flare = LOOK.flare
    pulse = 1 + flare.pulse * flicker(time, 1, flare.pulseHz)
    shown = pools.emitter.show(len(beams))
    for i, mesh in enumerate(shown):
        if i >= len(beams):
            continue
        line = beams[i]
        r = flare.radius * (flare.baseScale + line.spec.width / flare.widthDivisor) * pulse
        mesh.position.set(line.x, line.y, -1.2)
        mesh.rotation.z = -line.heading
        mesh.scaling.set(r, r * flare.stretch, 1)


class EnemyLasers:
    """The enemies' lasers (GFX-SHOT-16, GFX-SHOT-17): a blinking warning line, then a beam.

    The beam has a flare at its base, in the colour of their style (phase 8 review: each boss's
    lasers in its neon colour).
    """

    def __init__(self, scene: Any, contrast: bool = False) -> None:
        self.scene = scene
        # `contrast`: warning lines with a white core, wider (GFX-READ-11).
        self.contrast = contrast
        # The styles drawn so far, in order, and the pools of each.
        self.style_names: list[str] = []
        self.pools: dict[str, LaserPools] = {}

    def sync(self, lasers: list[Any], time: float) -> None:
        """Draws the lasers of this frame, one warning or beam per laser."""
        for laser in lasers:
            style = laser.spec.style
            if style not in self.style_names:
                self.style_names.append(style)
                self.pools[style] = lasers_of(self.scene, style, self.contrast)
        scale = ENEMY_LOOK.contrast.warningWidth if self.contrast else 1
        for style in self.style_names:
            pools = self.pools[style]
            own = [laser for laser in lasers if laser.spec.style == style]
            sync_warnings(
                pools.warning,
                [laser for laser in own if laser.phase == "warning"],
                time,
                LOOK.warning.width * scale,
            )
            sync_beams(
                pools,
                [laser for laser in own if laser.phase == "firing"],
                time,
            )

    def dispose(self) -> None:
        """Disposes the pooled meshes of every style."""
        for style in self.style_names:
            pools = self.pools[style]
            for pool in [pools.warning, pools.beam, pools.emitter]:
                pool.dispose()
            for template in pools.templates:
                template.dispose()
        self.style_names = []
        self.pools = {}
