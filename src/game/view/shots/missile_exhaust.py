"""The missile motor flares and exhaust trails (phase 5 review), ported from
`shots/missile-exhaust.ts`: a bright, flickering flare at each missile's nozzle and a glowing
exhaust trail behind it, added on, so the missiles show on any ground.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from core.systems.projectile_motion import Projectile  # noqa: E402

__pragma__("noskip")

from game.config.ship_look import PLAYER_SHIP_SCALE  # noqa: E402
from game.config.shot_look import SHOT_LOOK  # noqa: E402
from game.view.shot_geometry import build_glow_disc, build_tracer  # noqa: E402
from game.view.shots.shot_meshes import additive_template  # noqa: E402
from render.node_pool import NodePool  # noqa: E402

FLARE_LOOK = SHOT_LOOK.missile.flare
TRAIL_LOOK = SHOT_LOOK.missile.trail
DEPTH = SHOT_LOOK.missile.depth
# From the missile's centre back to its nozzle, px.
BACK = (SHOT_LOOK.missile.length / 2) * PLAYER_SHIP_SCALE


def _exhaust(sync: Any, dispose: Any) -> Any:
    """The exhaust as a plain object with `sync` and `dispose`."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def create_missile_exhaust(scene: Any) -> Any:
    """The flares and trails of the missiles in `scene`."""
    flare_template = additive_template(
        "missile-flare", build_glow_disc(FLARE_LOOK.segments, FLARE_LOOK.colors), scene
    )
    flares = NodePool(lambda i: flare_template.clone("missile-flare-" + str(i)))
    trail_template = additive_template(
        "missile-trail", build_tracer(TRAIL_LOOK.colors, TRAIL_LOOK.rows), scene
    )
    trails = NodePool(lambda i: trail_template.clone("missile-trail-" + str(i)))

    def sync(shots: list[Projectile]) -> None:
        glows = flares.show(len(shots))
        for i, mesh in enumerate(trails.show(len(shots))):
            shot = shots[i]
            glow = glows[i]
            if not shot or not glow:
                continue
            x = shot.x - math.sin(shot.heading) * BACK
            y = shot.y - math.cos(shot.heading) * BACK
            size = FLARE_LOOK.radius * (
                1 + FLARE_LOOK.flicker * math.sin(shot.age * FLARE_LOOK.flickerRate)
            )
            glow.position.set(x, y, DEPTH)
            glow.scaling.set(size, size, 1)
            mesh.position.set(x, y, DEPTH)
            mesh.rotation.z = -shot.heading
            # Grows from the launch point, like a tracer.
            mesh.scaling.set(TRAIL_LOOK.width, min(TRAIL_LOOK.length, shot.age * shot.speed), 1)

    def dispose() -> None:
        flares.dispose()
        trails.dispose()
        flare_template.dispose()
        trail_template.dispose()

    return _exhaust(sync, dispose)
