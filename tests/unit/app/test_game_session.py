# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/game_session.py`."""
# (DEV-OPT-04 to DEV-OPT-06, PERF-12): the debug choices on the look, the level and ship a menu
# state names, what a level keeps for the next; then the session itself over a fake `GamePlay` and
# fake loading steps (PERF-09, PERF-13: the level loading in steps, the level built ahead).

from types import SimpleNamespace
from typing import Any

import pytest
from helpers.memory_storage import MemoryStorage

from app import game_session, level_prepare
from app.game_session import (
    BUILD_AHEAD_AFTER,
    COMPILE_FRAMES,
    GameDebugOptions,
    GameSession,
    GameSessionOptions,
    SessionAudio,
    SessionScores,
    atmosphere_of,
    highlighted_level,
    ship_of,
)
from app.saved_supplies import load_saved_supplies, save_supplies, saved_supplies_key
from app.saved_weapons import load_saved_weapons, save_weapons
from core.systems.level_run_types import Supplies
from core.systems.run_arsenal import WeaponLevels


def state(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "screen": "game",
        "selected_id": None,
        "chosen_ship_id": None,
        "highlighted_ship_id": "alpha",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_perf_12_the_highlighted_level_is_prefetched_only_on_the_level_select_screen() -> None:
    assert highlighted_level(state(screen="level-select", selected_id="1-2")) == "1-2"
    assert highlighted_level(state(screen="title", selected_id="start")) is None


def test_perf_13_the_ship_of_the_levels_is_the_chosen_one_or_else_the_highlighted() -> None:
    """The level built ahead is flown with the highlighted ship."""
    assert ship_of(state(chosen_ship_id="beta")) == "beta"
    assert ship_of(state(chosen_ship_id=None, highlighted_ship_id="gamma")) == "gamma"


def test_dev_opt_04_without_debug_options_the_look_is_the_levels_own() -> None:
    """Also DEV-OPT-05 and DEV-OPT-06."""
    options = atmosphere_of(None)
    assert (options.time_of_day, options.weather, options.tile_grid) == (None, None, None)


def test_dev_opt_05_debug_options_force_the_time_of_day_and_weather_off_and_the_tiles() -> None:
    """Also DEV-OPT-04 and DEV-OPT-06."""
    debug = GameDebugOptions("1-1", 0, None, None, weather=False, time_of_day="night", tiles=True)
    options = atmosphere_of(debug)
    assert options.time_of_day == "night"
    assert options.weather is False
    assert options.tile_grid is True


def test_dev_opt_06_the_tile_grid_is_left_to_the_level_when_not_asked() -> None:
    debug = GameDebugOptions("1-1", 0, None, None, None, None, tiles=False)
    options = atmosphere_of(debug)
    assert options.weather is None
    assert options.tile_grid is None


def _session(storage: MemoryStorage | None, completed: list[object]) -> GameSession:
    """Return a game session with only what its carry-over reads: the storage and the game's id."""
    session = GameSession.__new__(GameSession)
    session.options = SimpleNamespace(storage=storage)
    session.game = SimpleNamespace(id="game")
    session._on_complete = completed.append
    return session


def _played(phase: str, weapons: WeaponLevels, supplies: Supplies) -> SimpleNamespace:
    """Return a level as its run ends: its phase, its weapons (arsenal), lives and bombs."""
    run = SimpleNamespace(
        phase=phase,
        arsenal=SimpleNamespace(snapshot=lambda: weapons),
        supplies=supplies,
    )
    return SimpleNamespace(run=run)


def test_game_level_14_a_completed_level_keeps_its_weapons_lives_and_bombs() -> None:
    storage = MemoryStorage()
    completed: list[object] = []
    weapons = WeaponLevels("laser", {"guns": 2.0, "laser": 3.0})
    play = _played("complete", weapons, Supplies(5, 7))
    _session(storage, completed)._completed(play)
    kept_weapons = load_saved_weapons(storage, "game")
    kept_supplies = load_saved_supplies(storage, "game")
    assert kept_weapons is not None
    assert kept_weapons.weapon == "laser"
    assert kept_weapons.levels == {"guns": 2.0, "laser": 3.0}
    assert kept_supplies is not None
    assert (kept_supplies.lives, kept_supplies.bombs) == (5, 7)
    assert completed == [play]


def test_game_level_14_a_game_over_keeps_nothing_new() -> None:
    """What was kept before stays: the level lost keeps neither its weapons nor its supplies."""
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("guns", {"guns": 1.0}))
    save_supplies(storage, "game", Supplies(3, 3))
    completed: list[object] = []
    play = _played("over", WeaponLevels("laser", {"guns": 4.0, "laser": 4.0}), Supplies(9, 9))
    _session(storage, completed)._completed(play)
    kept_weapons = load_saved_weapons(storage, "game")
    kept_supplies = load_saved_supplies(storage, "game")
    assert kept_weapons is not None
    assert kept_weapons.weapon == "guns"
    assert kept_weapons.levels == {"guns": 1.0}
    assert kept_supplies is not None
    assert (kept_supplies.lives, kept_supplies.bombs) == (3, 3)
    assert completed == [play]


def test_game_life_12_a_continue_keeps_the_weapons_but_not_the_supplies() -> None:
    """A Continue starts again with the starting lives and bombs (GAME-LIFE-11): none are read."""
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("guns", {"guns": 2.0}))
    save_supplies(storage, "game", Supplies(5, 7))
    session = _session(storage, [])
    weapons, supplies = session._kept(SimpleNamespace(resume=True))
    assert weapons is not None
    assert weapons.levels == {"guns": 2.0}
    assert supplies is None
    weapons, supplies = session._kept(SimpleNamespace(resume=None))
    assert supplies is not None
    assert (supplies.lives, supplies.bombs) == (5, 7)


def test_game_life_12_an_unreadable_saved_supply_is_kept_as_none() -> None:
    storage = MemoryStorage()
    storage.set(saved_supplies_key("game"), "not json")
    _weapons, supplies = _session(storage, [])._kept(SimpleNamespace(resume=None))
    assert supplies is None


def test_game_level_14_without_storage_nothing_is_kept_or_saved() -> None:
    session = _session(None, [])
    assert session._kept(SimpleNamespace(resume=None)) == (None, None)
    session._completed(_played("complete", WeaponLevels("guns", {}), Supplies(5, 7)))


def test_game_level_14_a_completed_level_without_supplies_keeps_only_its_weapons() -> None:
    storage = MemoryStorage()
    completed: list[object] = []
    play = _played("complete", WeaponLevels("guns", {"guns": 3.0}), None)  # type: ignore[arg-type]
    _session(storage, completed)._completed(play)
    kept_weapons = load_saved_weapons(storage, "game")
    assert kept_weapons is not None
    assert kept_weapons.levels == {"guns": 3.0}
    assert load_saved_supplies(storage, "game") is None
    assert completed == [play]


# The session itself, over a fake `GamePlay` and fake loading steps (ENG-47).

# The steps of a level's loading (PERF-09): ground, textures, roads, scene, shaders asked, enemy
# models, first drawing, start.
STEPS = 8

GAME = SimpleNamespace(id="game", texts=SimpleNamespace(loading="Loading level"), game_levels=[])


class Answers:
    """What a loading step's check answers: the queued answers, then True."""

    def __init__(self) -> None:
        self.queued: list[bool] = []
        self.asked: list[tuple[Any, ...]] = []

    def __call__(self, *args: Any) -> bool:
        self.asked.append(args)
        return self.queued.pop(0) if len(self.queued) > 0 else True


class FakeScene:
    """A level's scene: ready (its shaders compiled) or not, and the drawings made."""

    def __init__(self, env: "Env") -> None:
        self._env = env
        self.meshes = ["mesh"]
        self.rendered = 0

    def getEngine(self) -> Any:
        caps = SimpleNamespace(parallelShaderCompile=self._env.parallel)
        return SimpleNamespace(getCaps=lambda: caps)

    def isReady(self, check_render_targets: bool) -> bool:
        assert check_render_targets is True
        return self._env.scene_ready

    def render(self) -> None:
        self.rendered += 1


class FakePlay:
    """A level built (`GamePlay`): what it was built with, and what it was asked."""

    def __init__(
        self, env: "Env", engine: Any, game: Any, choice: Any, controls: Any, options: Any
    ) -> None:
        self.engine = engine
        self.game = game
        self.choice = choice
        self.controls = controls
        self.options = options
        self.view = SimpleNamespace(scene=FakeScene(env))
        self.run = SimpleNamespace(phase="playing", score=0)
        self.calls: list[Any] = []
        self.enemies_left = env.enemies_left
        self.disposed = False

    def attach(self) -> None:
        self.calls.append("attach")

    def prepare(self, compile_now: bool) -> None:
        self.calls.append(("prepare", compile_now))

    def warm_shots(self, on: bool) -> None:
        self.calls.append(("warm", on))

    def build_enemies(self, compile_now: bool) -> bool:
        self.calls.append(("enemies", compile_now))
        self.enemies_left -= 1
        return self.enemies_left < 0

    def dispose(self) -> None:
        self.disposed = True


class FakeLoadingScreen:
    def __init__(self, doc: Any, parent: Any, text: str) -> None:
        self.doc = doc
        self.parent = parent
        self.text = text
        self.shown: list[float] = []
        self.disposed = False

    def show(self, progress: float) -> None:
        self.shown.append(progress)

    def dispose(self) -> None:
        self.disposed = True


class FakeLoader:
    """The background loader (the worker)."""

    def __init__(self) -> None:
        self.stopped = 0

    def stop(self) -> None:
        self.stopped += 1


class Env:
    """The patched module: the levels built, the loading steps' answers, the screens shown."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.plays: list[FakePlay] = []
        self.ground = Answers()
        self.textures = Answers()
        self.roads = Answers()
        self.outlines = True
        self.parallel: Any = "parallel"
        self.scene_ready = True
        self.enemies_left = 0
        self.screens: list[FakeLoadingScreen] = []
        self.loaders: list[FakeLoader] = []
        self.prefetched: list[tuple[str | None, Any]] = []
        self.listened: list[tuple[Any, Any, Any]] = []
        self.stopped_listening = 0
        monkeypatch.setattr(game_session, "GamePlay", self._play)
        monkeypatch.setattr(game_session, "prepare_level", self.ground)
        monkeypatch.setattr(game_session, "textures_ready", self.textures)
        monkeypatch.setattr(game_session, "roads_ready", self.roads)
        monkeypatch.setattr(game_session, "outlines_ready", lambda _meshes: self.outlines)
        monkeypatch.setattr(game_session, "LevelLoadingScreen", self._screen)
        monkeypatch.setattr(game_session, "start_background_loader", self._loader)
        monkeypatch.setattr(game_session, "listen_controls", self._listen)
        monkeypatch.setattr(level_prepare, "prefetch_level", self._prefetch)

    def _play(self, *args: Any) -> FakePlay:
        play = FakePlay(self, *args)
        self.plays.append(play)
        return play

    def _screen(self, doc: Any, parent: Any, text: str) -> FakeLoadingScreen:
        screen = FakeLoadingScreen(doc, parent, text)
        self.screens.append(screen)
        return screen

    def _loader(self) -> FakeLoader:
        loader = FakeLoader()
        self.loaders.append(loader)
        return loader

    def _listen(self, target: Any, controls: Any, current_play: Any) -> Any:
        self.listened.append((target, controls, current_play))

        def stop() -> None:
            self.stopped_listening += 1

        return stop

    def _prefetch(self, _game: Any, level_id: str | None, loader: Any) -> None:
        self.prefetched.append((level_id, loader))


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(monkeypatch)


def menu(screen: str = "game", **overrides: object) -> SimpleNamespace:
    """Return the menu flow's state: on `screen`, level 1-1 chosen with ship alpha."""
    values: dict[str, object] = {
        "screen": screen,
        "selected_id": None,
        "highlighted_ship_id": "alpha",
        "chosen_ship_id": "alpha",
        "chosen_level_id": "1-1",
        "attempt": 1,
        "level_result": None,
        "resume": None,
        "paused": False,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_session(
    completed: list[Any] | None = None,
    scores: SessionScores | None = None,
    audio: SessionAudio | None = None,
    **options: Any,
) -> GameSession:
    done = completed if completed is not None else []
    session_options = GameSessionOptions(False, "doc", **options)
    return GameSession("engine", GAME, session_options, done.append, scores, audio)


def load(session: GameSession, frames: int) -> None:
    for _ in range(frames):
        session.load_step(1 / 60)


def test_ui_level_08_without_stepped_loading_a_confirmed_level_starts_at_once(env: Env) -> None:
    """Also AUD-MUSIC-08 (its music starts) and GAME-SCORE-07 (the HUD's high score)."""
    started: list[str] = []
    session = make_session(
        scores=SessionScores(lambda: 900, lambda _score: None),
        audio=SessionAudio(started.append, lambda _run: None),
        stats_parent="stats",
        overlay="overlay",
        on_draw_calls="draw-calls",
    )
    session.sync(menu())
    (play,) = env.plays
    assert session.play is play
    assert session.loading is False
    assert (play.engine, play.game, play.controls) == ("engine", GAME, session.controls)
    assert (play.choice.ship_id, play.choice.level_id) == ("alpha", "1-1")
    options = play.options
    assert (options.environment, options.debug, options.start_time, options.start_boss) == (
        False,
        False,
        0.0,
        None,
    )
    assert (options.resume, options.journey, options.weapons, options.supplies) == (
        None,
        None,
        None,
        None,
    )
    assert options.high_score == 900
    assert (options.doc, options.stats_parent, options.hud_parent) == ("doc", "stats", "overlay")
    assert options.on_draw_calls == "draw-calls"
    atmosphere = options.atmosphere
    assert (atmosphere.time_of_day, atmosphere.weather, atmosphere.tile_grid) == (None, None, None)
    # Without stepped loading, nothing is compiled or built ahead of the start.
    assert play.calls == [("warm", False), "attach"]
    assert play.view.scene.rendered == 0
    assert started == ["1-1"]
    assert env.ground.asked == [(GAME, "1-1")]
    assert env.textures.asked == [(GAME, "1-1", None, 1)]
    assert env.roads.asked == [(GAME, "1-1", False, 1)]
    assert env.screens == []


def test_aud_engine_09_each_step_of_the_level_is_heard_and_its_end_reported(env: Env) -> None:
    """Also GAME-LEVEL-13: the end of the level goes to the session's owner."""
    stepped: list[Any] = []
    completed: list[Any] = []
    session = make_session(completed, audio=SessionAudio(lambda _level: None, stepped.append))
    session.sync(menu())
    (play,) = env.plays
    play.options.on_step("run")
    assert stepped == ["run"]
    play.options.on_complete("result")
    assert completed == [play]


def test_aud_engine_09_without_audio_nothing_hears_the_level(env: Env) -> None:
    session = make_session()
    session.sync(menu())
    (play,) = env.plays
    play.options.on_step("run")
    assert play.options.high_score == 0
    assert play.calls == [("warm", False), "attach"]


def test_perf_09_a_level_loads_one_step_a_frame_behind_the_loading_screen(env: Env) -> None:
    """Also UI-LOAD-06, PERF-10 and PERF-20 (the shaders compile while it loads)."""
    session = make_session(overlay="overlay", stepped_loading=True)
    session.sync(menu())
    assert session.loading is True
    (screen,) = env.screens
    assert (screen.doc, screen.parent, screen.text) == ("doc", "overlay", "Loading level")
    assert screen.shown == [0]
    load(session, STEPS - 1)
    # A sync while it loads does not start it again.
    session.sync(menu())
    assert session.loading is True
    assert session.play is None
    load(session, 1)
    assert session.loading is False
    (play,) = env.plays
    assert session.play is play
    assert screen.shown == [pytest.approx(done / STEPS) for done in range(STEPS + 1)]
    assert screen.disposed is True
    assert play.calls == [
        ("prepare", True),
        ("warm", True),
        ("enemies", True),
        ("warm", False),
        "attach",
    ]
    assert play.view.scene.rendered == 1


def test_perf_09_a_step_not_over_runs_again_on_the_next_frame(env: Env) -> None:
    """Its tries are counted, for the waits of PERF-18; no overlay, no loading screen."""
    env.ground.queued = [False]
    env.textures.queued = [False]
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, 5)
    assert len(env.ground.asked) == 2
    assert env.textures.asked == [(GAME, "1-1", None, 1), (GAME, "1-1", None, 2)]
    assert env.roads.asked == [(GAME, "1-1", False, 1)]
    load(session, STEPS)
    assert session.play is env.plays[0]
    assert env.screens == []


def test_dev_opt_06_the_roads_are_made_with_the_tile_grid_when_it_shows(env: Env) -> None:
    session = make_session(debug=GameDebugOptions("1-1", 0, None, None, tiles=True))
    session.sync(menu())
    assert env.roads.asked == [(GAME, "1-1", True, 1)]


def test_perf_20_the_first_drawing_waits_for_the_shaders_compiled_in_parallel(env: Env) -> None:
    env.scene_ready = False
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, 6 + 2)
    (play,) = env.plays
    assert play.view.scene.rendered == 0
    env.scene_ready = True
    load(session, 1)
    assert play.view.scene.rendered == 1
    load(session, 1)
    assert session.play is play


def test_perf_20_the_first_drawing_waits_for_the_outlines_too(env: Env) -> None:
    env.outlines = False
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, 6 + 1)
    assert env.plays[0].view.scene.rendered == 0
    env.outlines = True
    load(session, 1)
    assert env.plays[0].view.scene.rendered == 1


def test_perf_20_the_wait_for_the_shaders_is_given_up_after_some_frames(env: Env) -> None:
    env.scene_ready = False
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, 6 + COMPILE_FRAMES - 1)
    assert env.plays[0].view.scene.rendered == 0
    load(session, 1)
    assert env.plays[0].view.scene.rendered == 1


def test_perf_20_without_parallel_compiling_the_first_drawing_is_made_at_once(env: Env) -> None:
    env.scene_ready = False
    env.parallel = None
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, 6 + 1)
    assert env.plays[0].view.scene.rendered == 1


def test_perf_20_the_shaders_are_not_compiled_ahead_when_it_is_off(env: Env) -> None:
    session = make_session(stepped_loading=True, precompile_shaders=False)
    session.sync(menu())
    load(session, STEPS)
    (play,) = env.plays
    assert play.calls == [
        ("prepare", False),
        ("warm", True),
        ("enemies", False),
        ("warm", False),
        "attach",
    ]
    assert play.view.scene.rendered == 0


def test_perf_21_the_enemy_models_are_built_one_a_frame_while_it_loads(env: Env) -> None:
    env.enemies_left = 2
    session = make_session(stepped_loading=True)
    session.sync(menu())
    load(session, STEPS + 1)
    assert session.loading is True
    load(session, 1)
    assert session.play is env.plays[0]
    assert env.plays[0].calls.count(("enemies", True)) == 3


def test_dev_perf_01_the_start_of_a_level_s_loading_is_reported(env: Env) -> None:
    starts: list[bool] = []
    session = make_session(on_load_start=lambda: starts.append(True))
    session.sync(menu())
    assert starts == [True]
    assert len(env.plays) == 1


def test_perf_12_a_confirmed_level_is_prefetched_at_once(env: Env) -> None:
    session = make_session(background_loading=True)
    (loader,) = env.loaders
    session.sync(menu())
    assert env.prefetched == [("1-1", loader)]


def test_ui_flow_06_leaving_the_level_ends_it_and_records_its_score(env: Env) -> None:
    """Also GAME-SCORE-05 and GAME-CTRL-07 (the presses made in it are let go)."""
    recorded: list[float] = []
    session = make_session(scores=SessionScores(lambda: 0, recorded.append))
    session.sync(menu())
    (play,) = env.plays
    play.run.score = 1234
    session.controls.bomb()
    session.sync(menu("level-select", chosen_level_id=None))
    assert recorded == [1234]
    assert play.disposed is True
    assert session.play is None
    assert session.controls.read(0.1, 100).bomb is False


def test_ui_pause_04_presses_made_while_paused_do_not_carry_into_the_level(env: Env) -> None:
    """Also UI-PAUSE-03: the paused level is kept, and gets no debug keys (DEV-OPT-10)."""
    session = make_session(keyboard_target="keyboard")
    ((target, controls, current_play),) = env.listened
    assert (target, controls) == ("keyboard", session.controls)
    session.sync(menu())
    (play,) = env.plays
    assert current_play() is play
    session.controls.bomb()
    session.sync(menu("pause", paused=True))
    assert session.paused is True
    assert session.play is play
    assert play.disposed is False
    assert current_play() is None
    assert session.controls.read(0.1, 100).bomb is False
    session.sync(menu())
    assert session.paused is False
    assert current_play() is play
    assert len(env.plays) == 1


def test_game_life_11_continue_starts_the_level_again_from_its_checkpoint(env: Env) -> None:
    """Also GAME-LIFE-12 and UI-OVER-07: the weapons are kept, but not the lives and bombs."""
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("guns", {"guns": 2.0}))
    save_supplies(storage, "game", Supplies(5, 7))
    session = make_session(storage=storage)
    session.sync(menu())
    first = env.plays[0]
    assert first.options.supplies is not None
    session.sync(menu(attempt=2, resume="checkpoint"))
    assert first.disposed is True
    second = env.plays[1]
    assert session.play is second
    assert second.options.resume == "checkpoint"
    assert second.options.weapons.levels == {"guns": 2.0}
    assert second.options.supplies is None


def test_game_level_13_a_level_on_its_end_panel_is_not_started_again(env: Env) -> None:
    session = make_session()
    session.sync(menu(level_result="result"))
    assert env.plays == []
    assert session.loading is False


def test_dev_opt_02_the_debug_start_time_and_boss_apply_to_the_first_level_only(env: Env) -> None:
    """Also DEV-OPT-03 and DEV-OPT-05 (the time of day of the debug options)."""
    debug = GameDebugOptions("1-1", 120, None, "mini", None, "night", None)
    session = make_session(debug=debug)
    session.sync(menu())
    first = env.plays[0].options
    assert (first.debug, first.start_time, first.start_boss) == (True, 120, "mini")
    assert first.atmosphere.time_of_day == "night"
    session.sync(menu("level-select", chosen_level_id=None))
    session.sync(menu(attempt=2))
    second = env.plays[1].options
    assert (second.start_time, second.start_boss) == (0.0, None)


def ahead_session() -> GameSession:
    return make_session(stepped_loading=True, prebuild_levels=True, overlay="overlay")


def selecting(level_id: str, ship_id: str = "beta") -> SimpleNamespace:
    """Return the level select screen, its highlight on `level_id`, flown by `ship_id`."""
    return menu("level-select", selected_id=level_id, chosen_ship_id=ship_id, chosen_level_id=None)


def test_perf_13_the_level_the_highlight_rests_on_is_built_ahead_but_not_started(
    env: Env,
) -> None:
    """Also PERF-12: the level highlighted is prefetched first."""
    session = ahead_session()
    session.sync(selecting("1-2"))
    session.load_step(BUILD_AHEAD_AFTER / 2)
    assert ("1-2", None) in env.prefetched
    assert env.plays == []
    load(session, 1)
    session.load_step(BUILD_AHEAD_AFTER)
    load(session, STEPS)
    (play,) = env.plays
    assert (play.choice.ship_id, play.choice.level_id) == ("beta", "1-2")
    assert play.options.resume is None
    # Every step but its start: the shaders are compiled, the level is not in the page.
    assert play.calls == [("prepare", True), ("warm", True), ("enemies", True)]
    assert play.view.scene.rendered == 1
    assert session.play is None
    assert session.loading is False


def test_perf_13_a_level_built_ahead_starts_in_the_very_frame_it_is_confirmed(env: Env) -> None:
    """Also UI-LOAD-06: no loading screen shows."""
    session = ahead_session()
    session.sync(selecting("1-2"))
    session.load_step(BUILD_AHEAD_AFTER)
    load(session, STEPS)
    session.sync(menu(chosen_ship_id="beta", chosen_level_id="1-2"))
    (play,) = env.plays
    assert session.play is play
    assert play.calls[-2:] == [("warm", False), "attach"]
    assert env.screens == []


def test_perf_13_the_level_built_ahead_is_dropped_for_another_level_or_ship(env: Env) -> None:
    session = ahead_session()
    session.sync(selecting("1-2"))
    session.load_step(BUILD_AHEAD_AFTER)
    load(session, 4)
    first = env.plays[0]
    session.sync(selecting("1-3"))
    session.load_step(BUILD_AHEAD_AFTER)
    assert first.disposed is True
    load(session, 3)
    second = env.plays[1]
    assert second.choice.level_id == "1-3"
    session.sync(selecting("1-3", "gamma"))
    load(session, 1)
    assert second.disposed is True
    # Off the level select screen, the one being built ahead is dropped too.
    session.sync(menu("title", chosen_ship_id=None, chosen_level_id=None))
    load(session, 1)
    assert session._ahead is None
    assert len(env.plays) == 2


def test_perf_13_a_continue_does_not_start_from_the_level_built_ahead(env: Env) -> None:
    session = ahead_session()
    session.sync(selecting("1-1", "alpha"))
    session.load_step(BUILD_AHEAD_AFTER)
    load(session, STEPS)
    ahead = env.plays[0]
    session.sync(menu(resume="checkpoint"))
    assert ahead.disposed is True
    assert session.loading is True
    assert len(env.screens) == 1


def test_perf_13_nothing_is_built_ahead_without_stepped_loading(env: Env) -> None:
    session = make_session(prebuild_levels=True)
    session.sync(selecting("1-2"))
    load(session, 30)
    assert env.plays == []


def test_ui_flow_06_leaving_a_level_being_loaded_drops_it_and_its_loading_screen(
    env: Env,
) -> None:
    recorded: list[float] = []
    session = make_session(
        scores=SessionScores(lambda: 0, recorded.append), stepped_loading=True, overlay="overlay"
    )
    session.sync(menu())
    load(session, 4)
    (play,) = env.plays
    session.sync(menu("title", chosen_level_id=None))
    assert play.disposed is True
    assert env.screens[0].disposed is True
    assert session.loading is False
    # It was not played: no score is recorded.
    assert recorded == []


def test_ui_flow_06_a_level_left_before_it_is_built_leaves_nothing(env: Env) -> None:
    session = make_session(stepped_loading=True)
    session.sync(menu())
    session.sync(menu("title", chosen_level_id=None))
    assert session.loading is False
    assert env.plays == []


def test_dispose_ends_the_level_and_stops_the_keys_and_the_worker(env: Env) -> None:
    session = make_session(background_loading=True, prebuild_levels=True, stepped_loading=True)
    session.sync(selecting("1-2"))
    session.load_step(BUILD_AHEAD_AFTER)
    load(session, 4)
    ahead = env.plays[0]
    session.dispose()
    assert ahead.disposed is True
    assert env.stopped_listening == 1
    assert env.loaders[0].stopped == 1


def test_dispose_without_a_worker(env: Env) -> None:
    session = make_session()
    session.sync(menu())
    session.dispose()
    assert env.plays[0].disposed is True
    assert env.stopped_listening == 1
    assert env.loaders == []
