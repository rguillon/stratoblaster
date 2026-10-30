"""Unit tests of `src/app/start_app.py`."""
# p/start_app.py`: the frame split (simulate, then render), the input set-up, the scene sync and
# the debug start (P13-R01, P06-R09, P12-R03). The Babylon engine and the scenes are fakes here;
# the start-up itself is run by the browser.

from types import SimpleNamespace
from unittest.mock import MagicMock

from helpers.gamepads import FakeGamepad

from app import start_app
from app.start_app import (
    FrameControls,
    _index_of,
    create_input,
    dispose_scenes,
    frame_ticker,
    run_loop,
    start_debug_level,
    sync_scenes,
)
from config.engine import ENGINE_CONFIG
from config.menu import MENU_CONFIG
from input.menu_input import MenuInput


class FakeClock:
    def __init__(self, step_seconds: float = 1 / 60) -> None:
        self.step_seconds = step_seconds
        self.advanced: list[float] = []

    def advance(self, dt: float) -> None:
        self.advanced.append(dt)


def test_p13_r01_a_frame_is_timed_and_simulated_then_drawn() -> None:
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


def test_p13_r01_whole_steps_draw_only_the_last_one_when_asked() -> None:
    simulated: list[float] = []
    renders: list[str] = []
    ticker = SimpleNamespace(
        simulate=simulated.append,
        render=lambda: renders.append("render"),
    )
    perf = MagicMock()
    clock = FakeClock(step_seconds=0.1)
    FrameControls(clock, ticker, perf).step(3, True)
    assert simulated == [0.1, 0.1, 0.1]
    assert renders == ["render"]
    assert perf.frame_started.call_count == 3


def test_p13_r01_steps_without_drawing_draw_nothing() -> None:
    renders: list[str] = []
    ticker = SimpleNamespace(simulate=lambda dt: None, render=lambda: renders.append("r"))
    FrameControls(FakeClock(), ticker, MagicMock()).step(2, False)
    assert renders == []


def test_p13_r01_zero_steps_with_drawing_still_draw_once() -> None:
    renders: list[str] = []
    ticker = SimpleNamespace(simulate=lambda dt: None, render=lambda: renders.append("r"))
    FrameControls(FakeClock(), ticker, MagicMock()).step(0, True)
    assert renders == ["r"]


def test_p13_r02_an_index_is_found_or_is_minus_one() -> None:
    assert _index_of(["alpha", "beta"], "beta") == 1
    assert _index_of(["alpha"], "gamma") == -1
    assert _index_of(["alpha"], None) == -1


def test_p12_r03_the_keyboard_is_always_an_input_and_listens_to_its_target() -> None:
    target = MagicMock()
    handle = create_input(SimpleNamespace(keyboard_target=target, gamepads=None))
    assert isinstance(handle.input, MenuInput)
    assert target.addEventListener.call_count == 3
    handle.stop()
    assert target.removeEventListener.call_count == 3


def test_p12_r03_gamepads_are_added_as_a_second_device_when_given() -> None:
    pad = FakeGamepad().press(0)
    handle = create_input(SimpleNamespace(keyboard_target=None, gamepads=lambda: [pad]))
    assert handle.input.update(0.0) == ["confirm"]
    handle.stop()


def test_p12_r03_without_a_target_nothing_listens_to_the_keyboard() -> None:
    handle = create_input(SimpleNamespace(keyboard_target=None, gamepads=None))
    handle.stop()


def test_p12_r04_the_menu_scenes_show_the_screen_and_the_highlighted_ship() -> None:
    backdrop = {"showScreen": MagicMock()}
    stage = MagicMock()
    scenes = SimpleNamespace(backdrop=backdrop, stage=stage)
    state = SimpleNamespace(screen="ship-select", highlighted_ship_id="beta")
    sync_scenes(scenes, state, ["alpha", "beta"])
    backdrop["showScreen"].assert_called_once_with("ship-select")
    stage.select.assert_called_once_with(1)


def test_p01_r13_syncing_without_scenes_does_nothing() -> None:
    sync_scenes(None, SimpleNamespace(screen="title"), [])


def test_p13_r01_disposing_the_menu_scenes_releases_both_and_none_is_fine() -> None:
    scenes = SimpleNamespace(backdrop_scene=MagicMock(), ship_scene=MagicMock())
    dispose_scenes(scenes)
    scenes.backdrop_scene.dispose.assert_called_once()
    scenes.ship_scene.dispose.assert_called_once()
    dispose_scenes(None)


def test_p01_r13_the_render_loop_gets_each_frame_in_seconds() -> None:
    engine = MagicMock()
    engine.getDeltaTime.return_value = 16.0
    tick = MagicMock()
    run_loop(engine, tick)
    frame = engine.runRenderLoop.call_args.args[0]
    frame()
    tick.assert_called_once_with(0.016)


def test_p06_r09_a_debug_start_plays_its_level_once_loading_is_over() -> None:
    menu = MagicMock()
    debug = SimpleNamespace(level_id="2-1", ship_id="beta")
    start_debug_level(menu, debug, ["alpha", "beta"])
    menu.play_direct.assert_called_once_with("beta", "2-1")


def test_p06_r09_without_a_ship_the_first_one_is_used_and_no_debug_does_nothing() -> None:
    menu = MagicMock()
    start_debug_level(menu, SimpleNamespace(level_id="1-1", ship_id=None), ["alpha"])
    menu.play_direct.assert_called_once_with("alpha", "1-1")
    start_debug_level(menu, None, ["alpha"])
    assert menu.play_direct.call_count == 1
    start_debug_level(menu, SimpleNamespace(level_id="1-1", ship_id=None), [])
    menu.play_direct.assert_called_with("", "1-1")


def test_p01_r15_a_frame_is_capped_at_the_longest_the_menus_accept() -> None:
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


def test_p12_r01_a_paused_level_does_not_advance_but_a_lost_pad_pauses_the_menu() -> None:
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


def test_p12_r01_a_running_level_advances_each_frame() -> None:
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


def test_p13_r01_the_level_is_drawn_and_its_load_is_finished_at_its_first_frame() -> None:
    clock = FakeClock()
    menu = MagicMock()
    play = MagicMock()
    session = SimpleNamespace(play=play, paused=False, controls=MagicMock())
    perf = MagicMock(loading=True)
    ticker = frame_ticker(clock, menu, lambda: None, session, perf)
    ticker.render()
    play.view.scene.render.assert_called_once()
    perf.load_finished.assert_called_once_with(ENGINE_CONFIG.simulation_hz)


def test_p01_r13_the_menu_scenes_are_drawn_for_the_menu_screen() -> None:
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
    assert start_app.create_dev("engine", None, options, lambda: None) is None


def test_d199_with_dev_the_session_sends_its_wheel_commands_to_the_menu(monkeypatch) -> None:
    monkeypatch.setattr(start_app, "dev_catalog", lambda game: {"ships": ["item"]})
    monkeypatch.setattr(start_app, "dev_labels", lambda catalog: {"ships": ["Item"]})
    monkeypatch.setattr(start_app, "dev_groups", lambda catalog: {"ships": [""]})
    menu = MagicMock()
    options = SimpleNamespace(dev=True, environment=False, overlay="overlay")
    session, labels, groups = start_app.create_dev("engine", "game", options, lambda: menu)
    assert labels == {"ships": ["Item"]}
    assert groups == {"ships": [""]}
    session._command("right")
    menu.command.assert_called_once_with("right")


def test_d199_the_dev_viewer_moves_on_with_the_menus_and_is_drawn_instead_of_them() -> None:
    clock = FakeClock()
    menu = MagicMock()
    menu.flow.state.screen = "dev-viewer"
    session = SimpleNamespace(play=None, load_step=MagicMock(), controls=MagicMock())
    dev = MagicMock(active=True)
    dev.render.return_value = True
    drawn: list = []
    original = start_app.render_menu_scenes
    start_app.render_menu_scenes = lambda loaded, screen: drawn.append(screen)
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
