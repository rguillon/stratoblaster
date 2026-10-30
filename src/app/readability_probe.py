"""Measures how readable a level's frame is (P14-R08)

The frame is drawn once as it is and once without the playfield (the background alone), and the
two are compared around each object. The report is a plain JavaScript object with camelCase
key names, for the test API.
"""

from org.transcrypt.stubs.browser import __pragma__, window

from config.game_play import GAME_PLAY_CONFIG
from core.math.pixel_contrast import PixelBox, Pixels, box_contrast, brightest_but
from render.babylon import babylon_class, js_object, js_set, set_enabled, vector3

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

CFG = GAME_PLAY_CONFIG.readability_probe


class Spot:
    """A playfield circle: centre and radius, in logical pixels."""

    def __init__(self, x: float, y: float, radius: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius


class _Spots:
    """Where each kind of object is on the playfield, if any is in view."""

    def __init__(self, player: Spot, enemy: Any, enemy_bullet: Any, player_shot: Any) -> None:
        self.player = player
        self.enemy = enemy
        self.enemy_bullet = enemy_bullet
        self.player_shot = player_shot


def _first_in_view(items: Any, in_view: Any, radius: Any) -> Any:
    """The first of `items` wholly in view (a margin round it), as a spot of its `radius`."""
    for item in items:
        m = radius(item) + CFG.margin
        if in_view(item.x - m, item.y - m) and in_view(item.x + m, item.y + m):
            return Spot(item.x, item.y, radius(item))
    return None


def _spots_of(run: Any, in_view: Any) -> _Spots:
    """Where each kind of object is on the playfield, if any is in view: player shots away from
    the ship (not over it, nor leaving its guns).
    """
    ship = run.ship
    enemies = run.enemies
    shots = run.shots
    ahead = [p for p in shots.projectiles if p.alive and p.y > ship.y + CFG.shot_ahead]
    bullets = [b for b in enemies.shots.bullets if b.alive]
    return _Spots(
        Spot(ship.x, ship.y, CFG.ship_radius),
        _first_in_view(enemies.enemies, in_view, lambda e: e.radius),
        _first_in_view(bullets, in_view, lambda b: b.radius),
        _first_in_view(ahead, in_view, lambda _p: CFG.shot_radius),
    )


async def _read_frame(scene: Any) -> Any:
    """Reads the canvas back, row 0 at the bottom (as WebGL reads it)."""
    engine = scene.getEngine()
    width = engine.getRenderWidth()
    height = engine.getRenderHeight()
    scene.render()
    data = await engine.readPixels(0, 0, width, height)
    return Pixels(width, height, data)


def _pixel_box(scene: Any, root: Any, spot: Spot) -> PixelBox:
    """The box of pixels (WebGL rows, bottom up) that `spot` covers on screen."""
    engine = scene.getEngine()
    camera = scene.activeCamera
    if camera is None:
        raise ValueError("The level has no camera")
    width = engine.getRenderWidth()
    height = engine.getRenderHeight()
    world = root.getWorldMatrix()
    viewport = camera.viewport.toGlobal(width, height)
    vector = babylon_class("Vector3")
    identity = babylon_class("Matrix").IdentityReadOnly

    def project(x: float, y: float) -> Any:
        point = vector.TransformCoordinates(vector3(x, y, 0), world)
        return vector.Project(point, identity, scene.getTransformMatrix(), viewport)

    centre = project(spot.x, spot.y)
    edge = project(spot.x + spot.radius, spot.y)
    radius = max(1, window.Math.hypot(edge.x - centre.x, edge.y - centre.y))
    return PixelBox(centre.x, height - 1 - centre.y, radius)


async def probe_readability(
    scene: Any,
    playfield: Any,
    run: Any,
    in_view: Any,
    bright_share: float,
) -> Any:
    """Measures how readable the level's current frame is (P14-R08): draws it once as it is and
    once without the playfield (the background alone), and compares the two around each object.
    """
    spots = _spots_of(run, in_view)
    frame = await _read_frame(scene)
    set_enabled(playfield, False)
    try:
        background = await _read_frame(scene)
    finally:
        set_enabled(playfield, True)
    scene.render()

    def contrast(spot: Any) -> Any:
        if spot is None:
            return None
        return box_contrast(frame, background, _pixel_box(scene, playfield, spot))

    report = js_object()
    js_set(report, "player", contrast(spots.player))
    js_set(report, "enemy", contrast(spots.enemy))
    js_set(report, "enemyBullet", contrast(spots.enemy_bullet))
    js_set(report, "playerShot", contrast(spots.player_shot))
    js_set(report, "backgroundLuminance", brightest_but(background, bright_share))
    return report
