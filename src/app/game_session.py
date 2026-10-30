"""The game session of the app: it starts the level chosen on
the game screen, and ends it when the menu flow leaves it (P06-R02), or starts it again from its
checkpoint (P07-R08). The debug options' start time and boss apply to the first level played only.

Levels load in steps, one per frame, behind a loading screen (P13-R02, R03), and the level the
level select highlight rests on is built ahead (P13-R03).
"""

from org.transcrypt.stubs.browser import __pragma__

from app.game_play import GameChoice, GamePlay, GamePlayOptions
from app.level_prepare import LevelPrefetcher, prepare_level, roads_ready, textures_ready
from app.listen_controls import listen_controls
from app.saved_supplies import load_saved_supplies, save_supplies
from app.saved_weapons import load_saved_weapons, save_weapons
from config.game_controls import GAME_CONTROLS_CONFIG
from input.game_controls import GameControls
from render.outline import outlines_ready
from render.scenery.atmosphere_of import AtmosphereOptions
from render.scenery.background_loader import start_background_loader
from ui.level_loading import LevelLoadingScreen

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Most frames a level's loading waits for its shaders to compile in parallel (P13-R03).
COMPILE_FRAMES = 60

# Seconds the level select highlight rests on a level before it is built ahead (P13-R03): longer
# than a move across the grid, so passing over a level does not build it.
BUILD_AHEAD_AFTER = 0.6


class GameDebugOptions:
    """Debug options from the URL (P06-R09), e.g. `?level=1-3&t=120&ship=heavy`: start a level
    straight away, at a given time, with the playback keys and the FPS / polygons tile.

    `level_id`; `time` (seconds into the level to start at); `ship_id` (None: the game's first
    ship); `boss` (the rank of the mini or final boss to start at instead, P07-R09, or None);
    `weather` (False: no weather, P08-R12; None: the level's own); `time_of_day` (the level at that
    time of day, P08-R12, or None); `tiles` (True: the grid of tiles over the districts, P15-R10).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        level_id: str,
        time: float,
        ship_id: str | None,
        boss: str | None,
        weather: bool | None = None,
        time_of_day: str | None = None,
        tiles: bool | None = None,
    ) -> None:
        self.level_id = level_id
        self.time = time
        self.ship_id = ship_id
        self.boss = boss
        self.weather = weather
        self.time_of_day = time_of_day
        self.tiles = tiles


def atmosphere_of(debug: GameDebugOptions | None) -> AtmosphereOptions:
    """The debug choices on the level's look (P08-R12): none without debug options."""
    if debug is None:
        return AtmosphereOptions(None, None, None)
    weather = False if debug.weather is False else None
    tile_grid = True if debug.tiles else None
    return AtmosphereOptions(debug.time_of_day, weather, tile_grid)


class GameSessionOptions:
    """What a `GameSession` needs from the app's options, positional. `None` stands for an
    omitted option: `debug` (GameDebugOptions), `stats_parent` (the debug tile's), `overlay` (where
    the in-game HUD and the loading screen go), `keyboard_target` (no keyboard when None),
    `gamepads`, `storage` (where the weapons and supplies are kept; not kept when None),
    `on_load_start` (P13-R01), `stepped_loading` (P13-R02, R03), `precompile_shaders` (P13-R04;
    None: on), `background_loading` (P13-R03: the worker), `prebuild_levels` (P13-R03).
    """

    def __init__(  # noqa: PLR0913, PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        environment: bool,
        doc: Any,
        debug: GameDebugOptions | None = None,
        stats_parent: Any = None,
        overlay: Any = None,
        keyboard_target: Any = None,
        gamepads: Any = None,
        storage: Any = None,
        on_load_start: Any = None,
        stepped_loading: bool = False,
        precompile_shaders: bool | None = None,
        background_loading: bool = False,
        prebuild_levels: bool = False,
    ) -> None:
        self.environment = environment
        self.doc = doc
        self.debug = debug
        self.stats_parent = stats_parent
        self.overlay = overlay
        self.keyboard_target = keyboard_target
        self.gamepads = gamepads
        self.storage = storage
        self.on_load_start = on_load_start
        self.stepped_loading = stepped_loading
        self.precompile_shaders = precompile_shaders
        self.background_loading = background_loading
        self.prebuild_levels = prebuild_levels


class SessionScores:
    """Where a `GameSession` reads the high score from and records its scores (P11-R03):
    `high_score()` (the saved one, for the HUD) and `record(score)` (a level attempt ended, with
    `score`: completed, lost or left).
    """

    def __init__(self, high_score: Any, record: Any) -> None:
        self.high_score = high_score
        self.record = record


class SessionAudio:
    """What the audio hears of the levels played (P12-R07, P12-R09): `started(level_id)` (a level
    starts, or starts again from its checkpoint) and `step(run)` (a step of the level was run).
    """

    def __init__(self, started: Any, step: Any) -> None:
        self.started = started
        self.step = step


class LevelLoad:
    """A level being loaded in steps (P13-R03). `state` is the flow's state the level was confirmed
    in (None while it is built ahead); `steps` return False when they are not over (they run again
    on the next frame); `tries` counts the frames the step being run has taken so far.
    """

    def __init__(self, level_id: str, ship_id: str, state: Any) -> None:
        self.level_id = level_id
        self.ship_id = ship_id
        self.state = state
        self.steps: list[Any] = []
        self.tries = 0
        self.done = 0
        self.play: Any = None
        self.screen: Any = None


def highlighted_level(state: Any) -> str | None:
    """The cell highlighted on the level select screen, if it shows (P13-R03: prefetched)."""
    if state.screen == "level-select":
        selected: str | None = state.selected_id
        return selected
    return None


def ship_of(state: Any) -> str:
    """The ship the flow's levels are flown with: the one chosen, or else the one highlighted."""
    if state.chosen_ship_id is not None:
        chosen: str = state.chosen_ship_id
        return chosen
    highlighted: str = state.highlighted_ship_id
    return highlighted


class GameSession:
    """Starts the level chosen on the game screen, and ends it when the flow leaves it (P06-R02),
    or starts it again from its checkpoint (P07-R08). The debug options' start time and boss apply
    to the first level played only.
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        game: Any,
        options: GameSessionOptions,
        on_complete: Any,
        scores: SessionScores | None = None,
        audio: SessionAudio | None = None,
    ) -> None:
        self.engine = engine
        self.game = game
        self.options = options
        self._on_complete = on_complete
        self._scores = scores
        self._audio = audio
        self.play: GamePlay | None = None
        # Whether the level being played is paused (P12-R01): it is kept, but not advanced.
        self.paused = False
        # The player's in-game controls, fed by the keyboard target and the gamepads.
        # The config's bindings match `GameControlBindings` at run time (typed Any here).
        bindings: Any = GAME_CONTROLS_CONFIG
        self.controls = GameControls(bindings, options.gamepads)
        debug = options.debug
        self._start_time = debug.time if debug is not None else 0.0
        self._start_boss = debug.boss if debug is not None else None
        # The menu flow's attempt the level being played was started for.
        self._attempt = -1
        self._load: LevelLoad | None = None
        # The level highlighted on the level select screen, built ahead (P13-R03).
        self._ahead: LevelLoad | None = None
        self._loader = start_background_loader() if options.background_loading else None
        self._prefetcher = LevelPrefetcher(game, self._loader)
        # The level highlighted on the level select screen, if it shows.
        self._highlighted: str | None = None
        # The ship the level highlighted on the level select screen would be flown with.
        self._ahead_ship: str | None = None

        def current_play() -> Any:
            # No debug keys while paused (P12-R01: nothing in the level changes).
            return None if self.paused else self.play

        self._stop_listening = listen_controls(options.keyboard_target, self.controls, current_play)

    def dispose(self) -> None:
        """Ends the level being played and stops listening to the keys."""
        self.end()
        self._drop_ahead()
        self._stop_listening()
        if self._loader is not None:
            self._loader.stop()

    def sync(self, state: Any) -> None:
        self._highlighted = highlighted_level(state)
        self._ahead_ship = ship_of(state)
        in_level = state.screen == "game" or state.paused
        level_id = state.chosen_level_id if in_level else None
        # Presses made while paused (e.g. a bomb key) do not carry into the level (P12-R01).
        if state.paused != self.paused:
            self.controls.clear()
        self.paused = state.paused
        if level_id is None:
            self.end()
            return
        # Continue from a checkpoint (P07-R08): the level starts again.
        if self.play is not None and state.attempt != self._attempt:
            self.end()
        if self.play is not None or self._load is not None or state.level_result:
            return
        self._start(state, level_id)

    @property
    def loading(self) -> bool:
        """Whether a level is being loaded (P13-R03)."""
        return self._load is not None

    def load_step(self, dt: float = 0) -> None:
        """Runs the next step of the level being loaded, if any (P13-R03), one per frame of `dt`
        seconds, and prefetches the level highlighted on the level select screen once it rests
        there.
        """
        self._prefetcher.update(dt, self._highlighted)
        load = self._load
        if load is None:
            self._build_ahead()
            return
        if self._run_step(load):
            self._load = None

    def _run_step(self, load: LevelLoad) -> bool:
        """Runs the next step of `load`; true once its last step has run."""
        load.tries += 1
        if load.steps[load.done]() is False:
            return False
        load.done += 1
        load.tries = 0
        if load.screen is not None:
            load.screen.show(load.done / len(load.steps))
        if load.done < len(load.steps):
            return False
        if load.screen is not None:
            load.screen.dispose()
        return True

    def _build_ahead(self) -> None:
        """Builds the level the level select highlight rests on, one step per frame (P13-R03),
        short of starting it; drops the one built for another level or ship.
        """
        if not self.options.prebuild_levels or not self.options.stepped_loading:
            return
        # Off the level select screen, the level built ahead is dropped.
        if self._highlighted is None:
            self._drop_ahead()
        level_id = self._prefetcher.rested_on(BUILD_AHEAD_AFTER)
        ship_id = self._ahead_ship
        if level_id is None or ship_id is None:
            return
        if not self._is_ahead(level_id, ship_id):
            self._drop_ahead()
        if self._ahead is None:
            self._ahead = self._new_load(level_id, ship_id, None)
        ahead = self._ahead
        # Its last step (starting it) waits for the confirmation.
        if ahead.done < len(ahead.steps) - 1:
            self._run_step(ahead)

    def _is_ahead(self, level_id: str, ship_id: str) -> bool:
        """Whether the level built ahead (if any) is `level_id` flown by `ship_id`."""
        ahead = self._ahead
        return ahead is not None and ahead.level_id == level_id and ahead.ship_id == ship_id

    def _drop_ahead(self) -> None:
        if self._ahead is not None and self._ahead.play is not None:
            self._ahead.play.dispose()
        self._ahead = None

    def _start(self, state: Any, level_id: str) -> None:
        """Starts `level_id` for the flow's attempt (from its checkpoint when it has one): at once,
        or in steps (P13-R03): the level's ground, its scene, a first drawing that compiles its
        shaders.
        """
        if self.options.on_load_start is not None:
            self.options.on_load_start()
        self._prefetcher.start(level_id)
        load = self._take_ahead(state, level_id)
        if load is None:
            load = self._new_load(level_id, ship_of(state), state)
        load.state = state
        self._load = load
        if not self.options.stepped_loading:
            while self._load is load:
                self.load_step()
            return
        # Already built: it starts in this very frame; otherwise behind the loading screen.
        overlay = self.options.overlay
        if load.done >= len(load.steps) - 1:
            self.load_step()
        elif overlay is not None:
            load.screen = LevelLoadingScreen(self.options.doc, overlay, self.game.texts.loading)
            load.screen.show(load.done / len(load.steps))

    def _take_ahead(self, state: Any, level_id: str) -> LevelLoad | None:
        """The level built ahead on the level select screen, if it is the one confirmed."""
        usable = self._is_ahead(level_id, ship_of(state)) and not state.resume
        if not usable:
            self._drop_ahead()
        ahead = self._ahead
        self._ahead = None
        return ahead

    def _compile_wait(self, load: LevelLoad) -> bool:
        """Hidden by the loading screen (or the menus), the shaders compile (in parallel where
        WebGL can, over a few frames), then a first drawing finishes them.
        """
        scene = load.play.view.scene if load.play is not None else None
        if not self.options.stepped_loading or scene is None:
            return True
        if self.options.precompile_shaders is False:
            return True
        # `!= None` also catches the undefined of a missing WebGL capability.
        caps = scene.getEngine().getCaps()
        parallel = caps.parallelShaderCompile != None  # noqa: E711
        ready = scene.isReady(True) and outlines_ready(scene.meshes)
        if not ready and parallel and load.tries < COMPILE_FRAMES:
            return False
        scene.render()
        return True

    def _road_grid(self) -> bool:
        """Whether the tile grid is drawn (the debug option), so the roads are made with it."""
        debug = self.options.debug
        return debug is not None and debug.tiles is True

    def _roads_step(self, level_id: str, load: LevelLoad) -> bool:
        """The street surfaces of the first screens, made by the worker (P13-R03)."""
        return roads_ready(self.game, level_id, self._road_grid(), load.tries)

    def _enemies_step(self, load: LevelLoad) -> bool:
        """The enemy models, one a frame, here rather than in play (P13-R04)."""
        if not self.options.stepped_loading or load.play is None:
            return True
        precompile = self.options.precompile_shaders
        built: bool = load.play.build_enemies(True if precompile is None else precompile)
        return built

    def _new_load(self, level_id: str, ship_id: str, state: Any) -> LevelLoad:
        """The steps loading `level_id` flown by `ship_id` (P13-R03): the level's ground, its
        scene, a first drawing that compiles its shaders, then its start (for the flow's state when
        it is confirmed).
        """
        load = LevelLoad(level_id, ship_id, state)

        def ground() -> bool:
            # The ground, generated in the background (often already, while the level was chosen).
            return prepare_level(self.game, level_id)

        def build() -> None:
            load.play = self._new_play(load.state, level_id, ship_id)

        def prepare_play() -> None:
            if self.options.stepped_loading and load.play is not None:
                precompile = self.options.precompile_shaders
                load.play.prepare(True if precompile is None else precompile)
                # The bullets are shown while the shaders compile (see `start`).
                load.play.warm_shots(True)

        def start() -> None:
            if load.play is not None:
                load.play.warm_shots(False)
            if load.play and load.state:
                self._started(load.play, load.state, level_id)

        def textures() -> bool:
            # The textures the worker makes, before the scene (which would make them here).
            return textures_ready(self.game, level_id, self._loader, load.tries)

        load.steps = [
            ground,
            textures,
            lambda: self._roads_step(level_id, load),
            build,
            prepare_play,
            lambda: self._enemies_step(load),
            lambda: self._compile_wait(load),
            start,
        ]
        return load

    def _kept(self, state: Any) -> tuple[Any, Any]:
        """What the player kept from the levels completed before: the weapons (D-071), the lives and
        bombs (reviewer, 2026-10-28). A Continue, after a game over, starts again with the starting
        lives and bombs. Returns (weapons, supplies), None for those not kept.
        """
        storage = self.options.storage
        if storage is None:
            return None, None
        weapons = load_saved_weapons(storage, self.game.id)
        supplies = None
        if not (state is not None and state.resume):
            supplies = load_saved_supplies(storage, self.game.id)
        return weapons, supplies

    def _new_play(self, state: Any, level_id: str, ship_id: str) -> GamePlay:
        # Presses made outside the level (e.g. a bomb key on a menu) do not carry into it.
        self.controls.clear()
        weapons, supplies = self._kept(state)
        resume = state.resume if state is not None else None
        debug = self.options.debug
        high_score = self._scores.high_score() if self._scores is not None else 0
        audio = self._audio

        def on_complete(_result: Any) -> None:
            self._completed(play)

        def on_step(run: Any) -> None:
            if audio is not None:
                audio.step(run)

        play_options = GamePlayOptions(
            self.options.environment,
            debug is not None,
            self._start_time,
            self._start_boss,
            resume,
            None,
            weapons,
            supplies,
            high_score,
            atmosphere_of(debug),
            self.options.doc,
            self.options.stats_parent,
            self.options.overlay,
            on_complete,
            on_step,
        )
        choice = GameChoice(ship_id, level_id)
        play = GamePlay(self.engine, self.game, choice, self.controls, play_options)
        return play

    def _started(self, play: GamePlay, state: Any, level_id: str) -> None:
        """The level is loaded: it is played from now on."""
        # Presses made while it loaded do not carry into it either.
        self.controls.clear()
        play.attach()
        if self._audio is not None:
            self._audio.started(level_id)
        self._start_time = 0.0
        self._start_boss = None
        self._attempt = state.attempt
        self.play = play

    def _completed(self, play: GamePlay) -> None:
        """The level is over: a completed one keeps its weapons (D-071), lives and bombs (reviewer,
        2026-10-28) for the next.
        """
        storage = self.options.storage
        if storage is not None and play.run.phase == "complete":
            save_weapons(storage, self.game.id, play.run.arsenal.snapshot())
            supplies = play.run.supplies
            if supplies:
                save_supplies(storage, self.game.id, supplies)
        self._on_complete(play)

    def end(self) -> None:
        """Ends the level being played, or drops the one being loaded (its score counts)."""
        load = self._load
        if load is not None:
            if load.play is not None:
                load.play.dispose()
            if load.screen is not None:
                load.screen.dispose()
            self._load = None
        if self.play is not None and self._scores is not None:
            self._scores.record(self.play.run.score)
        if self.play is not None:
            self.play.dispose()
        self.play = None
        self.controls.clear()
