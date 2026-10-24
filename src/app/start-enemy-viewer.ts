import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { Scene } from '@babylonjs/core/scene';
import type { GameDefinition } from '../core/content/game-definition';
import { validateEnemyKinds } from '../core/entities/enemy';
import { shipMaxSpeedPxPerSec } from '../core/entities/player-ship';
import { validateWeapons, type WeaponDefinition } from '../core/entities/weapon';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { createRng } from '../core/math/rng';
import { EnemyWorld, type EnemyBlast } from '../core/systems/enemy-world';
import { ShotWorld, type ShotImpact } from '../core/systems/shot-world';
import { EnemyLayer } from '../render/enemy-layer';
import type { GameView } from '../render/game-view';
import { visibleHalfWidth } from '../render/scenery/playfield-framing';
import { HeldDirections } from '../input/held-directions';
import { EnemyViewerPanel, type EnemyViewerSelection } from '../ui/enemy-viewer-panel';
import { StatsTile } from '../ui/stats-tile';
import { ENEMY_VIEWER_CONFIG as CFG } from '../config/enemy-viewer';
import { EnemyCloseUp } from './enemy-close-up';
import { HELP, shortcut, SWITCH_KEYS } from './enemy-viewer-keys';
import { buildEnemyViewerScene, type EnemyViewerScene } from './enemy-viewer-scene';
import { EnemyViewerShots } from './enemy-viewer-shots';
import { RateMeter } from './rate-meter';
import { PlayfieldShip } from './shot-viewer-scene';

/** Options of {@link startEnemyViewer}. */
export interface EnemyViewerOptions {
  /** Generated textures, sky lighting, shadows and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  readonly doc: Pick<Document, 'createElement'>;
  /** Where the controls go. */
  readonly panelParent: HTMLElement;
  /** Where the FPS / polygons tile goes. No tile when omitted. */
  readonly statsParent?: HTMLElement;
  /** Where keys are listened to (movement, shortcuts). No keyboard when omitted. */
  readonly keyboardTarget?: Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;
  /** Seconds elapsed since the previous frame. Defaults to the engine's frame time. */
  readonly frameSeconds?: () => number;
  /** Starts the engine's render loop (off in unit tests, which call `frame()`). */
  readonly renderLoop: boolean;
}

/** Handle on a running enemies page. */
export interface RunningEnemyViewer {
  readonly scene: Scene;
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly panel: EnemyViewerPanel;
  /** The model view's own scene. */
  readonly closeUp: EnemyCloseUp;
  readonly player: { readonly x: number; readonly y: number };
  /** Advances and draws one frame of `dt` seconds. */
  frame(dt: number): void;
  /** A key going down (`down` true) or up; `code` is `KeyboardEvent.code`. */
  key(key: string, code: string, down: boolean): void;
  dispose(): void;
}

function weaponAt(game: GameDefinition, index: number): WeaponDefinition {
  const weapon = game.playerWeapons[index];
  if (!weapon) throw new Error(`No weapon at index ${String(index)}`);
  return weapon;
}

/** The pieces of a running page; see {@link startEnemyViewer}. */
class EnemyViewer {
  readonly view: EnemyViewerScene;
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly panel: EnemyViewerPanel;
  readonly closeUp: EnemyCloseUp;
  readonly player: { x: number; y: number } = { ...CFG.shipStart };
  readonly held = new HeldDirections();
  readonly #random = createRng(CFG.seed);
  readonly #clock = new FixedStepClock(CFG.stepHz, CFG.maxStepsPerFrame);
  readonly #layer: EnemyLayer;
  readonly #drawn: EnemyViewerShots;
  readonly #ship: PlayfieldShip;
  readonly #speed: number;
  readonly #stats: StatsTile | undefined;
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  #noseOffset = 0;
  #previous = 0;
  #respawnIn = 0;
  /** The kind and view shown, to restart only when they change. */
  #kind = -1;
  #modelView = false;

  constructor(
    engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    options: EnemyViewerOptions,
  ) {
    validateWeapons(game.playerWeapons);
    validateEnemyKinds(game.enemyKinds);
    const { width, height } = game.screen;
    this.view = buildEnemyViewerScene(engine, game, {
      environment: options.environment,
      glow: game.view.enemies.glow,
    });
    const area = { width, height, cullMargin: CFG.cullMargin };
    this.enemies = new EnemyWorld({ ...area, maxEnemyAge: CFG.maxEnemyAge }, this.#random);
    this.shots = new ShotWorld(area, weaponAt(game, 0));
    this.shots.targets = this.enemies.targets;
    const pf = this.view.playfield;
    this.#layer = pf.run(() => new EnemyLayer(this.view.scene, game.view.enemies.models));
    this.#drawn = new EnemyViewerShots(game, pf);
    this.#ship = this.#buildShip();
    this.#speed = shipMaxSpeedPxPerSec(game.playerShips, game.playerShips.ships[0]?.id ?? '');
    this.closeUp = new EnemyCloseUp(engine, options.environment, game.view.enemies.glow);
    this.#stats = options.statsParent
      ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
      : undefined;
    this.panel = new EnemyViewerPanel({
      doc: options.doc,
      parent: options.panelParent,
      kinds: game.enemyKinds.map((k) => k.name),
      weapons: game.playerWeapons.map((w) => w.name),
      levelCounts: game.playerWeapons.map((w) => w.levels.length),
      initial: { kind: 0, view: 'behaviour', weapon: 0, level: 1, fire: true, paused: false },
      help: HELP,
      onChange: (selection) => {
        this.#apply(selection);
      },
    });
    this.#apply(this.panel.selection);
    this.frame(0);
  }

  /** The game's first ship; the muzzle is measured on its model, before it joins the playfield. */
  #buildShip(): PlayfieldShip {
    const first = this.game.playerShips.ships[0];
    const model = first && this.game.view.playerShipModels[first.id];
    return this.view.playfield.run(() => {
      const ship = new PlayfieldShip(this.view.scene, this.game.view.playerShipScale, 0, 0);
      if (model) this.#noseOffset = ship.show(model) - CFG.muzzleInset;
      return ship;
    });
  }

  #apply(s: EnemyViewerSelection): void {
    this.shots.select(weaponAt(this.game, s.weapon), s.level);
    this.shots.firing = s.fire;
    // The wireframe view is the model view drawn as lines (phase 5 review: to see the polygons).
    const modelView = s.view !== 'behaviour';
    this.closeUp.wireframe = s.view === 'wireframe';
    if (s.kind !== this.#kind || modelView !== this.#modelView) {
      this.#kind = s.kind;
      this.#modelView = modelView;
      this.#restart();
    }
    this.#ship.pivot.setEnabled(!modelView);
  }

  /** Starts the picked kind again: a new group, or its model in the model view. */
  #restart(): void {
    this.enemies.clear();
    for (const shot of this.shots.projectiles) shot.alive = false;
    this.#layer.clear();
    this.#respawnIn = 0;
    const kind = this.game.enemyKinds[this.panel.selection.kind];
    if (!kind) return;
    const [first] = kind.spawn(this.#area());
    const build = first ? this.game.view.enemies.models[first.model] : undefined;
    if (first && build) this.closeUp.show(build, first);
    if (!this.#modelView) this.#spawn();
  }

  #area() {
    return { ...this.game.screen, random: this.#random };
  }

  #spawn(): void {
    const kind = this.game.enemyKinds[this.panel.selection.kind];
    if (kind) this.enemies.add(...kind.spawn(this.#area()));
  }

  frame(dt: number): void {
    const { paused } = this.panel.selection;
    const { steps, alpha } = this.#clock.advance(dt);
    const blasts: EnemyBlast[] = [];
    const impacts: ShotImpact[] = [];
    for (let i = 0; i < steps && !paused; i++) {
      const step = this.#clock.stepSeconds;
      this.#previous = this.view.track.distance;
      this.view.track.step(step);
      if (this.view.track.ended) this.view.track.seek(0);
      if (this.#modelView) continue;
      this.#fly(step);
      this.enemies.step(step);
      blasts.push(...this.enemies.blasts);
      this.shots.step(step);
      impacts.push(...this.shots.impacts);
      this.#respawn(step);
    }
    const track = this.view.track;
    const distance = this.#previous + (track.distance - this.#previous) * (paused ? 1 : alpha);
    this.view.update(distance, dt);
    this.#draw(paused ? 0 : dt, blasts, impacts);
  }

  /** Moves the player ship with the held keys, within what the camera shows. */
  #fly(dt: number): void {
    const { x, y } = this.held.direction;
    const { width, height } = this.game.screen;
    const m = CFG.shipMargin;
    const py = Math.min(height - m.top, Math.max(m.bottom, this.player.y + y * this.#speed * dt));
    const half = visibleHalfWidth(this.view.stage.framing, width / height, py) - m.side;
    const px = this.player.x + x * this.#speed * dt;
    this.player.x = Math.min(width / 2 + half, Math.max(width / 2 - half, px));
    this.player.y = py;
    this.enemies.playerX = this.player.x;
    this.enemies.playerY = this.player.y;
    this.shots.muzzleX = this.shots.centerX = this.player.x;
    this.shots.centerY = this.player.y;
    this.shots.muzzleY = this.player.y + this.#noseOffset;
  }

  #respawn(dt: number): void {
    if (this.enemies.enemies.length > 0) return;
    this.#respawnIn += dt;
    if (this.#respawnIn < CFG.respawnDelay) return;
    this.#respawnIn = 0;
    this.#spawn();
  }

  #draw(dt: number, blasts: readonly EnemyBlast[], impacts: readonly ShotImpact[]): void {
    this.#ship.pivot.position.set(this.player.x, this.player.y, 0);
    this.#ship.update(dt);
    this.view.playfield.run(() => {
      this.#layer.sync(this.enemies.enemies, dt);
    });
    this.#drawn.sync({ enemies: this.enemies, shots: this.shots, blasts, impacts, dt });
    this.closeUp.update(dt);
    this.panel.showReadout({
      enemies: this.enemies.enemies.length,
      shots: this.enemies.shots.count,
      kills: this.enemies.kills,
      score: this.enemies.score,
    });
    this.#fps.add(dt, ++this.#frames);
    const scene = this.activeScene;
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons: scene.getActiveIndices() / 3 });
  }

  /** The scene to draw: the close-up in the model view, the level otherwise. */
  get activeScene(): Scene {
    return this.#modelView ? this.closeUp.scene : this.view.scene;
  }

  key(key: string, code: string, down: boolean): void {
    if (this.#modelView && down && SWITCH_KEYS[code] !== undefined) {
      const n = this.game.enemyKinds.length;
      this.panel.update({ kind: (this.panel.selection.kind + (SWITCH_KEYS[code] ?? 0) + n) % n });
      return;
    }
    if (this.held.key(code, down) || !down) return;
    const counts = { kinds: this.game.enemyKinds.length, weapons: this.game.playerWeapons.length };
    const change = shortcut(key, this.panel.selection, counts);
    if (change) this.panel.update(change);
  }

  dispose(): void {
    this.#layer.dispose();
    this.#drawn.dispose();
    this.panel.root.remove();
    this.#stats?.root.remove();
    this.closeUp.dispose();
    this.view.scene.dispose();
  }
}

/**
 * Starts the enemies debug page (P05-R11): the enemy kind picked spawns over Level Zero, again
 * and again, while a player ship flies (arrows / WASD) and shoots it with any weapon and level;
 * the model view shows the enemy's model alone, turning.
 */
export function startEnemyViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: EnemyViewerOptions,
): RunningEnemyViewer {
  const viewer = new EnemyViewer(engine, game, options);
  const onKey = (event: Event): void => {
    const e = event as KeyboardEvent;
    viewer.key(e.key, e.code, e.type === 'keydown');
  };
  const onBlur = (): void => {
    viewer.held.clear();
  };
  options.keyboardTarget?.addEventListener('keydown', onKey);
  options.keyboardTarget?.addEventListener('keyup', onKey);
  options.keyboardTarget?.addEventListener('blur', onBlur);
  const frameSeconds = options.frameSeconds ?? (() => engine.getDeltaTime() / 1000);
  if (options.renderLoop) {
    engine.runRenderLoop(() => {
      viewer.frame(Math.min(frameSeconds(), CFG.maxFrameSeconds));
      viewer.activeScene.render();
    });
  }
  return {
    scene: viewer.view.scene,
    enemies: viewer.enemies,
    shots: viewer.shots,
    panel: viewer.panel,
    closeUp: viewer.closeUp,
    player: viewer.player,
    frame: (dt) => {
      viewer.frame(dt);
    },
    key: (key, code, down) => {
      viewer.key(key, code, down);
    },
    dispose: () => {
      engine.stopRenderLoop();
      for (const type of ['keydown', 'keyup'])
        options.keyboardTarget?.removeEventListener(type, onKey);
      options.keyboardTarget?.removeEventListener('blur', onBlur);
      viewer.dispose();
    },
  };
}
