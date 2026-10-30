"""A dev viewer (D-199): the item picked in the dev menu, drawn as in game.

Every viewer shows a level's scene built as a level is (`build_level_scene`, with the game's lights,
glow and rims). The player ships, the enemies and the bosses stand on its playfield, at the middle
of the view, over the first level's ground; the enemies and bosses live their own lives (their
moves turn them, their turrets, limbs and rings move) pinned at the middle. A level's scenery shows
at the time the wheel scrubs to. The close-up narrows the camera's field of view: the model and the
ground are magnified together. The props are not shown over a level: they stand alone on a floor
ruled in blocks (`DevPropStage`, D-205), no ground loaded.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from app.dev_catalog import DevItem
from app.dev_prop_stage import DevPropStage
from app.level_prepare import level_of, prepare_level, scenery_with_runout
from app.level_scene import LevelSceneOptions, build_level_scene
from app.shot_viewer_scene import PlayfieldShip
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG
from config.game_play import GAME_PLAY_CONFIG
from core.entities.enemy import EnemySpawnArea
from core.entities.muzzle import PlanePoint
from core.math.rng import create_rng
from render.babylon import dispose_node, get_hierarchy_bounding_vectors
from render.enemy_layer import EnemyLayer

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# The smallest number of seconds written with two digits.
TWO_DIGITS = 10


def clock_text(seconds: float) -> str:
    """`m:ss`."""
    whole = int(math.floor(max(0, seconds)))
    rest = whole % 60
    return str(whole // 60) + ":" + ("0" if rest < TWO_DIGITS else "") + str(rest)


def close_up_fov(size: float, distance: float, fill: float, widest: float) -> float:
    """The vertical field of view in which something `size` across, `distance` away, fills `fill`
    of the screen's height; never wider than `widest`."""
    if size <= 0 or distance <= 0 or fill <= 0:
        return widest
    return min(widest, 2 * math.atan(size / (2 * distance * fill)))


def eased_time(time: float, target: float, ease: float, dt: float) -> float:
    """`time` moved towards `target` by the share `ease * dt` of the way (all of it at most)."""
    return time + (target - time) * min(1, ease * dt)


def _within(enemy: Any, screen: Any, margin: float) -> bool:
    """Whether the enemy's centre is within `margin` of the playfield."""
    x: float = enemy.x
    y: float = enemy.y
    inside_x = x >= -margin and x <= screen.width + margin
    return inside_x and y >= -margin and y <= screen.height + margin


class DevEnemyContext:
    """The world an enemy of a dev viewer lives in (`EnemyContext`): the playfield, the player at
    the bottom middle, nothing it fires or sends out kept."""

    def __init__(self, screen: Any, random: Any) -> None:
        self.width = screen.width
        self.height = screen.height
        self.player_x = screen.width / 2
        self.player_y = GAME_PLAY_CONFIG.ship_start_y
        self.random = random
        self.fire_rate = 1.0

    def seen(self, point: Any) -> PlanePoint:
        return PlanePoint(point.x, point.y)

    def fire_bullet(self, x: float, y: float, heading: float, spec: Any) -> None:
        return None

    def fire_missile(self, x: float, y: float, heading: float, spec: Any) -> None:
        return None

    def fire_laser(self, owner: Any, spec: Any) -> None:
        return None

    def spawn(self, enemy: Any) -> None:
        return None

    def explode(self, x: float, y: float, radius: float) -> None:
        return None

    def break_part(self, part: Any) -> None:
        return None


class DevViewer:
    """One dev viewer (`viewer`, one of `DEV_VIEWERS`) and its `items`. Each frame, `show` says
    which item and toggle the menu has, `frame` builds what is missing and moves on; `scene` is
    what to draw (None while it is being built)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        engine: Any,
        game: Any,
        viewer: str,
        items: list[DevItem],
        environment: bool,
    ) -> None:
        self._engine = engine
        self.game = game
        self.viewer = viewer
        self._items = items
        self._environment = environment
        self._index = 0
        self._toggle = False
        # The level the scene is built over, and the scene (None until built).
        self._host: str | None = None
        self._view: Any = None
        # The item the scene shows (-1: none yet), what was built for it, and its size.
        self._shown = -1
        self._ship: Any = None
        self._layer: Any = None
        self._enemy: Any = None
        self._size = 0.0
        self._fov = 0.0
        # Where the view is along the level.
        self._at = 0.0
        # The props viewer's stage (D-205), once built.
        self._props: DevPropStage | None = None
        # Enemies and bosses: the item, where it is drawn, the world it lives in, whether it has
        # come onto the playfield, and the time not stepped yet.
        self._item: DevItem | None = None
        self._middle_point = [0.0, 0.0]
        self._context: Any = None
        self._entered = False
        self._sim_left = 0.0
        # How far the reviewer has turned the model with the mouse (radians): around its nose
        # and nose up or down (props: the camera, round the prop and up or down). Kept from one
        # item to the next.
        self._turn = [0.0, 0.0]
        # Levels viewer: the time shown, the time the wheel asked for, and the level's length.
        self._time = 0.0
        self._target = 0.0
        self._duration = 0.0

    @property
    def scene(self) -> Any:
        """The scene to draw, once built."""
        if self._props is not None:
            return self._props.scene
        return self._view.scene if self._view is not None else None

    @property
    def status(self) -> str:
        """The status line: building, the level's time, the props' grid."""
        if self._props is not None:
            return CFG.texts.grid_note
        if self._view is None:
            return CFG.texts.loading
        if self.viewer == "levels":
            return clock_text(self._time) + " / " + clock_text(self._duration)
        return ""

    def show(self, index: int, toggle: bool) -> None:
        """The item the menu picked, and its toggle (close-up, or play for the levels)."""
        self._index = max(0, min(index, len(self._items) - 1))
        self._toggle = toggle

    def turn(self, dx: float, dy: float) -> None:
        """A drag of (`dx`, `dy`) screen pixels turns the model (see `_turn`)."""
        self._turn[0] += dx * CFG.turn_per_pixel
        self._turn[1] += dy * CFG.turn_per_pixel

    def scrub(self, delta_y: float) -> None:
        """Levels viewer: the wheel turned by `delta_y` pixels moves the time shown on or back."""
        seconds = delta_y / CFG.wheel_step * CFG.scrub_seconds
        self._target = max(0, min(self._duration, self._target + seconds))

    def frame(self, dt: float) -> None:
        """Builds the scene of the item's level if needed (once its ground is ready), shows the
        item, and moves on by `dt` seconds."""
        if len(self._items) == 0:
            return
        item = self._items[self._index]
        if self.viewer == "props":
            self._show_prop(item)
            return
        if item.host != self._host:
            self._drop_scene()
            self._host = item.host
        if self._view is None:
            if not prepare_level(self.game, item.host):
                return
            self._build_scene(item.host)
        if self.viewer == "levels":
            self._play(dt)
            return
        if self._shown != self._index:
            self._show_item(item)
        self._animate(dt)

    def _build_scene(self, level_id: str) -> None:
        level = level_of(self.game, level_id)
        view = self.game.view
        self._view = build_level_scene(
            self._engine,
            self.game,
            LevelSceneOptions(
                scenery_with_runout(level),
                self._environment,
                view.enemies.glow,
                int(GAME_PLAY_CONFIG.environment_cube_size),
                GAME_PLAY_CONFIG.stage,
                None,
                view.outline if self._environment else None,
            ),
        )
        self._fov = self._view.stage.camera.fov
        self._duration = self._view.track.duration
        self._time = 0.0
        self._target = 0.0
        self._shown = -1
        self._view.update(0, 0)

    def _play(self, dt: float) -> None:
        """Levels viewer: the time eases to the wheel's, and goes on at the level's pace while
        playing."""
        if self._toggle:
            self._target = min(self._duration, self._target + dt)
        self._time = eased_time(self._time, self._target, CFG.scrub_ease, dt)
        self._view.update(self._time * self._view.track.speed, dt)

    def _middle(self) -> list[float]:
        """The playfield point drawn at the middle of the view (where the camera looks, on the
        flight plane), as [x, y]."""
        stage = self._view.stage
        camera = stage.camera.position
        direction = stage.framing.direction
        altitude = self.game.view.scenery.camera.flightAltitude
        t = (altitude - camera.y) / direction[0] if direction[0] != 0 else 0
        return [self.game.screen.width / 2, camera.z + t * direction[1]]

    def _drop_item(self) -> None:
        self._at = 0.0
        if self._ship is not None:
            dispose_node(self._ship.pivot)
        if self._layer is not None:
            self._layer.dispose()
        self._ship = None
        self._layer = None
        self._enemy = None
        self._shown = -1

    def _show_item(self, item: DevItem) -> None:
        """Builds the model of `item` at the middle of the view, and measures it."""
        self._drop_item()
        self._shown = self._index
        view = self._view
        middle = self._middle()
        if self.viewer == "ships":
            model = self.game.view.player_ship_models.get(item.id)
            scale = self.game.view.player_ship_scale
            ship = view.playfield.run(
                lambda: PlayfieldShip(view.scene, scale, middle[0], middle[1])
            )
            if model is not None:
                view.playfield.run(lambda: ship.show(model))
            self._ship = ship
        else:
            self._item = item
            self._middle_point = middle
            self._context = DevEnemyContext(self.game.screen, create_rng(int(CFG.model_seed)))
            self._enemy = self._spawn(item)
            models = self.game.view.enemies.models
            self._layer = view.playfield.run(lambda: EnemyLayer(view.scene, models, []))
            self._sync(0)
        self._size = self._measure(view.playfield.root)

    def _spawn(self, item: DevItem) -> Any:
        """One enemy (or the boss) of `item`'s kind, where its kind brings it in; it then lives
        its own life (see `_live`)."""
        screen = self.game.screen
        area = EnemySpawnArea(screen.width, screen.height, create_rng(int(CFG.model_seed)))
        enemy: Any = None
        if self.viewer == "bosses":
            for kind in self.game.boss_kinds:
                if kind.id == item.id:
                    enemy = kind.spawn(area)
        else:
            for kind in self.game.enemy_kinds:
                if kind.id == item.id:
                    group = kind.spawn(area)
                    enemy = group[0] if len(group) > 0 else None
        if enemy is None:
            raise ValueError('No enemy kind "' + item.id + '"')
        self._entered = False
        return enemy

    def _show_prop(self, item: DevItem) -> None:
        """Props viewer (D-205): builds the stage once, puts the prop picked on it, and places the
        camera as dragged."""
        if self._props is None:
            self._props = DevPropStage(self._engine, self.game, self._environment)
        if self._shown != self._index:
            self._props.show(item)
            self._shown = self._index
        self._props.update(self._turn, self._toggle)

    def _measure(self, root: Any) -> float:
        """The size of what hangs from `root`: its largest side, in world units."""
        bounds = get_hierarchy_bounding_vectors(root)
        low = bounds.min
        high = bounds.max
        size: float = max(high.x - low.x, high.y - low.y, high.z - low.z)
        return size

    def _live(self, dt: float) -> None:
        """Runs the enemy's own life for `dt` seconds, in steps of the game's: its moves, its
        turrets and limbs, a boss's coming in and its patterns (what it fires is dropped). Once it
        has left the playfield, or is older than the game lets an enemy get, a new one comes."""
        enemy = self._enemy
        if enemy is None or self._item is None:
            return
        step = 1 / GAME_PLAY_CONFIG.step_hz
        self._sim_left += dt
        while self._sim_left >= step:
            self._sim_left -= step
            enemy.age += step
            enemy.update(self._context, step)
        if self._ended(enemy):
            self._enemy = self._spawn(self._item)

    def _ended(self, enemy: Any) -> bool:
        """Whether the enemy is gone as the game's world would say (`EnemyWorld._check_gone`)."""
        if enemy.gone:
            return True
        if not enemy.expires:
            return False
        if _within(enemy, self.game.screen, enemy.radius):
            self._entered = True
        left = self._entered and not _within(enemy, self.game.screen, GAME_PLAY_CONFIG.cull_margin)
        return left or enemy.age > GAME_PLAY_CONFIG.max_enemy_age

    def _sync(self, dt: float) -> None:
        """Draws the enemy at the middle of the view, turned as it is in its own life."""
        layer = self._layer
        enemy = self._enemy
        if layer is None or enemy is None:
            return
        x = enemy.x
        y = enemy.y
        enemy.x = self._middle_point[0]
        enemy.y = self._middle_point[1]
        self._view.playfield.run(lambda: layer.sync([enemy], dt))
        enemy.x = x
        enemy.y = y

    def _animate(self, dt: float) -> None:
        """Steps the model's animations and sets the camera's field of view (the close-up's)."""
        if self._ship is not None:
            self._ship.update(dt)
        self._live(dt)
        self._sync(dt)
        self._apply_turn()
        self._view.update(self._at, dt)
        camera = self._view.stage.camera
        camera.fov = self._fov
        if self._toggle:
            camera.fov = close_up_fov(self._size, self._distance(), CFG.close_up_fill, self._fov)

    def _apply_turn(self) -> None:
        """Turns the model as dragged: a ship or an enemy around its nose and nose up or down (on
        top of the bank and heading the game gives them)."""
        pivot: Any = None
        if self._ship is not None:
            pivot = self._ship.pivot
        elif self._layer is not None and self._enemy is not None:
            pivot = self._layer.pivot_of(self._enemy)
        if pivot is not None:
            pivot.rotation.y = self._turn[0]
            pivot.rotation.x = self._turn[1]

    def _distance(self) -> float:
        """How far the camera is from the middle of the view's subject."""
        camera = self._view.stage.camera.position
        middle = self._middle()
        dy = self.game.view.scenery.camera.flightAltitude - camera.y
        dz = middle[1] - camera.z
        return math.sqrt(dy * dy + dz * dz)

    def _drop_scene(self) -> None:
        self._drop_item()
        if self._view is not None:
            self._view.scene.dispose()
        self._view = None

    def dispose(self) -> None:
        self._drop_scene()
        if self._props is not None:
            self._props.dispose()
        self._props = None
        self._host = None
