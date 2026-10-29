"""Minigun tracers (P03-R01, phase 5 review): white-hot streaks cooling to red along their tail,
flickering, and a burst of sparkling metal sparks where they hit. Ported from
`shots/bullet-renderer.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from render.game_view import ShotRenderer  # noqa: E402

__pragma__("noskip")

import math  # noqa: E402

from core.math.rng import create_rng  # noqa: E402
from game.config.shot_look import SHOT_LOOK  # noqa: E402
from game.view.shot_geometry import build_glow_disc, build_tracer  # noqa: E402
from game.view.shots.shot_meshes import additive_template  # noqa: E402
from game.view.shots.spark_bursts import SparkBursts  # noqa: E402
from render.node_pool import NodePool  # noqa: E402


def _shot_renderer(sync: Any, dispose: Any) -> Any:
    """A `ShotRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def create_bullet_renderer(scene: Any) -> ShotRenderer:
    """The minigun's tracers and sparks, drawn in `scene`."""
    look = SHOT_LOOK.bullet
    template = additive_template("bullet", build_tracer(look.colors, look.rows), scene)
    pool = NodePool(lambda i: template.clone("bullet-" + str(i)))
    spark_look = SHOT_LOOK.impact.bullet
    spark_template = additive_template(
        "bullet-spark", build_glow_disc(spark_look.segments, spark_look.colors), scene
    )
    spark_pool = NodePool(lambda i: spark_template.clone("bullet-spark-" + str(i)))
    sparks = SparkBursts(spark_look, create_rng(spark_look.seed))

    def sync(frame: Any) -> None:
        for i, mesh in enumerate(pool.show(len(frame.projectiles))):
            shot = frame.projectiles[i]
            if not shot:
                continue
            mesh.position.set(shot.x, shot.y, look.depth)
            mesh.rotation.z = -shot.heading
            # Grows out of the muzzle, then keeps its length; its width flickers.
            length = min(look.length, shot.age * shot.speed + look.width)
            flicker = 1 + look.flicker * math.sin(shot.age * look.flickerRate + shot.x)
            mesh.scaling.set(look.width * flicker, length, 1)
        for impact in frame.impacts:
            sparks.emit(impact.x, impact.y)
        spots = sparks.step(frame.dtSeconds)
        for i, mesh in enumerate(spark_pool.show(len(spots))):
            spark = spots[i]
            if not spark:
                continue
            # Additive: a dimmer, thinner streak reads as a fading spark.
            width = spark_look.width * spark.brightness
            mesh.position.set(spark.x, spark.y, -1)
            mesh.rotation.z = -spark.heading
            mesh.scaling.set(width, max(width, spark.length_ / 2), 1)

    def dispose() -> None:
        pool.dispose()
        spark_pool.dispose()
        template.dispose()
        spark_template.dispose()

    renderer: ShotRenderer = _shot_renderer(sync, dispose)
    return renderer
