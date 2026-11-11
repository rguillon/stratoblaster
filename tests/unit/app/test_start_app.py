# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/start_app.py`."""
# p/start_app.py`: the frame split (simulate, then render), the input set-up, the scene sync and
# the debug start (DEV-PERF-01, DEV-API-08, DEV-OPT-01, UI-INPUT-01). The Babylon engine and the
# scenes are fakes here;
# the start-up itself is run by the browser.

import asyncio
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest
from helpers.gamepads import FakeGamepad

from app import start_app
from app.start_app import (
    AppOptions,
    FrameControls,
    MenuHandle,
    RunningApp,
    SceneLoad,
    TouchHandlers,
    _index_of,
    create_input,
    dispose_scenes,
    frame_ticker,
    run_loop,
    start_debug_level,
    sync_scenes,
)
from config.engine import ENGINE_CONFIG
from config.game_play import GAME_PLAY_CONFIG
from config.menu import MENU_CONFIG
from input.menu_input import MenuInput


class FakeClock:
    def __init__(self, step_seconds: float = 1 / 60) -> None:
        self.step_seconds = step_seconds
        self.advanced: list[float] = []

    def advance(self, dt: float) -> None:
        self.advanced.append(dt)


def test_dev_perf_01_a_frame_is_timed_and_simulated_then_drawn() -> None:
    order: list[str] = []
    ticker = SimpleNamespace(
        simulate=lambda dt: order.append(f"simulate {dt}"),
        render=lambda: order.append("render"),
    )
    perf = MagicMock()
    FrameControls(FakeClock(), ticker, perf).tick(0.02)
    assert order == ["simulate 0.02", "render"]
    perf.frame_started.assert_called_once()
    perf.frame_ended.assert_called_once()


def test_dev_api_08_whole_steps_draw_only_the_last_one_when_asked() -> None:
    """Also DEV-PERF-01 (each step timed as a frame) and ENG-58."""
    simulated: list[float] = []
    renders: list[str] = []
    ticker = SimpleNamespace(
        simulate=simulated.append,
        render=lambda: renders.append("render"),
    )
    perf = MagicMock()
    clock = FakeClock(step_seconds=0.1)
    FrameControls(clock, ticker, perf).step(3, render=True)
    assert simulated == [0.1, 0.1, 0.1]
    assert renders == ["render"]
    assert perf.frame_started.call_count == 3


def test_dev_api_08_steps_without_drawing_draw_nothing() -> None:
    renders: list[str] = []
    ticker = SimpleNamespace(simulate=lambda _dt: None, render=lambda: renders.append("r"))
    FrameControls(FakeClock(), ticker, MagicMock()).step(2, render=False)
    assert renders == []


def test_dev_api_08_zero_steps_with_drawing_still_draw_once() -> None:
    renders: list[str] = []
    ticker = SimpleNamespace(simulate=lambda _dt: None, render=lambda: renders.append("r"))
    FrameControls(FakeClock(), ticker, MagicMock()).step(0, render=True)
    assert renders == ["r"]


def test_perf_07_an_index_is_found_or_is_minus_one() -> None:
    assert _index_of(["alpha", "beta"], "beta") == 1
    assert _index_of(["alpha"], "gamma") == -1
    assert _index_of(["alpha"], None) == -1


def test_ui_input_01_the_keyboard_is_always_an_input_and_listens_to_its_target() -> None:
    target = MagicMock()
    handle = create_input(SimpleNamespace(keyboard_target=target, gamepads=None))
    assert isinstance(handle.input, MenuInput)
    assert target.addEventListener.call_count == 3
    handle.stop()
    assert target.removeEventListener.call_count == 3


def test_ui_input_01_gamepads_are_added_as_a_second_device_when_given() -> None:
    pad = FakeGamepad().press(0)
    handle = create_input(SimpleNamespace(keyboard_target=None, gamepads=lambda: [pad]))
    assert handle.input.update(0.0) == ["confirm"]
    handle.stop()


def test_ui_input_01_without_a_target_nothing_listens_to_the_keyboard() -> None:
    handle = create_input(SimpleNamespace(keyboard_target=None, gamepads=None))
    handle.stop()


def test_ui_title_09_the_menu_scenes_show_the_screen_and_the_highlighted_ship() -> None:
    """Also UI-SHIP-03 (the highlighted ship)."""
    backdrop = {"showScreen": MagicMock()}
    stage = MagicMock()
    scenes = SimpleNamespace(backdrop=backdrop, stage=stage)
    state = SimpleNamespace(screen="ship-select", highlighted_ship_id="beta")
    sync_scenes(scenes, state, ["alpha", "beta"])
    backdrop["showScreen"].assert_called_once_with("ship-select")
    stage.select.assert_called_once_with(1)


def test_ui_title_09_syncing_without_scenes_does_nothing() -> None:
    sync_scenes(None, SimpleNamespace(screen="title"), [])


def test_ui_title_09_disposing_the_menu_scenes_releases_both_and_none_is_fine() -> None:
    scenes = SimpleNamespace(backdrop_scene=MagicMock(), ship_scene=MagicMock())
    dispose_scenes(scenes)
    scenes.backdrop_scene.dispose.assert_called_once()
    scenes.ship_scene.dispose.assert_called_once()
    dispose_scenes(None)


def test_eng_100_the_render_loop_gets_each_frame_in_seconds() -> None:
    engine = MagicMock()
    engine.getDeltaTime.return_value = 16.0
    tick = MagicMock()
    run_loop(engine, tick)
    frame = engine.runRenderLoop.call_args.args[0]
    frame()
    tick.assert_called_once_with(0.016)


def test_dev_opt_01_a_debug_start_plays_its_level_once_loading_is_over() -> None:
    menu = MagicMock()
    debug = SimpleNamespace(level_id="2-1", ship_id="beta")
    start_debug_level(menu, debug, ["alpha", "beta"])
    menu.play_direct.assert_called_once_with("beta", "2-1")


def test_dev_opt_01_without_a_ship_the_first_one_is_used_and_no_debug_does_nothing() -> None:
    menu = MagicMock()
    start_debug_level(menu, SimpleNamespace(level_id="1-1", ship_id=None), ["alpha"])
    menu.play_direct.assert_called_once_with("alpha", "1-1")
    start_debug_level(menu, None, ["alpha"])
    assert menu.play_direct.call_count == 1
    start_debug_level(menu, SimpleNamespace(level_id="1-1", ship_id=None), [])
    menu.play_direct.assert_called_with("", "1-1")


def test_eng_100_a_frame_is_capped_at_the_longest_the_menus_accept() -> None:
    clock = FakeClock()
    menu = MagicMock()
    session = SimpleNamespace(
        play=None,
        load_step=MagicMock(),
        controls=MagicMock(),
    )
    backdrop_update = MagicMock()
    stage_update = MagicMock()
    scenes = SimpleNamespace(
        backdrop={"update": backdrop_update},
        stage=SimpleNamespace(update=stage_update),
    )
    ticker = frame_ticker(clock, menu, lambda: scenes, session, MagicMock())
    ticker.simulate(5.0)
    assert clock.advanced == [MENU_CONFIG.max_frame_seconds]
    menu.tick.assert_called_once_with(MENU_CONFIG.max_frame_seconds)
    session.load_step.assert_called_once_with(MENU_CONFIG.max_frame_seconds)
    backdrop_update.assert_called_once_with(MENU_CONFIG.max_frame_seconds)


def test_ui_pause_03_a_paused_level_does_not_advance_but_a_lost_pad_pauses_the_menu() -> None:
    """Also UI-PAUSE-11 (the lost gamepad)."""
    clock = FakeClock()
    menu = MagicMock()
    play = MagicMock()
    session = SimpleNamespace(
        play=play,
        paused=True,
        controls=MagicMock(take_disconnect=MagicMock(return_value=True)),
    )
    ticker = frame_ticker(clock, menu, lambda: None, session, MagicMock())
    ticker.simulate(0.02)
    play.frame.assert_not_called()
    menu.pause.assert_called_once()


def test_ui_pause_03_a_running_level_advances_each_frame() -> None:
    clock = FakeClock()
    menu = MagicMock()
    play = MagicMock()
    session = SimpleNamespace(
        play=play,
        paused=False,
        controls=MagicMock(take_disconnect=MagicMock(return_value=False)),
    )
    ticker = frame_ticker(clock, menu, lambda: None, session, MagicMock())
    ticker.simulate(0.02)
    play.frame.assert_called_once_with(0.02)
    menu.pause.assert_not_called()


def test_dev_perf_02_the_level_is_drawn_and_its_load_is_finished_at_its_first_frame() -> None:
    clock = FakeClock()
    menu = MagicMock()
    play = MagicMock()
    session = SimpleNamespace(play=play, paused=False, controls=MagicMock())
    perf = MagicMock(loading=True)
    ticker = frame_ticker(clock, menu, lambda: None, session, perf)
    ticker.render()
    play.view.scene.render.assert_called_once()
    perf.load_finished.assert_called_once_with(ENGINE_CONFIG.simulation_hz)


def test_ui_title_09_the_menu_scenes_are_drawn_for_the_menu_screen() -> None:
    clock = FakeClock()
    menu = MagicMock()
    menu.flow.state.screen = "title"
    session = SimpleNamespace(play=None, load_step=MagicMock(), controls=MagicMock())
    scenes = SimpleNamespace(backdrop={"update": MagicMock()}, stage=MagicMock())
    drawn: list = []
    original = start_app.render_menu_scenes
    start_app.render_menu_scenes = lambda loaded, screen: drawn.append((loaded, screen))
    try:
        frame_ticker(clock, menu, lambda: scenes, session, MagicMock()).render()
    finally:
        start_app.render_menu_scenes = original
    assert drawn == [(scenes, "title")]


# D-199: the dev viewers.


def test_d199_without_dev_there_are_no_dev_viewers() -> None:
    options = SimpleNamespace(dev=None)
    assert start_app.create_dev("engine", None, options, "audio") is None


def test_d199_with_dev_there_is_a_session_and_its_items_labels_and_groups(monkeypatch: Any) -> None:
    """DEV-MENU-02."""
    monkeypatch.setattr(start_app, "dev_catalog", lambda _game: {"ships": ["item"]})
    monkeypatch.setattr(start_app, "dev_labels", lambda _catalog: {"ships": ["Item"]})
    monkeypatch.setattr(start_app, "dev_groups", lambda _catalog: {"ships": [""]})
    options = SimpleNamespace(dev=True, environment=False, overlay="overlay", keyboard_target=None)
    session, labels, groups = start_app.create_dev("engine", "game", options, "audio")
    assert session._catalog == {"ships": ["item"]}
    assert session._audio == "audio"
    assert labels == {"ships": ["Item"]}
    assert groups == {"ships": [""]}


def test_d199_the_dev_viewer_moves_on_with_the_menus_and_is_drawn_instead_of_them() -> None:
    """DEV-MENU-05."""
    clock = FakeClock()
    menu = MagicMock()
    menu.flow.state.screen = "dev-viewer"
    session = SimpleNamespace(play=None, load_step=MagicMock(), controls=MagicMock())
    dev = MagicMock(active=True)
    dev.render.return_value = True
    drawn: list = []
    original = start_app.render_menu_scenes
    start_app.render_menu_scenes = lambda _loaded, screen: drawn.append(screen)
    try:
        ticker = frame_ticker(clock, menu, lambda: None, session, MagicMock(), dev)
        ticker.simulate(0.02)
        ticker.render()
        dev.frame.assert_called_once_with(0.02)
        assert drawn == []
        # Until its scene is built, the menu backdrop is drawn.
        dev.render.return_value = False
        start_app.draw_menus("scenes", "dev-viewer", dev)
        assert drawn == ["dev-viewer"]
    finally:
        start_app.render_menu_scenes = original


# The app's handles and options.


def test_eng_83_the_app_options_keep_the_browser_pieces_and_default_to_none() -> None:
    """Also DEV-OPT-01 (debug), DEV-PERF-01 (the clock), PERF-09, PERF-12, PERF-13, PERF-20."""
    options = AppOptions(True, "doc", "overlay", "storage", "yield", False, "1.2.0", "abc1234")
    assert (options.environment, options.doc, options.overlay) == (True, "doc", "overlay")
    assert (options.storage, options.yield_to_browser, options.render_loop) == (
        "storage",
        "yield",
        False,
    )
    assert (options.version, options.commit) == ("1.2.0", "abc1234")
    optional = [
        options.keyboard_target,
        options.debug,
        options.stats_parent,
        options.now,
        options.perf_parent,
        options.stepped_loading,
        options.precompile_shaders,
        options.background_loading,
        options.prebuild_levels,
        options.audio,
        options.gamepads,
        options.gesture_target,
        options.visibility,
        options.every,
        options.dev,
        options.fullscreen,
    ]
    assert optional == [None for _ in optional]


def test_eng_83_every_optional_piece_is_given_by_position() -> None:
    """ENG-151: no keyword arguments, so each option has its place."""
    given = [f"option-{i}" for i in range(16)]
    options = AppOptions(False, "doc", "overlay", "storage", "yield", True, "1", "c", *given)
    assert [
        options.keyboard_target,
        options.debug,
        options.stats_parent,
        options.now,
        options.perf_parent,
        options.stepped_loading,
        options.precompile_shaders,
        options.background_loading,
        options.prebuild_levels,
        options.audio,
        options.gamepads,
        options.gesture_target,
        options.visibility,
        options.every,
        options.dev,
        options.fullscreen,
    ] == given


def test_dev_api_08_the_running_app_hands_on_to_its_parts() -> None:
    """The handle `main.py` and the test API use (DEV-API-08: whole steps)."""
    menu = MagicMock()
    frames = MagicMock()
    dispose = MagicMock()
    scenes_box: list[Any] = [None]
    session = SimpleNamespace(play=None)
    app = RunningApp(
        "clock",
        menu,
        "loaded",
        [0.5],
        scenes_box,
        session,
        "controls",
        "audio",
        "perf",
        frames,
        dispose,
    )
    assert (app.clock, app.menu, app.loaded, app.loading_progress) == (
        "clock",
        menu,
        "loaded",
        [0.5],
    )
    assert (app.controls, app.audio, app.perf) == ("controls", "audio", "perf")
    assert app.scenes() is None
    scenes_box[0] = "scenes"
    assert app.scenes() == "scenes"
    assert app.game() is None
    session.play = "play"
    assert app.game() == "play"
    session.step_watchers = []
    app.watch_steps(print)
    assert session.step_watchers == [print]
    app.command("confirm")
    menu.command.assert_called_once_with("confirm")
    app.tick(0.02)
    frames.tick.assert_called_once_with(0.02)
    app.step(3, False)
    frames.step.assert_called_once_with(3, False)
    app.dispose()
    dispose.assert_called_once_with()


def test_the_touch_controls_fire_and_drag_the_ship() -> None:
    controls = MagicMock()
    touch = TouchHandlers(controls)
    touch.fire(True)
    touch.drag(3.0, -2.0)
    controls.set_touch_fire.assert_called_once_with(True)
    controls.drag.assert_called_once_with(3.0, -2.0)


def test_dev_perf_01_the_browser_clock_is_read_in_milliseconds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    window = SimpleNamespace(performance=SimpleNamespace(now=lambda: 1234.5))
    monkeypatch.setattr(start_app, "window", window)
    assert start_app.performance_now() == 1234.5


async def _yield() -> None:
    return None


def test_ui_load_03_the_menu_scenes_load_with_their_real_progress() -> None:
    """Also UI-LOAD-04 (the title follows by itself once loaded)."""
    menu = MagicMock()
    log: list[Any] = []
    menu.set_progress.side_effect = lambda value: log.append(value)
    menu.finish_loading.side_effect = lambda: log.append("finished")

    async def compile_shaders() -> None:
        log.append("compiled")

    prepared = SimpleNamespace(
        tasks=[lambda: log.append("built"), compile_shaders], result=lambda: "scenes"
    )
    loaded: list[Any] = []
    options = SimpleNamespace(yield_to_browser=_yield)
    load = start_app.load_menu_scenes(prepared, menu, options, loaded.append)
    assert isinstance(load, SceneLoad)
    asyncio.run(load.loaded)
    assert load.progress == [0, 0.5, 1]
    assert log == [0, "built", 0.5, "compiled", 1, "finished"]
    assert loaded == ["scenes"]


class MenuParts:
    """The overlay and controller `create_menu` makes, replaced by recorders."""

    def __init__(self) -> None:
        self.overlay_args: tuple[Any, ...] = ()
        self.controller_args: tuple[Any, ...] = ()
        self.menu = MagicMock()
        self.menu.flow.state.volumes = "volumes"

    def overlay(self, *args: Any) -> str:
        self.overlay_args = args
        return "overlay"

    def controller(self, *args: Any) -> MagicMock:
        self.controller_args = args
        return self.menu


@pytest.fixture
def menu_parts(monkeypatch: pytest.MonkeyPatch) -> MenuParts:
    parts = MenuParts()
    monkeypatch.setattr(start_app, "MenuOverlay", parts.overlay)
    monkeypatch.setattr(start_app, "MenuController", parts.controller)
    return parts


def _menu_options() -> AppOptions:
    return AppOptions(False, "doc", "overlay-root", "storage", _yield, False, "1.2.0", "abc1234")


def test_ui_flow_01_the_menu_is_wired_to_its_overlay_input_audio_and_scenes(
    menu_parts: MenuParts,
) -> None:
    """Also UI-SHIP-02 (the cards' width) and AUD-ENGINE-09 (the menu sounds)."""
    audio = MagicMock()
    controls = MagicMock()
    input_handle = start_app.InputHandle("menu-input", lambda: None)
    handle = start_app.create_menu(
        "game", _menu_options(), input_handle, controls, audio, "on-change"
    )
    assert isinstance(handle, MenuHandle)
    assert (handle.menu, handle.overlay) == (menu_parts.menu, "overlay")
    doc, root, on_command, overlay_options, touch, on_wheel, on_turn, on_hold = (
        menu_parts.overlay_args
    )
    assert (doc, root, on_wheel, on_turn, on_hold) == ("doc", "overlay-root", None, None, None)
    assert overlay_options.transition_seconds == MENU_CONFIG.transition_seconds
    touch.fire(True)
    controls.set_touch_fire.assert_called_once_with(True)
    game, deps = menu_parts.controller_args
    assert game == "game"
    assert (deps.display, deps.input, deps.storage) == ("overlay", "menu-input", "storage")
    assert deps.transition_seconds == MENU_CONFIG.transition_seconds
    assert deps.result_delay_seconds == GAME_PLAY_CONFIG.complete_delay
    assert deps.cards_width_percent == 100 / MENU_CONFIG.ship_select.camera.framing_margin
    assert (deps.version, deps.commit, deps.on_change) == ("1.2.0", "abc1234", "on-change")
    assert (deps.dev_labels, deps.dev_groups) == (None, None)
    # The overlay's commands go to the menu, its feedback to the audio with the volumes.
    on_command("back")
    menu_parts.menu.command.assert_called_once_with("back")
    deps.on_feedback("confirm", "moved")
    audio.menu_feedback.assert_called_once_with("confirm", "moved", "volumes")


def test_d199_the_dev_menu_gets_its_labels_groups_wheel_and_drag(menu_parts: MenuParts) -> None:
    """Also D-202 (the groups)."""
    input_handle = start_app.InputHandle("menu-input", lambda: None)
    dev = [{"ships": ["Alpha"]}, "on-wheel", "on-turn", {"ships": [""]}, "on-hold"]
    start_app.create_menu(
        "game", _menu_options(), input_handle, MagicMock(), MagicMock(), None, dev
    )
    assert menu_parts.overlay_args[5:] == ("on-wheel", "on-turn", "on-hold")
    deps = menu_parts.controller_args[1]
    assert (deps.dev_labels, deps.dev_groups) == ({"ships": ["Alpha"]}, {"ships": [""]})


def test_dev_perf_02_a_level_already_loaded_is_only_drawn() -> None:
    play = MagicMock()
    session = SimpleNamespace(play=play, paused=False, controls=MagicMock())
    perf = MagicMock(loading=False)
    frame_ticker(FakeClock(), MagicMock(), lambda: None, session, perf).render()
    play.view.scene.render.assert_called_once()
    perf.load_finished.assert_not_called()


def test_ui_title_09_nothing_is_drawn_before_the_menu_scenes_are_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also DEV-MENU-05: an inactive dev viewer leaves the menus drawn."""
    drawn: list[Any] = []
    monkeypatch.setattr(
        start_app, "render_menu_scenes", lambda _loaded, screen: drawn.append(screen)
    )
    start_app.draw_menus(None, "title", None)
    start_app.draw_menus(None, "title", MagicMock(active=False))
    assert drawn == []
    start_app.draw_menus("scenes", "title", MagicMock(active=False))
    assert drawn == ["title"]


def test_dev_perf_01_the_session_options_are_the_app_s_and_two_callbacks() -> None:
    """Also ENG-106 (the draw calls), PERF-09, PERF-12, PERF-13 and PERF-20 passed through."""
    options = AppOptions(
        True,
        "doc",
        "overlay",
        "storage",
        _yield,
        False,
        "1",
        "c",
        "keyboard",
        "debug",
        "stats",
        None,
        None,
        "stepped",
        "precompile",
        "background",
        "prebuild",
        None,
        "gamepads",
    )
    session = start_app.session_options(options, "on-load-start", "on-draw-calls")
    assert (session.environment, session.doc, session.debug) == (True, "doc", "debug")
    assert (session.stats_parent, session.overlay) == ("stats", "overlay")
    assert (session.keyboard_target, session.gamepads, session.storage) == (
        "keyboard",
        "gamepads",
        "storage",
    )
    assert session.on_load_start == "on-load-start"
    assert (session.stepped_loading, session.precompile_shaders) == ("stepped", "precompile")
    assert (session.background_loading, session.prebuild_levels) == ("background", "prebuild")
    assert session.on_draw_calls == "on-draw-calls"


def test_game_score_05_the_session_reports_to_the_menus_the_audio_and_the_perf(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also DEV-PERF-01 (the level's loading time) and ENG-106 (the draw calls)."""
    made: list[tuple[Any, ...]] = []
    monkeypatch.setattr(start_app, "GameSession", lambda *args: made.append(args) or "session")
    menu = MagicMock(high_score=900)
    audio = MagicMock()
    perf = MagicMock()
    session = start_app.create_session("engine", "game", _menu_options(), lambda: menu, audio, perf)
    assert session == "session"
    ((engine, game, options, on_complete, scores, session_audio),) = made
    assert (engine, game) == ("engine", "game")
    options.on_load_start()
    perf.load_started.assert_called_once_with()
    options.on_draw_calls(42)
    perf.record_draw_calls.assert_called_once_with(42)
    play = SimpleNamespace(run=SimpleNamespace(result="won"))
    on_complete(play)
    audio.level_ended.assert_called_once_with("won")
    menu.complete_level.assert_called_once_with("won")
    assert scores.high_score() == 900
    scores.record(1500)
    menu.record_score.assert_called_once_with(1500)
    session_audio.started("1-1")
    audio.level_started.assert_called_once_with("1-1")
    session_audio.step("run")
    audio.level_step.assert_called_once_with("run")


# The start-up: every part `start_app` wires together is a recorder here.


class AppParts:
    """The audio, session, dev viewers, menu, page listeners, menu scenes and perf overlay."""

    def __init__(self, dev: bool) -> None:
        self.audio = MagicMock(name="audio")
        self.session = SimpleNamespace(
            play=None,
            paused=False,
            controls=MagicMock(name="controls"),
            sync=MagicMock(name="session.sync"),
            dispose=MagicMock(name="session.dispose"),
            load_step=MagicMock(name="session.load_step"),
        )
        self.engine = MagicMock(name="engine")
        self.dev = MagicMock(name="dev", active=False) if dev else None
        self.menu = MagicMock(name="menu")
        self.menu.flow.state = SimpleNamespace(screen="title", highlighted_ship_id="beta")
        self.overlay = MagicMock(name="overlay")
        self.stop_page = MagicMock(name="stop_page")
        self.scenes = SimpleNamespace(
            backdrop={"showScreen": MagicMock(), "update": MagicMock()},
            stage=MagicMock(name="stage"),
            backdrop_scene=MagicMock(name="backdrop_scene"),
            ship_scene=MagicMock(name="ship_scene"),
        )
        self.perf_overlay = MagicMock(name="perf_overlay")
        self.perf_overlay.wrap.side_effect = lambda ticker: ticker
        self.perf_overlay_options: Any = None
        self.get_menu: Any = None
        self.on_change: Any = None
        self.dev_menu: Any = None
        self.loops: list[tuple[Any, Any]] = []

    def create_app_audio(self, _game: Any, _options: Any) -> SimpleNamespace:
        return SimpleNamespace(audio=self.audio, with_audio=lambda ticker: ticker)

    def create_session(self, *args: Any) -> SimpleNamespace:
        self.get_menu = args[3]
        assert args[4] is self.audio
        return self.session

    def create_dev(self, _engine: Any, _game: Any, _options: Any, _audio: Any) -> Any:
        return None if self.dev is None else [self.dev, "labels", "groups"]

    def create_menu(self, *args: Any) -> MenuHandle:
        self.on_change = args[5]
        self.dev_menu = args[6]
        return MenuHandle(self.menu, self.overlay)

    def listen_to_page(self, _options: Any, menu: Any, audio: Any) -> MagicMock:
        assert (menu, audio) == (self.menu, self.audio)
        return self.stop_page

    def prepare_menu_scenes(self, _engine: Any, _game: Any, _environment: bool) -> Any:
        return SimpleNamespace(tasks=[], result=lambda: self.scenes)

    def make_perf_overlay(self, options: Any, _perf: Any) -> MagicMock:
        self.perf_overlay_options = options
        return self.perf_overlay

    def run_loop(self, engine: Any, tick: Any) -> None:
        self.loops.append((engine, tick))


GAME = SimpleNamespace(
    player_ships=SimpleNamespace(ships=[SimpleNamespace(id="alpha"), SimpleNamespace(id="beta")])
)


def start(
    monkeypatch: pytest.MonkeyPatch,
    dev: bool,
    render_loop: bool,
    debug: Any = None,
    now: Any = None,
) -> tuple[RunningApp, AppParts, MagicMock]:
    """Start the app with recorders for its parts; returns the app, the parts and the key target."""
    parts = AppParts(dev)
    for name, value in {
        "create_app_audio": parts.create_app_audio,
        "create_session": parts.create_session,
        "create_dev": parts.create_dev,
        "create_menu": parts.create_menu,
        "listen_to_page": parts.listen_to_page,
        "prepare_menu_scenes": parts.prepare_menu_scenes,
        "perf_overlay": parts.make_perf_overlay,
        "run_loop": parts.run_loop,
    }.items():
        monkeypatch.setattr(start_app, name, value)
    target = MagicMock(name="keyboard_target")
    options = AppOptions(
        False, "doc", "overlay", "storage", _yield, render_loop, "1", "c", target, debug, None, now
    )
    return start_app.start_app(parts.engine, GAME, options), parts, target


def test_eng_100_the_app_starts_its_menus_on_a_fixed_step_clock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also UI-FLOW-01, DEV-PERF-01 (the browser's clock by default) and DEV-PERF-03."""
    app, parts, target = start(monkeypatch, False, False)
    assert app.clock.step_seconds == pytest.approx(1 / ENGINE_CONFIG.simulation_hz)
    assert (app.menu, app.audio, app.controls) == (parts.menu, parts.audio, parts.session.controls)
    assert parts.get_menu() is parts.menu
    assert parts.dev_menu is None
    assert app.perf._now is start_app.performance_now
    assert parts.perf_overlay_options.doc == "doc"
    assert parts.perf_overlay_options.keyboard_target is target
    assert target.addEventListener.call_count == 3
    # ENG-52: the unit tests and the e2e builds drive the frames themselves.
    assert parts.loops == []
    assert app.scenes() is None
    assert app.loading_progress == []
    app.loaded.close()


def test_ui_load_04_once_loaded_the_scenes_show_the_menu_s_screen_and_ship(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also UI-TITLE-09 and UI-LOAD-03 (the progress, here with no step)."""
    app, parts, _ = start(monkeypatch, False, False)
    asyncio.run(app.loaded)
    assert app.loading_progress == [0, 1]
    parts.menu.finish_loading.assert_called_once_with()
    assert app.scenes() is parts.scenes
    parts.scenes.backdrop["showScreen"].assert_called_once_with("title")
    parts.scenes.stage.select.assert_called_once_with(1)
    # No debug options: the title screen stays.
    parts.menu.play_direct.assert_not_called()


def test_ui_flow_01_each_menu_change_goes_to_the_scenes_session_and_audio(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, parts, _ = start(monkeypatch, False, False)
    state = SimpleNamespace(screen="ship-select", highlighted_ship_id="alpha")
    # Before the scenes are loaded, only the session and the audio follow.
    parts.on_change(state)
    parts.session.sync.assert_called_once_with(state)
    parts.audio.menu_changed.assert_called_once_with(state)
    asyncio.run(app.loaded)
    parts.on_change(state)
    parts.scenes.backdrop["showScreen"].assert_called_with("ship-select")
    parts.scenes.stage.select.assert_called_with(0)
    assert parts.audio.menu_changed.call_count == 2


def test_eng_100_a_frame_moves_and_draws_the_menu_scenes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Also PERF-09 (a loading step each frame) and UI-TITLE-09."""
    app, parts, _ = start(monkeypatch, False, False, None, lambda: 0.0)
    asyncio.run(app.loaded)
    app.tick(0.02)
    parts.menu.tick.assert_called_once_with(0.02)
    parts.session.load_step.assert_called_once_with(0.02)
    parts.scenes.backdrop["update"].assert_called_once_with(0.02)
    parts.scenes.stage.update.assert_called_once_with(0.02)
    parts.scenes.backdrop_scene.render.assert_called_once_with()


def test_dev_opt_01_a_debug_start_plays_its_level_once_the_menus_are_loaded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also DEV-PERF-01 (the clock given) and ENG-100 (Babylon's render loop when asked)."""
    now = MagicMock(return_value=0.0)
    debug = SimpleNamespace(level_id="2-1", ship_id=None)
    app, parts, _ = start(monkeypatch, False, True, debug, now)
    assert app.perf._now is now
    assert parts.loops == [(parts.engine, app._frames.tick)]
    parts.menu.play_direct.assert_not_called()
    asyncio.run(app.loaded)
    parts.menu.play_direct.assert_called_once_with("alpha", "2-1")


def test_d199_the_dev_viewers_follow_the_menus_and_are_released_with_the_app(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """DEV-MENU-02, DEV-MENU-05; D-202 (the groups)."""
    app, parts, _ = start(monkeypatch, True, False, None, lambda: 0.0)
    dev = parts.dev
    assert dev is not None
    assert parts.dev_menu == ["labels", dev.wheel, dev.turn, "groups", dev.hold]
    state = SimpleNamespace(screen="dev-viewer", highlighted_ship_id=None)
    parts.on_change(state)
    dev.sync.assert_called_once_with(state)
    app.tick(0.02)
    dev.frame.assert_called_once_with(0.02)
    app.dispose()
    dev.dispose.assert_called_once_with()
    app.loaded.close()


def test_eng_100_disposing_the_app_releases_everything_it_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Also DEV-PERF-03 (the perf overlay) and UI-INPUT-01 (the keyboard)."""
    app, parts, target = start(monkeypatch, False, False)
    asyncio.run(app.loaded)
    app.dispose()
    parts.engine.stopRenderLoop.assert_called_once_with()
    assert target.removeEventListener.call_count == 3
    parts.stop_page.assert_called_once_with()
    parts.session.dispose.assert_called_once_with()
    parts.overlay.dispose.assert_called_once_with()
    parts.perf_overlay.dispose.assert_called_once_with()
    parts.scenes.backdrop_scene.dispose.assert_called_once_with()
    parts.scenes.ship_scene.dispose.assert_called_once_with()


def test_eng_100_an_app_disposed_while_loading_has_no_scenes_to_release(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app, parts, _ = start(monkeypatch, False, False)
    app.dispose()
    parts.session.dispose.assert_called_once_with()
    parts.scenes.backdrop_scene.dispose.assert_not_called()
    # The loading that never ran is closed, not left pending.
    app.loaded.close()
