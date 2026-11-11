# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/game_play.py`: the game screen of a level, over fake layers.

The level scene, the run (`LevelRun`), the models, the shots and the HUD are fakes (ENG-47): the
tests check how a `GamePlay` builds them, steps the run at its fixed step and draws it. The fixed
step clock, the FPS meter, the model keys of the level and the hit blasts are the real ones.
"""

import itertools
import math
from types import SimpleNamespace
from typing import Any

import pytest
from helpers import js_shims
from helpers.render_fakes import FakeNode

from app import game_play
from app.game_play import GameChoice, GamePlay, GamePlayOptions
from app.game_play_hud import StatsShown
from config.game_controls import GAME_CONTROLS_CONFIG
from config.game_play import GAME_PLAY_CONFIG as CFG
from core.entities.player_ship import PlayerShipDefinition, PlayerShipRoster
from core.systems.level_run_types import LandedHit
from core.systems.shot_world import ShotImpact

# The nose of the ship's model, past its pivot (GAME-WPN-05).
NOSE = 30.0
# The base speed of the ships, and the speed factor of the one flown: 200 px/s.
BASE_SPEED = 100.0
SPEED = 2 * BASE_SPEED
# How far the level scrolls each second (the fake run's track).
TRACK_SPEED = 60.0
# What the fake framing says is half the width shown, at any height.
HALF_WIDTH = 200.0


class FakeScene:
    def __init__(self) -> None:
        self.meshes = ["sky-mesh", "ground-mesh"]
        self.disposed = False

    def getActiveIndices(self) -> float:
        return 300.0

    def dispose(self) -> None:
        self.disposed = True


class FakePlayfield:
    """The playfield layer: whatever is made in `run` hangs from it."""

    def __init__(self) -> None:
        self.root = "playfield-root"
        self.runs = 0

    def run(self, create: Any) -> Any:
        self.runs += 1
        return create()


class FakeView:
    """The level scene: what `build_level_scene` returns, and every scroll it was asked for."""

    def __init__(self, options: Any) -> None:
        self.options = options
        self.scene = FakeScene()
        self.playfield = FakePlayfield()
        self.stage = SimpleNamespace(framing="framing")
        self.look = SimpleNamespace(shotStyle="shot-style")
        self.updates: list[tuple[float, float]] = []

    def update(self, distance: float, dt: float) -> None:
        self.updates.append((distance, dt))


class FakeShip:
    """The playfield ship (`PlayfieldShip`)."""

    def __init__(self, scene: Any, scale: float, x: float, y: float) -> None:
        self.scene = scene
        self.scale = scale
        self.at = (x, y)
        self.pivot = FakeNode("ship")
        self.model: Any = None
        self.dts: list[float] = []

    def show(self, model: Any) -> float:
        self.model = model
        return NOSE

    def update(self, dt: float) -> None:
        self.dts.append(dt)


class FakeLayer:
    """The enemy layer: the enemies drawn, and one model built ahead per `prepare_next`."""

    def __init__(self, scene: Any, models: Any, keys: list[str]) -> None:
        self.scene = scene
        self.models = models
        self.keys = keys
        self.synced: list[tuple[Any, float]] = []
        self.ahead = [["gnat-mesh"], ["warden-mesh"]]
        self.disposed = False

    def sync(self, enemies: Any, dt: float) -> None:
        self.synced.append((enemies, dt))

    def prepare_next(self) -> list[Any]:
        return self.ahead.pop(0) if len(self.ahead) > 0 else []

    def dispose(self) -> None:
        self.disposed = True


class FakeShots:
    """The enemy shots, blasts and impacts (`EnemyViewerShots`)."""

    def __init__(self, game: Any, playfield: Any, style: Any) -> None:
        self.game = game
        self.playfield = playfield
        self.style = style
        self.drawn: list[Any] = []
        self.warmed: list[bool] = []
        self.disposed = False

    def sync(self, frame: Any) -> None:
        self.drawn.append(frame)

    def warm(self, on: bool) -> None:
        self.warmed.append(on)

    def dispose(self) -> None:
        self.disposed = True


class FakeRenderer:
    """The bonus or the bomb renderer: every frame it drew."""

    def __init__(self, scene: Any) -> None:
        self.scene = scene
        self.frames: list[Any] = []
        self.disposed = False

    def sync(self, frame: Any) -> None:
        self.frames.append(frame)

    def dispose(self) -> None:
        self.disposed = True


class FakeRun:
    """The level run (`LevelRun`): it scrolls at `TRACK_SPEED` and records what it is asked."""

    def __init__(self, options: Any) -> None:
        self.options = options
        self.track = SimpleNamespace(distance=0.0, time=0.0, speed=TRACK_SPEED)
        self.fights = SimpleNamespace(
            bosses=[
                SimpleNamespace(rank="mini", at=600.0),
                SimpleNamespace(rank="final", at=1200.0),
            ]
        )
        self.phase = "playing"
        self.result = SimpleNamespace(level_id=options.level.id)
        self.ship = SimpleNamespace(x=240.0, y=90.0, vx=0.0)
        self.hull: Any = None
        self.blasts: list[Any] = []
        self.impacts: list[Any] = []
        self.hits: list[Any] = []
        self.bonuses: Any = None
        self.bombs: Any = None
        self.enemies = SimpleNamespace(enemies=["gnat"])
        self.shots = "shot-world"
        self.steps: list[tuple[float, Any]] = []
        self.seeks: list[float] = []
        self.broken = 0

    def step(self, dt: float, controls: Any) -> None:
        self.steps.append((dt, controls))
        self.track.time += dt
        self.track.distance += TRACK_SPEED * dt

    def seek(self, time: float) -> None:
        self.seeks.append(time)
        self.track.time = time
        self.track.distance = time * TRACK_SPEED

    def break_boss_part(self) -> None:
        self.broken += 1


class FakeHud:
    def __init__(self) -> None:
        self.frames: list[Any] = []
        self.disposed = False

    def update(self, frame: Any) -> None:
        self.frames.append(frame)

    def dispose(self) -> None:
        self.disposed = True


class FakeStats:
    """The debug tile: its updates, and whether its element left the page."""

    def __init__(self) -> None:
        self.updates: list[tuple[float, Any]] = []
        self.removed = False
        self.root = SimpleNamespace(remove=self._remove)

    def _remove(self) -> None:
        self.removed = True

    def update(self, dt: float, stats: Any) -> None:
        self.updates.append((dt, stats))


class FakeControls:
    """The game controls: each read, and the touch bomb button's taps."""

    def __init__(self) -> None:
        self.reads: list[tuple[float, float]] = []
        self.bombs = 0

    def read(self, dt: float, max_speed: float) -> str:
        self.reads.append((dt, max_speed))
        return "controls-" + str(len(self.reads))

    def bomb(self) -> None:
        self.bombs += 1


class Env:
    """The patched module: what it built, drew, compiled and showed."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.level = level()
        self.views: list[FakeView] = []
        self.runs: list[FakeRun] = []
        self.ships: list[FakeShip] = []
        self.layers: list[FakeLayer] = []
        self.shots: list[FakeShots] = []
        self.compiled: list[Any] = []
        self.enabled: list[bool] = []
        self.overlays: list[tuple[Any, str, Any, Any]] = []
        self.hud: Any = FakeHud()
        self.stats: Any = FakeStats()
        self.stats_made: list[Any] = []
        self.probes: list[tuple[Any, ...]] = []
        self.draw_calls = 42.0
        self.stats_shown = StatsShown()
        monkeypatch.setattr(game_play, "level_of", self._level_of)
        monkeypatch.setattr(game_play, "scenery_with_runout", lambda lvl: ("with-runout", lvl.id))
        monkeypatch.setattr(game_play, "build_level_scene", self._build)
        monkeypatch.setattr(game_play, "new_draw_call_counter", lambda scene: ("counter", scene))
        monkeypatch.setattr(game_play, "draw_calls_last_frame", self._draw_calls)
        monkeypatch.setattr(game_play, "PlayfieldShip", self._ship)
        monkeypatch.setattr(game_play, "LevelRun", self._run)
        monkeypatch.setattr(game_play, "EnemyLayer", self._layer)
        monkeypatch.setattr(game_play, "EnemyViewerShots", self._shots)
        monkeypatch.setattr(game_play, "compile_shaders", self.compiled.append)
        monkeypatch.setattr(game_play, "set_enabled", lambda _node, on: self.enabled.append(on))
        monkeypatch.setattr(game_play, "js_set", js_shims.js_set)
        monkeypatch.setattr(game_play, "level_state", self._level_state)
        monkeypatch.setattr(game_play, "sky_state", lambda view, sea, middle: (view, sea, middle))
        monkeypatch.setattr(game_play, "probe_readability", self._probe)
        monkeypatch.setattr(game_play, "create_level_overlays", self._overlays)
        monkeypatch.setattr(game_play, "create_stats", self._create_stats)
        monkeypatch.setattr(game_play, "hud_frame", self._hud_frame)
        monkeypatch.setattr(game_play, "STATS_SHOWN", self.stats_shown)
        monkeypatch.setattr(game_play, "playfield_eye", lambda _screen, framing: ("eye", framing))
        monkeypatch.setattr(
            game_play, "visible_half_width", lambda _framing, _aspect, _y: HALF_WIDTH
        )

    def _level_of(self, _game: Any, level_id: str) -> Any:
        assert level_id == self.level.id
        return self.level

    def _build(self, _engine: Any, _game: Any, options: Any) -> FakeView:
        view = FakeView(options)
        self.views.append(view)
        return view

    def _draw_calls(self, counter: Any) -> float:
        assert counter == ("counter", self.views[-1].scene)
        return self.draw_calls

    def _ship(self, scene: Any, scale: float, x: float, y: float) -> FakeShip:
        ship = FakeShip(scene, scale, x, y)
        self.ships.append(ship)
        return ship

    def _run(self, options: Any) -> FakeRun:
        run = FakeRun(options)
        self.runs.append(run)
        return run

    def _layer(self, scene: Any, models: Any, keys: list[str]) -> FakeLayer:
        layer = FakeLayer(scene, models, keys)
        self.layers.append(layer)
        return layer

    def _shots(self, game: Any, playfield: Any, style: Any) -> FakeShots:
        shots = FakeShots(game, playfield, style)
        self.shots.append(shots)
        return shots

    def _level_state(self, run: Any, time_scale: float, max_health: float) -> dict[str, Any]:
        return {"run": run, "time_scale": time_scale, "max_health": max_health}

    def _probe(self, *args: Any) -> str:
        self.probes.append(args)
        return "readability"

    def _overlays(self, options: Any, ship: str, texts: Any, on_bomb: Any) -> tuple[Any, Any]:
        self.overlays.append((options, ship, texts, on_bomb))
        shown = self.stats_shown.shown(bool(options.debug))
        return self.hud, self.stats if shown else None

    def _create_stats(self, options: Any) -> Any:
        self.stats_made.append(options)
        return self.stats

    def _hud_frame(self, run: Any, max_health: float, texts: Any, high_score: int) -> Any:
        return ("hud-frame", run, max_health, texts, high_score)


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(monkeypatch)


def gnat_kind(areas: list[Any]) -> SimpleNamespace:
    def spawn(area: Any) -> list[Any]:
        areas.append(area)
        return [SimpleNamespace(model="gnat-model")]

    return SimpleNamespace(id="gnat", spawn=spawn)


def make_game(*, bombs: bool = True, model: bool = True, weapons: Any = None) -> SimpleNamespace:
    areas: list[Any] = []
    view = SimpleNamespace(
        outline="outline",
        enemies=SimpleNamespace(glow="glow", models={"gnat-model": "gnat"}, child_models=["spark"]),
        player_ship_scale=2.0,
        player_ship_models={"alpha": "alpha-model"} if model else {},
        bonuses=FakeRenderer,
        bombs=FakeRenderer if bombs else None,
    )
    return SimpleNamespace(
        playfield=SimpleNamespace(width=480, height=720, viewport=None),
        player_ships=PlayerShipRoster(BASE_SPEED, [PlayerShipDefinition("alpha", "Alpha", 2, 5)]),
        player_weapons=["guns", "laser"] if weapons is None else weapons,
        enemy_kinds=[gnat_kind(areas)],
        boss_kinds=[
            SimpleNamespace(id="warden", spawn=lambda _area: SimpleNamespace(model="boss"))
        ],
        bonuses="bonus-rules",
        bombs="bomb-rules",
        hull="hull-rules",
        boss_fights="boss-rules",
        texts="texts",
        view=view,
        areas=areas,
    )


def level(*, bosses: Any = "warden") -> SimpleNamespace:
    level_bosses = None if bosses is None else [SimpleNamespace(kind=bosses)]
    return SimpleNamespace(
        id="1-1",
        waves=[SimpleNamespace(kind="gnat", entry="left")],
        bosses=level_bosses,
        scenery=SimpleNamespace(sea="sea"),
    )


def options(**overrides: Any) -> GamePlayOptions:
    completed: list[Any] = []
    values: dict[str, Any] = {
        "environment": False,
        "debug": False,
        "start_time": 0.0,
        "start_boss": None,
        "resume": None,
        "journey": None,
        "weapons": None,
        "supplies": None,
        "high_score": None,
        "atmosphere": "atmosphere",
        "doc": "doc",
        "stats_parent": "stats-parent",
        "hud_parent": "hud-parent",
        "on_complete": completed.append,
        "on_step": None,
        "on_draw_calls": None,
    }
    values.update(overrides)
    return GamePlayOptions(*values.values())


def make_play(game: Any = None, **overrides: Any) -> tuple[GamePlay, FakeControls]:
    controls = FakeControls()
    played = game if game is not None else make_game()
    play = GamePlay("engine", played, GameChoice("alpha", "1-1"), controls, options(**overrides))
    return play, controls


def test_game_level_08_the_scene_is_built_over_the_level_with_its_runout(env: Env) -> None:
    """Also GAME-SCREEN-03: the environment's outline only with a real WebGL engine."""
    make_play()
    scene_options = env.views[0].options
    assert scene_options.level == ("with-runout", "1-1")
    assert (scene_options.environment, scene_options.glow) == (False, "glow")
    assert scene_options.environment_cube_size == int(CFG.environment_cube_size)
    assert (scene_options.atmosphere, scene_options.outline) == ("atmosphere", None)
    make_play(environment=True)
    assert env.views[1].options.outline == "outline"


def test_game_ship_07_the_run_starts_the_ship_at_the_bottom_in_the_middle(env: Env) -> None:
    """Also GAME-WPN-05: the muzzle is at the model's nose, set in by `muzzle_inset`."""
    make_play(weapons="kept", supplies="supplies", resume="checkpoint")
    run_options = env.runs[0].options
    ship = run_options.ship
    assert (ship.start.x, ship.start.y) == (240, CFG.ship_start_y)
    assert ship.max_speed == SPEED
    assert ship.acceleration_seconds == GAME_CONTROLS_CONFIG.acceleration_seconds
    assert ship.muzzle_offset == max(0, NOSE - CFG.muzzle_inset)
    assert ship.max_health == 5
    assert (run_options.weapon, run_options.weapons) == ("guns", ["guns", "laser"])
    assert (run_options.start_weapons, run_options.start_supplies) == ("kept", "supplies")
    assert (run_options.checkpoint, run_options.journey) == ("checkpoint", CFG.journey)
    assert run_options.eye == ("eye", "framing")
    assert (run_options.bonuses, run_options.bombs, run_options.hull) == (
        "bonus-rules",
        "bomb-rules",
        "hull-rules",
    )
    assert env.ships[0].model == "alpha-model"
    assert env.ships[0].scale == 2.0


def test_game_wpn_05_a_ship_without_a_model_fires_from_its_pivot(env: Env) -> None:
    make_play(make_game(model=False))
    assert env.ships[0].model is None
    assert env.runs[0].options.ship.muzzle_offset == 0


def test_the_ship_does_not_fly_in_and_off_when_the_journey_is_off(env: Env) -> None:
    make_play(journey=False)
    assert env.runs[0].options.journey is None


@pytest.mark.usefixtures("env")
def test_a_game_without_a_player_weapon_cannot_be_played() -> None:
    with pytest.raises(ValueError, match="no player weapon"):
        make_play(make_game(weapons=[]))


def test_perf_21_the_enemy_models_of_the_level_are_those_of_its_waves_and_bosses(env: Env) -> None:
    """The enemies the others send out come after them; the kinds spawn in the playfield."""
    game = make_game()
    make_play(game)
    layer = env.layers[0]
    assert layer.keys == ["gnat-model", "boss", "spark"]
    assert layer.models == {"gnat-model": "gnat"}
    (area,) = game.areas
    assert (area.width, area.height, area.entry) == (480, 720, "left")


def test_perf_21_a_level_without_bosses_needs_only_its_wave_models(env: Env) -> None:
    env.level = level(bosses=None)
    game = make_game()
    game.boss_kinds = None
    make_play(game)
    assert env.layers[0].keys == ["gnat-model", "spark"]


def test_game_screen_04_only_what_the_tilted_camera_shows_is_in_view(env: Env) -> None:
    """Also GAME-WPN-16 and ENM-13: the run is told what can be hit."""
    make_play()
    in_view = env.runs[0].options.in_view
    assert in_view(240, 0) is True
    assert in_view(240 + HALF_WIDTH, 720) is True
    assert in_view(240 + HALF_WIDTH + 1, 360) is False
    assert in_view(240, -1) is False
    assert in_view(240, 721) is False


def test_game_screen_05_the_ship_flies_inside_what_the_camera_shows(env: Env) -> None:
    make_play()
    bounds = env.runs[0].options.bounds
    margin = CFG.ship_margin
    assert (bounds.min_y, bounds.max_y) == (margin.bottom, 720 - margin.top)
    assert bounds.center_x == 240
    assert bounds.half_width_at(100) == HALF_WIDTH - margin.side


def test_dev_opt_02_the_level_starts_at_the_time_asked(env: Env) -> None:
    make_play(start_time=12.5)
    assert env.runs[0].seeks == [12.5]
    # The first frame is drawn there, not scrolled from the start.
    assert env.views[0].updates[0] == (12.5 * TRACK_SPEED, 0)


def test_dev_opt_03_the_level_starts_at_the_boss_asked(env: Env) -> None:
    make_play(start_boss="final")
    assert env.runs[0].seeks == [1200.0 / TRACK_SPEED]
    make_play(start_boss="other")
    assert env.runs[1].seeks == []


def test_game_level_15_the_level_runs_at_a_fixed_step_whatever_the_frame_rate(env: Env) -> None:
    """Also AUD-ENGINE-09: each step is heard."""
    heard: list[Any] = []
    play, controls = make_play(on_step=heard.append)
    run = env.runs[0]
    play.frame(0.05)
    step = 1 / CFG.step_hz
    assert [dt for dt, _ in run.steps] == [pytest.approx(step)] * 3
    assert [state for _, state in run.steps] == ["controls-1", "controls-2", "controls-3"]
    assert controls.reads == [(pytest.approx(step), SPEED)] * 3
    assert heard == [run, run, run]


def test_eng_100_the_scroll_is_drawn_between_two_steps(env: Env) -> None:
    play, _ = make_play()
    play.frame(0.025)
    # One step of 1 / 60 s run, and half of the next: the scroll is drawn half way.
    distance, dt = env.views[0].updates[-1]
    assert distance == pytest.approx(0.5 * TRACK_SPEED / CFG.step_hz)
    assert dt == 0.025


def test_gfx_fx_01_the_blasts_impacts_and_hits_of_the_steps_are_drawn(env: Env) -> None:
    """Also GFX-FX-04 (a hit that cost a life blows up at the ship) and GFX-FX-03.

    D-321: a missile hit blows up a little where it hit; a bullet hit does not.
    """
    play, _ = make_play()
    run = env.runs[0]
    run.blasts = ["enemy-blast"]
    missile = ShotImpact("missile", 50, 60, 10, False)
    bullet = ShotImpact("bullet", 70, 80, 0, False)
    run.impacts = [missile, bullet]
    run.hits = [LandedHit("bullet", 10, 20, "hit"), LandedHit("bullet", 0, 0, "life")]
    play.frame(0.05)
    frame = env.shots[0].drawn[-1]
    assert frame.enemies is run.enemies
    assert frame.shots == "shot-world"
    assert frame.impacts == [missile, bullet] * 3
    assert frame.dt == 0.05
    sparks = [blast for blast in frame.blasts if blast != "enemy-blast"]
    assert len(sparks) == 9
    assert (sparks[0].kind, sparks[0].x, sparks[0].y) == ("missile", 10, 20)
    assert (sparks[1].kind, sparks[1].x, sparks[1].y) == ("enemy", 240.0, 90.0)
    assert (sparks[2].kind, sparks[2].x, sparks[2].y, sparks[2].radius) == ("missile", 50, 60, 10)
    assert frame.blasts.count("enemy-blast") == 3


def test_the_enemies_bonuses_and_bomb_are_drawn_on_the_playfield(env: Env) -> None:
    game = make_game()
    play, _ = make_play(game)
    run = env.runs[0]
    run.bonuses = SimpleNamespace(bonuses=["falling"], picked=["picked"])
    run.bombs = SimpleNamespace(active="bomb")
    play.frame(0.05)
    assert env.layers[0].synced[-1] == (["gnat"], 0.05)
    bonuses = play._bonuses.frames[-1]
    assert (bonuses.bonuses, bonuses.picked, bonuses.dt_seconds) == (
        ["falling"],
        ["picked"] * 3,
        0.05,
    )
    bomb = play._bombs.frames[-1]
    assert (bomb.bomb, bomb.dt_seconds) == ("bomb", 0.05)
    run.bombs = None
    play.frame(0.05)
    assert play._bombs.frames[-1].bomb is None


def test_without_bonuses_or_a_bomb_renderer_none_is_drawn(env: Env) -> None:
    play, _ = make_play(make_game(bombs=False))
    play.frame(0.05)
    assert play._bombs is None
    assert play._bonuses.frames[-1].bonuses == []
    assert env.layers[0].synced[-1][0] == ["gnat"]


def test_gfx_read_08_the_ship_is_drawn_where_it_flies_and_banks(env: Env) -> None:
    """Also GAME-SHIP-05 and GAME-LIFE-07 (hidden once the game is over)."""
    play, _ = make_play()
    run = env.runs[0]
    run.ship = SimpleNamespace(x=100.0, y=50.0, vx=SPEED)
    play.frame(10.0)
    pivot = env.ships[0].pivot
    assert (pivot.position.x, pivot.position.y, pivot.position.z) == (100.0, 50.0, 0)
    assert pivot.rotation.y == pytest.approx(-math.radians(CFG.roll.max_deg))
    assert play.roll == pivot.rotation.y
    assert env.ships[0].dts[-1] == 10.0
    assert env.enabled[-1] is True
    run.phase = "over"
    play.frame(0)
    assert env.enabled[-1] is False


def test_ui_hud_02_the_hud_follows_the_run_once_attached(env: Env) -> None:
    """Also GAME-SCORE-07: the saved high score, 0 without one."""
    play, _ = make_play()
    play.frame(0.05)
    assert env.hud.frames == []
    play.attach()
    play.frame(0.05)
    assert env.hud.frames[-1] == ("hud-frame", env.runs[0], 5, "texts", 0)
    play2, _ = make_play(high_score=900)
    play2.attach()
    assert env.hud.frames[-1] == ("hud-frame", env.runs[1], 5, "texts", 900)
    play2.frame(0.05)
    assert env.hud.frames[-1][4] == 900


def test_dev_perf_04_the_debug_tile_shows_the_fps_and_polygons(env: Env) -> None:
    play, _ = make_play(debug=True)
    play.attach()
    for _ in range(3):
        play.frame(0.5)
    dt, stats = env.stats.updates[-1]
    assert dt == 0.5
    # Four frames drawn (with the first, of 0 s), one every 0.5 s.
    assert stats.fps == pytest.approx(2.0)
    assert stats.polygons == 100.0


def test_eng_106_the_draw_calls_of_the_last_frame_are_reported(env: Env) -> None:
    counts: list[float] = []
    play, _ = make_play(on_draw_calls=counts.append)
    env.draw_calls = 17.0
    play.frame(0.05)
    assert counts == [42.0, 17.0]


def test_game_level_13_a_completed_level_reports_its_result_once(env: Env) -> None:
    completed: list[Any] = []
    play, _ = make_play(on_complete=completed.append)
    run = env.runs[0]
    play.frame(0.05)
    assert completed == []
    run.phase = "complete"
    play.frame(0.05)
    play.frame(0.05)
    assert completed == [run.result]


def test_ui_over_05_the_game_over_waits_a_little_before_its_overlay(env: Env) -> None:
    """Also GAME-LIFE-09: the time counts at the level's pace."""
    completed: list[Any] = []
    play, _ = make_play(on_complete=completed.append, debug=True)
    run = env.runs[0]
    run.phase = "over"
    play.frame(CFG.damage.game_over_delay / 2)
    assert completed == []
    assert play.debug_key("KeyF", True) is True
    play.frame(CFG.damage.game_over_delay / 8)
    assert completed == [run.result]


def test_dev_opt_08_the_playback_keys_fast_forward_and_jump(env: Env) -> None:
    """Also DEV-OPT-09: K breaks the next part of the boss fought."""
    play, _ = make_play(debug=True)
    run = env.runs[0]
    assert play.time_scale == 1
    assert play.debug_key("KeyF", True) is True
    assert play.time_scale == CFG.debug.fast_forward
    assert play.debug_key("KeyF", False) is True
    assert play.time_scale == CFG.debug.fast_forward
    play.frame(0.05)
    assert len(run.steps) == 12
    assert play.debug_key("KeyF", True) is True
    assert play.time_scale == 1
    assert play.debug_key("KeyK", True) is True
    assert run.broken == 1
    run.track.time = 30.0
    assert play.debug_key("ArrowRight", True) is True
    assert play.debug_key("ArrowLeft", True) is True
    assert run.seeks == [30.0 + CFG.debug.seek_step, 30.0]
    assert play._previous == run.track.distance
    assert play.debug_key("KeyQ", True) is False


def test_dev_opt_10_without_debug_mode_no_playback_key_is_used(env: Env) -> None:
    play, _ = make_play(debug=False)
    for code in ["KeyF", "KeyK", "ArrowLeft", "ArrowRight"]:
        assert play.debug_key(code, True) is False
    assert play.time_scale == 1
    assert env.runs[0].broken == 0


def test_a_completed_level_is_not_moved_by_a_jump(env: Env) -> None:
    play, _ = make_play(debug=True)
    run = env.runs[0]
    run.phase = "complete"
    play.frame(0.05)
    assert play.debug_key("ArrowRight", True) is True
    assert run.seeks == []


def test_d212_its_key_shows_and_hides_the_debug_tile_in_any_mode(env: Env) -> None:
    """Also DEV-PERF-05: before the level is in the page, only the choice flips."""
    play, _ = make_play(debug=False)
    assert play.debug_key(CFG.stats.key, True) is True
    assert env.stats_shown.chosen is True
    assert env.stats_made == []
    assert play.debug_key(CFG.stats.key, False) is True
    assert env.stats_shown.chosen is True
    play.attach()
    assert play._stats is env.stats
    play.debug_key(CFG.stats.key, True)
    assert env.stats.removed is True
    assert play._stats is None
    play.debug_key(CFG.stats.key, True)
    assert play._stats is env.stats
    (made,) = env.stats_made
    assert (made.doc, made.debug, made.stats_parent, made.hud_parent) == (
        "doc",
        False,
        "stats-parent",
        "hud-parent",
    )


def test_d212_a_key_press_without_a_tile_parent_shows_none(env: Env) -> None:
    env.stats = None
    play, _ = make_play(debug=True)
    play.attach()
    assert play._stats is None
    # Hidden, then shown again: the tile has no parent, so none is made.
    play.debug_key(CFG.stats.key, True)
    play.debug_key(CFG.stats.key, True)
    assert play._stats is None


def test_perf_13_the_hud_joins_the_page_when_the_level_starts_only_once(env: Env) -> None:
    """Also GAME-CTRL-06: the HUD's bomb button sets a bomb off."""
    play, controls = make_play(debug=True)
    assert env.overlays == []
    play.attach()
    play.attach()
    ((overlays, ship, texts, on_bomb),) = env.overlays
    assert (overlays.doc, overlays.debug, overlays.stats_parent, overlays.hud_parent) == (
        "doc",
        True,
        "stats-parent",
        "hud-parent",
    )
    assert (ship, texts) == ("Alpha", "texts")
    on_bomb()
    assert controls.bombs == 1
    assert len(env.hud.frames) == 1


def test_ui_hud_01_a_level_without_a_hud_parent_has_no_hud(env: Env) -> None:
    env.hud = None
    play, _ = make_play()
    play.attach()
    play.frame(0.05)
    play.dispose()
    assert play._hud is None


def test_dev_api_03_the_state_reports_the_run_and_the_sky_where_the_view_is(env: Env) -> None:
    """Also DEV-API-05."""
    play, _ = make_play(debug=True)
    run = env.runs[0]
    run.track.distance = 100.0
    play.debug_key("KeyF", True)
    state = play.state
    assert state["run"] is run
    assert (state["time_scale"], state["max_health"]) == (CFG.debug.fast_forward, 5)
    assert state["sky"] == (env.views[0], "sea", 100.0 + 360)


def test_dev_api_09_the_readability_probe_reads_the_scene_and_the_run(env: Env) -> None:
    play, _ = make_play()
    assert play.readability(0.25) == "readability"
    ((scene, root, run, in_view, share),) = env.probes
    assert (scene, root, run, share) == (env.views[0].scene, "playfield-root", env.runs[0], 0.25)
    assert in_view(240, 360) is True


def test_perf_20_the_scene_and_the_models_built_ahead_compile_their_shaders(env: Env) -> None:
    """Also PERF-23: one model built ahead per frame, compiled once asked."""
    play, _ = make_play()
    # The first frame built the first model; nothing compiles until asked.
    assert env.compiled == []
    play.prepare(False)
    assert env.compiled == []
    play.prepare(True)
    assert env.compiled == [["sky-mesh", "ground-mesh"]]
    play.frame(0.05)
    assert env.compiled[-1] == ["warden-mesh"]


def test_perf_20_the_level_shows_one_bullet_of_each_colour_while_it_loads(env: Env) -> None:
    play, _ = make_play()
    play.warm_shots(True)
    play.warm_shots(False)
    assert env.shots[0].warmed == [True, False]
    assert env.shots[0].style == "shot-style"


def test_perf_21_the_enemy_models_are_built_one_a_frame_while_loading(env: Env) -> None:
    play, _ = make_play()
    # The first frame built the first; the next is built and compiled here.
    assert play.build_enemies(True) is False
    assert env.compiled == [["warden-mesh"]]
    assert play.build_enemies(False) is True
    assert env.compiled == [["warden-mesh"]]


def test_dispose_releases_the_models_shots_overlays_and_scene(env: Env) -> None:
    play, _ = make_play(debug=True)
    play.attach()
    play.dispose()
    assert env.layers[0].disposed
    assert env.shots[0].disposed
    assert play._bonuses.disposed
    assert play._bombs.disposed
    assert env.stats.removed
    assert env.hud.disposed
    assert env.views[0].scene.disposed


def test_dispose_without_a_bomb_renderer_or_debug_tile(env: Env) -> None:
    play, _ = make_play(make_game(bombs=False))
    play.dispose()
    assert env.layers[0].disposed
    assert env.stats.removed is False
    assert env.views[0].scene.disposed


# -- The ship's bank and blink (GAME-SHIP-05, GFX-SHIP-08, GAME-LIFE-07) ---------------------------
# The level and its ship are not built: a `GamePlay` with only the fields these read.


def _bare_play(
    speed: float = 300.0, roll: float = 0.0, phase: str = "playing", hull: Any = None
) -> GamePlay:
    play = GamePlay.__new__(GamePlay)
    play._speed = speed
    play._roll = roll
    play.run = SimpleNamespace(phase=phase, hull=hull)
    return play


def _hull(invincible: float) -> SimpleNamespace:
    return SimpleNamespace(invincible=invincible)


def test_game_ship_05_the_ship_banks_at_full_sideways_speed_up_to_max_deg() -> None:
    """Flying right, the ship dips to the right's negative bank; flying left, the other way."""
    max_bank = math.radians(CFG.roll.max_deg)
    play = _bare_play(speed=300.0)
    assert play._bank(300.0, 10.0) == pytest.approx(-max_bank)
    assert play._bank(-300.0, 10.0) == pytest.approx(max_bank)


def test_game_ship_05_the_bank_is_proportional_to_the_sideways_speed() -> None:
    max_bank = math.radians(CFG.roll.max_deg)
    play = _bare_play(speed=300.0)
    assert play._bank(150.0, 10.0) == pytest.approx(-max_bank / 2)


def test_gfx_ship_08_the_bank_eases_towards_its_target_and_back_to_level() -> None:
    """Each step closes a share `ease_per_sec * dt` of the gap.

    The share is capped at the whole gap; with no sideways speed the bank goes back to level.
    """
    max_bank = math.radians(CFG.roll.max_deg)
    play = _bare_play(speed=300.0)
    step = 0.05
    share = min(1, CFG.roll.ease_per_sec * step)
    banked = play._bank(300.0, step)
    assert banked == pytest.approx(-max_bank * share)
    settled = banked
    for _ in range(200):
        settled = play._bank(0.0, step)
    assert settled == pytest.approx(0.0, abs=1e-9)


def test_game_life_07_the_ship_is_hidden_once_the_game_is_over() -> None:
    assert _bare_play(phase="over", hull=_hull(1.0))._ship_shown() is False


def test_game_life_07_the_ship_shows_when_it_is_not_invincible() -> None:
    assert _bare_play(hull=_hull(0.0))._ship_shown() is True
    assert _bare_play(hull=None)._ship_shown() is True


def test_game_life_07_the_ship_blinks_every_0_05_seconds_while_invincible() -> None:
    """Blinking at `blink_hz` (10): shown and hidden alternately every 0.05 s over 2 s.

    The 2 s are the invincibility, and the blink is sampled in the middle of each 0.05 s step.
    """
    step = 1 / (2 * CFG.damage.blink_hz)
    assert step == pytest.approx(0.05)
    shown = []
    for i in range(40):
        invincible = 2.0 - (i + 0.5) * step
        shown.append(_bare_play(hull=_hull(invincible))._ship_shown())
    assert all(a != b for a, b in itertools.pairwise(shown))
    assert shown[0] is False
