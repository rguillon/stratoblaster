"""Wires the layers together (ENG-11): loads the menu scenes
behind a loading screen, then runs the menus (P01-R01..R15) and the levels (P06) in
Babylon's render loop with a fixed-step clock (ENG-100).

`start_app(engine, game, options)` is what `main.py` calls. `AppOptions` is a plain class: every
argument is passed by position (Transcrypt has no keyword arguments); the optional ones are None
when omitted. The version and commit are the `version` and `commit` options (main.py supplies them).
"""

from org.transcrypt.stubs.browser import __pragma__, window

from app.game_audio import GameAudio
from app.game_session import GameSession, GameSessionOptions, SessionAudio, SessionScores
from app.menu_controller import MenuController, MenuControllerDeps
from app.menu_scenes import prepare_menu_scenes, render_menu_scenes
from app.page_audio import (
    AudioOptions,
    PageOptions,
    PageVisibility,
    Ticker,
    create_app_audio,
    listen_to_page,
)
from app.perf_monitor import PerfMonitor, PerfOverlayOptions, perf_overlay
from assets.loading_tasks import run_loading_tasks
from config.engine import ENGINE_CONFIG
from config.game_play import GAME_PLAY_CONFIG
from config.menu import MENU_CONFIG
from config.menu_input import MENU_INPUT_CONFIG
from core.loop.fixed_step_clock import FixedStepClock
from input.gamepad_menu_input import GamepadMenuInput
from input.keyboard_menu_input import KeyboardMenuInput
from input.menu_input import MenuInput
from ui.menu_overlay import MenuOverlay, MenuOverlayOptions

__pragma__("skip")
from typing import Any  # noqa: E402

from app.game_play import GamePlay  # noqa: E402
from app.menu_state import MenuState  # noqa: E402
from input.menu_action import MenuCommand  # noqa: E402

__pragma__("noskip")


class AppOptions(PageOptions):
    """Browser pieces the app runs on, with the page options
    (`PageOptions`) it extends."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        environment: bool,
        doc: Any,
        overlay: Any,
        storage: Any,
        yield_to_browser: Any,
        render_loop: bool,
        version: str,
        commit: str,
        keyboard_target: Any | None = None,
        debug: Any | None = None,
        stats_parent: Any | None = None,
        now: Any | None = None,
        perf_parent: Any | None = None,
        stepped_loading: Any | None = None,
        precompile_shaders: Any | None = None,
        background_loading: Any | None = None,
        prebuild_levels: Any | None = None,
        audio: AudioOptions | None = None,
        gamepads: Any | None = None,
        gesture_target: Any | None = None,
        visibility: PageVisibility | None = None,
        every: Any | None = None,
    ) -> None:
        PageOptions.__init__(self, audio, gamepads, gesture_target, visibility, every)
        # Image-based lighting and glow. Needs a real WebGL engine.
        self.environment = environment
        self.doc = doc
        # Element the menu overlay renders into.
        self.overlay = overlay
        # Persistent storage (cookies in the browser).
        self.storage = storage
        # Where keyboard events are listened to. No keyboard when None.
        self.keyboard_target = keyboard_target
        # Lets the browser paint between loading steps; returns a promise.
        self.yield_to_browser = yield_to_browser
        # Starts Babylon's render loop. Unit tests leave it off; e2e builds too (ENG-52).
        self.render_loop = render_loop
        # The app's version and short commit hash, shown on the title screen (ENG-83).
        self.version = version
        self.commit = commit
        # Debug options (P06-R09); None when omitted.
        self.debug = debug
        # Where the debug FPS / polygons tile goes.
        self.stats_parent = stats_parent
        # The clock frames and level starts are timed with, in ms (P13-R01); None: the browser's.
        self.now = now
        # Where the debug perf overlay goes (P13-R01, F3; dev and e2e builds). None when omitted.
        self.perf_parent = perf_parent
        # Loads the levels in steps, one per frame, behind a loading screen (P13-R03).
        self.stepped_loading = stepped_loading
        # Compiles a level's shaders while it loads (P13-R04); on when None.
        self.precompile_shaders = precompile_shaders
        # Prepares the level highlighted on the level select screen in a worker (P13-R03).
        self.background_loading = background_loading
        # Builds the level highlighted on the level select screen ahead (P13-R03).
        self.prebuild_levels = prebuild_levels


class RunningApp:
    """Handle on a running app, used by `main.py`, the test API and tests. `scenes()` and `game()`
    are methods."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        clock: FixedStepClock,
        menu: MenuController,
        loaded: Any,
        loading_progress: list[float],
        scenes_box: list[Any],
        session: GameSession,
        controls: Any,
        audio: GameAudio,
        perf: PerfMonitor,
        frames: "FrameControls",
        dispose: Any,
    ) -> None:
        self.clock = clock
        self.menu = menu
        # Resolves when loading is over and the title screen is shown.
        self.loaded = loaded
        # Every progress value the loading screen showed, in order.
        self.loading_progress = loading_progress
        self._scenes_box = scenes_box
        self._session = session
        self.controls = controls
        # The game's music and sounds (P12-R05).
        self.audio = audio
        # Frame and level loading times (P13-R01).
        self.perf = perf
        self._frames = frames
        self._dispose = dispose

    def scenes(self) -> Any:
        """The menu scenes, once loaded (None before)."""
        return self._scenes_box[0]

    def game(self) -> GamePlay | None:
        """The level being played, on the game screen."""
        return self._session.play

    def command(self, command: MenuCommand) -> None:
        """Sends a menu command, as any input device would."""
        self.menu.command(command)

    def tick(self, dt_seconds: float) -> None:
        """Runs one frame: input, menus, animations, rendering."""
        self._frames.tick(dt_seconds)

    def step(self, frames: int, render: bool) -> None:
        """Runs `frames` frames of one simulation step each, then renders once (unless `render`
        is False): the e2e tests' clock (ENG-52). Both arguments are passed (no defaults in
        Transcrypt closures).
        """
        self._frames.step(frames, render)

    def dispose(self) -> None:
        self._dispose()


class FrameControls:
    """Runs frames: a frame of real time (`tick`, the render loop, unit tests), and whole steps
    (`step`, the e2e tests). Each step is timed as a frame; the last one with the drawing
    (P13-R01)."""

    def __init__(self, clock: FixedStepClock, ticker: Ticker, perf: PerfMonitor) -> None:
        self._clock = clock
        self._ticker = ticker
        self._perf = perf

    def tick(self, dt_seconds: float) -> None:
        self._perf.frame_started()
        self._ticker.simulate(dt_seconds)
        self._ticker.render()
        self._perf.frame_ended()

    def step(self, frames: int, render: bool) -> None:
        for i in range(frames):
            self._perf.frame_started()
            self._ticker.simulate(self._clock.step_seconds)
            if render and i == frames - 1:
                self._ticker.render()
            self._perf.frame_ended()
        if render and frames == 0:
            self._ticker.render()


class InputHandle:
    """The menu input and the function that stops listening to the keyboard."""

    def __init__(self, input_: MenuInput, stop: Any) -> None:
        self.input = input_
        self.stop = stop


class SceneLoad:
    """The menu scenes' loading: the promise and the progress every step showed."""

    def __init__(self, loaded: Any, progress: list[float]) -> None:
        self.loaded = loaded
        self.progress = progress


class MenuHandle:
    """The menu controller and the overlay it renders into."""

    def __init__(self, menu: MenuController, overlay: MenuOverlay) -> None:
        self.menu = menu
        self.overlay = overlay


class TouchHandlers:
    """The on-screen touch controls: fire button and drag (`GameTouchHandlers`)."""

    def __init__(self, controls: Any) -> None:
        self._controls = controls

    def fire(self, held: bool) -> None:
        self._controls.set_touch_fire(held)

    def drag(self, dx: float, dy: float) -> None:
        self._controls.drag(dx, dy)


def _nothing() -> None:
    return None


def _index_of(items: list[str], item: str | None) -> int:
    """The index of `item` in `items`, or -1 (as JavaScript's `indexOf`)."""
    for i in range(len(items)):
        if items[i] == item:
            return i
    return -1


def performance_now() -> float:
    """The browser's clock, in milliseconds (P13-R01)."""
    now: float = window.performance.now()
    return now


def create_input(options: AppOptions) -> InputHandle:
    """The keyboard, and the gamepads when there are some (P12-R03)."""
    keyboard = KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG)
    target = options.keyboard_target
    stop = keyboard.listen(target) if target is not None else _nothing
    sources: list[Any] = [keyboard]
    if options.gamepads is not None:
        # The config's stick type is wider than the input's protocol (typing only).
        bindings: Any = MENU_INPUT_CONFIG
        sources.append(GamepadMenuInput(options.gamepads, bindings))
    return InputHandle(MenuInput(sources), stop)


def sync_scenes(scenes: Any, state: MenuState, ship_ids: list[str]) -> None:
    if scenes is None:
        return
    # The backdrop handle is a JavaScript object: its callbacks are read by their JS names.
    scenes.backdrop["showScreen"](state.screen)
    scenes.stage.select(max(0, _index_of(ship_ids, state.highlighted_ship_id)))


def load_menu_scenes(
    prepared: Any, menu: MenuController, options: AppOptions, on_loaded: Any
) -> SceneLoad:
    """Runs the menu scenes' loading tasks, then `on_loaded` with the scenes."""
    progress: list[float] = []

    def on_progress(value: float) -> None:
        progress.append(value)
        menu.set_progress(value)

    async def run() -> None:
        await run_loading_tasks(prepared.tasks, on_progress, options.yield_to_browser)
        scenes = prepared.result()
        menu.finish_loading()
        on_loaded(scenes)

    return SceneLoad(run(), progress)


def create_menu(
    game: Any,
    options: AppOptions,
    input_: InputHandle,
    controls: Any,
    audio: GameAudio,
    on_change: Any,
) -> MenuHandle:
    """The menu controller and its overlay (P01-R01): the overlay's commands go to the controller,
    and the controller's changes and feedback to the scenes and the audio."""

    def on_command(command: Any) -> None:
        menu.command(command)

    overlay = MenuOverlay(
        options.doc,
        options.overlay,
        on_command,
        MenuOverlayOptions(MENU_CONFIG.transition_seconds),
        TouchHandlers(controls),
    )

    def on_feedback(command: MenuCommand, feedback: Any) -> None:
        audio.menu_feedback(command, feedback, menu.flow.state.volumes)

    deps = MenuControllerDeps(
        overlay,
        input_.input,
        options.storage,
        MENU_CONFIG.transition_seconds,
        GAME_PLAY_CONFIG.complete_delay,
        100 / MENU_CONFIG.ship_select.camera.framing_margin,
        options.version,
        options.commit,
        on_change,
        on_feedback,
    )
    menu = MenuController(game, deps)
    return MenuHandle(menu, overlay)


def frame_ticker(
    clock: FixedStepClock,
    menu: MenuController,
    get_scenes: Any,
    session: GameSession,
    perf: PerfMonitor,
) -> Ticker:
    """One frame, split in two: the simulation (clock, menu input and state, then the level being
    played or the menu scenes' animations), then the drawing of what it left."""

    def simulate(dt_seconds: float) -> None:
        dt = min(max(0, dt_seconds), MENU_CONFIG.max_frame_seconds)
        clock.advance(dt)
        menu.tick(dt)
        play = session.play
        if play is not None:
            # Paused (P12-R01): nothing in the level advances; its last frame is drawn again.
            if not session.paused:
                play.frame(dt)
            # The gamepad in use was disconnected (P12-R03).
            if session.controls.take_disconnect():
                menu.pause()
            return
        # P13-R03: a step of the level being loaded, if any, each frame.
        session.load_step(dt)
        loaded = get_scenes()
        if loaded is not None:
            loaded.backdrop["update"](dt)
            loaded.stage.update(dt)

    def render() -> None:
        play = session.play
        if play is not None:
            play.view.scene.render()
            # The level's first frame is drawn: it is loaded; its first second is not counted.
            if perf.loading:
                perf.load_finished(ENGINE_CONFIG.simulation_hz)
            return
        loaded = get_scenes()
        if loaded is not None:
            render_menu_scenes(loaded, menu.flow.state.screen)

    return Ticker(simulate, render)


def dispose_scenes(scenes: Any) -> None:
    """Disposes the menu scenes, once loaded."""
    if scenes is None:
        return
    scenes.backdrop_scene.dispose()
    scenes.ship_scene.dispose()


def run_loop(engine: Any, tick: Any) -> None:
    """Runs `tick` on every frame of Babylon's render loop, with the frame time in seconds."""

    def frame() -> None:
        tick(engine.getDeltaTime() / 1000)

    engine.runRenderLoop(frame)


def start_debug_level(menu: MenuController, debug: Any | None, ship_ids: list[str]) -> None:
    """With debug options (P06-R09), starts their level straight away once loading is over."""
    if debug is None:
        return
    ship = debug.ship_id
    if ship is None:
        ship = ship_ids[0] if len(ship_ids) > 0 else ""
    menu.play_direct(ship, debug.level_id)


def session_options(options: AppOptions, on_load_start: Any) -> GameSessionOptions:
    """The game session's options: the app's, with `on_load_start` (P13-R01)."""
    # None passes through: the session applies its own default (typed Any here).
    stepped: Any = options.stepped_loading
    precompile: Any = options.precompile_shaders
    background: Any = options.background_loading
    prebuild: Any = options.prebuild_levels
    return GameSessionOptions(
        options.environment,
        options.doc,
        options.debug,
        options.stats_parent,
        options.overlay,
        options.keyboard_target,
        options.gamepads,
        options.storage,
        on_load_start,
        stepped,
        precompile,
        background,
        prebuild,
    )


def create_session(
    engine: Any,
    game: Any,
    options: AppOptions,
    get_menu: Any,
    audio: GameAudio,
    perf: PerfMonitor,
) -> GameSession:
    """The game session: its levels' results go to the menus, and its scores to the high score
    (P11-R03). `get_menu` is read when they come, once the menu exists."""

    def on_load_start() -> None:
        perf.load_started()

    def on_complete(play: GamePlay) -> None:
        audio.level_ended(play.run.result)
        get_menu().complete_level(play.run.result)

    def high_score() -> float:
        score: float = get_menu().high_score
        return score

    def record(score: float) -> None:
        get_menu().record_score(score)

    def started(level_id: str) -> None:
        audio.level_started(level_id)

    def step(run: Any) -> None:
        audio.level_step(run)

    return GameSession(
        engine,
        game,
        session_options(options, on_load_start),
        on_complete,
        SessionScores(high_score, record),
        SessionAudio(started, step),
    )


def start_app(engine: Any, game: Any, options: AppOptions) -> RunningApp:
    """Starts the app (see the module doc). Returns the handle `main.py` and the test API use."""
    clock = FixedStepClock(ENGINE_CONFIG.simulation_hz, int(ENGINE_CONFIG.max_steps_per_frame))
    ship_ids = [ship.id for ship in game.player_ships.ships]
    input_handle = create_input(options)
    # The menu scenes, once loaded: a one-element list, read and written by the closures.
    scenes_box: list[Any] = [None]
    app_audio = create_app_audio(game, options)
    audio: GameAudio = app_audio.audio
    perf = PerfMonitor(
        ENGINE_CONFIG.long_frame_ms, options.now if options.now is not None else performance_now
    )

    def get_menu() -> MenuController:
        return menu

    session = create_session(engine, game, options, get_menu, audio, perf)
    controls = session.controls

    def on_change(state: MenuState) -> None:
        sync_scenes(scenes_box[0], state, ship_ids)
        session.sync(state)
        audio.menu_changed(state)

    menu_handle = create_menu(game, options, input_handle, controls, audio, on_change)
    menu = menu_handle.menu
    overlay = menu_handle.overlay
    stop_page = listen_to_page(options, menu, audio)
    prepared = prepare_menu_scenes(engine, game, options.environment)

    def on_loaded(loaded: Any) -> None:
        scenes_box[0] = loaded
        sync_scenes(loaded, menu.flow.state, ship_ids)
        start_debug_level(menu, options.debug, ship_ids)

    loading = load_menu_scenes(prepared, menu, options, on_loaded)

    def get_scenes() -> Any:
        return scenes_box[0]

    overlay_perf = perf_overlay(
        PerfOverlayOptions(options.doc, options.perf_parent, options.keyboard_target), perf
    )
    ticker = overlay_perf.wrap(
        app_audio.with_audio(frame_ticker(clock, menu, get_scenes, session, perf))
    )
    frames = FrameControls(clock, ticker, perf)
    if options.render_loop:
        run_loop(engine, frames.tick)

    def dispose() -> None:
        engine.stopRenderLoop()
        input_handle.stop()
        stop_page()
        session.dispose()
        overlay.dispose()
        overlay_perf.dispose()
        dispose_scenes(scenes_box[0])

    return RunningApp(
        clock,
        menu,
        loading.loaded,
        loading.progress,
        scenes_box,
        session,
        controls,
        audio,
        perf,
        frames,
        dispose,
    )
