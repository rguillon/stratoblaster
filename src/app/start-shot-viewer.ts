import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { LinesMesh } from '@babylonjs/core/Meshes/linesMesh';
import type { Scene } from '@babylonjs/core/scene';
import type { GameDefinition } from '../core/content/game-definition';
import { validateWeapons, type WeaponDefinition } from '../core/entities/weapon';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { ShotWorld, type ShotImpact } from '../core/systems/shot-world';
import type { GameView, ShotRenderer } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { buildPlayfieldGrid, buildStreamGuides, TargetMarkers } from '../render/shot-playfield';
import { ShotViewerPanel, type ShotViewerSelection } from '../ui/shot-viewer-panel';
import { StatsTile } from '../ui/stats-tile';
import { weaponSummary } from '../ui/weapon-summary';
import { SHOT_VIEWER_CONFIG as CFG } from '../config/shot-viewer';
import { DummyTargets } from './dummy-targets';
import { RateMeter } from './rate-meter';
import { createPlayfieldScene, PlayfieldShip } from './shot-viewer-scene';

/** Options of {@link startShotViewer}. */
export interface ShotViewerOptions {
  /** Procedural image-based lighting and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  /** Where the controls go. */
  readonly doc: Pick<Document, 'createElement'>;
  readonly panelParent: HTMLElement;
  /** Where the FPS / polygons tile goes. No tile when omitted. */
  readonly statsParent?: HTMLElement;
  /** Where keyboard shortcuts are listened to. No shortcuts when omitted. */
  readonly keyboardTarget?: Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;
  /** Seconds elapsed since the previous frame. Defaults to the engine's frame time. */
  readonly frameSeconds?: () => number;
  /** Starts the engine's render loop (off in unit tests, which call `frame()`). */
  readonly renderLoop: boolean;
}

/** Handle on a running shots viewer. */
export interface RunningShotViewer {
  readonly scene: Scene;
  readonly world: ShotWorld;
  readonly targets: DummyTargets;
  readonly panel: ShotViewerPanel;
  /** Advances and draws one frame of `dt` seconds. */
  frame(dt: number): void;
  dispose(): void;
}

function renderersOf(game: GameDefinition<GameView>, scene: Scene): Map<string, ShotRenderer> {
  return new Map(
    game.playerWeapons.map((weapon) => {
      const factory = game.view.playerShotRenderers[weapon.id];
      if (!factory) throw new Error(`No shot renderer for weapon "${weapon.id}"`);
      return [weapon.id, factory(scene)];
    }),
  );
}

function weaponAt(game: GameDefinition, index: number): WeaponDefinition {
  const weapon = game.playerWeapons[index];
  if (!weapon) throw new Error(`No weapon at index ${String(index)}`);
  return weapon;
}

/** Keyboard shortcuts: 1-9 level, W next weapon, S next ship, G guides, T targets. */
function shortcut(key: string, s: ShotViewerSelection, game: GameDefinition) {
  const wrap = (i: number, n: number): number => (i + 1) % Math.max(1, n);
  const k = key.toLowerCase();
  if (/^[1-9]$/.test(k)) return { level: Number(k) };
  if (k === 'w') return { weapon: wrap(s.weapon, game.playerWeapons.length), level: 1 };
  if (k === 's') return { ship: wrap(s.ship, game.playerShips.ships.length) };
  if (k === 'g') return { guides: !s.guides };
  if (k === 't') return { targets: !s.targets };
  return undefined;
}

interface Point {
  readonly x: number;
  readonly y: number;
}

/** Where a weapon's streams start: the muzzle, or the ship's centre. */
function launchOrigin(weapon: WeaponDefinition, muzzle: Point, center: Point): Point {
  return weapon.kind === 'projectile' && weapon.launchPoint === 'center' ? center : muzzle;
}

/** Streams to draw guides for: those of a projectile level, or straight ahead for a beam. */
function guideStreams(weapon: WeaponDefinition, level: number) {
  return weapon.kind === 'projectile'
    ? (weapon.levels[level - 1] ?? [])
    : [{ offsetX: 0, angleDeg: 0 }];
}

/** The pieces of a running viewer; see {@link startShotViewer}. */
class ShotViewer implements RunningShotViewer {
  readonly scene: Scene;
  readonly world: ShotWorld;
  readonly targets = new DummyTargets(CFG.targets);
  readonly panel: ShotViewerPanel;
  readonly #ship: PlayfieldShip;
  readonly #markers: TargetMarkers;
  readonly #renderers: Map<string, ShotRenderer>;
  readonly #clock = new FixedStepClock(CFG.stepHz, CFG.maxStepsPerFrame);
  readonly #damage = new RateMeter(CFG.damageRateWindow);
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  readonly #stats: StatsTile | undefined;
  #muzzle: Point;
  readonly #center: Point;
  #guides: LinesMesh | undefined;

  constructor(
    engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    options: ShotViewerOptions,
  ) {
    validateWeapons(game.playerWeapons);
    const { width, height } = game.screen;
    this.scene = createPlayfieldScene(engine, game.screen);
    if (options.environment) {
      applyShowcaseEnvironment(this.scene, { ...CFG.environment, glow: CFG.glow });
    }
    buildPlayfieldGrid(this.scene, game.screen, CFG.grid.cell, CFG.grid.depth, CFG.grid.color);
    this.#muzzle = { x: width / 2, y: CFG.shipY };
    this.#center = { x: width / 2, y: CFG.shipY };
    this.#ship = new PlayfieldShip(
      this.scene,
      game.view.playerShipScale,
      this.#muzzle.x,
      CFG.shipY,
    );
    this.world = new ShotWorld({ width, height, cullMargin: CFG.cullMargin }, weaponAt(game, 0));
    this.world.muzzleX = this.#muzzle.x;
    this.world.muzzleY = this.#muzzle.y;
    this.world.centerX = this.#center.x;
    this.world.centerY = this.#center.y;
    this.world.targets = this.targets.targets;
    this.#markers = new TargetMarkers(this.scene, this.targets.targets, CFG.targets);
    this.#renderers = renderersOf(game, this.scene);
    this.#stats = options.statsParent
      ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
      : undefined;
    this.panel = new ShotViewerPanel({
      doc: options.doc,
      parent: options.panelParent,
      ships: game.playerShips.ships.map((s) => s.name),
      weapons: game.playerWeapons.map((w) => w.name),
      levelCounts: game.playerWeapons.map((w) => w.levels.length),
      initial: { ship: 0, weapon: 0, level: 1, guides: false, targets: true },
      onChange: (selection) => {
        this.#apply(selection);
      },
    });
    this.#apply(this.panel.selection);
  }

  /** Shows the selected ship, fires the selected weapon and level, toggles guides and targets. */
  #apply(s: ShotViewerSelection): void {
    const shipDef = this.game.playerShips.ships[s.ship];
    const model = shipDef && this.game.view.playerShipModels[shipDef.id];
    if (model) {
      const noseY = this.#ship.show(model);
      this.#muzzle = { x: this.#muzzle.x, y: noseY - CFG.muzzleInset };
      this.world.muzzleY = this.#muzzle.y;
    }
    const weapon = weaponAt(this.game, s.weapon);
    this.world.select(weapon, s.level);
    if (this.targets.enabled !== s.targets) this.targets.setEnabled(s.targets);
    this.#guides?.dispose();
    this.#guides = s.guides
      ? buildStreamGuides(
          this.scene,
          launchOrigin(weapon, this.#muzzle, this.#center),
          guideStreams(weapon, this.world.level),
          CFG.guides.length,
          CFG.guides.color,
        )
      : undefined;
  }

  frame(dt: number): void {
    const { steps } = this.#clock.advance(dt);
    const impacts: ShotImpact[] = [];
    for (let i = 0; i < steps; i++) {
      this.targets.update(this.#clock.stepSeconds);
      this.world.step(this.#clock.stepSeconds);
      impacts.push(...this.world.impacts);
    }
    this.#damage.add(dt, this.world.totalDamage);
    this.#ship.update(dt);
    this.#markers.sync(this.targets.targets);
    const flying = this.world.projectiles.filter((p) => p.alive);
    for (const [id, renderer] of this.#renderers) {
      renderer.sync({
        projectiles: flying.filter((p) => p.weapon.id === id),
        beam: this.world.weapon.id === id ? this.world.beam : [],
        impacts: impacts.filter((impact) => impact.weaponId === id),
        dtSeconds: dt,
      });
    }
    this.panel.showReadout({
      summary: weaponSummary(this.world.weapon, this.world.level),
      shots: flying.length,
      damagePerSecond: this.#damage.rate,
      kills: this.targets.kills,
    });
    this.#fps.add(dt, ++this.#frames);
    // Triangles drawn by the last render (before this frame's).
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons: this.scene.getActiveIndices() / 3 });
  }

  /** Applies a keyboard shortcut, if `key` is one. */
  key(key: string): void {
    const change = shortcut(key, this.panel.selection, this.game);
    if (change) this.panel.update(change);
  }

  dispose(): void {
    for (const renderer of this.#renderers.values()) renderer.dispose();
    this.panel.root.remove();
    this.#stats?.root.remove();
    this.scene.dispose();
  }
}

/**
 * Starts the player shots viewer (P03-R10): one ship at the bottom of the playfield firing the
 * selected weapon at the selected level, at dummy targets, with controls to switch ship,
 * weapon and level.
 */
export function startShotViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: ShotViewerOptions,
): RunningShotViewer {
  const viewer = new ShotViewer(engine, game, options);
  const onKey = (event: Event): void => {
    viewer.key((event as KeyboardEvent).key);
  };
  options.keyboardTarget?.addEventListener('keydown', onKey);
  const frameSeconds = options.frameSeconds ?? (() => engine.getDeltaTime() / 1000);
  if (options.renderLoop) {
    engine.runRenderLoop(() => {
      viewer.frame(frameSeconds());
      viewer.scene.render();
    });
  }
  return {
    scene: viewer.scene,
    world: viewer.world,
    targets: viewer.targets,
    panel: viewer.panel,
    frame: (dt) => {
      viewer.frame(dt);
    },
    dispose: () => {
      engine.stopRenderLoop();
      options.keyboardTarget?.removeEventListener('keydown', onKey);
      viewer.dispose();
    },
  };
}
