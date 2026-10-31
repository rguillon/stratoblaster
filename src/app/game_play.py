"""The game screen of a level (P06-R02): the chosen ship flies over
the chosen level's scrolling scenery, moved and fired by the game controls, while the level's waves
come in. It runs the level (`LevelRun`) at a fixed step and draws it on the playfield layer.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from app.enemy_viewer_shots import EnemyViewerShots, ShotsToDraw
from app.game_play_hud import (
    STATS_SHOWN,
    LevelOverlaysOptions,
    create_level_overlays,
    create_stats,
    hud_frame,
)
from app.game_play_state import level_state
from app.hit_blasts import hit_blasts
from app.level_prepare import level_of, scenery_with_runout
from app.level_scene import LevelSceneOptions, build_level_scene, compile_shaders, sky_state
from app.rate_meter import RateMeter
from app.readability_probe import probe_readability
from app.shot_viewer_scene import PlayfieldShip
from config.game_controls import GAME_CONTROLS_CONFIG
from config.game_play import GAME_PLAY_CONFIG as CFG
from core.entities.enemy import EnemySpawnArea
from core.entities.muzzle import PlanePoint
from core.entities.player_ship import find_player_ship, ship_max_speed_px_per_sec
from core.loop.fixed_step_clock import FixedStepClock
from core.math.rng import create_rng
from core.systems.level_models import level_model_keys
from core.systems.level_run import LevelRun
from core.systems.level_run_types import LevelRunOptions, RunShip
from render.babylon import js_set, set_enabled
from render.enemy_layer import EnemyLayer
from render.game_view import BombFrame, BonusFrame
from render.scenery.playfield_framing import playfield_eye, visible_half_width
from ui.stats_tile import RenderStats

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class GameChoice:
    """What the player chose: a ship (`ship_id`) and a level (`level_id`)."""

    def __init__(self, ship_id: str, level_id: str) -> None:
        self.ship_id = ship_id
        self.level_id = level_id


class GamePlayOptions:
    """Options of a `GamePlay`, positional (Transcrypt drops keyword arguments). `None` stands for
    an omitted optional field: `environment` (generated textures, sky lighting, shadows and glow;
    needs a real WebGL engine), `debug` (P06-R09: playback keys and the FPS / polygons tile),
    `start_time` (seconds into the level, P06-R09), `start_boss` (the rank of the boss to start at,
    P07-R09), `resume` (a checkpoint, P07-R08), `journey` (False: the ship does not fly in and
    off; reviewer, 2026-10-28), `weapons` and `supplies` (kept from the levels before), `high_score`
    (P11-R02), `atmosphere` (debug choices on the look, P08-R12), `doc`, `stats_parent` (the debug
    tile's), `hud_parent` (the HUD's), `on_complete(result)` (P06-R03, GD-20) and `on_step(run)`
    (P12-R09).
    """

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        environment: bool,
        debug: bool,
        start_time: float,
        start_boss: str | None,
        resume: Any,
        journey: bool | None,
        weapons: Any,
        supplies: Any,
        high_score: int | None,
        atmosphere: Any,
        doc: Any,
        stats_parent: Any,
        hud_parent: Any,
        on_complete: Any,
        on_step: Any,
    ) -> None:
        self.environment = environment
        self.debug = debug
        self.start_time = start_time
        self.start_boss = start_boss
        self.resume = resume
        self.journey = journey
        self.weapons = weapons
        self.supplies = supplies
        self.high_score = high_score
        self.atmosphere = atmosphere
        self.doc = doc
        self.stats_parent = stats_parent
        self.hud_parent = hud_parent
        self.on_complete = on_complete
        self.on_step = on_step


class PlayfieldBounds:
    """Where the player ship may fly, in playfield logical pixels: the `FlightBounds` of
    `core/systems/player_flight.py` (structural)."""

    def __init__(self, min_y: float, max_y: float, center_x: float, half_width_at: Any) -> None:
        self.min_y = min_y
        self.max_y = max_y
        self.center_x = center_x
        self.half_width_at = half_width_at


class GamePlay:
    """The game screen (P06-R02): the chosen ship flies over the chosen level's scrolling scenery,
    moved and fired by the game controls, while the level's waves come in. It runs the level
    (`LevelRun`) at a fixed step and draws it on the playfield layer.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        game: Any,
        choice: GameChoice,
        controls: Any,
        options: GamePlayOptions,
    ) -> None:
        self.game = game
        self._controls = controls
        self._options = options
        self._clock = FixedStepClock(CFG.step_hz, int(CFG.max_steps_per_frame))
        self._fps = RateMeter(CFG.stats.fps_window)
        self._frames = 0
        self._previous = 0.0
        self._time_scale = 1.0
        # How far the ship is banked, in radians (visual only).
        self._roll = 0.0
        self._completed = False
        # Whether the shaders of the enemy models built ahead are compiled (see `prepare`).
        self._compile_shaders = False
        # Seconds since the last life was lost (the "Game over" overlay waits a little).
        self._over_for = 0.0
        self._hud: Any = None
        self._stats: Any = None
        # Whether the level is in the page (see `attach`).
        self._attached = False

        level = level_of(game, choice.level_id)
        outline = game.view.outline if options.environment else None
        self.view = build_level_scene(
            engine,
            game,
            LevelSceneOptions(
                # Extra ground past the end, for the final boss fight (P07-R03).
                scenery_with_runout(level),
                options.environment,
                game.view.enemies.glow,
                int(CFG.environment_cube_size),
                CFG.stage,
                options.atmosphere,
                outline,
            ),
        )
        self._speed = ship_max_speed_px_per_sec(game.player_ships, choice.ship_id)
        self._ship_def: Any = find_player_ship(game.player_ships, choice.ship_id)
        playfield = self.view.playfield
        scale = game.view.player_ship_scale
        model = game.view.player_ship_models.get(choice.ship_id)

        def build_ship() -> list[Any]:
            ship = PlayfieldShip(self.view.scene, scale, 0, 0)
            # The nose is measured on the model before it joins the playfield.
            nose = ship.show(model) if model is not None else 0
            return [ship, nose]

        built = playfield.run(build_ship)
        self._ship: Any = built[0]
        nose = built[1]
        self.run: LevelRun = self._new_run(level, max(0, nose - CFG.muzzle_inset))
        keys = self._model_keys(level)
        self._enemies = playfield.run(
            lambda: EnemyLayer(self.view.scene, game.view.enemies.models, keys)
        )
        self._shots = EnemyViewerShots(game, playfield, self.view.look.shotStyle)
        self._bonuses = playfield.run(lambda: game.view.bonuses(self.view.scene))
        self._bombs = playfield.run(
            lambda: game.view.bombs(self.view.scene) if game.view.bombs is not None else None
        )
        if options.start_time > 0:
            self._seek(options.start_time)
        for boss in self.run.fights.bosses:
            if boss.rank == options.start_boss:
                self._seek(boss.at / self.run.track.speed)
                break
        self.frame(0)

    def _new_run(self, level: Any, muzzle_offset: float) -> LevelRun:
        weapons = self.game.player_weapons
        if len(weapons) == 0:
            raise ValueError("The game has no player weapon")
        screen = self.game.screen
        ship = RunShip(
            PlanePoint(screen.width / 2, CFG.ship_start_y),
            self._speed,
            GAME_CONTROLS_CONFIG.acceleration_seconds,
            muzzle_offset,
            self._ship_def.max_health,
        )
        # The config journey is a ShipJourney, not its JourneyRules (a config mismatch, typed Any).
        journey: Any = None if self._options.journey is False else CFG.journey
        return LevelRun(
            LevelRunOptions(
                screen,
                level,
                self.game.enemy_kinds,
                weapons[0],
                1,
                ship,
                self._bounds(),
                CFG.cull_margin,
                CFG.max_enemy_age,
                CFG.end_wait,
                int(CFG.seed),
                weapons,
                self._options.weapons,
                self._options.supplies,
                playfield_eye(screen, self.view.stage.framing),
                self._in_view(),
                self.game.bonuses,
                self.game.bombs,
                self.game.hull,
                self.game.boss_kinds,
                self.game.boss_fights,
                self._options.resume,
                journey,
            )
        )

    def _model_keys(self, level: Any) -> list[str]:
        """The enemy models `level` needs (P13-R03), built while it loads: those of its waves and
        bosses, and the enemies they send out. The kinds are spawned with their own random numbers,
        so the level's are untouched."""
        game = self.game
        screen = game.screen
        random = create_rng(int(CFG.seed))

        def area_of(entry: Any) -> EnemySpawnArea:
            return EnemySpawnArea(screen.width, screen.height, random, entry)

        bosses = level.bosses if level.bosses is not None else []
        boss_kinds = game.boss_kinds if game.boss_kinds is not None else []
        children: list[str] = game.view.enemies.child_models
        return level_model_keys(
            level.waves, bosses, game.enemy_kinds, boss_kinds, area_of, children
        )

    def _in_view(self) -> Any:
        """Whether a playfield point is inside what the tilted camera shows."""
        screen = self.game.screen
        width = screen.width
        height = screen.height
        framing = self.view.stage.framing

        def in_view(x: float, y: float) -> bool:
            return (
                y >= 0
                and y <= height
                and abs(x - width / 2) <= visible_half_width(framing, width / height, y)
            )

        return in_view

    def _bounds(self) -> PlayfieldBounds:
        """Where the ship may fly: inside what the tilted camera shows (P06-R02)."""
        screen = self.game.screen
        width = screen.width
        height = screen.height
        margin = CFG.ship_margin
        framing = self.view.stage.framing

        def half_width_at(y: float) -> float:
            return visible_half_width(framing, width / height, y) - margin.side

        return PlayfieldBounds(margin.bottom, height - margin.top, width / 2, half_width_at)

    @property
    def time_scale(self) -> float:
        return self._time_scale

    def frame(self, dt: float) -> None:
        """Advances and draws one frame of `dt` real seconds."""
        advance = self._clock.advance(dt * self._time_scale)
        blasts: list[Any] = []
        impacts: list[Any] = []
        picked: list[Any] = []
        step = self._clock.step_seconds
        for _ in range(advance.steps):
            self._previous = self.run.track.distance
            self.run.step(step, self._controls.read(step, self._speed))
            if self._options.on_step is not None:
                self._options.on_step(self.run)
            blasts.extend(self.run.blasts)
            impacts.extend(self.run.impacts)
            if self.run.bonuses is not None:
                picked.extend(self.run.bonuses.picked)
            blasts.extend(hit_blasts(self.run.hits, self.run.ship))
        track = self.run.track
        distance = self._previous + (track.distance - self._previous) * advance.alpha
        self.view.update(distance, dt)
        self._draw(dt, blasts, impacts, picked)
        # One more enemy model built ahead of its first appearance, each frame (P13-R04).
        enemies = self._enemies
        built = self.view.playfield.run(enemies.prepare_next)
        if self._compile_shaders:
            compile_shaders(built)
        if self.run.phase == "over":
            self._over_for += dt * self._time_scale
        over = self._over_for >= CFG.damage.game_over_delay
        if (self.run.phase == "complete" or over) and not self._completed:
            self._completed = True
            self._options.on_complete(self.run.result)

    def _draw(self, dt: float, blasts: list[Any], impacts: list[Any], picked: list[Any]) -> None:
        run = self.run
        ship = run.ship
        enemies = run.enemies
        shots = run.shots
        self._ship.pivot.position.set(ship.x, ship.y, 0)
        set_enabled(self._ship.pivot, self._ship_shown())
        self._ship.pivot.rotation.y = self._bank(ship.vx, dt)
        self._ship.update(dt)

        def sync_playfield() -> None:
            self._enemies.sync(enemies.enemies, dt)
            bonuses = run.bonuses.bonuses if run.bonuses is not None else []
            self._bonuses.sync(BonusFrame(bonuses, picked, dt))
            if self._bombs is not None:
                bomb = run.bombs.active if run.bombs is not None else None
                self._bombs.sync(BombFrame(bomb, dt))

        self.view.playfield.run(sync_playfield)
        self._shots.sync(ShotsToDraw(enemies, shots, blasts, impacts, dt))
        high_score = self._options.high_score if self._options.high_score is not None else 0
        if self._hud is not None:
            self._hud.update(hud_frame(run, self._ship_def.max_health, self.game.texts, high_score))
        self._frames += 1
        self._fps.add(dt, self._frames)
        polygons = self.view.scene.getActiveIndices() / 3
        if self._stats is not None:
            self._stats.update(dt, RenderStats(self._fps.rate, polygons))

    def _ship_shown(self) -> bool:
        """Whether the ship shows: not once the game is over, blinking while invincible (GD-22)."""
        hull = self.run.hull
        if self.run.phase == "over":
            return False
        if hull is None or hull.invincible <= 0:
            return True
        return math.floor(hull.invincible * CFG.damage.blink_hz * 2) % 2 == 0

    def _bank(self, vx: float, dt: float) -> float:
        """The ship's bank for a sideways speed `vx` (phase 6 review): the wing on the side it flies
        to dips, more the faster it goes, easing in and out. Around the nose (the playfield's Y),
        negative turns +X away from the camera.
        """
        max_deg = CFG.roll.max_deg
        ease = CFG.roll.ease_per_sec
        target = -(vx / self._speed) * ((max_deg * math.pi) / 180)
        self._roll += (target - self._roll) * min(1, ease * dt)
        return self._roll

    @property
    def roll(self) -> float:
        """The ship's bank, in radians: negative when flying right."""
        return self._roll

    def debug_key(self, code: str, down: bool) -> bool:
        """A debug key (P06-R09): F toggles x4 fast forward, left / right jump 10 s back or on, K
        destroys the next part of the boss fought (P07-R09). Returns whether the key was used;
        without debug mode no key is, but the debug tile's (D-212: F2 shows or hides it).
        """
        if code == CFG.stats.key:
            if down:
                self._toggle_stats()
            return True
        fast_forward = CFG.debug.fast_forward
        seek_step = CFG.debug.seek_step
        jumps = code in ("ArrowLeft", "ArrowRight")
        known = code in ("KeyF", "KeyK") or jumps
        if not self._options.debug or not known:
            return False
        if not down:
            return True
        if code == "KeyF":
            self._time_scale = fast_forward if self._time_scale == 1 else 1
        elif code == "KeyK":
            self.run.break_boss_part()
        else:
            jump = -seek_step if code == "ArrowLeft" else seek_step
            self._seek(self.run.track.time + jump)
        return True

    def _seek(self, time: float) -> None:
        if self._completed:
            return
        self.run.seek(time)
        self._previous = self.run.track.distance

    @property
    def state(self) -> Any:
        """The state of the level for the test API, with its look where the view is (P08)."""
        middle = self.run.track.distance + self.game.screen.height / 2
        sea = level_of(self.game, self.run.result.level_id).scenery.sea
        state = level_state(self.run, self._time_scale, self._ship_def.max_health)
        js_set(state, "sky", sky_state(self.view, sea, middle))
        return state

    def readability(self, bright_share: float) -> Any:
        """How readable the frame is (P14-R08): `bright_share` is the share of brightest pixels."""
        scene = self.view.scene
        playfield = self.view.playfield
        return probe_readability(scene, playfield.root, self.run, self._in_view(), bright_share)

    def attach(self) -> None:
        """Shows the level's HUD (and the debug tile) in the page: when it starts, not while it is
        built ahead on the level select screen (P13-R03).
        """
        if self._attached:
            return
        self._attached = True
        overlays = self._overlays()

        def on_bomb() -> None:
            self._controls.bomb()

        hud, stats = create_level_overlays(overlays, self._ship_def.name, self.game.texts, on_bomb)
        self._hud = hud
        self._stats = stats
        if self._hud is not None:
            high_score = self._options.high_score
            high_score = high_score if high_score is not None else 0
            self._hud.update(
                hud_frame(self.run, self._ship_def.max_health, self.game.texts, high_score)
            )

    def _overlays(self) -> LevelOverlaysOptions:
        options = self._options
        return LevelOverlaysOptions(
            options.doc, options.debug, options.stats_parent, options.hud_parent
        )

    def _toggle_stats(self) -> None:
        """Flips the debug tile's choice (D-212), for this level and the next ones. The tile itself
        follows only once the level is in the page: `attach` shows it as chosen."""
        shown = STATS_SHOWN.toggle(bool(self._options.debug))
        if not self._attached:
            return
        if shown and self._stats is None:
            self._stats = create_stats(self._overlays())
        elif not shown and self._stats is not None:
            self._stats.root.remove()
            self._stats = None

    def prepare(self, compile_now: bool) -> None:
        """Gets the level ready to play smoothly (P13-R04): with `compile_now`, the shaders of
        everything in the scene compiled before play starts, and those of each enemy model built
        ahead of its first appearance (one per frame, see `frame`).
        """
        self._compile_shaders = compile_now
        if compile_now:
            compile_shaders(self.view.scene.meshes)

    def warm_shots(self, on: bool) -> None:
        """Shows (or hides) one enemy bullet of each colour while the level loads (P13-R04)."""
        self._shots.warm(on)

    def build_enemies(self, compile_now: bool) -> bool:
        """Builds one more enemy model (of the kinds not built yet), and compiles its shaders with
        `compile_now` (P13-R04). Called while the level loads, one model a frame, so no model is
        built in play. True once every kind has one.
        """
        built = self.view.playfield.run(self._enemies.prepare_next)
        if compile_now:
            compile_shaders(built)
        return len(built) == 0

    def dispose(self) -> None:
        self._enemies.dispose()
        self._shots.dispose()
        self._bonuses.dispose()
        if self._bombs is not None:
            self._bombs.dispose()
        if self._stats is not None:
            self._stats.root.remove()
        if self._hud is not None:
            self._hud.dispose()
        self.view.scene.dispose()
