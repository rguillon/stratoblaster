# Copyright (c) 2026 Renaud Guillon
"""What the game gives the engine to draw it ().

The interfaces are plain classes here, so they can be imported at run time and implemented
structurally (no base class needed). The type aliases are for annotations only: import them inside a
`__pragma__("skip")` block.

Models face +Z (nose), with +Y up, and are centred on the origin. The playfield is the XY plane at Z
= 0, one world unit per logical pixel, Y up, seen from -Z.
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

# Builds a model in the scene and returns its root node.
ModelFactory = Callable[[Any], Any]
# __pragma__ ("noskip")


class MenuBackdrop:
    """The animated 3D scene behind the menus, built by the game.

    Implementations provide `update(dt_seconds)` and the attribute `glow_excluded_meshes` (self-lit
    meshes, sky and sun, that must not bloom in the glow layer).
    """


class ShotRenderer:
    """Draws the shots of one weapon, frame after frame: `sync(frame)`, `dispose()`."""


class ShotFrame:
    """What a shot renderer draws on one frame.

    `projectiles`: projectiles of this renderer's weapon in flight. `beam`: beam segments of this
    weapon (empty when it is not firing). `impacts`: impacts since the previous frame.
    """

    def __init__(
        self, projectiles: list[Any], beam: list[Any], impacts: list[Any], dt_seconds: float
    ) -> None:
        self.projectiles = projectiles
        self.beam = beam
        self.impacts = impacts
        self.dt_seconds = dt_seconds


class BombFrame:
    """What the bomb renderer draws on one frame, in playfield space.

    `bomb` is the bomb going off, if any.
    """

    def __init__(self, bomb: Any, dt_seconds: float) -> None:
        self.bomb = bomb
        self.dt_seconds = dt_seconds


class BombRenderer:
    """Draws a bomb going off: `sync(frame)`, `dispose()`."""


class BonusFrame:
    """What the bonus renderer draws on one frame.

    It shows the `bonuses` falling, and the `picked` ones up since the previous frame (where they
    were).
    """

    def __init__(self, bonuses: list[Any], picked: list[Any], dt_seconds: float) -> None:
        self.bonuses = bonuses
        self.picked = picked
        self.dt_seconds = dt_seconds


class BonusRenderer:
    """Draws the bonuses falling, each kind its own look, and a flash where the ship picks one up.

    Methods: `sync(frame)`, `dispose()`.
    """


class EnemyShotFrame:
    """What the enemy shot renderer draws on one frame.

    `bullets` and `missiles` in flight, and `lasers` in their warning or firing phase.
    """

    def __init__(
        self,
        bullets: list[Any],
        missiles: list[Any],
        lasers: list[Any],
        dt_seconds: float,
    ) -> None:
        self.bullets = bullets
        self.missiles = missiles
        self.lasers = lasers
        self.dt_seconds = dt_seconds


class GlowLook:
    """Glow of the self-lit parts: `intensity` and the blur kernel size."""

    def __init__(self, intensity: float, blur_kernel_size: float) -> None:
        self.intensity = intensity
        self.blur_kernel_size = blur_kernel_size


class EnemyBindings:
    """Presentation of the enemies (`GameDefinition.enemyKinds`).

    `models`: one model per `EnemyStats.model` key, a `root` node (facing +Z with +Y up, centred on
    the origin, in logical pixels) and `sync(enemy, dt_seconds)`. `shots(scene, style)`: the enemy
    shot renderer (`sync(frame)`, `dispose()`), in the level's style if any. `blasts(scene)`: the
    explosion renderer (`sync(blasts, dt_seconds)` with the blasts new since the previous frame,
    `dispose()`). `glow`: a `GlowLook`. `set_idle_motion(on)` (optional): turns the idle animation
    on or off. `child_models`: the models of the enemies other enemies send out (e.g. a carrier's
    drones), built with every level's own models (PERF-21).
    """

    def __init__(
        self,
        models: dict[str, Any],
        shots: Any,
        blasts: Any,
        glow: GlowLook,
        set_idle_motion: Any = None,
        child_models: list[str] | None = None,
    ) -> None:
        self.models = models
        self.shots = shots
        self.blasts = blasts
        self.glow = glow
        self.set_idle_motion = set_idle_motion
        self.child_models = child_models if child_models is not None else []


class PropGroup:
    """A named group of prop model ids, shown together on the `props/` page.

    `notes` (optional, a dict of id to text) is a note shown after some ids' names. `streets` says
    whether the props stand in blocks ringed by road tiles.
    """

    def __init__(
        self,
        label: str,
        ids: list[str],
        notes: dict[str, str] | None = None,
        streets: bool | None = None,
    ) -> None:
        self.label = label
        self.ids = ids
        self.notes = notes
        self.streets = streets


class PropTiles:
    """The ground of the `props/` page: its tiles, their look and its road pieces.

    `tile` is the grid of tiles, `look` how its road tiles look, and `pieces` (optional) the models
    drawn as road pieces by id.
    """

    def __init__(self, tile: Any, look: Any, pieces: dict[str, list[Any]] | None = None) -> None:
        self.tile = tile
        self.look = look
        self.pieces = pieces


class SceneryBindings:
    """Presentation of the levels with generated ground (`GameDefinition.sceneryLevels`).

    `camera`: a `PlayfieldCameraLook`. `looks`: one `SceneryLook` per scenery level id.
    `prop_models`: one model per prop kind id. `prop_groups` (optional): how the `props/` page
    groups the prop models. `prop_tiles` (optional): a `PropTiles`.
    """

    def __init__(
        self,
        camera: Any,
        looks: dict[str, Any],
        prop_models: dict[str, Any],
        prop_groups: list[PropGroup] | None = None,
        prop_tiles: PropTiles | None = None,
    ) -> None:
        self.camera = camera
        self.looks = looks
        self.prop_models = prop_models
        self.prop_groups = prop_groups
        self.prop_tiles = prop_tiles


class GameView:
    """Presentation bindings a game provides to the engine (`GameDefinition.view`).

    The fields, in order: `player_ship_models` (one model per player ship id), `player_ship_scale`
    (logical pixels per model unit), `player_shot_renderers` (one per player weapon id),
    `menu_backdrop` (`scene -> None`: fills it with the menu backdrop), `scenery`
    (`SceneryBindings`), `enemies` (`EnemyBindings`), `bonuses` (`scene -> BonusRenderer`).
    Optional, None when left out: `bombs` (`scene -> BombRenderer`), `audio` (`AudioBindings`),
    `outline` (`OutlineLook`).
    """

    def __init__(
        self,
        player_ship_models: dict[str, Any],
        player_ship_scale: float,
        player_shot_renderers: dict[str, Any],
        menu_backdrop: Any,
        scenery: SceneryBindings,
        enemies: EnemyBindings,
        bonuses: Any,
        bombs: Any = None,
        audio: Any = None,
        outline: Any = None,
    ) -> None:
        self.player_ship_models = player_ship_models
        self.player_ship_scale = player_ship_scale
        self.player_shot_renderers = player_shot_renderers
        self.menu_backdrop = menu_backdrop
        self.scenery = scenery
        self.enemies = enemies
        self.bonuses = bonuses
        self.bombs = bombs
        self.audio = audio
        self.outline = outline
