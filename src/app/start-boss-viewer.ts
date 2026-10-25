import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { Scene } from '@babylonjs/core/scene';
import type { GameDefinition } from '../core/content/game-definition';
import type { Boss } from '../core/entities/boss';
import { shipMaxSpeedPxPerSec } from '../core/entities/player-ship';
import { validateWeapons, type WeaponDefinition } from '../core/entities/weapon';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { createRng } from '../core/math/rng';
import type { BossKindDefinition } from '../core/systems/boss-fights';
import type { EnemyBlast } from '../core/systems/enemy-world';
import type { ShotImpact } from '../core/systems/shot-world';
import type { GameView } from '../render/game-view';
import { HeldDirections } from '../input/held-directions';
import { EnemyViewerPanel, type EnemyViewerSelection } from '../ui/enemy-viewer-panel';
import { StatsTile } from '../ui/stats-tile';
import { BOSS_VIEWER_CONFIG as CFG } from '../config/boss-viewer';
import {
  bossViewerState,
  BossViewerStage,
  circlesOf,
  levelOfBoss,
  type BossViewerState,
} from './boss-viewer-stage';
import { EnemyCloseUp } from './enemy-close-up';
import { shortcut, SWITCH_KEYS } from './enemy-viewer-keys';
import type { EnemyViewerOptions } from './start-enemy-viewer';
import { RateMeter } from './rate-meter';

/** Options of {@link startBossViewer}: as for the enemies page. */
export type BossViewerOptions = EnemyViewerOptions;

export type { BossViewerState } from './boss-viewer-stage';

/** Handle on a running bosses page. */
export interface RunningBossViewer {
  readonly panel: EnemyViewerPanel;
  readonly closeUp: EnemyCloseUp;
  /** The scene drawn now: the level's, or the model view's. */
  readonly activeScene: Scene;
  state(): BossViewerState;
  frame(dt: number): void;
  /** A key going down (`down` true) or up; `code` is `KeyboardEvent.code`. */
  key(key: string, code: string, down: boolean): void;
  dispose(): void;
}

const HELP =
  'Move: arrows / WASD · N / B: next / previous boss · K: destroy a part · M: model · V: wireframe (← / →: switch boss) · X: weapon · 1-5: level · F: fire · P: pause';

function weaponAt(game: GameDefinition, index: number): WeaponDefinition {
  const weapon = game.playerWeapons[index];
  if (!weapon) throw new Error(`No weapon at index ${String(index)}`);
  return weapon;
}

/** The pieces of a running page; see {@link startBossViewer}. */
class BossViewer {
  readonly panel: EnemyViewerPanel;
  readonly closeUp: EnemyCloseUp;
  readonly player: { x: number; y: number } = { ...CFG.shipStart };
  readonly held = new HeldDirections();
  #stage: BossViewerStage;
  #boss: Boss | undefined;
  readonly #random = createRng(CFG.seed);
  readonly #clock = new FixedStepClock(CFG.stepHz, CFG.maxStepsPerFrame);
  readonly #speed: number;
  readonly #stats: StatsTile | undefined;
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  #previous = 0;
  #respawnIn = 0;
  #kind = -1;
  #modelView = false;

  constructor(
    private readonly engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    private readonly options: BossViewerOptions,
  ) {
    validateWeapons(game.playerWeapons);
    if (game.bossKinds.length === 0) throw new Error('The game has no boss');
    this.#stage = this.#newStage(this.#kindAt(0));
    this.#speed = shipMaxSpeedPxPerSec(game.playerShips, game.playerShips.ships[0]?.id ?? '');
    this.closeUp = new EnemyCloseUp(engine, options.environment, game.view.enemies.glow);
    this.#stats = options.statsParent
      ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
      : undefined;
    this.panel = new EnemyViewerPanel({
      doc: options.doc,
      parent: options.panelParent,
      title: 'Bosses',
      kinds: game.bossKinds.map((k) => k.name),
      weapons: game.playerWeapons.map((w) => w.name),
      levelCounts: game.playerWeapons.map((w) => w.levels.length),
      initial: { kind: 0, view: 'behaviour', weapon: 0, level: 3, fire: true, paused: false },
      help: HELP,
      onChange: (selection) => {
        this.#apply(selection);
      },
    });
    this.#apply(this.panel.selection);
    this.frame(0);
  }

  #kindAt(index: number): BossKindDefinition {
    const kind = this.game.bossKinds[index] ?? this.game.bossKinds[0];
    if (!kind) throw new Error('The game has no boss');
    return kind;
  }

  #newStage(kind: BossKindDefinition): BossViewerStage {
    const weapon = weaponAt(this.game, 0);
    const level = levelOfBoss(this.game, kind);
    const { environment } = this.options;
    return new BossViewerStage(this.engine, this.game, level, {
      environment,
      random: this.#random,
      weapon,
    });
  }

  #apply(s: EnemyViewerSelection): void {
    const modelView = s.view !== 'behaviour';
    this.closeUp.wireframe = s.view === 'wireframe';
    if (s.kind !== this.#kind || modelView !== this.#modelView) {
      const kind = this.#kindAt(s.kind);
      if (levelOfBoss(this.game, kind) !== this.#stage.level) {
        this.#stage.dispose();
        this.#stage = this.#newStage(kind);
      }
      this.#kind = s.kind;
      this.#modelView = modelView;
      this.#restart(kind);
    }
    this.#stage.shots.select(weaponAt(this.game, s.weapon), s.level);
    this.#stage.shots.firing = s.fire;
    this.#stage.ship.pivot.setEnabled(!modelView);
  }

  /** The picked boss again: it comes in anew, or shows in the model view. */
  #restart(kind: BossKindDefinition): void {
    const stage = this.#stage;
    stage.enemies.clear();
    for (const shot of stage.shots.projectiles) shot.alive = false;
    stage.layer.clear();
    this.#respawnIn = 0;
    const shown = kind.spawn({ ...this.game.screen, random: this.#random, topRange: stage.reach });
    const build = this.game.view.enemies.models[shown.model];
    if (build) this.closeUp.show(build, shown, circlesOf(shown));
    this.#boss = undefined;
    stage.view.track.setSpeedFactor(1, 0);
    if (!this.#modelView) this.#spawn();
  }

  #spawn(): void {
    const kind = this.#kindAt(this.panel.selection.kind);
    this.#boss = this.#stage.spawn(kind, this.#random);
    this.#stage.view.track.setSpeedFactor(
      this.#boss.groundSpeed,
      this.game.bossFights.speedEaseSeconds,
    );
  }

  frame(dt: number): void {
    const { paused } = this.panel.selection;
    const { steps, alpha } = this.#clock.advance(dt);
    const blasts: EnemyBlast[] = [];
    const impacts: ShotImpact[] = [];
    const { track } = this.#stage.view;
    for (let i = 0; i < steps && !paused; i++) {
      const step = this.#clock.stepSeconds;
      this.#previous = track.distance;
      this.#stepTrack(step);
      if (this.#modelView) continue;
      this.#fly(step);
      this.#stage.enemies.step(step);
      blasts.push(...this.#stage.enemies.blasts);
      this.#stage.shots.step(step);
      impacts.push(...this.#stage.shots.impacts);
      this.#respawn(step);
    }
    const distance = this.#previous + (track.distance - this.#previous) * (paused ? 1 : alpha);
    this.#stage.view.update(distance, dt);
    this.#draw(paused ? 0 : dt, blasts, impacts);
  }

  /** The ground scrolls at the boss's speed, and loops back once the level's end is reached. */
  #stepTrack(dt: number): void {
    const { track } = this.#stage.view;
    track.step(dt);
    if (!track.ended) return;
    const factor = track.speedFactor;
    track.restart();
    track.setSpeedFactor(factor, 0);
    this.#previous = 0;
  }

  /** Moves the player ship with the held keys, within what the camera shows. */
  #fly(dt: number): void {
    const { x, y } = this.held.direction;
    const { width, height } = this.game.screen;
    const m = CFG.shipMargin;
    const py = Math.min(height - m.top, Math.max(m.bottom, this.player.y + y * this.#speed * dt));
    const half = this.#stage.halfWidthAt(py);
    const px = this.player.x + x * this.#speed * dt;
    this.player.x = Math.min(width / 2 + half, Math.max(width / 2 - half, px));
    this.player.y = py;
    const { enemies, shots, muzzle } = this.#stage;
    enemies.playerX = shots.muzzleX = shots.centerX = this.player.x;
    enemies.playerY = shots.centerY = this.player.y;
    shots.muzzleY = this.player.y + muzzle;
  }

  /** Once the boss has blown up, the ground eases back, then the boss comes again. */
  #respawn(dt: number): void {
    if (this.#boss && !this.#boss.gone) return;
    if (this.#boss) {
      this.#boss = undefined;
      this.#stage.view.track.setSpeedFactor(1, this.game.bossFights.speedEaseSeconds);
    }
    this.#respawnIn += dt;
    if (this.#respawnIn < CFG.respawnDelay) return;
    this.#respawnIn = 0;
    this.#spawn();
  }

  #draw(dt: number, blasts: readonly EnemyBlast[], impacts: readonly ShotImpact[]): void {
    const { ship, view, layer, drawn, enemies, shots } = this.#stage;
    ship.pivot.position.set(this.player.x, this.player.y, 0);
    ship.update(dt);
    view.playfield.run(() => {
      layer.sync(enemies.enemies, dt);
    });
    drawn.sync({ enemies, shots, blasts, impacts, dt });
    this.closeUp.update(dt);
    const boss = this.state().boss;
    this.panel.showReadout({
      enemies: enemies.enemies.length,
      shots: enemies.shots.count,
      kills: enemies.kills,
      score: enemies.score,
      stage: boss
        ? `${boss.name}: stage ${String(boss.stage)} / ${String(boss.parts)} (${boss.state})`
        : '',
    });
    this.#fps.add(dt, ++this.#frames);
    const scene = this.activeScene;
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons: scene.getActiveIndices() / 3 });
  }

  get activeScene(): Scene {
    return this.#modelView ? this.closeUp.scene : this.#stage.view.scene;
  }

  state(): BossViewerState {
    return bossViewerState(this.#stage, this.#boss, this.player);
  }

  key(key: string, code: string, down: boolean): void {
    const n = this.game.bossKinds.length;
    if (this.#modelView && down && SWITCH_KEYS[code] !== undefined) {
      this.panel.update({ kind: (this.panel.selection.kind + (SWITCH_KEYS[code] ?? 0) + n) % n });
      return;
    }
    if (this.held.key(code, down) || !down) return;
    if (code === 'KeyK') {
      this.#boss?.breakNext();
      return;
    }
    const counts = { kinds: n, weapons: this.game.playerWeapons.length };
    const change = shortcut(key, this.panel.selection, counts);
    if (change) this.panel.update(change);
  }

  dispose(): void {
    this.#stage.dispose();
    this.panel.root.remove();
    this.#stats?.root.remove();
    this.closeUp.dispose();
  }
}

/**
 * Starts the bosses debug page (P07-R09): the boss picked comes in and fights over the scenery
 * of its level, at its fight ground speed, again and again, while a player ship that cannot die
 * flies (arrows / WASD) and shoots it with any weapon and level; K destroys its next part, and
 * the model and wireframe views show its model alone, turning, with its hit circles.
 */
export function startBossViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: BossViewerOptions,
): RunningBossViewer {
  const viewer = new BossViewer(engine, game, options);
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
    panel: viewer.panel,
    closeUp: viewer.closeUp,
    get activeScene() {
      return viewer.activeScene;
    },
    state: () => viewer.state(),
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
