"""What the `bosses/` page shows of one level (P07-R09), ported from `app/boss-viewer-stage.ts`: its
scenery under the playfield camera, the enemies (the boss, and what it launches) and the player's
shots, all drawn on the playfield layer, and the player ship. Rebuilt when a boss of another level
is picked."""

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.enemy_close_up import HitCircle  # noqa: E402
from app.enemy_viewer_shots import EnemyViewerShots  # noqa: E402
from app.level_scene import LevelSceneOptions, build_level_scene  # noqa: E402
from app.shot_viewer_scene import PlayfieldShip  # noqa: E402
from config.boss_viewer import BOSS_VIEWER_CONFIG as CFG  # noqa: E402
from core.content.game_level import GameLevel  # noqa: E402
from core.entities.enemy import EnemySpawnArea  # noqa: E402
from core.scenery.scenery_level import with_runout  # noqa: E402
from core.systems.enemy_world import EnemyDifficulty, EnemyWorld, EnemyWorldOptions  # noqa: E402
from core.systems.shot_world import ShotWorld, ShotWorldOptions  # noqa: E402
from render.babylon import js_object, js_set  # noqa: E402
from render.enemy_layer import EnemyLayer  # noqa: E402
from render.scenery.playfield_framing import playfield_eye, visible_half_width  # noqa: E402
from ui.enemy_viewer_panel import EnemyGroup  # noqa: E402


def level_of_boss(game: Any, kind: Any) -> Any:
    """The level a boss belongs to (P07-R09: it is fought over that level's scenery), or None."""
    for level in game.game_levels:
        for b in level.bosses or []:
            if b.kind == kind.id:
                return level
    return None


def boss_groups(game: Any) -> list[EnemyGroup]:
    """Headings of the boss buttons (P08-R12): a world's bosses come after the ones before, under
    `World N`, from the level each boss is fought in (its id's first part)."""
    groups: list[EnemyGroup] = []
    for i in range(len(game.boss_kinds)):
        level = level_of_boss(game, game.boss_kinds[i])
        world = level.id.split("-")[0] if level else None
        label = "Other" if world is None else "World " + world
        if len(groups) == 0 or groups[len(groups) - 1].label != label:
            groups.append(EnemyGroup(label, i))
    return groups


def _scenery_of(game: Any, level: GameLevel | None) -> Any:
    """The scenery a boss is fought over: its level's (and its extra ground), or the first's."""
    if level:
        runout = level.runout if level.runout is not None else 0
        return with_runout(level.scenery, runout)
    if len(game.game_levels) == 0:
        raise ValueError("The game has no level")
    return game.game_levels[0].scenery


class BossViewerStage:
    """The stage of one level of the bosses page: scenery, enemies, shots and the ship."""

    def __init__(
        self,
        engine: Any,
        game: Any,
        level: Any,
        environment: bool,
        random: Any,
        weapon: Any,
    ) -> None:
        self.game = game
        self.level = level
        self.view = build_level_scene(
            engine,
            game,
            LevelSceneOptions(
                _scenery_of(game, level),
                environment,
                game.view.enemies.glow,
                int(CFG.environment_cube_size),
                CFG.stage,
                None,
                None,
            ),
        )
        screen = game.screen
        width = screen.width
        height = screen.height
        difficulty = level.difficulty if level and level.difficulty else EnemyDifficulty(1, 1)
        eye = playfield_eye(screen, self.view.stage.framing)
        self.enemies = EnemyWorld(
            EnemyWorldOptions(width, height, CFG.cull_margin, CFG.max_enemy_age, eye),
            random,
            difficulty,
        )
        self.shots = ShotWorld(ShotWorldOptions(width, height, CFG.cull_margin), weapon)
        self.shots.targets = self.enemies.targets
        pf = self.view.playfield
        self.layer = pf.run(lambda: EnemyLayer(self.view.scene, game.view.enemies.models))
        self.drawn = EnemyViewerShots(game, pf, self.view.look.shot_style)
        first = game.player_ships.ships[0] if len(game.player_ships.ships) > 0 else None
        model = game.view.player_ship_models.get(first.id) if first else None

        def build_ship() -> list[Any]:
            ship = PlayfieldShip(self.view.scene, game.view.player_ship_scale, 0, 0)
            nose = ship.show(model) if model else 0
            return [ship, nose]

        built = pf.run(build_ship)
        self.ship = built[0]
        nose = built[1]
        self.muzzle = window.Math.max(0, nose - CFG.muzzle_inset)
        half = self.half_width_at(CFG.ship_margin.bottom)
        self.reach = (width / 2 - half, width / 2 + half)

    def half_width_at(self, y: float) -> float:
        """Half the width the ship may fly in at height `y` (inside what the camera shows)."""
        screen = self.game.screen
        return (
            visible_half_width(self.view.stage.framing, screen.width / screen.height, y)
            - CFG.ship_margin.side
        )

    def spawn(self, kind: Any, random: Any) -> Any:
        """A new boss of `kind`, coming in from the top."""
        screen = self.game.screen
        boss = kind.spawn(EnemySpawnArea(screen.width, screen.height, random, None, self.reach))
        self.enemies.add(boss)
        return boss

    def dispose(self) -> None:
        self.layer.dispose()
        self.drawn.dispose()
        self.view.scene.dispose()


def circles_of(boss: Any) -> list[HitCircle]:
    """The hit circles of a boss for the wireframe view: core, shielding parts, other parts."""
    circles = CFG.circles
    result = [HitCircle(0, 0, boss.core.radius, circles.core)]
    for part in boss.parts:
        color = circles.shield if part.shields_core else circles.part
        result.append(HitCircle(part.spec.x, part.spec.y, part.radius, color))
    return result


def _alive(items: list[Any]) -> int:
    count = 0
    for item in items:
        if item.alive:
            count += 1
    return count


def _boss_state(boss: Any) -> Any:
    """The readout of one boss, with the camelCase keys of the test API."""
    result = js_object()
    js_set(result, "id", boss.model)
    js_set(result, "name", boss.name)
    js_set(result, "state", boss.state)
    js_set(result, "stage", boss.stage)
    js_set(result, "parts", len(boss.parts))
    parts_left = 0
    for part in boss.parts:
        if not part.destroyed:
            parts_left += 1
    js_set(result, "partsLeft", parts_left)
    js_set(result, "health", boss.remaining_health)
    js_set(result, "fullHealth", boss.full_health)
    return result


def boss_viewer_state(stage: Any, shown: Any, player: Any) -> Any:
    """What the bosses page reports (its e2e test API, the readout): a JavaScript object."""
    boss = shown if shown and not shown.gone else None
    enemies = stage.enemies
    view = stage.view
    result = js_object()
    js_set(result, "boss", _boss_state(boss) if boss else None)
    js_set(result, "kills", enemies.kills)
    js_set(result, "bullets", _alive(enemies.shots.bullets))
    js_set(result, "missiles", _alive(enemies.shots.missiles))
    js_set(result, "lasers", len(enemies.shots.lasers))
    js_set(result, "groundSpeed", view.track.speed_factor)
    position = js_object()
    js_set(position, "x", player.x)
    js_set(position, "y", player.y)
    js_set(result, "player", position)
    return result
