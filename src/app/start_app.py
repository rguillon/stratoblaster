"""Wires the layers together (ENG-11): loads the menu scenes
behind a loading screen, then runs the menus (P01-R01..R15) and the levels (P06) in
Babylon's render loop with a fixed-step clock (ENG-100).

`start_app(engine, game, options)` is what `main.py` calls. `AppOptions` is a plain class: every
argument is passed by position (Transcrypt has no keyword arguments); the optional ones are None
when omitted. The version and commit are the `version` and `commit` options (main.py supplies them).

The frames, the menus, the scenes and the loading it drives live in `start_app_runtime.py`.
"""

from org.transcrypt.stubs.browser import __pragma__

from app.game_audio import GameAudio
from app.game_play import GamePlay
from app.game_session import GameSession
from app.menu_controller import MenuController
from app.menu_scenes import prepare_menu_scenes
from app.menu_state import MenuState
from app.page_audio import create_app_audio, listen_to_page
from app.perf_monitor import PerfMonitor, PerfOverlayOptions, perf_overlay
from app.start_app_runtime import (
    AppOptions,
    FrameControls,
    create_dev,
    create_input,
    create_menu,
    create_session,
    dispose_scenes,
    frame_ticker,
    load_menu_scenes,
    performance_now,
    run_loop,
    start_debug_level,
    sync_scenes,
)
from config.engine import ENGINE_CONFIG
from core.loop.fixed_step_clock import FixedStepClock
from input.menu_action import MenuCommand

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


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
        frames: FrameControls,
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
    dev = create_dev(engine, game, options)

    def on_change(state: MenuState) -> None:
        sync_scenes(scenes_box[0], state, ship_ids)
        session.sync(state)
        if dev is not None:
            dev[0].sync(state)
        audio.menu_changed(state)

    dev_menu = [dev[1], dev[0].wheel, dev[0].turn, dev[2]] if dev is not None else None
    menu_handle = create_menu(game, options, input_handle, controls, audio, on_change, dev_menu)
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
        app_audio.with_audio(
            frame_ticker(
                clock, menu, get_scenes, session, perf, dev[0] if dev is not None else None
            )
        )
    )
    frames = FrameControls(clock, ticker, perf)
    if options.render_loop:
        run_loop(engine, frames.tick)

    def dispose() -> None:
        engine.stopRenderLoop()
        input_handle.stop()
        stop_page()
        session.dispose()
        if dev is not None:
            dev[0].dispose()
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
