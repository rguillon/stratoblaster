"""The player shots viewer (P03-R10), ported from `app/start-shot-viewer.ts`: one ship at the bottom
of the playfield firing the selected weapon at the selected level, at dummy targets, with controls
to switch ship, weapon and level."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from app.dummy_targets import DummyTargets  # noqa: E402
from app.rate_meter import RateMeter  # noqa: E402
from app.shot_viewer_scene import PlayfieldShip, create_playfield_scene  # noqa: E402
from app.start_ship_viewer import frame_source  # noqa: E402
from config.shot_viewer import SHOT_VIEWER_CONFIG as CFG  # noqa: E402
from core.entities.weapon import ShotStream, validate_weapons  # noqa: E402
from core.loop.fixed_step_clock import FixedStepClock  # noqa: E402
from core.systems.shot_world import ShotWorld, ShotWorldOptions  # noqa: E402
from render.environment.showcase_environment_visual import (  # noqa: E402
    ShowcaseEnvironmentOptions,
    ShowcaseGlow,
    apply_showcase_environment,
)
from render.game_view import ShotFrame  # noqa: E402
from render.shot_playfield import TargetMarkers, build_playfield_grid, build_stream_guides  # noqa: E402
from ui.shot_viewer_panel import (  # noqa: E402
    ShotViewerPanel,
    ShotViewerPanelOptions,
    ShotViewerReadout,
    ShotViewerSelection,
)
from ui.stats_tile import RenderStats, StatsTile  # noqa: E402
from ui.weapon_summary import weapon_summary  # noqa: E402


class ShotViewerOptions:
    """Options of `start_shot_viewer`.

    `environment`: procedural image-based lighting and glow (needs a real WebGL engine). `doc` and
    `panel_parent`: where the controls go. `stats_parent`: where the FPS / polygons tile goes (None:
    no tile). `keyboard_target`: where shortcuts are listened to (None: none). `frame_seconds`:
    seconds since the previous frame (None: the engine's). `render_loop`: starts the engine's render
    loop (off in unit tests, which call `frame()`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        environment: bool,
        doc: Any,
        panel_parent: Any,
        stats_parent: Any,
        keyboard_target: Any,
        frame_seconds: Any,
        render_loop: bool,
    ) -> None:
        self.environment = environment
        self.doc = doc
        self.panel_parent = panel_parent
        self.stats_parent = stats_parent
        self.keyboard_target = keyboard_target
        self.frame_seconds = frame_seconds
        self.render_loop = render_loop


class _Point:
    """A point on the playfield (logical pixels, Y up)."""

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


def _renderers_of(game: Any, scene: Any) -> list[list[Any]]:
    """One shot renderer per player weapon, as [weapon id, renderer] pairs in weapon order."""
    pairs: list[list[Any]] = []
    for weapon in game.player_weapons:
        factory = game.view.player_shot_renderers.get(weapon.id)
        if not factory:
            raise ValueError('No shot renderer for weapon "' + weapon.id + '"')
        pairs.append([weapon.id, factory(scene)])
    return pairs


def _weapon_at(game: Any, index: int) -> Any:
    if index < 0 or index >= len(game.player_weapons):
        raise ValueError("No weapon at index " + str(index))
    return game.player_weapons[index]


def _wrap_next(i: int, n: int) -> int:
    """`(i + 1) % max(1, n)`: the next index, cycling through `n` items."""
    return (i + 1) % max(1, n)


def _shot_shortcut(key: str, s: ShotViewerSelection, game: Any) -> dict[str, Any] | None:
    """Keyboard shortcuts: 1-9 level, W next weapon, S next ship, G guides, T targets."""
    k = key.lower()
    if len(k) == 1 and k >= "1" and k <= "9":
        return {"level": int(k)}
    if k == "w":
        return {"weapon": _wrap_next(s.weapon, len(game.player_weapons)), "level": 1}
    if k == "s":
        return {"ship": _wrap_next(s.ship, len(game.player_ships.ships))}
    if k == "g":
        return {"guides": not s.guides}
    if k == "t":
        return {"targets": not s.targets}
    return None


def _launch_origin(weapon: Any, muzzle: _Point, center: _Point) -> _Point:
    """Where a weapon's streams start: the muzzle, or the ship's centre."""
    if weapon.kind == "projectile" and weapon.launch_point == "center":
        return center
    return muzzle


def _guide_streams(weapon: Any, level: int) -> Any:
    """Streams to draw guides for: those of a projectile level, or straight ahead for a beam."""
    if weapon.kind == "projectile":
        levels = weapon.levels
        if 0 <= level - 1 < len(levels):
            return levels[level - 1]
        return []
    return [ShotStream(0, 0)]


class _ShotViewer:
    """The pieces of a running viewer; see `start_shot_viewer`."""

    def __init__(self, engine: Any, game: Any, options: ShotViewerOptions) -> None:
        self.game = game
        self._clock = FixedStepClock(CFG.step_hz, int(CFG.max_steps_per_frame))
        self._damage = RateMeter(CFG.damage_rate_window)
        self._fps = RateMeter(CFG.stats.fps_window)
        self._frames = 0
        targets_config: Any = CFG.targets
        self.targets = DummyTargets(targets_config)
        validate_weapons(game.player_weapons)
        width = game.screen.width
        height = game.screen.height
        self.scene = create_playfield_scene(engine, game.screen)
        if options.environment:
            env: Any = CFG.environment
            glow: Any = CFG.glow
            apply_showcase_environment(
                self.scene,
                ShowcaseEnvironmentOptions(
                    env.cube_size,
                    env.intensity,
                    env.stops,
                    ShowcaseGlow(glow.intensity, glow.blur_kernel_size),
                ),
            )
        build_playfield_grid(
            self.scene, game.screen, CFG.grid.cell, CFG.grid.depth, list(CFG.grid.color)
        )
        self._muzzle = _Point(width / 2, CFG.ship_y)
        self._center = _Point(width / 2, CFG.ship_y)
        self._ship = PlayfieldShip(
            self.scene, game.view.player_ship_scale, self._muzzle.x, CFG.ship_y
        )
        self.world = ShotWorld(
            ShotWorldOptions(width, height, CFG.cull_margin), _weapon_at(game, 0)
        )
        self.world.muzzle_x = self._muzzle.x
        self.world.muzzle_y = self._muzzle.y
        self.world.center_x = self._center.x
        self.world.center_y = self._center.y
        targets_list: Any = self.targets.targets
        self.world.targets = targets_list
        self._markers = TargetMarkers(self.scene, self.targets.targets, targets_config)
        self._renderers = _renderers_of(game, self.scene)
        self._stats: Any = None
        if options.stats_parent:
            self._stats = StatsTile(options.doc, options.stats_parent, CFG.stats.refresh)
        self._guides: Any = None

        def on_change(selection: ShotViewerSelection) -> None:
            self._apply(selection)

        self.panel = ShotViewerPanel(
            ShotViewerPanelOptions(
                options.doc,
                options.panel_parent,
                [s.name for s in game.player_ships.ships],
                [w.name for w in game.player_weapons],
                [len(w.levels) for w in game.player_weapons],
                ShotViewerSelection(0, 0, 1, False, True),
                on_change,
            )
        )
        self._apply(self.panel.selection)

    def _apply(self, s: ShotViewerSelection) -> None:
        """Shows the selected ship, fires the selected weapon and level, toggles guides, targets."""
        ship_def = (
            self.game.player_ships.ships[s.ship]
            if s.ship < len(self.game.player_ships.ships)
            else None
        )
        model = self.game.view.player_ship_models.get(ship_def.id) if ship_def else None
        if model:
            nose_y = self._ship.show(model)
            self._muzzle = _Point(self._muzzle.x, nose_y - CFG.muzzle_inset)
            self.world.muzzle_y = self._muzzle.y
        weapon = _weapon_at(self.game, s.weapon)
        self.world.select(weapon, s.level)
        if self.targets.enabled != s.targets:
            self.targets.set_enabled(s.targets)
        if self._guides:
            self._guides.dispose()
        self._guides = None
        if s.guides:
            origin = _launch_origin(weapon, self._muzzle, self._center)
            self._guides = build_stream_guides(
                self.scene,
                origin,
                _guide_streams(weapon, self.world.level),
                CFG.guides.length_,
                list(CFG.guides.color),
            )

    def frame(self, dt: float) -> None:
        advance = self._clock.advance(dt)
        impacts: list[Any] = []
        for _step in range(advance.steps):
            self.targets.update(self._clock.step_seconds)
            self.world.step(self._clock.step_seconds)
            for impact in self.world.impacts:
                impacts.append(impact)
        self._damage.add(dt, self.world.total_damage)
        self._ship.update(dt)
        self._markers.sync(self.targets.targets)
        flying = [p for p in self.world.projectiles if p.alive]
        for pair in self._renderers:
            weapon_id = pair[0]
            beam = self.world.beam if self.world.weapon.id == weapon_id else []
            pair[1].sync(
                ShotFrame(
                    [p for p in flying if p.weapon.id == weapon_id],
                    beam,
                    [i for i in impacts if i.weapon_id == weapon_id],
                    dt,
                )
            )
        self.panel.show_readout(
            ShotViewerReadout(
                weapon_summary(self.world.weapon, self.world.level),
                len(flying),
                self._damage.rate,
                self.targets.kills,
            )
        )
        self._frames += 1
        self._fps.add(dt, self._frames)
        # Triangles drawn by the last render (before this frame's).
        if self._stats:
            self._stats.update(dt, RenderStats(self._fps.rate, self.scene.getActiveIndices() / 3))

    def key(self, key: str) -> None:
        """Applies a keyboard shortcut, if `key` is one."""
        change = _shot_shortcut(key, self.panel.selection, self.game)
        if change:
            self.panel.update(change)

    def dispose(self) -> None:
        for pair in self._renderers:
            pair[1].dispose()
        self.panel.root.remove()
        if self._stats:
            self._stats.root.remove()
        self.scene.dispose()


class RunningShotViewer:
    """Handle on a running shots viewer: `scene`, `world`, `targets` and `panel`, `frame(dt)` and
    `dispose()`."""

    def __init__(self, engine: Any, viewer: _ShotViewer, on_key: Any, keyboard_target: Any) -> None:
        self._engine = engine
        self._viewer = viewer
        self._on_key = on_key
        self._keyboard_target = keyboard_target
        self.scene = viewer.scene
        self.world = viewer.world
        self.targets = viewer.targets
        self.panel = viewer.panel

    def frame(self, dt: float) -> None:
        self._viewer.frame(dt)

    def dispose(self) -> None:
        self._engine.stopRenderLoop()
        if self._keyboard_target:
            self._keyboard_target.removeEventListener("keydown", self._on_key)
        self._viewer.dispose()


def start_shot_viewer(engine: Any, game: Any, options: ShotViewerOptions) -> RunningShotViewer:
    """Starts the player shots viewer (P03-R10): one ship at the bottom of the playfield firing the
    selected weapon at the selected level, at dummy targets, with controls to switch ship, weapon
    and level."""
    viewer = _ShotViewer(engine, game, options)

    def on_key(event: Any) -> None:
        viewer.key(event.key)

    if options.keyboard_target:
        options.keyboard_target.addEventListener("keydown", on_key)
    frame_seconds = options.frame_seconds if options.frame_seconds else frame_source(engine)
    if options.render_loop:

        def render_frame() -> None:
            viewer.frame(frame_seconds())
            viewer.scene.render()

        engine.runRenderLoop(render_frame)
    return RunningShotViewer(engine, viewer, on_key, options.keyboard_target)
