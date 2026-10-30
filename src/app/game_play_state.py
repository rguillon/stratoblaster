"""A snapshot of a running level, for the test API

The snapshots are plain JavaScript objects with camelCase key names (`levelId`,
`bonusKinds`...): the test scripts read them from JavaScript (`debug/test_api.py`).
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import js_object, js_set

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def game_play_sky(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    weather: str,
    second_weather: str,
    weather_particles: int,
    rain_rings: float,
    lightning: float,
    flash: float,
    aurora: float,
    ground_lights: float,
    sun_intensity: float,
    fog_end: float,
    lava: bool,
    liquid_depth: float,
    plumes: int,
    shot_style: str,
) -> Any:
    """A `GamePlaySky` object (P08-R04, R05, P10-R05): how the level looks where the view is."""
    sky = js_object()
    js_set(sky, "weather", weather)
    js_set(sky, "secondWeather", second_weather)
    js_set(sky, "weatherParticles", weather_particles)
    js_set(sky, "rainRings", rain_rings)
    js_set(sky, "lightning", lightning)
    js_set(sky, "flash", flash)
    js_set(sky, "aurora", aurora)
    js_set(sky, "groundLights", ground_lights)
    js_set(sky, "sunIntensity", sun_intensity)
    js_set(sky, "fogEnd", fog_end)
    js_set(sky, "lava", lava)
    js_set(sky, "liquidDepth", liquid_depth)
    js_set(sky, "plumes", plumes)
    js_set(sky, "shotStyle", shot_style)
    return sky


def _boss_state(run: Any) -> Any:
    """The boss being fought, or null (P07)."""
    fights = run.fights
    boss = fights.boss
    rank = fights.rank
    if not boss or not rank:
        return None
    result = js_object()
    js_set(result, "name", boss.name)
    js_set(result, "rank", rank)
    js_set(result, "state", boss.state)
    js_set(result, "stage", boss.stage)
    js_set(result, "partsLeft", len([p for p in boss.parts if not p.destroyed]))
    js_set(result, "parts", len(boss.parts))
    js_set(result, "health", boss.remaining_health)
    js_set(result, "fullHealth", boss.full_health)
    return result


def level_state(run: Any, time_scale: float, max_health: float) -> Any:
    """The state of `run` for the test API; `max_health` stands for the health without a hull."""
    track = run.track
    enemies = run.enemies
    shots = run.shots
    ship = run.ship
    waves = run.waves
    hull = run.hull
    bombs = run.bombs
    bonuses = run.bonuses
    state = js_object()
    js_set(state, "levelId", run.result.level_id)
    js_set(state, "phase", run.phase)
    js_set(state, "time", track.time)
    js_set(state, "duration", track.duration)
    js_set(state, "timeScale", time_scale)
    js_set(state, "enemies", len(enemies.enemies))
    js_set(state, "destroyed", enemies.kills)
    js_set(state, "spawned", enemies.spawned)
    js_set(state, "wavesTriggered", waves.triggered)
    js_set(state, "player", _point(ship.x, ship.y))
    js_set(state, "firing", shots.firing)
    js_set(state, "shots", shots.active_count)
    js_set(state, "weaponLevel", shots.level)
    # Bonuses falling (P11-R07): their number, the dropped ones and their kinds.
    js_set(state, "bonuses", len(bonuses.bonuses) if bonuses is not None else 0)
    js_set(state, "bonusesDropped", bonuses.dropped if bonuses is not None else 0)
    js_set(state, "bonusKinds", [b.kind for b in bonuses.bonuses] if bonuses is not None else [])
    js_set(state, "score", run.score)
    js_set(state, "bombs", bombs.count if bombs is not None else 0)
    js_set(state, "enemyShots", enemies.shots.count)
    js_set(state, "health", hull.health if hull is not None else max_health)
    js_set(state, "lives", hull.lives if hull is not None else 0)
    js_set(state, "invincible", hull.invincible if hull is not None else 0)
    js_set(state, "boss", _boss_state(run))
    js_set(state, "bossesDefeated", len(run.fights.defeated))
    js_set(state, "groundSpeed", track.speed_factor)
    js_set(state, "checkpoint", run.checkpoint is not None)
    return state


def _point(x: float, y: float) -> Any:
    point = js_object()
    js_set(point, "x", x)
    js_set(point, "y", y)
    return point
