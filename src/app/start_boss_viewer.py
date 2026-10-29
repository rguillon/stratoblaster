"""The bosses debug page (P07-R09), ported from `app/start-boss-viewer.ts`: the boss picked comes in
and fights over the scenery of its level, at its fight ground speed, again and again, while a player
ship that cannot die flies (arrows / WASD) and shoots it with any weapon and level; K destroys its
next part, and the model and wireframe views show its model alone, turning, with its hit circles."""

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.boss_viewer_stage import (  # noqa: E402
    BossViewerStage,
    boss_groups,
    boss_viewer_state,
    circles_of,
    level_of_boss,
)
from app.enemy_close_up import EnemyCloseUp  # noqa: E402
from app.enemy_viewer_keys import SWITCH_KEYS, ShortcutCounts, listen_to_keys, shortcut  # noqa: E402
from app.enemy_viewer_shots import ShotsToDraw  # noqa: E402
from app.rate_meter import RateMeter  # noqa: E402
from app.start_enemy_viewer import EnemyViewerOptions, ShipPosition, weapon_at  # noqa: E402
from app.start_ship_viewer import frame_source  # noqa: E402
from config.boss_viewer import BOSS_VIEWER_CONFIG as CFG  # noqa: E402
from core.entities.enemy import EnemySpawnArea  # noqa: E402
from core.entities.player_ship import ship_max_speed_px_per_sec  # noqa: E402
from core.entities.weapon import validate_weapons  # noqa: E402
from core.loop.fixed_step_clock import FixedStepClock  # noqa: E402
from core.math.rng import create_rng  # noqa: E402
from input.held_directions import HeldDirections  # noqa: E402
from ui.enemy_viewer_panel import (  # noqa: E402
    EnemyViewerPanel,
    EnemyViewerPanelOptions,
    EnemyViewerReadout,
    EnemyViewerSelection,
)
from ui.stats_tile import RenderStats, StatsTile  # noqa: E402

# Options of `start_boss_viewer`: as for the enemies page.
BossViewerOptions = EnemyViewerOptions

HELP = (
    "Move: arrows / WASD · N / B: next / previous boss · K: destroy a part · M: model · "
    "V: wireframe "
    "(← / →: switch boss) · X: weapon · 1-5: level · F: fire · P: pause · L: motion · H: hitbox"
)


class BossViewer:
    """The pieces of a running bosses page; see `start_boss_viewer`."""

    def __init__(self, engine: Any, game: Any, options: BossViewerOptions) -> None:
        self.engine = engine
        self.game = game
        self.options = options
        self.player = ShipPosition(CFG.ship_start.x, CFG.ship_start.y)
        self.held = HeldDirections()
        self._random = create_rng(int(CFG.seed))
        self._clock = FixedStepClock(CFG.step_hz, int(CFG.max_steps_per_frame))
        self._fps = RateMeter(CFG.stats.fps_window)
        self._frames = 0
        self._previous = 0.0
        self._respawn_in = 0.0
        self._kind = -1
        self._model_view = False
        self._boss: Any = None
        validate_weapons(game.player_weapons)
        if len(game.boss_kinds) == 0:
            raise ValueError("The game has no boss")
        self._stage: BossViewerStage = self._new_stage(self._kind_at(0))
        first_id = game.player_ships.ships[0].id if len(game.player_ships.ships) > 0 else ""
        self._speed = ship_max_speed_px_per_sec(game.player_ships, first_id)
        self.close_up = EnemyCloseUp(engine, options.environment, game.view.enemies.glow)
        self._stats: Any = None
        if options.stats_parent:
            self._stats = StatsTile(options.doc, options.stats_parent, CFG.stats.refresh)

        def on_change(selection: EnemyViewerSelection) -> None:
            self._apply(selection)

        self.panel = EnemyViewerPanel(
            EnemyViewerPanelOptions(
                options.doc,
                options.panel_parent,
                [k.name for k in game.boss_kinds],
                [w["name"] for w in game.player_weapons],
                [len(w.levels) for w in game.player_weapons],
                EnemyViewerSelection(0, "behaviour", 0, 3, True, False, True, False),
                HELP,
                on_change,
                "Bosses",
                boss_groups(game),
            )
        )
        self._apply(self.panel.selection)
        self.frame(0)

    def _kind_at(self, index: int) -> Any:
        kinds = self.game.boss_kinds
        kind = kinds[index] if 0 <= index < len(kinds) else (kinds[0] if len(kinds) > 0 else None)
        if kind is None:
            raise ValueError("The game has no boss")
        return kind

    def _new_stage(self, kind: Any) -> BossViewerStage:
        weapon = weapon_at(self.game, 0)
        level = level_of_boss(self.game, kind)
        return BossViewerStage(
            self.engine,
            self.game,
            level,
            self.options.environment,
            self._random,
            weapon,
        )

    def _apply(self, s: EnemyViewerSelection) -> None:
        model_view = s.view != "behaviour"
        self.close_up.wireframe = s.view == "wireframe"
        self.close_up.hitbox = s.hitbox
        if self.game.view.enemies.set_idle_motion:
            self.game.view.enemies.set_idle_motion(s.living)
        if s.kind != self._kind or model_view != self._model_view:
            kind = self._kind_at(s.kind)
            if level_of_boss(self.game, kind) is not self._stage.level:
                self._stage.dispose()
                self._stage = self._new_stage(kind)
            self._kind = s.kind
            self._model_view = model_view
            self._restart(kind)
        self._stage.shots.select(weapon_at(self.game, s.weapon), s.level)
        self._stage.shots.firing = s.fire
        self._stage.ship.pivot.setEnabled(not model_view)

    def _restart(self, kind: Any) -> None:
        """The picked boss again: it comes in anew, or shows in the model view."""
        stage = self._stage
        stage.enemies.clear()
        for shot in stage.shots.projectiles:
            shot.alive = False
        stage.layer.clear()
        self._respawn_in = 0
        screen = self.game.screen
        shown = kind.spawn(
            EnemySpawnArea(screen.width, screen.height, self._random, None, stage.reach)
        )
        build = self.game.view.enemies.models.get(shown.model)
        if build:
            self.close_up.show(build, shown, circles_of(shown))
        self._boss = None
        stage.view.track.set_speed_factor(1, 0)
        if not self._model_view:
            self._spawn()

    def _spawn(self) -> None:
        kind = self._kind_at(self.panel.selection.kind)
        self._boss = self._stage.spawn(kind, self._random)
        self._stage.view.track.set_speed_factor(
            self._boss.ground_speed, self.game.boss_fights.speedEaseSeconds
        )

    def frame(self, dt: float) -> None:
        paused = self.panel.selection.paused
        advance = self._clock.advance(dt)
        blasts: list[Any] = []
        impacts: list[Any] = []
        track = self._stage.view.track
        for _step in range(advance.steps):
            if paused:
                break
            step = self._clock.step_seconds
            self._previous = track.distance
            self._step_track(step)
            if self._model_view:
                continue
            self._fly(step)
            self._stage.enemies.step(step)
            for blast in self._stage.enemies.blasts:
                blasts.append(blast)
            self._stage.shots.step(step)
            for impact in self._stage.shots.impacts:
                impacts.append(impact)
            self._respawn(step)
        factor = 1 if paused else advance.alpha
        distance = self._previous + (track.distance - self._previous) * factor
        self._stage.view.update(distance, dt)
        self._draw(0 if paused else dt, blasts, impacts)

    def _step_track(self, dt: float) -> None:
        """The ground scrolls at the boss's speed, and loops back at the level's end."""
        track = self._stage.view.track
        track.step(dt)
        if not track.ended:
            return
        factor = track.speed_factor
        track.restart()
        track.set_speed_factor(factor, 0)
        self._previous = 0

    def _fly(self, dt: float) -> None:
        """Moves the player ship with the held keys, within what the camera shows."""
        direction = self.held.direction
        screen = self.game.screen
        m = CFG.ship_margin
        py = window.Math.min(
            screen.height - m.top,
            window.Math.max(m.bottom, self.player.y + direction.y * self._speed * dt),
        )
        half = self._stage.half_width_at(py)
        px = self.player.x + direction.x * self._speed * dt
        self.player.x = window.Math.min(
            screen.width / 2 + half, window.Math.max(screen.width / 2 - half, px)
        )
        self.player.y = py
        stage = self._stage
        stage.enemies.player_x = self.player.x
        stage.shots.muzzle_x = self.player.x
        stage.shots.center_x = self.player.x
        stage.enemies.player_y = self.player.y
        stage.shots.center_y = self.player.y
        stage.shots.muzzle_y = self.player.y + stage.muzzle

    def _respawn(self, dt: float) -> None:
        """Once the boss has blown up, the ground eases back, then the boss comes again."""
        if self._boss and not self._boss.gone:
            return
        if self._boss:
            self._boss = None
            self._stage.view.track.set_speed_factor(1, self.game.boss_fights.speedEaseSeconds)
        self._respawn_in += dt
        if self._respawn_in < CFG.respawn_delay:
            return
        self._respawn_in = 0
        self._spawn()

    def _draw(self, dt: float, blasts: list[Any], impacts: list[Any]) -> None:
        stage = self._stage
        stage.ship.pivot.position.set(self.player.x, self.player.y, 0)
        stage.ship.update(dt)
        stage.view.playfield.run(lambda: stage.layer.sync(stage.enemies.enemies, dt))
        stage.drawn.sync(ShotsToDraw(stage.enemies, stage.shots, blasts, impacts, dt))
        self.close_up.update(dt)
        shown = self._boss if self._boss and not self._boss.gone else None
        stage_text = ""
        if shown:
            stage_text = (
                shown.name
                + ": stage "
                + str(shown.stage)
                + " / "
                + str(len(shown.parts))
                + " ("
                + shown.state
                + ")"
            )
        self.panel.show_readout(
            EnemyViewerReadout(
                len(stage.enemies.enemies),
                stage.enemies.shots.count,
                stage.enemies.kills,
                int(stage.enemies.score),
                stage_text,
            )
        )
        self._frames += 1
        self._fps.add(dt, self._frames)
        if self._stats:
            scene = self.active_scene
            self._stats.update(dt, RenderStats(self._fps.rate, scene.getActiveIndices() / 3))

    @property
    def active_scene(self) -> Any:
        """The scene drawn now: the level's, or the model view's."""
        return self.close_up.scene if self._model_view else self._stage.view.scene

    def state(self) -> Any:
        return boss_viewer_state(self._stage, self._boss, self.player)

    def key(self, key: str, code: str, down: bool) -> None:
        n = len(self.game.boss_kinds)
        step = SWITCH_KEYS.get(code, 0)
        if self._model_view and down and step != 0:
            self.panel.update({"kind": (self.panel.selection.kind + step + n) % n})
            return
        if self.held.key(code, down) or not down:
            return
        if code == "KeyK":
            if self._boss:
                self._boss.break_next()
            return
        counts = ShortcutCounts(n, len(self.game.player_weapons))
        change = shortcut(key, self.panel.selection, counts)
        if change:
            self.panel.update(change)

    def dispose(self) -> None:
        self._stage.dispose()
        self.panel.root.remove()
        if self._stats:
            self._stats.root.remove()
        self.close_up.dispose()


class RunningBossViewer:
    """Handle on a running bosses page: `panel`, `close_up`, `active_scene`, `state()`, `frame(dt)`,
    `key(key, code, down)` and `dispose()`."""

    def __init__(self, engine: Any, viewer: BossViewer, stop_listening: Any) -> None:
        self._engine = engine
        self._viewer = viewer
        self._stop_listening = stop_listening
        self.panel = viewer.panel
        self.close_up = viewer.close_up

    @property
    def active_scene(self) -> Any:
        return self._viewer.active_scene

    def state(self) -> Any:
        return self._viewer.state()

    def frame(self, dt: float) -> None:
        self._viewer.frame(dt)

    def key(self, key: str, code: str, down: bool) -> None:
        self._viewer.key(key, code, down)

    def dispose(self) -> None:
        self._engine.stopRenderLoop()
        self._stop_listening()
        self._viewer.dispose()


def start_boss_viewer(engine: Any, game: Any, options: BossViewerOptions) -> RunningBossViewer:
    """Starts the bosses debug page (P07-R09): the boss picked comes in and fights over the scenery
    of its level, at its fight ground speed, again and again, while a player ship that cannot die
    flies (arrows / WASD) and shoots it with any weapon and level; K destroys its next part, and the
    model and wireframe views show its model alone, turning, with its hit circles."""
    viewer = BossViewer(engine, game, options)
    stop_listening = listen_to_keys(options.keyboard_target, viewer)
    frame_seconds = options.frame_seconds if options.frame_seconds else frame_source(engine)
    if options.render_loop:

        def render_frame() -> None:
            viewer.frame(window.Math.min(frame_seconds(), CFG.max_frame_seconds))
            viewer.active_scene.render()

        engine.runRenderLoop(render_frame)
    return RunningBossViewer(engine, viewer, stop_listening)
