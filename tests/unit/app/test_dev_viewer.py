# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/dev_viewer.py` (D-199): the dev viewers, over a fake level scene."""

import math
from types import SimpleNamespace
from typing import Any, ClassVar

import pytest
from helpers.fakes import ProbeBoss

from app import dev_viewer
from app.dev_catalog import DevItem
from app.dev_viewer import DevViewer, clock_text, close_up_fov, eased_time, zoomed, zoomed_fov
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG
from core.entities.boss import BossDeath, BossPartSpec, BossStats

ALTITUDE = 320.0


class FakeCamera:
    def __init__(self) -> None:
        self.fov = 0.8
        self.position = SimpleNamespace(x=0.0, y=ALTITUDE + 100, z=0.0)
        self.position.set = self._set
        self.target = SimpleNamespace(x=0.0, y=0.0, z=0.0)

    def _set(self, x: float, y: float, z: float) -> None:
        self.position.x, self.position.y, self.position.z = x, y, z

    def getTarget(self) -> Any:
        return self.target

    def setTarget(self, target: Any) -> None:
        self.target = target


class FakeStage:
    def __init__(self) -> None:
        self.camera = FakeCamera()
        # Looking down at 45°: the middle of the view is 100 ahead of the camera, on the flight
        # plane.
        self.framing = SimpleNamespace(direction=[-1.0, 1.0], back=-50.0, height=100.0)


class FakeView:
    def __init__(self, stage: FakeStage) -> None:
        self.stage = stage
        self.scene = SimpleNamespace(disposed=False)
        self.scene.dispose = lambda: setattr(self.scene, "disposed", True)
        self.track = SimpleNamespace(duration=100.0, speed=10.0, length_=1000.0)
        self.playfield = SimpleNamespace(run=lambda create: create(), root="playfield-root")
        self.updates: list[tuple[float, float]] = []

    def update(self, distance: float, dt: float) -> None:
        self.updates.append((distance, dt))
        camera = self.stage.camera
        camera.position.x = 0.0
        camera.position.z = distance + self.stage.framing.back
        camera.target = SimpleNamespace(x=0.0, y=ALTITUDE, z=camera.position.z + 100)


def pivot() -> SimpleNamespace:
    return SimpleNamespace(rotation=SimpleNamespace(x=0.0, y=0.0, z=0.0))


class FakeShip:
    made: ClassVar[list["FakeShip"]] = []

    def __init__(self, _scene: Any, _scale: float, x: float, y: float) -> None:
        self.at = (x, y)
        self.pivot = pivot()
        self.model: Any = None
        self.dt = 0.0
        FakeShip.made.append(self)

    def show(self, model: Any) -> float:
        self.model = model
        return 0.0

    def update(self, dt: float) -> None:
        self.dt += dt


class FakeLayer:
    def __init__(self, _scene: Any, _models: Any, _keys: list[str]) -> None:
        self.synced: list[Any] = []
        self.disposed = False
        self.pivot = pivot()

    def pivot_of(self, enemy: Any) -> Any:
        return self.pivot if enemy in self.synced else None

    def sync(self, enemies: list[Any], _dt: float) -> None:
        self.synced = enemies

    def dispose(self) -> None:
        self.disposed = True


class FakeBlasts:
    """The explosions' renderer: every list of blasts it drew."""

    made: ClassVar[list["FakeBlasts"]] = []

    def __init__(self, _scene: Any) -> None:
        self.drawn: list[Any] = []
        self.disposed = False
        FakeBlasts.made.append(self)

    def sync(self, blasts: list[Any], _dt: float) -> None:
        self.drawn.extend(blasts)

    def dispose(self) -> None:
        self.disposed = True


class FakePropStage:
    made: ClassVar[list["FakePropStage"]] = []

    def __init__(self, _engine: Any, _game: Any, _environment: bool) -> None:
        self.scene = SimpleNamespace(name="props-scene")
        self.shown: list[str] = []
        self.updates: list[tuple[list[float], bool, float]] = []
        self.disposed = False
        FakePropStage.made.append(self)

    def show(self, item: DevItem) -> None:
        self.shown.append(item.id)

    def update(self, turn: list[float], close_up: bool, zoom: float) -> None:
        self.updates.append((list(turn), close_up, zoom))

    def dispose(self) -> None:
        self.disposed = True


class Env:
    """The patched module: the ground ready or not, the scenes built, the nodes disposed."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch) -> None:
        self.ready = True
        self.views: list[FakeView] = []
        self.disposed: list[Any] = []
        FakeShip.made = []
        monkeypatch.setattr(dev_viewer, "prepare_level", lambda _game, _level: self.ready)
        monkeypatch.setattr(dev_viewer, "level_of", lambda _game, level: SimpleNamespace(id=level))
        monkeypatch.setattr(dev_viewer, "scenery_with_runout", lambda level: level)
        monkeypatch.setattr(dev_viewer, "build_level_scene", self._build)
        self.groundless: list[Any] = []
        monkeypatch.setattr(dev_viewer, "build_model_scene", self._build_groundless)
        FakeBlasts.made = []
        monkeypatch.setattr(dev_viewer, "PlayfieldShip", FakeShip)
        monkeypatch.setattr(dev_viewer, "EnemyLayer", FakeLayer)
        monkeypatch.setattr(dev_viewer, "dispose_node", self.disposed.append)
        bounds = SimpleNamespace(
            min=SimpleNamespace(x=0, y=0, z=0), max=SimpleNamespace(x=40, y=10, z=20)
        )
        monkeypatch.setattr(dev_viewer, "get_hierarchy_bounding_vectors", lambda _root: bounds)
        monkeypatch.setattr(dev_viewer, "DevPropStage", FakePropStage)
        monkeypatch.setattr(dev_viewer, "vector3", lambda x, y, z: SimpleNamespace(x=x, y=y, z=z))
        FakePropStage.made = []

    def _build_groundless(self, engine: Any, game: Any, _level: Any, options: Any) -> FakeView:
        view = self._build(engine, game, options)
        self.groundless.append(view)
        return view

    def _build(self, _engine: Any, _game: Any, options: Any) -> FakeView:
        view = FakeView(FakeStage())
        view.level = options.level
        self.views.append(view)
        return view


class FakeEnemy:
    """Comes in from above the playfield and flies down at `speed`, turning as it goes."""

    def __init__(self, item_id: str, expires: bool = True, speed: float = 100.0) -> None:
        self.id = item_id
        self.model = item_id
        self.x = 240.0
        self.y = 760.0
        self.heading = math.pi
        self.age = 0.0
        self.gone = False
        self.expires = expires
        self.radius = 20.0
        self.speed = speed
        self.contexts: list[Any] = []

    def update(self, ctx: Any, dt: float) -> None:
        self.contexts.append(ctx)
        self.y -= self.speed * dt
        self.heading += dt


def spawned(kind_id: str) -> Any:
    def spawn(_area: Any) -> list[Any]:
        return [FakeEnemy(kind_id)]

    return spawn


def game() -> SimpleNamespace:
    scenery = SimpleNamespace(camera=SimpleNamespace(flightAltitude=ALTITUDE))
    scenery_dict = {"propModels": {"hut": "hut-factory"}}
    view = SimpleNamespace(
        enemies=SimpleNamespace(glow="glow", models={}, blasts=FakeBlasts),
        outline="outline",
        player_ship_models={"alpha": "alpha-model"},
        player_ship_scale=2.0,
        scenery=SimpleNamespace(camera=scenery.camera, __getitem__=None),
    )
    view.scenery = FakeScenery(scenery.camera, scenery_dict)
    boss = FakeEnemy("warden", expires=False, speed=0.0)
    return SimpleNamespace(
        view=view,
        playfield=SimpleNamespace(width=480, height=720),
        enemy_kinds=[SimpleNamespace(id="gnat", spawn=spawned("gnat"))],
        boss_kinds=[SimpleNamespace(id="warden", spawn=lambda _area: boss)],
    )


class FakeScenery:
    def __init__(self, camera: Any, fields: dict[str, Any]) -> None:
        self.camera = camera
        self._fields = fields

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]


def viewer(name: str, items: list[DevItem]) -> DevViewer:
    return DevViewer("engine", game(), name, items, environment=True)


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(monkeypatch)


def test_d199_the_clock_reads_minutes_and_seconds() -> None:
    assert clock_text(0) == "0:00"
    assert clock_text(65.9) == "1:05"
    assert clock_text(600) == "10:00"
    assert clock_text(-3) == "0:00"


def test_d199_the_close_up_fills_its_share_of_the_screen_and_never_widens() -> None:
    """DEV-MENU-09."""
    fov = close_up_fov(10, 100, 0.5, 1.0)
    assert math.isclose(2 * 100 * math.tan(fov / 2) * 0.5, 10)
    assert close_up_fov(1000, 100, 0.5, 1.0) == 1.0
    assert close_up_fov(0, 100, 0.5, 1.0) == 1.0


def test_d199_the_time_eases_towards_the_wheel_without_overshooting() -> None:
    assert eased_time(0, 10, 2, 0.25) == 5
    assert eased_time(0, 10, 2, 1) == 10


def test_d199_the_scene_waits_for_the_level_ground(env: Env) -> None:
    """DEV-MENU-08."""
    env.ready = False
    v = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    v.frame(0.1)
    assert v.scene is None
    assert v.status == CFG.texts.loading
    env.ready = True
    v.frame(0.1)
    assert v.scene is env.views[0].scene
    assert env.views[0].level.id == "1-1"
    assert v.status == ""


def test_d199_a_ship_is_shown_at_the_middle_of_the_view_in_close_up(env: Env) -> None:
    """DEV-MENU-12."""
    v = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    v.show(0, toggle=True)
    v.frame(0.1)
    ship = FakeShip.made[0]
    # The camera is 100 above the flight plane, looking down at 45°: the middle is 100 ahead.
    assert ship.at == (240, -50 + 100)
    assert ship.model == "alpha-model"
    assert ship.dt == pytest.approx(0.1)
    camera = env.views[0].stage.camera
    assert camera.fov < 0.8
    v.show(0, toggle=False)
    v.frame(0.1)
    assert camera.fov == 0.8


def test_d199_another_item_replaces_the_model_on_the_same_scene(env: Env) -> None:
    items = [DevItem("alpha", "Alpha", "1-1"), DevItem("beta", "Beta", "1-1")]
    v = viewer("ships", items)
    v.frame(0)
    v.show(1, toggle=True)
    v.frame(0)
    assert len(env.views) == 1
    assert env.disposed == [FakeShip.made[0].pivot]
    assert FakeShip.made[1].model is None
    # Out of range: the last item.
    v.show(9, toggle=True)
    assert v._index == 1


class Drawn:
    """What the fake layer saw of the enemy while it drew it."""

    def __init__(self, layer: Any) -> None:
        self.at: list[tuple[float, float, float]] = []
        original = layer.sync

        def sync(enemies: list[Any], dt: float) -> None:
            for enemy in enemies:
                self.at.append((enemy.x, enemy.y, enemy.heading))
            original(enemies, dt)

        layer.sync = sync


@pytest.mark.usefixtures("env")
def test_d199_an_enemy_lives_its_own_life_but_is_drawn_at_the_middle() -> None:
    """DEV-MENU-13."""
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    drawn = Drawn(v._layer)
    v.frame(0.5)
    enemy = v._enemy
    # It flew down for 0.5 s (in the game's steps) and turned, but is drawn at the middle.
    assert enemy.age == pytest.approx(0.5)
    assert enemy.y == pytest.approx(760 - 50)
    assert drawn.at[-1] == (240, 50, pytest.approx(math.pi + 0.5))
    ctx = enemy.contexts[0]
    assert (ctx.width, ctx.height, ctx.player_x) == (480, 720, 240)
    assert ctx.fire_rate == 1.0


@pytest.mark.usefixtures("env")
def test_d199_an_enemy_that_left_the_playfield_comes_again() -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    first = v._enemy
    for _ in range(20):
        v.frame(0.5)
    # From 760 down past the bottom of the playfield and its margin: a new one came.
    assert v._enemy is not first
    assert v._enemy.y > 0


@pytest.mark.usefixtures("env")
def test_d199_an_enemy_gone_or_too_old_comes_again() -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    first = v._enemy
    first.gone = True
    v.frame(0.1)
    assert v._enemy is not first
    second = v._enemy
    second.speed = 0
    second.age = dev_viewer.GAME_PLAY_CONFIG.max_enemy_age + 1
    v.frame(0.1)
    assert v._enemy is not second


@pytest.mark.usefixtures("env")
def test_d199_a_boss_does_not_expire() -> None:
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1")])
    v.frame(0)
    boss = v._enemy
    boss.age = 1e6
    v.frame(0.1)
    assert v._enemy is boss


def test_d199_the_enemy_world_drops_what_the_enemy_does_but_keeps_what_blows_up() -> None:
    ctx = dev_viewer.DevEnemyContext(SimpleNamespace(width=100, height=200), "random")
    point = ctx.seen(SimpleNamespace(x=3, y=4, z=9))
    assert (point.x, point.y) == (3, 4)
    assert ctx.fire_bullet(0, 0, 0, None) is None
    assert ctx.fire_missile(0, 0, 0, None) is None
    assert ctx.fire_laser(None, None) is None
    assert ctx.spawn(None) is None
    assert ctx.random == "random"
    ctx.explode(5, 6, 1)
    ctx.break_part(SimpleNamespace(x=7, y=8, radius=2))
    assert [(b.x, b.y, b.radius) for b in ctx.blasts] == [(5, 6, 1), (7, 8, 2)]


@pytest.mark.usefixtures("env")
def test_d199_a_boss_is_spawned_too_and_an_unknown_kind_is_an_error() -> None:
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1"), DevItem("x", "X", "1-1")])
    v.frame(0)
    assert v._layer.synced[0].id == "warden"
    v.show(1, toggle=True)
    with pytest.raises(ValueError, match="No enemy kind"):
        v.frame(0)


def test_d199_the_levels_viewer_scrubs_within_the_level_and_plays(env: Env) -> None:
    """DEV-MENU-18."""
    v = viewer("levels", [DevItem("1-1", "1-1", "1-1")])
    v.frame(0)
    v.scrub(-500)
    v.frame(1)
    assert v._time == 0
    v.scrub(CFG.wheel_step * 5)
    for _ in range(100):
        v.frame(1)
    assert v._time == pytest.approx(5 * CFG.scrub_seconds)
    assert env.views[0].updates[-1][0] == pytest.approx(v._time * 10)
    assert v.status == clock_text(v._time) + " / 1:40"
    v.scrub(1e9)
    v.show(0, toggle=True)
    for _ in range(50):
        v.frame(1)
    assert v._time == pytest.approx(100)


@pytest.mark.usefixtures("env")
def test_d199_a_viewer_without_items_does_nothing() -> None:
    v = viewer("bosses", [])
    v.frame(1)
    assert v.scene is None


def test_d199_dispose_drops_the_model_and_the_scene(env: Env) -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    layer = v._layer
    v.dispose()
    assert layer.disposed
    assert env.views[0].scene.disposed
    assert v.scene is None


@pytest.mark.usefixtures("env")
def test_d199_a_drag_turns_a_ship_and_the_turn_is_kept_for_the_next() -> None:
    """DEV-MENU-10."""
    items = [DevItem("alpha", "Alpha", "1-1"), DevItem("beta", "Beta", "1-1")]
    v = viewer("ships", items)
    v.frame(0)
    v.turn(100, -50)
    v.frame(0)
    rotation = FakeShip.made[0].pivot.rotation
    step = CFG.turn_per_pixel
    assert (rotation.y, rotation.x) == pytest.approx((100 * step, -50 * step))
    v.show(1, toggle=True)
    v.frame(0)
    assert FakeShip.made[1].pivot.rotation.y == pytest.approx(100 * step)


@pytest.mark.usefixtures("env")
def test_d199_a_drag_turns_an_enemy_on_top_of_its_heading() -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    v.turn(0, 30)
    v.frame(0)
    assert v._layer.pivot.rotation.x == pytest.approx(30 * CFG.turn_per_pixel)


def test_d205_a_prop_is_shown_on_its_own_stage_without_a_level(env: Env) -> None:
    """DEV-MENU-16."""
    items = [DevItem("hut", "hut", "1-1"), DevItem("barn", "barn", "2-1")]
    v = viewer("props", items)
    v.frame(0)
    v.frame(0)
    stage = FakePropStage.made[0]
    assert env.views == []
    assert v.scene is stage.scene
    assert stage.shown == ["hut"]
    assert v.status == CFG.texts.grid_note
    v.show(1, toggle=True)
    v.frame(0)
    assert len(FakePropStage.made) == 1
    assert stage.shown == ["hut", "barn"]
    assert env.views == []


@pytest.mark.usefixtures("env")
def test_d205_a_drag_and_the_toggle_reach_the_props_camera() -> None:
    """DEV-MENU-17."""
    v = viewer("props", [DevItem("hut", "hut", "1-1")])
    v.show(0, toggle=True)
    v.turn(50, -20)
    v.frame(0)
    turn, close_up, zoom = FakePropStage.made[0].updates[-1]
    step = CFG.turn_per_pixel
    assert turn == pytest.approx([50 * step, -20 * step])
    assert close_up is True
    assert zoom == 1


@pytest.mark.usefixtures("env")
def test_d205_dispose_drops_the_props_stage() -> None:
    v = viewer("props", [DevItem("hut", "hut", "1-1")])
    v.frame(0)
    v.dispose()
    assert FakePropStage.made[0].disposed
    assert v.scene is None


def test_d208_the_wheel_zooms_in_up_and_out_down_within_its_range() -> None:
    """DEV-MENU-11."""
    assert zoomed(1, -100) == pytest.approx(math.exp(100 * CFG.zoom_per_pixel))
    assert zoomed(1, 100) == pytest.approx(math.exp(-100 * CFG.zoom_per_pixel))
    assert zoomed(1, -1e6) == pytest.approx(CFG.zoom_range[1])
    assert zoomed(1, 1e6) == pytest.approx(CFG.zoom_range[0])


def test_d208_a_zoom_narrows_the_field_of_view_so_things_look_that_much_bigger() -> None:
    fov = 0.8
    assert math.tan(zoomed_fov(fov, 2) / 2) == pytest.approx(math.tan(fov / 2) / 2)
    assert zoomed_fov(fov, 1) == pytest.approx(fov)


def test_d208_the_wheel_zooms_a_ship_and_the_props_camera(env: Env) -> None:
    v = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    v.show(0, toggle=False)
    v.frame(0)
    camera = env.views[0].stage.camera
    before = camera.fov
    v.zoom(-200)
    v.frame(0)
    assert camera.fov == pytest.approx(zoomed_fov(before, zoomed(1, -200)))
    props = viewer("props", [DevItem("hut", "hut", "1-1")])
    props.zoom(-200)
    props.frame(0)
    assert FakePropStage.made[0].updates[-1][2] == pytest.approx(zoomed(1, -200))


def test_the_enemies_and_bosses_are_shown_with_no_ground_and_none_waited_for(env: Env) -> None:
    env.ready = False
    for name, item in [("enemies", "gnat"), ("bosses", "warden")]:
        v = viewer(name, [DevItem(item, item, "1-1")])
        v.frame(0)
        assert v.scene is not None
    assert len(env.groundless) == 2
    ships = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    ships.frame(0)
    # The other viewers still wait for their level's ground.
    assert ships.scene is None


def _probe_boss() -> Any:

    parts = [BossPartSpec("gun", 30, 0, 8, 10, shields_core=False, drop_chance=0.0)]
    stats = BossStats("warden", 40, 100, 1000, "Warden", 12, parts, 1, 1, BossDeath(1, 0.25))
    boss = ProbeBoss(240, 600, stats)
    boss.state = "fighting"
    return boss


@pytest.mark.usefixtures("env")
def test_k_breaks_the_boss_part_and_its_blast_is_drawn_where_the_boss_is_shown() -> None:
    """DEV-MENU-14."""
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1")])
    boss = _probe_boss()
    v.game.boss_kinds[0].spawn = lambda _area: boss
    v.frame(0)
    v.break_part()
    v.frame(0.1)
    assert boss.parts[0].destroyed
    (blast,) = FakeBlasts.made[0].drawn
    # Drawn at the part's place on the boss shown at the middle of the view.
    assert blast.x - v._middle_point[0] == pytest.approx(boss.parts[0].x - boss.x)
    assert blast.y - v._middle_point[1] == pytest.approx(boss.parts[0].y - boss.y)


@pytest.mark.usefixtures("env")
def test_k_does_nothing_to_an_enemy() -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    v.break_part()
    v.frame(0.1)
    assert FakeBlasts.made[0].drawn == []


@pytest.mark.usefixtures("env")
def test_d199_the_enemy_shown_is_of_the_item_s_kind_among_the_game_s() -> None:
    v = viewer("enemies", [DevItem("wasp", "Wasp", "1-1")])
    v.game.enemy_kinds.append(SimpleNamespace(id="wasp", spawn=spawned("wasp")))
    v.game.enemy_kinds.append(SimpleNamespace(id="moth", spawn=spawned("moth")))
    v.frame(0)
    assert v._layer.synced[0].id == "wasp"


@pytest.mark.usefixtures("env")
def test_d199_a_game_without_an_explosion_renderer_shows_its_enemies_without_blasts() -> None:
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1")])
    boss = _probe_boss()
    v.game.boss_kinds[0].spawn = lambda _area: boss
    v.game.view.enemies.blasts = lambda _scene: None
    v.frame(0)
    v.break_part()
    v.frame(0.1)
    assert boss.parts[0].destroyed
    assert v._layer.synced == [boss]
    assert FakeBlasts.made == []
    v.dispose()
    assert v.scene is None


class WorldEnemy(FakeEnemy):
    """A `FakeEnemy` the game view's `EnemyWorld` can hold."""

    def __init__(self, item_id: str, speed: float = 100.0) -> None:
        super().__init__(item_id, True, speed)
        self.max_health = 10.0
        self.health = 10.0
        self.shot_targets: list[Any] = []
        self.points = 0.0
        self.on_destroyed = None


def _game_view(speed: float = 100.0) -> DevViewer:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.game.enemy_kinds = [
        SimpleNamespace(id="gnat", spawn=lambda _area: [WorldEnemy("gnat", speed)])
    ]
    shots = SimpleNamespace(synced=[], disposed=False)
    shots.sync = shots.synced.append
    shots.dispose = lambda: setattr(shots, "disposed", True)
    v.game.view.enemies.shots = lambda _scene, _style: shots
    v.shots = shots  # type: ignore[attr-defined]
    return v


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_game_view_draws_the_enemy_where_it_is_not_at_the_middle() -> None:
    v = _game_view()
    v.show(0, toggle=True, mode=2)
    v.frame(0)
    drawn = Drawn(v._layer)
    v.frame(0.5)
    enemy = v._enemy
    assert drawn.at[-1][:2] == (240, pytest.approx(760 - 50))
    assert enemy.y == pytest.approx(710)
    assert v._world is not None
    assert v.shots.synced
    # Game size: the close-up does not narrow the view.
    assert v._view.stage.camera.fov == pytest.approx(v._fov)


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_game_view_comes_back_to_the_model_view_and_a_wireframe() -> None:
    v = _game_view()
    v.show(0, toggle=False, mode=2)
    v.frame(0)
    v.show(0, toggle=False, mode=0)
    v.frame(0.1)
    assert v._world is None
    assert v.shots.disposed
    assert v._view.scene.forceWireframe is False
    v.show(0, toggle=False, mode=1)
    v.frame(0.1)
    assert v._view.scene.forceWireframe is True
    assert v._world is None
    v.show(0, toggle=False, mode=0)
    v.frame(0.1)
    assert v._view.scene.forceWireframe is False


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_game_view_brings_a_new_enemy_once_the_world_is_empty() -> None:
    v = _game_view(speed=1000.0)
    v.show(0, toggle=False, mode=2)
    v.frame(0)
    first = v._enemy
    for _ in range(60):
        v.frame(0.1)
    assert v._enemy is not first
    assert len(v._world.enemies) >= 1


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_ships_have_no_views() -> None:
    v = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    v.show(0, toggle=True, mode=2)
    v.frame(0)
    assert v._world is None


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_game_view_keeps_the_enemy_in_the_middle_of_the_screen() -> None:
    v = _game_view()
    v.show(0, toggle=False, mode=2)
    v.frame(0)
    v.frame(0.5)
    enemy = v._enemy
    dx = enemy.x - v._middle_point[0]
    dy = enemy.y - v._middle_point[1]
    assert dy != 0
    camera = v._view.stage.camera
    framing = v._view.stage.framing
    # The camera, then the point it looks at, moved by the enemy's offset from the middle.
    assert camera.position.x == pytest.approx(dx)
    assert camera.position.z == pytest.approx(framing.back + dy)
    assert camera.target.z == pytest.approx(camera.position.z + framing.direction[1])
    # Back in the model view: the camera is where it was.
    v.show(0, toggle=False, mode=0)
    v.frame(0.1)
    assert camera.position.x == 0
    assert camera.position.z == pytest.approx(framing.back)


@pytest.mark.usefixtures("env")
def test_dev_menu_21_the_game_view_shots_leave_from_where_the_camera_sees_the_barrels() -> None:
    v = _game_view()
    v.show(0, toggle=False, mode=2)
    v.frame(0)
    v.frame(0.1)
    eye = v._world.options.eye
    framing = v._view.stage.framing
    # The eye moves with the camera that follows the enemy.
    assert (eye.x, eye.y) == (240 + v._shift[0], framing.back + v._shift[1])
    assert eye.height == framing.height
