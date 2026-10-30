"""A bomb going off (P11-R05): in playfield space, a
shockwave ring growing from where the ship was over the whole playfield, and a flash there that
fades in a fraction of a second.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from render.game_view import BombRenderer  # noqa: E402

__pragma__("noskip")

from game.config.bomb_look import BOMB_LOOK  # noqa: E402
from game.view.shot_geometry import build_glow_disc  # noqa: E402
from game.view.shots.shot_meshes import additive_template  # noqa: E402

LOOK = BOMB_LOOK


def _bomb_renderer(sync: Any, dispose: Any) -> Any:
    """A `BombRenderer` as a plain object (the renderer calls `sync` and `dispose`)."""
    __pragma__("js", "{}", "return {sync: sync, dispose: dispose};")
    return None


def wave_reach(t: float) -> float:
    """How far out the shockwave is, 0..1, `t` (0..1) into the bomb: fast, then slowing."""
    clamped = min(1, max(0, t))
    value: float = 1 - (1 - clamped) ** 2
    return value


def flash_strength(age: float) -> float:
    """How bright the flash is, `age` seconds into the bomb: full at once, gone after its time."""
    value: float = max(0, 1 - age / LOOK.flash.seconds)
    return value


def create_bomb_renderer(scene: Any) -> BombRenderer:
    """The bomb's shockwave and flash, drawn in `scene`."""
    wave = LOOK.wave
    flash = LOOK.flash
    depth = LOOK.depth
    ring = additive_template("bomb-wave", build_glow_disc(wave.segments, wave.colors), scene)
    glow = additive_template("bomb-flash", build_glow_disc(flash.segments, flash.colors), scene)

    def show(bomb: Any) -> None:
        # `!= None` also covers an undefined bomb (no bomb this frame).
        ring.setEnabled(bomb != None)  # noqa: E711
        glow.setEnabled(bomb != None and flash_strength(bomb.age) > 0)  # noqa: E711
        if not bomb:
            return
        t = bomb.age / bomb.seconds
        radius = max(1, wave.radius * wave_reach(t))
        ring.position.set(bomb.x, bomb.y, depth)
        ring.scaling.set(radius, radius, 1)
        ring.visibility = 1 - t * t
        glow.position.set(bomb.x, bomb.y, depth + 0.5)
        glow.scaling.set(flash.radius, flash.radius, 1)
        glow.visibility = flash_strength(bomb.age)

    def sync(frame: Any) -> None:
        show(frame.bomb)

    def dispose() -> None:
        ring.dispose()
        glow.dispose()

    renderer: BombRenderer = _bomb_renderer(sync, dispose)
    return renderer
