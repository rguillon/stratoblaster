# Copyright (c) 2026 Renaud Guillon
"""What is on the playfield of a level run, for a player outside the page (D-265).

`__GAME_TEST__.getScene()` (e2e builds only) gives it to the AI player of `make serve-ai`, which
reads it from Python, chooses its moves and presses the game's keys. Everything is a number, a
string, a boolean or a list of them (arrays in JavaScript), so Playwright copies it out as is:

- `ship`: x, y, vx, vy, top speed;
- `hull`: health, full health, lives, seconds of invincibility left (null without a hull);
- `bombs`: bombs left, whether one is going off (null without bombs);
- `weapon`, `weapons`: the weapon in use, and [id, level] of each weapon used so far;
- `track`: the level's progress and length;
- `boss`: whether a boss is fought, its rank, its health and full health;
- `targets`: [x, y, radius, health, full health, a boss's] of each enemy and boss piece;
- `bullets`, `missiles`: [x, y, heading, speed] of each enemy bullet and missile;
- `lasers`: [x, y, heading, length, firing] of each laser (its warning line until it fires);
- `bonuses`: [x, y, kind] of each falling bonus.
"""

from render.babylon import js_object, js_set

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def _targets(run: Any) -> list[list[Any]]:
    """Every enemy, and each piece the player's shots can hit of the boss fought."""
    boss = run.fights.boss
    out: list[list[Any]] = []
    for enemy in run.enemies.enemies:
        if enemy.gone:
            continue
        is_boss = enemy is boss
        pieces = enemy.shot_targets if is_boss else [enemy]
        if len(pieces) == 0:
            pieces = [enemy]
        out.extend([[p.x, p.y, p.radius, p.health, p.max_health, is_boss] for p in pieces])
    return out


def _shots(run: Any) -> list[list[list[float]]]:
    """Return the enemy bullets and missiles in flight."""
    shots = run.enemies.shots
    bullets = [[b.x, b.y, b.heading, b.speed] for b in shots.bullets if b.alive]
    missiles = [[m.x, m.y, m.heading, m.speed] for m in shots.missiles if m.alive]
    return [bullets, missiles]


def _lasers(run: Any) -> list[list[Any]]:
    return [
        [laser.x, laser.y, laser.heading, laser.length, laser.phase == "firing"]
        for laser in run.enemies.shots.lasers
    ]


def _player(run: Any, scene: Any) -> None:
    """Set the ship, its hull, its bombs and its weapons."""
    ship = run.ship
    js_set(scene, "ship", [ship.x, ship.y, ship.vx, ship.vy, ship.max_speed])
    hull = run.hull
    hull_state = None
    if hull is not None:
        hull_state = [hull.health, hull.max_health, hull.lives, hull.invincible]
    js_set(scene, "hull", hull_state)
    bombs = run.bombs
    js_set(scene, "bombs", [bombs.count, bombs.active is not None] if bombs is not None else None)
    saved = run.arsenal.snapshot()
    js_set(scene, "weapon", saved.weapon)
    js_set(scene, "weapons", [[key, saved.levels[key]] for key in saved.levels.keys()])


def play_scene(run: Any) -> Any:
    """Return what is on the playfield of `run` (a `LevelRun`), as the module's docstring lists."""
    scene = js_object()
    _player(run, scene)
    js_set(scene, "track", [run.track.progress, run.track.length_])
    fights = run.fights
    boss = fights.boss
    health = [boss.health, boss.max_health] if boss is not None else [0, 0]
    js_set(scene, "boss", [fights.active, fights.rank, health[0], health[1]])
    js_set(scene, "targets", _targets(run))
    shots = _shots(run)
    js_set(scene, "bullets", shots[0])
    js_set(scene, "missiles", shots[1])
    js_set(scene, "lasers", _lasers(run))
    bonuses = run.bonuses
    falling = [[b.x, b.y, b.kind] for b in bonuses.bonuses] if bonuses is not None else []
    js_set(scene, "bonuses", falling)
    return scene
