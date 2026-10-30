"""The enemies' lasers (GD-43): a blinking warning line, then a beam with a flare at its base, in
the colour of their style (phase 8 review)"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402
from typing import Any  # noqa: E402

type Rgb = list[float]
__pragma__("noskip")

from core.math.color import fold_into_family  # noqa: E402
from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.enemy_look import (  # noqa: E402
    ENEMY_LOOK,
    laser_palette,
)
from game.config.readability import READABILITY  # noqa: E402
from game.view.reactor_flame import flicker  # noqa: E402
from game.view.shot_geometry import (  # noqa: E402
    build_glow_bar,
    build_glow_disc,
)
from game.view.shots.shot_meshes import additive_template  # noqa: E402, E501
from render.babylon import node_name  # noqa: E402
from render.node_adopter import ON_TOP_ALPHA_INDEX  # noqa: E402
from render.node_pool import NodePool  # noqa: E402

LOOK = ENEMY_LOOK.laser


class LaserPools:
    """The warning lines, beams and base flares of the lasers of one colour."""

    def __init__(self, warning: Any, beam: Any, emitter: Any, templates: list[Any]) -> None:
        self.warning = warning
        self.beam = beam
        self.emitter = emitter
        self.templates = templates


def color_of(style: str) -> Sequence[float]:
    """The colour of the lasers of `style`: a boss's neon, or the Lancer's (phase 8 review), moved
    into the enemy shots' colour family (P14-R02)."""
    neon = BOSS_LOOK.neon[style]
    color = neon if neon != None else LOOK.color  # noqa: E711
    return fold_into_family(color, READABILITY.families.enemyShot)


def contrast_warning(color: Sequence[float]) -> list[Rgb]:
    """A warning line with a white core, standing out over red grounds (P10-R07)."""
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
    __pragma__("js", "{}", "return Object.assign({}, base, {warning: warning});")
    return None


def pool_of(template: Any) -> Any:
    """A pool of clones of `template`, named after it and their index (factory: no loop
    closure)."""
    return NodePool(lambda i: template.clone(node_name(template) + "-" + str(i)))


def lasers_of(scene: Any, style: str, contrast: bool) -> LaserPools:
    """The pools of the lasers of one style (their templates, clones and warning colour)."""
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
    # P14-R05: over the player's shots and the blasts, under the bullets (their clones too).
    for template in templates:
        template.alphaIndex = ON_TOP_ALPHA_INDEX
    return LaserPools(
        pool_of(templates[0]),
        pool_of(templates[1]),
        pool_of(templates[2]),
        templates,
    )


def sync_warnings(pool: Any, warnings: list[Any], time: float, width: float) -> None:
    """The warning lines, blinking: drawn at full or half width."""
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
    """The beams, and a pulsing flare where each leaves, as the player's laser's: bigger for wider
    beams, stretched along the beam."""
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
    """The enemies' lasers (GD-43): a blinking warning line, then a beam with a flare at its base,
    in the colour of their style (phase 8 review: each boss's lasers in its neon colour)."""

    def __init__(self, scene: Any, contrast: bool = False) -> None:
        self.scene = scene
        # `contrast`: warning lines with a white core, wider (P10-R07).
        self.contrast = contrast
        # The styles drawn so far, in order, and the pools of each.
        self.style_names: list[str] = []
        self.pools: dict[str, LaserPools] = {}

    def sync(self, lasers: list[Any], time: float) -> None:
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
        for style in self.style_names:
            pools = self.pools[style]
            for pool in [pools.warning, pools.beam, pools.emitter]:
                pool.dispose()
            for template in pools.templates:
                template.dispose()
        self.style_names = []
        self.pools = {}
