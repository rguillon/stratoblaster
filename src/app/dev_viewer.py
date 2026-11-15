# Copyright (c) 2026 Renaud Guillon
"""A dev viewer (D-199): the item picked in the dev menu, drawn as in game (DEV-MENU-08).

Every viewer shows a level's scene built as a level is (`build_level_scene`, with the game's lights,
glow and rims). The player ships, the enemies and the bosses stand on its playfield, at the middle
of the view, with no level's ground (D-334; the enemies and bosses since D-199); the enemies and
bosses live their own lives (their
moves turn them, their turrets, limbs and rings move) pinned at the middle. A level's scenery shows
at the time the wheel scrubs to. The close-up narrows the camera's field of view: the model and the
ground are magnified together (DEV-MENU-09). The props are not shown over a level: they stand
alone on a floor ruled in blocks (`DevPropStage`, D-205), no ground loaded.
"""

import math

from app.dev_catalog import DevItem
from app.dev_model_scene import build_model_scene
from app.dev_prop_stage import DevPropStage
from app.level_prepare import level_of, prepare_level, scenery_with_runout
from app.level_scene import LevelSceneOptions, build_level_scene
from app.shot_viewer_scene import PlayfieldShip
from config.dev_viewer import DEV_VIEW_MODES
from config.dev_viewer import DEV_VIEWER_CONFIG as CFG
from config.game_play import GAME_PLAY_CONFIG
from core.entities.boss import Boss
from core.entities.enemy import EnemySpawnArea
from core.entities.muzzle import PlanePoint
from core.math.rng import create_rng
from core.systems.enemy_world import EnemyBlast, EnemyWorld, EnemyWorldOptions
from render.babylon import dispose_node, get_hierarchy_bounding_vectors, vector3
from render.enemy_layer import EnemyLayer
from render.game_view import EnemyShotFrame
from render.scenery.playfield_framing import playfield_eye

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The smallest number of seconds written with two digits.
TWO_DIGITS = 10


def clock_text(seconds: float) -> str:
    """`m:ss`."""
    whole = math.floor(max(0, seconds))
    rest = whole % 60
    return str(whole // 60) + ":" + ("0" if rest < TWO_DIGITS else "") + str(rest)


def close_up_fov(size: float, distance: float, fill: float, widest: float) -> float:
    """Return the vertical field of view in which something `size` across, `distance` away.

    Fills `fill` of the screen's height; never wider than `widest`.
    """
    if size <= 0 or distance <= 0 or fill <= 0:
        return widest
    return min(widest, 2 * math.atan(size / (2 * distance * fill)))


def zoomed_fov(fov: float, zoom: float) -> float:
    """Return the field of view `fov` narrowed `zoom` times (DEV-MENU-11, D-208).

    What is seen looks `zoom` times as big.
    """
    return 2 * math.atan(math.tan(fov / 2) / zoom)


def zoomed(zoom: float, delta_y: float) -> float:
    """`zoom` after the wheel turned by `delta_y` pixels (D-208): in when it turns up (negative).

    Out when it turns down, within `zoom_range`.
    """
    low = math.log(CFG.zoom_range[0])
    high = math.log(CFG.zoom_range[1])
    return math.exp(max(low, min(high, math.log(zoom) - delta_y * CFG.zoom_per_pixel)))


def eased_time(time: float, target: float, ease: float, dt: float) -> float:
    """`time` moved towards `target` by the share `ease * dt` of the way (all of it at most)."""
    return time + (target - time) * min(1, ease * dt)


def _within(enemy: Any, screen: Any, margin: float) -> bool:
    """Whether the enemy's centre is within `margin` of the playfield."""
    x: float = enemy.x
    y: float = enemy.y
    inside_x = x >= -margin and x <= screen.width + margin
    return inside_x and y >= -margin and y <= screen.height + margin


class DevCues:
    """What blew up in the viewer since the last time its sounds were asked for (D-262).

    The radii of the explosions, how many parts broke, and whether a boss was destroyed: the
    events a level would sound (`LevelCues`), for the dev session to play.
    """

    def __init__(self, blasts: list[float], parts: int, boss: bool) -> None:
        self.blasts = blasts
        self.parts = parts
        self.boss = boss


class DevEnemyContext:
    """The world an enemy of the enemies viewer (DEV-MENU-13) lives in (`EnemyContext`).

    The playfield, the player at the bottom middle, nothing it fires or sends out kept; what blows
    up is kept for the viewer to draw (`blasts`).
    """

    def __init__(self, screen: Any, random: Any) -> None:
        self.width = screen.width
        self.height = screen.height
        self.player_x = screen.width / 2
        self.player_y = GAME_PLAY_CONFIG.ship_start_y
        self.random = random
        self.fire_rate = 1.0
        # What blew up since the viewer last drew it (a boss's parts, its death).
        self.blasts: list[EnemyBlast] = []
        # How many parts of an enemy broke since the viewer last took them (they blow up too).
        self.broken = 0

    def seen(self, point: Any) -> PlanePoint:
        """Return the plane position of `point`, as the viewer shows it."""
        return PlanePoint(point.x, point.y)

    def fire_bullet(self, _x: float, _y: float, _heading: float, _spec: Any) -> None:
        """Do nothing: the viewer fires no bullets."""

    def fire_missile(
        self, _x: float, _y: float, _heading: float, _spec: Any, _height: float = 0
    ) -> None:
        """Do nothing: the viewer fires no missiles."""

    def fire_laser(self, _owner: Any, _spec: Any) -> None:
        """Do nothing: the viewer fires no lasers."""

    def spawn(self, _enemy: Any) -> None:
        """Do nothing: the viewer spawns no enemies."""

    def explode(self, x: float, y: float, radius: float) -> None:
        """Add a blast of enemy colour at the given position."""
        self.blasts.append(EnemyBlast("enemy", x, y, radius))

    def break_part(self, part: Any) -> None:
        """Add a blast where a part of an enemy broke."""
        self.broken += 1
        self.blasts.append(EnemyBlast("enemy", part.x, part.y, part.radius))


class DevViewer:
    """One dev viewer (`viewer`, one of `DEV_VIEWERS`) and its `items`.

    Each frame, `show` says which item and toggle the menu has, `frame` builds what is missing and
    moves on; `scene` is what to draw (None while it is being built).
    """

    def __init__(
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
        # The view of the enemies and bosses (DEV-MENU-21): one of `DEV_VIEW_MODES`.
        self._mode = DEV_VIEW_MODES[0]
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
        # The game view (DEV-MENU-21): the enemy world the enemy lives in, as in a level, the
        # renderer of its shots, and whether the item shown was built for it.
        self._world: EnemyWorld | None = None
        self._shot_layer: Any = None
        self._in_game = False
        # Game view: how far the camera is moved off the middle of the playfield to keep the enemy
        # in the middle of the screen (playfield X and Y; zero in the other views).
        self._shift = [0.0, 0.0]
        # Enemies and bosses: the explosions' renderer, and the explosions to draw next.
        self._blasts: Any = None
        self._new_blasts: list[EnemyBlast] = []
        # What to sound: the radii of the explosions, the parts broken, a boss destroyed (D-262).
        self._cue_blasts: list[float] = []
        self._cue_parts = 0
        self._cue_boss = False
        # How far the reviewer has turned the model with the mouse (radians): around its nose
        # and nose up or down (props: the camera, round the prop and up or down). Kept from one
        # item to the next.
        self._turn = [0.0, 0.0]
        # D-208: how many times as big the wheel makes the model look. Kept from one item to the
        # next.
        self._zoom = 1.0
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

    def take_cues(self) -> DevCues:
        """Return what blew up since the last call, for its sounds (D-262), and forget it."""
        cues = DevCues(self._cue_blasts, self._cue_parts, self._cue_boss)
        self._cue_blasts = []
        self._cue_parts = 0
        self._cue_boss = False
        return cues

    @property
    def status(self) -> str:
        """The status line (DEV-MENU-05): building, the level's time, the props' grid."""
        if self._props is not None:
            return CFG.texts.grid_note
        if self._view is None:
            return CFG.texts.loading
        if self.viewer == "levels":
            return clock_text(self._time) + " / " + clock_text(self._duration)
        return ""

    def show(self, index: int, toggle: bool, mode: int = 0) -> None:
        """Show the item the menu picked, its toggle (close-up, or play for the levels).

        And its view, an index into `DEV_VIEW_MODES` (enemies and bosses, DEV-MENU-21).
        """
        self._index = max(0, min(index, len(self._items) - 1))
        self._toggle = toggle
        self._mode = DEV_VIEW_MODES[max(0, min(mode, len(DEV_VIEW_MODES) - 1))]

    def zoom(self, delta_y: float) -> None:
        """Zoom in or out as the wheel turns by `delta_y` pixels (D-208)."""
        self._zoom = zoomed(self._zoom, delta_y)

    def turn(self, dx: float, dy: float) -> None:
        """Turn the model by a drag of (`dx`, `dy`) screen pixels (see `_turn`, DEV-MENU-10)."""
        self._turn[0] += dx * CFG.turn_per_pixel
        self._turn[1] += dy * CFG.turn_per_pixel

    def scrub(self, delta_y: float) -> None:
        """Levels viewer: the wheel turned by `delta_y` pixels moves the time shown on or back."""
        seconds = delta_y / CFG.wheel_step * CFG.scrub_seconds
        self._target = max(0, min(self._duration, self._target + seconds))

    def frame(self, dt: float) -> None:
        """Build the scene of the item's level if needed (once its ground is ready).

        Shows the item, and moves on by `dt` seconds.
        """
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
            # The ships, enemies and bosses are shown with no ground: nothing to wait for.
            if not self._groundless() and not prepare_level(self.game, item.host):
                return
            self._build_scene(item.host)
        if self.viewer == "levels":
            self._play(dt)
            return
        if self._shown != self._index or self._in_game != self._game_view():
            self._show_item(item)
        # DEV-MENU-21: the wireframe view draws every material as a wireframe.
        self._view.scene.forceWireframe = self._mode == "wireframe"
        self._animate(dt)

    def _groundless(self) -> bool:
        """Whether the viewer shows its models with no level's ground.

        The player ships (D-334, owner: "dont load a ground in the dev view for the player ship"),
        the enemies and the bosses.
        """
        return self.viewer in ("ships", "enemies", "bosses")

    def _game_view(self) -> bool:
        """Whether the enemy or boss is on the game's playfield, as in a level (DEV-MENU-21)."""
        return self._groundless() and self._mode == "game"

    def _build_scene(self, level_id: str) -> None:
        level = level_of(self.game, level_id)
        view = self.game.view
        options = LevelSceneOptions(
            scenery_with_runout(level),
            self._environment,
            view.enemies.glow,
            int(GAME_PLAY_CONFIG.environment_cube_size),
            GAME_PLAY_CONFIG.stage,
            None,
            view.outline if self._environment else None,
        )
        if self._groundless():
            self._view = build_model_scene(self._engine, self.game, options.level, options)
        else:
            self._view = build_level_scene(self._engine, self.game, options)
        self._fov = self._view.stage.camera.fov
        self._duration = self._view.track.duration if not self._groundless() else 0.0
        self._time = 0.0
        self._target = 0.0
        self._shown = -1
        self._view.update(0, 0)

    def _play(self, dt: float) -> None:
        """Levels viewer (DEV-MENU-18): the time eases to the wheel's.

        And goes on at the level's pace while playing.
        """
        if self._toggle:
            self._target = min(self._duration, self._target + dt)
        self._time = eased_time(self._time, self._target, CFG.scrub_ease, dt)
        self._view.update(self._time * self._view.track.speed, dt)

    def _middle(self) -> list[float]:
        """Return the playfield point drawn at the middle of the view, where the camera looks.

        On the flight plane, as [x, y].
        """
        stage = self._view.stage
        camera = stage.camera.position
        direction = stage.framing.direction
        altitude = self.game.view.scenery.camera.flightAltitude
        t = (altitude - camera.y) / direction[0] if direction[0] != 0 else 0
        return [self.game.playfield.width / 2, camera.z - self._shift[1] + t * direction[1]]

    def _drop_item(self) -> None:
        self._at = 0.0
        if self._ship is not None:
            dispose_node(self._ship.pivot)
        if self._layer is not None:
            self._layer.dispose()
        if self._blasts is not None:
            self._blasts.dispose()
        if self._shot_layer is not None:
            self._shot_layer.dispose()
        self._ship = None
        self._layer = None
        self._blasts = None
        self._shot_layer = None
        self._world = None
        self._in_game = False
        self._new_blasts = []
        self._enemy = None
        self._shown = -1

    def _show_item(self, item: DevItem) -> None:
        """Build the model of `item` at the middle of the view.

        And measures it (the ships viewer's ship, DEV-MENU-12, and the enemies' and bosses').
        """
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
            self._context = DevEnemyContext(self.game.playfield, create_rng(int(CFG.model_seed)))
            self._in_game = self._game_view()
            if self._in_game:
                self._start_world(item)
            else:
                self._enemy = self._spawn(item)
            models = self.game.view.enemies.models
            self._layer = view.playfield.run(lambda: EnemyLayer(view.scene, models, []))
            blasts = self.game.view.enemies.blasts
            self._blasts = view.playfield.run(lambda: blasts(view.scene))
            if self._in_game:
                shots = self.game.view.enemies.shots
                self._shot_layer = view.playfield.run(lambda: shots(view.scene, None))
            self._sync(0)
        self._size = self._measure(view.playfield.root)

    def _start_world(self, item: DevItem) -> None:
        """Game view (DEV-MENU-21): a world as a level's, with the player at the bottom middle.

        The enemy (or boss) comes in where its kind brings it in, and moves, fires and sends out
        enemies as in a level; the player's ship is not drawn and nothing hits it.
        """
        screen = self.game.playfield
        options = EnemyWorldOptions(
            screen.width,
            screen.height,
            GAME_PLAY_CONFIG.cull_margin,
            GAME_PLAY_CONFIG.max_enemy_age,
            # Shots leave from where the camera sees the barrels, as in a level (GFX-SHOT-09).
            playfield_eye(screen, self._view.stage.framing),
        )
        world = EnemyWorld(options, create_rng(int(CFG.model_seed)))
        world.player_x = screen.width / 2
        world.player_y = GAME_PLAY_CONFIG.ship_start_y
        group = self._ready(self._spawn_group(item))
        world.add(*group)
        self._world = world
        self._enemy = group[0]

    def _spawn(self, item: DevItem) -> Any:
        """One enemy (or the boss) of `item`'s kind.

        Where its kind brings it in It then lives its own life (see `_live`).
        """
        group = self._spawn_group(item)
        self._entered = False
        return group[0]

    def _ready(self, group: list[Any]) -> list[Any]:
        """Return `group` with a boss already in place, its guns opening fire at once (game view).

        No wait for it to come in and for its first volleys (DEV-MENU-21).
        """
        for enemy in group:
            if hasattr(enemy, "open_fire"):
                enemy.open_fire()
        return group

    def _spawn_group(self, item: DevItem) -> list[Any]:
        """Return the enemies (a boss alone) of `item`'s kind, where its kind brings them in."""
        screen = self.game.playfield
        area = EnemySpawnArea(screen.width, screen.height, create_rng(int(CFG.model_seed)))
        group: list[Any] = []
        if self.viewer == "bosses":
            for kind in self.game.boss_kinds:
                if kind.id == item.id:
                    group = [kind.spawn(area)]
        else:
            for kind in self.game.enemy_kinds:
                if kind.id == item.id:
                    group = list(kind.spawn(area))
        if len(group) == 0:
            raise ValueError('No enemy kind "' + item.id + '"')
        return group

    def _show_prop(self, item: DevItem) -> None:
        """Props viewer (D-205): builds the stage once.

        Puts the prop picked on it And places the camera as dragged.
        """
        if self._props is None:
            self._props = DevPropStage(self._engine, self.game, self._environment)
        if self._shown != self._index:
            self._props.show(item)
            self._shown = self._index
        self._props.update(self._turn, self._toggle, self._zoom)

    def _measure(self, root: Any) -> float:
        """Return the size of what hangs from `root`: its largest side, in world units."""
        bounds = get_hierarchy_bounding_vectors(root)
        low = bounds.min
        high = bounds.max
        size: float = max(high.x - low.x, high.y - low.y, high.z - low.z)
        return size

    def _live(self, dt: float) -> None:
        """Run the enemy's own life for `dt` seconds, in steps of the game's: its moves.

        Its turrets and limbs, a boss's coming in and its patterns (what it fires is dropped). Once
        it has left the playfield, or is older than the game lets an enemy get, a new one comes.
        """
        enemy = self._enemy
        if enemy is None or self._item is None:
            return
        step = 1 / GAME_PLAY_CONFIG.step_hz
        if self._world is not None:
            self._live_world(self._world, dt, step)
            return
        self._sim_left += dt
        while self._sim_left >= step:
            self._sim_left -= step
            enemy.age += step
            enemy.update(self._context, step)
            self._take_blasts(enemy)
        if self._ended(enemy):
            self._cue_boss = self._cue_boss or (self.viewer == "bosses" and enemy.gone)
            self._enemy = self._spawn(self._item)

    def _live_world(self, world: EnemyWorld, dt: float, step: float) -> None:
        """Game view: step the world as a level does; a new group comes once all are gone."""
        self._sim_left += dt
        while self._sim_left >= step:
            self._sim_left -= step
            world.step(step)
            self._new_blasts.extend(world.blasts)
            self._cue_blasts.extend([
                blast.radius for blast in world.blasts if blast.kind == "enemy"
            ])
            self._cue_parts += len(world.broken_parts)
        if len(world.enemies) == 0 and self._item is not None:
            self._cue_boss = self._cue_boss or self.viewer == "bosses"
            world.clear()
            group = self._ready(self._spawn_group(self._item))
            world.add(*group)
            self._enemy = group[0]

    def _take_blasts(self, enemy: Any) -> None:
        """Take the explosions of the last step, moved as the enemy is.

        The enemy is drawn at the middle of the view (see `_sync`).
        """
        dx = self._middle_point[0] - enemy.x
        dy = self._middle_point[1] - enemy.y
        for blast in self._context.blasts:
            self._new_blasts.append(
                EnemyBlast(blast.kind, blast.x + dx, blast.y + dy, blast.radius)
            )
            self._cue_blasts.append(blast.radius)
        self._cue_parts += self._context.broken
        self._context.blasts = []
        self._context.broken = 0

    def break_part(self) -> None:
        """Bosses viewer (DEV-MENU-14): destroys the boss's next part.

        Or its core once they are all gone (as K does in a level, DEV-OPT-09), to watch it break:
        blasts, transformations and its death. A new boss comes in once it is gone.
        """
        if self.viewer == "bosses" and isinstance(self._enemy, Boss):
            self._enemy.break_next()

    def _ended(self, enemy: Any) -> bool:
        """Whether the enemy is gone as the game's world would say (`EnemyWorld._check_gone`)."""
        if enemy.gone:
            return True
        if not enemy.expires:
            return False
        if _within(enemy, self.game.playfield, enemy.radius):
            self._entered = True
        playfield = self.game.playfield
        left = self._entered and not _within(enemy, playfield, GAME_PLAY_CONFIG.cull_margin)
        return left or enemy.age > GAME_PLAY_CONFIG.max_enemy_age

    def _sync(self, dt: float) -> None:
        """Draws the enemy at the middle of the view, turned as it is in its own life."""
        layer = self._layer
        enemy = self._enemy
        if layer is None or enemy is None:
            return
        if self._world is not None:
            self._sync_world(self._world, dt)
            return
        x = enemy.x
        y = enemy.y
        enemy.x = self._middle_point[0]
        enemy.y = self._middle_point[1]
        self._view.playfield.run(lambda: layer.sync([enemy], dt))
        enemy.x = x
        enemy.y = y
        if self._blasts is not None:
            blasts = self._new_blasts
            self._new_blasts = []
            self._view.playfield.run(lambda: self._blasts.sync(blasts, dt))

    def _sync_world(self, world: EnemyWorld, dt: float) -> None:
        """Game view: draw the enemies where they are, their shots and the explosions."""
        layer = self._layer
        enemies = [e for e in world.enemies if not e.gone]
        shots = world.shots
        frame = EnemyShotFrame(
            [b for b in shots.bullets if b.alive],
            [m for m in shots.missiles if m.alive],
            shots.lasers,
            dt,
        )
        blasts = self._new_blasts
        self._new_blasts = []

        def draw() -> None:
            layer.sync(enemies, dt)
            self._shot_layer.sync(frame)
            self._blasts.sync(blasts, dt)

        self._view.playfield.run(draw)

    def _animate(self, dt: float) -> None:
        """Step the model's animations and set the camera's field of view (the close-up's)."""
        if self._ship is not None:
            self._ship.update(dt)
        self._live(dt)
        self._sync(dt)
        if self._world is None:
            self._apply_turn()
        self._view.update(self._at, dt)
        camera = self._view.stage.camera
        self._follow(camera)
        camera.fov = self._fov
        # The game view is at game size: nothing to fill the screen with.
        if self._toggle and self._world is None:
            camera.fov = close_up_fov(self._size, self._distance(), CFG.close_up_fill, self._fov)
        camera.fov = zoomed_fov(camera.fov, self._zoom)

    def _follow(self, camera: Any) -> None:
        """Game view: move the camera so the enemy (the boss) is in the middle of the screen.

        The camera was just put where it looks at the middle of the playfield. The eye the enemies'
        shots are projected from moves with it (GFX-SHOT-09). Nowhere else is the camera moved.
        """
        world = self._world
        enemy = self._enemy
        if world is None or enemy is None:
            self._shift = [0.0, 0.0]
            return
        dx = enemy.x - self._middle_point[0]
        dy = enemy.y - self._middle_point[1]
        self._shift = [dx, dy]
        camera.position.x += dx
        camera.position.z += dy
        # Looking the way the stage's camera does, from where it is now.
        ahead = self._view.stage.framing.direction
        position = camera.position
        camera.setTarget(vector3(position.x, position.y + ahead[0], position.z + ahead[1]))
        screen = self.game.playfield
        eye = playfield_eye(screen, self._view.stage.framing)
        eye.x += dx
        eye.y += dy
        world.options.eye = eye

    def _apply_turn(self) -> None:
        """Turn the model as dragged.

        A ship or an enemy around its nose and nose up or down (on top of the bank and heading the
        game gives them).
        """
        # `_show_item` made a ship, or a layer and an enemy that `_sync` has just drawn.
        pivot = self._ship.pivot if self._ship is not None else self._layer.pivot_of(self._enemy)
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
        """Releases the scene and the props of the viewer."""
        self._drop_scene()
        if self._props is not None:
            self._props.dispose()
        self._props = None
        self._host = None
