"""Unit tests of `src/app/dev_viewer.py` (D-199): the dev viewers, over a fake level scene."""

import math
from types import SimpleNamespace
from typing import Any

import pytest

from app import dev_viewer
from app.dev_catalog import DevItem
from app.dev_viewer import DevViewer, clock_text, close_up_fov, eased_time, zoomed, zoomed_fov
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG

ALTITUDE = 320.0


class FakeCamera:
    def __init__(self) -> None:
        self.fov = 0.8
        self.position = SimpleNamespace(x=0.0, y=ALTITUDE + 100, z=0.0)
        self.position.set = self._set
        self.target = SimpleNamespace(x=0.0, y=0.0, z=0.0)

    def _set(self, x: float, y: float, z: float) -> None:
        self.position.x, self.position.y, self.position.z = x, y, z

    def getTarget(self) -> Any:  # noqa: N802 (Babylon's name)
        return self.target

    def setTarget(self, target: Any) -> None:  # noqa: N802 (Babylon's name)
        self.target = target


class FakeStage:
    def __init__(self, found: Any = None) -> None:
        self.camera = FakeCamera()
        # Looking down at 45°: the middle of the view is 100 ahead of the camera, on the flight
        # plane.
        self.framing = SimpleNamespace(direction=[-1.0, 1.0], back=-50.0, height=100.0)
        self.field = SimpleNamespace(height=lambda x, z: 4.0)
        self.ground_root = SimpleNamespace(
            scale=2.0, to_ground=lambda z: z / 2, to_world=lambda z: z * 2
        )
        self.found = found
        self.solo: list[Any] = []
        self.shifts: list[float] = []

    def find_prop(self, kind: str, z_end: float) -> Any:
        return self.found

    def solo_props(self, placements: list[Any]) -> None:
        self.solo = placements

    def shift_ground(self, x: float) -> None:
        self.shifts.append(x)


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
    made: list["FakeShip"] = []

    def __init__(self, scene: Any, scale: float, x: float, y: float) -> None:
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
    def __init__(self, scene: Any, models: Any, keys: list[str]) -> None:
        self.synced: list[Any] = []
        self.disposed = False
        self.pivot = pivot()

    def pivot_of(self, enemy: Any) -> Any:
        return self.pivot if enemy in self.synced else None

    def sync(self, enemies: list[Any], dt: float) -> None:
        self.synced = enemies

    def dispose(self) -> None:
        self.disposed = True


class FakePropStage:
    made: list["FakePropStage"] = []

    def __init__(self, engine: Any, game: Any, environment: bool) -> None:
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
        self.stage_found: Any = None
        self.views: list[FakeView] = []
        self.disposed: list[Any] = []
        FakeShip.made = []
        monkeypatch.setattr(dev_viewer, "prepare_level", lambda game, level: self.ready)
        monkeypatch.setattr(dev_viewer, "level_of", lambda game, level: SimpleNamespace(id=level))
        monkeypatch.setattr(dev_viewer, "scenery_with_runout", lambda level: level)
        monkeypatch.setattr(dev_viewer, "build_level_scene", self._build)
        monkeypatch.setattr(dev_viewer, "PlayfieldShip", FakeShip)
        monkeypatch.setattr(dev_viewer, "EnemyLayer", FakeLayer)
        monkeypatch.setattr(dev_viewer, "dispose_node", self.disposed.append)
        bounds = SimpleNamespace(
            min=SimpleNamespace(x=0, y=0, z=0), max=SimpleNamespace(x=40, y=10, z=20)
        )
        monkeypatch.setattr(dev_viewer, "get_hierarchy_bounding_vectors", lambda root: bounds)
        monkeypatch.setattr(dev_viewer, "DevPropStage", FakePropStage)
        FakePropStage.made = []

    def _build(self, engine: Any, game: Any, options: Any) -> FakeView:
        view = FakeView(FakeStage(self.stage_found))
        view.level = options.level
        self.views.append(view)
        return view


class FakeEnemy:
    """Comes in from above the playfield and flies down at `speed`, turning as it goes."""

    def __init__(self, id: str, expires: bool = True, speed: float = 100.0) -> None:
        self.id = id
        self.model = id
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
    def spawn(area: Any) -> list[Any]:
        return [FakeEnemy(kind_id)]

    return spawn


def game() -> SimpleNamespace:
    scenery = SimpleNamespace(camera=SimpleNamespace(flightAltitude=ALTITUDE))
    scenery_dict = {"propModels": {"hut": "hut-factory"}}
    view = SimpleNamespace(
        enemies=SimpleNamespace(glow="glow", models={}),
        outline="outline",
        player_ship_models={"alpha": "alpha-model"},
        player_ship_scale=2.0,
        scenery=SimpleNamespace(camera=scenery.camera, __getitem__=None),
    )
    view.scenery = FakeScenery(scenery.camera, scenery_dict)
    boss = FakeEnemy("warden", expires=False, speed=0.0)
    return SimpleNamespace(
        view=view,
        screen=SimpleNamespace(width=480, height=720),
        enemy_kinds=[SimpleNamespace(id="gnat", spawn=spawned("gnat"))],
        boss_kinds=[SimpleNamespace(id="warden", spawn=lambda area: boss)],
    )


class FakeScenery:
    def __init__(self, camera: Any, fields: dict[str, Any]) -> None:
        self.camera = camera
        self._fields = fields

    def __getitem__(self, key: str) -> Any:
        return self._fields[key]


def viewer(name: str, items: list[DevItem]) -> DevViewer:
    return DevViewer("engine", game(), name, items, True)


@pytest.fixture
def env(monkeypatch: pytest.MonkeyPatch) -> Env:
    return Env(monkeypatch)


def test_d199_the_clock_reads_minutes_and_seconds() -> None:
    assert clock_text(0) == "0:00"
    assert clock_text(65.9) == "1:05"
    assert clock_text(600) == "10:00"
    assert clock_text(-3) == "0:00"


def test_d199_the_close_up_fills_its_share_of_the_screen_and_never_widens() -> None:
    fov = close_up_fov(10, 100, 0.5, 1.0)
    assert math.isclose(2 * 100 * math.tan(fov / 2) * 0.5, 10)
    assert close_up_fov(1000, 100, 0.5, 1.0) == 1.0
    assert close_up_fov(0, 100, 0.5, 1.0) == 1.0


def test_d199_the_time_eases_towards_the_wheel_without_overshooting() -> None:
    assert eased_time(0, 10, 2, 0.25) == 5
    assert eased_time(0, 10, 2, 1) == 10


def test_d199_the_scene_waits_for_the_level_ground(env: Env) -> None:
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
    v = viewer("ships", [DevItem("alpha", "Alpha", "1-1")])
    v.show(0, True)
    v.frame(0.1)
    ship = FakeShip.made[0]
    # The camera is 100 above the flight plane, looking down at 45°: the middle is 100 ahead.
    assert ship.at == (240, -50 + 100)
    assert ship.model == "alpha-model"
    assert ship.dt == pytest.approx(0.1)
    camera = env.views[0].stage.camera
    assert camera.fov < 0.8
    v.show(0, False)
    v.frame(0.1)
    assert camera.fov == 0.8


def test_d199_another_item_replaces_the_model_on_the_same_scene(env: Env) -> None:
    items = [DevItem("alpha", "Alpha", "1-1"), DevItem("beta", "Beta", "1-1")]
    v = viewer("ships", items)
    v.frame(0)
    v.show(1, True)
    v.frame(0)
    assert len(env.views) == 1
    assert env.disposed == [FakeShip.made[0].pivot]
    assert FakeShip.made[1].model is None
    # Out of range: the last item.
    v.show(9, True)
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


def test_d199_an_enemy_lives_its_own_life_but_is_drawn_at_the_middle(env: Env) -> None:
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


def test_d199_an_enemy_that_left_the_playfield_comes_again(env: Env) -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    first = v._enemy
    for _ in range(20):
        v.frame(0.5)
    # From 760 down past the bottom of the playfield and its margin: a new one came.
    assert v._enemy is not first
    assert v._enemy.y > 0


def test_d199_an_enemy_gone_or_too_old_comes_again(env: Env) -> None:
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


def test_d199_a_boss_does_not_expire(env: Env) -> None:
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1")])
    v.frame(0)
    boss = v._enemy
    boss.age = 1e6
    v.frame(0.1)
    assert v._enemy is boss


def test_d199_the_enemy_world_drops_what_the_enemy_does() -> None:
    ctx = dev_viewer.DevEnemyContext(SimpleNamespace(width=100, height=200), "random")
    point = ctx.seen(SimpleNamespace(x=3, y=4, z=9))
    assert (point.x, point.y) == (3, 4)
    assert ctx.fire_bullet(0, 0, 0, None) is None
    assert ctx.fire_missile(0, 0, 0, None) is None
    assert ctx.fire_laser(None, None) is None
    assert ctx.spawn(None) is None
    assert ctx.explode(0, 0, 1) is None
    assert ctx.break_part(None) is None
    assert ctx.random == "random"


def test_d199_a_boss_is_spawned_too_and_an_unknown_kind_is_an_error(env: Env) -> None:
    v = viewer("bosses", [DevItem("warden", "Warden", "1-1"), DevItem("x", "X", "1-1")])
    v.frame(0)
    assert v._layer.synced[0].id == "warden"
    v.show(1, True)
    with pytest.raises(ValueError, match="No enemy kind"):
        v.frame(0)


def test_d199_the_levels_viewer_scrubs_within_the_level_and_plays(env: Env) -> None:
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
    v.show(0, True)
    for _ in range(50):
        v.frame(1)
    assert v._time == pytest.approx(100)


def test_d199_a_viewer_without_items_does_nothing(env: Env) -> None:
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


def test_d199_a_drag_turns_a_ship_and_the_turn_is_kept_for_the_next(env: Env) -> None:
    items = [DevItem("alpha", "Alpha", "1-1"), DevItem("beta", "Beta", "1-1")]
    v = viewer("ships", items)
    v.frame(0)
    v.turn(100, -50)
    v.frame(0)
    rotation = FakeShip.made[0].pivot.rotation
    step = CFG.turn_per_pixel
    assert (rotation.y, rotation.x) == pytest.approx((100 * step, -50 * step))
    v.show(1, True)
    v.frame(0)
    assert FakeShip.made[1].pivot.rotation.y == pytest.approx(100 * step)


def test_d199_a_drag_turns_an_enemy_on_top_of_its_heading(env: Env) -> None:
    v = viewer("enemies", [DevItem("gnat", "Gnat", "1-1")])
    v.frame(0)
    v.turn(0, 30)
    v.frame(0)
    assert v._layer.pivot.rotation.x == pytest.approx(30 * CFG.turn_per_pixel)


def test_d205_a_prop_is_shown_on_its_own_stage_without_a_level(env: Env) -> None:
    items = [DevItem("hut", "hut", "1-1"), DevItem("barn", "barn", "2-1")]
    v = viewer("props", items)
    v.frame(0)
    v.frame(0)
    stage = FakePropStage.made[0]
    assert env.views == []
    assert v.scene is stage.scene
    assert stage.shown == ["hut"]
    assert v.status == CFG.texts.grid_note
    v.show(1, True)
    v.frame(0)
    assert len(FakePropStage.made) == 1
    assert stage.shown == ["hut", "barn"]
    assert env.views == []


def test_d205_a_drag_and_the_toggle_reach_the_props_camera(env: Env) -> None:
    v = viewer("props", [DevItem("hut", "hut", "1-1")])
    v.show(0, True)
    v.turn(50, -20)
    v.frame(0)
    turn, close_up, zoom = FakePropStage.made[0].updates[-1]
    step = CFG.turn_per_pixel
    assert turn == pytest.approx([50 * step, -20 * step])
    assert close_up is True
    assert zoom == 1


def test_d205_dispose_drops_the_props_stage(env: Env) -> None:
    v = viewer("props", [DevItem("hut", "hut", "1-1")])
    v.frame(0)
    v.dispose()
    assert FakePropStage.made[0].disposed
    assert v.scene is None


def test_d208_the_wheel_zooms_in_up_and_out_down_within_its_range() -> None:
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
    v.show(0, False)
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
