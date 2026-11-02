# Copyright (c) 2026 Renaud Guillon
"""Missiles (GFX-SHOT-06): turned along their heading, with flames and impact explosions.

Explosions on impact are GFX-FX-03.

Missiles are drawn behind the ship, which covers them as they leave its centre (GFX-SHOT-08). Each
has a bright motor flare and a glowing exhaust trail, so it shows on any ground (GFX-SHOT-07).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.shot_look import SHOT_LOOK
from game.view.shots.impact_flashes import ImpactFlashes, flash_look
from game.view.shots.missile_exhaust import create_missile_exhaust
from game.view.shots.missile_model import build_missile
from render.model_animation import step_model_animations
from render.node_pool import NodePool

# isort: split
# __pragma__ ("skip")
from typing import Any

from render.game_view import ShotRenderer

# __pragma__ ("noskip")


def _shot_renderer(sync: Any, dispose: Any) -> Any:
    """Return a `ShotRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def create_missile_renderer(scene: Any) -> ShotRenderer:
    """Return the missiles and their explosions, drawn in `scene`."""
    pool = NodePool(lambda i: build_missile("missile-" + str(i), scene))
    exhaust = create_missile_exhaust(scene)
    depth = SHOT_LOOK.missile.depth
    look = SHOT_LOOK.impact.missile
    explosions = ImpactFlashes(
        scene,
        "missile-blast",
        flash_look(look.colors, SHOT_LOOK.impact.segments),
        look.duration,
        lambda impact: impact.blastRadius * look.radiusFactor,
    )

    def sync(frame: Any) -> None:
        shots = frame.projectiles
        for i, node in enumerate(pool.show(len(shots))):
            shot = shots[i]
            if not shot:
                continue
            node.position.set(shot.x, shot.y, depth)
            node.rotation.z = -shot.heading
            step_model_animations(node, frame.dt_seconds)
        exhaust.sync(shots)
        explosions.sync(frame.impacts, frame.dt_seconds)

    def dispose() -> None:
        pool.dispose()
        exhaust.dispose()
        explosions.dispose()

    renderer: ShotRenderer = _shot_renderer(sync, dispose)
    return renderer
