"""The enemies debug page (P05-R11), ported from `app/start-enemy-viewer.ts`: the enemy kind picked
spawns over the first level's ground, again and again, while a player ship flies (arrows / WASD) and
shoots it with any weapon and level; the model view shows the enemy's model alone, turning."""

from org.transcrypt.stubs.browser import __pragma__, window

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.enemy_close_up import EnemyCloseUp  # noqa: E402
from app.enemy_viewer_keys import HELP, SWITCH_KEYS, ShortcutCounts, listen_to_keys, shortcut  # noqa: E402
from app.enemy_viewer_scene import build_enemy_viewer_scene  # noqa: E402
from app.enemy_viewer_shots import EnemyViewerShots, ShotsToDraw  # noqa: E402
from app.rate_meter import RateMeter  # noqa: E402
from app.shot_viewer_scene import PlayfieldShip  # noqa: E402
from app.start_ship_viewer import frame_source  # noqa: E402
from config.enemy_viewer import ENEMY_VIEWER_CONFIG as CFG  # noqa: E402
from core.entities.enemy import EnemySpawnArea, validate_enemy_kinds  # noqa: E402
from core.entities.player_ship import ship_max_speed_px_per_sec  # noqa: E402
from core.entities.weapon import validate_weapons  # noqa: E402
from core.loop.fixed_step_clock import FixedStepClock  # noqa: E402
from core.math.rng import create_rng  # noqa: E402
from core.systems.enemy_world import EnemyWorld, EnemyWorldOptions  # noqa: E402
from core.systems.shot_world import ShotWorld, ShotWorldOptions  # noqa: E402
from input.held_directions import HeldDirections  # noqa: E402
from render.enemy_layer import EnemyLayer  # noqa: E402
from render.scenery.playfield_framing import playfield_eye, visible_half_width  # noqa: E402
from ui.enemy_viewer_panel import (  # noqa: E402
    EnemyViewerPanel,
    EnemyViewerPanelOptions,
    EnemyViewerReadout,
    EnemyViewerSelection,
)
from ui.stats_tile import RenderStats, StatsTile  # noqa: E402


class EnemyViewerOptions:
    """Options of `start_enemy_viewer` (also the bosses page's). `environment`: generated textures,
    sky lighting, shadows and glow (needs a real WebGL engine). `doc` and `panel_parent`: where the
    controls go. `stats_parent`: where the FPS / polygons tile goes (None: none). `keyboard_target`:
    where keys are listened to (None: no keyboard). `frame_seconds`: seconds since the last frame
    (None: the engine's). `render_loop`: starts the engine's render loop (off in unit tests)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        environment: bool,
        doc: Any,
        panel_parent: Any,
        stats_parent: Any,
        keyboard_target: Any,
        frame_seconds: Any,
        render_loop: bool,
    ) -> None:
        self.environment = environment
        self.doc = doc
        self.panel_parent = panel_parent
        self.stats_parent = stats_parent
        self.keyboard_target = keyboard_target
        self.frame_seconds = frame_seconds
        self.render_loop = render_loop


class ShipPosition:
    """Where the player ship is on the playfield (logical pixels, Y up)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def weapon_at(game: Any, index: int) -> Any:
    """The player weapon at `index`; raises when there is none."""
    if index < 0 or index >= len(game.player_weapons):
        raise ValueError("No weapon at index " + str(index))
    return game.player_weapons[index]


class EnemyViewer:
    """The pieces of a running enemies page; see `start_enemy_viewer`."""

    def __init__(self, engine: Any, game: Any, options: EnemyViewerOptions) -> None:
        self.game = game
        self.player = ShipPosition(CFG.ship_start.x, CFG.ship_start.y)
        self.held = HeldDirections()
        self._random = create_rng(int(CFG.seed))
        self._clock = FixedStepClock(CFG.step_hz, int(CFG.max_steps_per_frame))
        self._fps = RateMeter(CFG.stats.fps_window)
        self._frames = 0
        self._nose_offset = 0.0
        self._previous = 0.0
        self._respawn_in = 0.0
        # The kind and view shown, to restart only when they change.
        self._kind = -1
        self._model_view = False
        validate_weapons(game.player_weapons)
        validate_enemy_kinds(game.enemy_kinds)
        width = game.screen.width
        height = game.screen.height
        self.view = build_enemy_viewer_scene(
            engine, game, options.environment, game.view.enemies.glow
        )
        eye = playfield_eye(game.screen, self.view.stage.framing)
        self.enemies = EnemyWorld(
            EnemyWorldOptions(width, height, CFG.cull_margin, CFG.max_enemy_age, eye),
            self._random,
        )
        self.shots = ShotWorld(ShotWorldOptions(width, height, CFG.cull_margin), weapon_at(game, 0))
        self.shots.targets = self.enemies.targets
        pf = self.view.playfield
        self._layer = pf.run(lambda: EnemyLayer(self.view.scene, game.view.enemies.models))
        self._drawn = EnemyViewerShots(game, pf)
        self._ship = self._build_ship()
        first_speed_id = game.player_ships.ships[0].id if len(game.player_ships.ships) > 0 else ""
        self._speed = ship_max_speed_px_per_sec(game.player_ships, first_speed_id)
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
                [k.name for k in game.enemy_kinds],
                [w["name"] for w in game.player_weapons],
                [len(w.levels) for w in game.player_weapons],
                EnemyViewerSelection(0, "behaviour", 0, 1, True, False, True, False),
                HELP,
                on_change,
                None,
                None,
            )
        )
        self._apply(self.panel.selection)
        self.frame(0)

    def _build_ship(self) -> Any:
        """The game's first ship; the muzzle is measured on its model, before it joins the
        playfield."""
        ships = self.game.player_ships.ships
        first = ships[0] if len(ships) > 0 else None
        model = self.game.view.player_ship_models.get(first.id) if first else None
        scale = self.game.view.player_ship_scale
        scene = self.view.scene
        muzzle_inset = CFG.muzzle_inset

        def build() -> list[Any]:
            ship = PlayfieldShip(scene, scale, 0, 0)
            offset = ship.show(model) - muzzle_inset if model else 0
            return [ship, offset]

        built = self.view.playfield.run(build)
        self._nose_offset = built[1]
        return built[0]

    def _apply(self, s: EnemyViewerSelection) -> None:
        self.shots.select(weapon_at(self.game, s.weapon), s.level)
        self.shots.firing = s.fire
        # The wireframe view is the model view drawn as lines (phase 5 review: to see the polygons).
        model_view = s.view != "behaviour"
        self.close_up.wireframe = s.view == "wireframe"
        self.close_up.hitbox = s.hitbox
        if self.game.view.enemies.set_idle_motion:
            self.game.view.enemies.set_idle_motion(s.living)
        if s.kind != self._kind or model_view != self._model_view:
            self._kind = s.kind
            self._model_view = model_view
            self._restart()
        self._ship.pivot.setEnabled(not model_view)

    def _restart(self) -> None:
        """Starts the picked kind again: a new group, or its model in the model view."""
        self.enemies.clear()
        for shot in self.shots.projectiles:
            shot.alive = False
        self._layer.clear()
        self._respawn_in = 0
        kinds = self.game.enemy_kinds
        index = self.panel.selection.kind
        if index < 0 or index >= len(kinds):
            return
        spawned = kinds[index].spawn(self._area())
        first = spawned[0] if len(spawned) > 0 else None
        build = self.game.view.enemies.models.get(first.model) if first else None
        if first and build:
            self.close_up.show(build, first)
        if not self._model_view:
            self._spawn()

    def _area(self) -> Any:
        screen = self.game.screen
        return EnemySpawnArea(screen.width, screen.height, self._random)

    def _spawn(self) -> None:
        kinds = self.game.enemy_kinds
        index = self.panel.selection.kind
        if 0 <= index < len(kinds):
            for enemy in kinds[index].spawn(self._area()):
                self.enemies.add(enemy)

    def frame(self, dt: float) -> None:
        paused = self.panel.selection.paused
        advance = self._clock.advance(dt)
        blasts: list[Any] = []
        impacts: list[Any] = []
        track = self.view.track
        for _step in range(advance.steps):
            if paused:
                break
            step = self._clock.step_seconds
            self._previous = track.distance
            track.step(step)
            if track.ended:
                track.seek(0)
            if self._model_view:
                continue
            self._fly(step)
            self.enemies.step(step)
            for blast in self.enemies.blasts:
                blasts.append(blast)
            self.shots.step(step)
            for impact in self.shots.impacts:
                impacts.append(impact)
            self._respawn(step)
        factor = 1 if paused else advance.alpha
        distance = self._previous + (track.distance - self._previous) * factor
        self.view.update(distance, dt)
        self._draw(0 if paused else dt, blasts, impacts)

    def _fly(self, dt: float) -> None:
        """Moves the player ship with the held keys, within what the camera shows."""
        direction = self.held.direction
        screen = self.game.screen
        m = CFG.ship_margin
        py = window.Math.min(
            screen.height - m.top,
            window.Math.max(m.bottom, self.player.y + direction.y * self._speed * dt),
        )
        half = (
            visible_half_width(self.view.stage.framing, screen.width / screen.height, py) - m.side
        )
        px = self.player.x + direction.x * self._speed * dt
        self.player.x = window.Math.min(
            screen.width / 2 + half, window.Math.max(screen.width / 2 - half, px)
        )
        self.player.y = py
        self.enemies.player_x = self.player.x
        self.enemies.player_y = self.player.y
        self.shots.muzzle_x = self.player.x
        self.shots.center_x = self.player.x
        self.shots.center_y = self.player.y
        self.shots.muzzle_y = self.player.y + self._nose_offset

    def _respawn(self, dt: float) -> None:
        """A new group appears once the last one has gone."""
        if len(self.enemies.enemies) > 0:
            return
        self._respawn_in += dt
        if self._respawn_in < CFG.respawn_delay:
            return
        self._respawn_in = 0
        self._spawn()

    def _draw(self, dt: float, blasts: list[Any], impacts: list[Any]) -> None:
        self._ship.pivot.position.set(self.player.x, self.player.y, 0)
        self._ship.update(dt)
        self.view.playfield.run(lambda: self._layer.sync(self.enemies.enemies, dt))
        self._drawn.sync(ShotsToDraw(self.enemies, self.shots, blasts, impacts, dt))
        self.close_up.update(dt)
        self.panel.show_readout(
            EnemyViewerReadout(
                len(self.enemies.enemies),
                self.enemies.shots.count,
                self.enemies.kills,
                int(self.enemies.score),
            )
        )
        self._frames += 1
        self._fps.add(dt, self._frames)
        if self._stats:
            scene = self.active_scene
            self._stats.update(dt, RenderStats(self._fps.rate, scene.getActiveIndices() / 3))

    @property
    def active_scene(self) -> Any:
        """The scene to draw: the close-up in the model view, the level otherwise."""
        return self.close_up.scene if self._model_view else self.view.scene

    def key(self, key: str, code: str, down: bool) -> None:
        step = SWITCH_KEYS.get(code, 0)
        if self._model_view and down and step != 0:
            n = len(self.game.enemy_kinds)
            self.panel.update({"kind": (self.panel.selection.kind + step + n) % n})
            return
        if self.held.key(code, down) or not down:
            return
        counts = ShortcutCounts(len(self.game.enemy_kinds), len(self.game.player_weapons))
        change = shortcut(key, self.panel.selection, counts)
        if change:
            self.panel.update(change)

    def dispose(self) -> None:
        self._layer.dispose()
        self._drawn.dispose()
        self.panel.root.remove()
        if self._stats:
            self._stats.root.remove()
        self.close_up.dispose()
        self.view.scene.dispose()


class RunningEnemyViewer:
    """Handle on a running enemies page: `scene`, `enemies`, `shots`, `panel`, `close_up`, `player`,
    `active_scene`, and `frame(dt)`, `key(key, code, down)`, `dispose()`."""

    def __init__(self, engine: Any, viewer: EnemyViewer, stop_listening: Any) -> None:
        self._engine = engine
        self._viewer = viewer
        self._stop_listening = stop_listening
        self.scene = viewer.view.scene
        self.enemies = viewer.enemies
        self.shots = viewer.shots
        self.panel = viewer.panel
        self.close_up = viewer.close_up
        self.player = viewer.player

    @property
    def active_scene(self) -> Any:
        return self._viewer.active_scene

    def frame(self, dt: float) -> None:
        self._viewer.frame(dt)

    def key(self, key: str, code: str, down: bool) -> None:
        self._viewer.key(key, code, down)

    def dispose(self) -> None:
        self._engine.stopRenderLoop()
        self._stop_listening()
        self._viewer.dispose()


def start_enemy_viewer(engine: Any, game: Any, options: EnemyViewerOptions) -> RunningEnemyViewer:
    """Starts the enemies debug page (P05-R11): the enemy kind picked spawns over the first level's
    ground, again and again, while a player ship flies (arrows / WASD) and shoots it with any weapon
    and level; the model view shows the enemy's model alone, turning."""
    viewer = EnemyViewer(engine, game, options)
    stop_listening = listen_to_keys(options.keyboard_target, viewer)
    frame_seconds = options.frame_seconds if options.frame_seconds else frame_source(engine)
    if options.render_loop:

        def render_frame() -> None:
            viewer.frame(window.Math.min(frame_seconds(), CFG.max_frame_seconds))
            viewer.active_scene.render()

        engine.runRenderLoop(render_frame)
    return RunningEnemyViewer(engine, viewer, stop_listening)
