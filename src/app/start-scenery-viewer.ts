import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import { CreateLines } from '@babylonjs/core/Meshes/Builders/linesBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { GameDefinition } from '../core/content/game-definition';
import { FixedStepClock } from '../core/loop/fixed-step-clock';
import { levelLength, type SceneryLevel } from '../core/scenery/scenery-level';
import { ScrollTrack } from '../core/scenery/scroll-track';
import type { GameView } from '../render/game-view';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { stepModelAnimations } from '../render/model-animation';
import { createPlainSceneryKit } from '../render/scenery/scenery-kit';
import { createSceneryKit } from '../render/scenery/scenery-kit.visual';
import type { SceneryLook } from '../render/scenery/scenery-look';
import {
  ABOVE_CLOUDS_GROUP,
  BELOW_CLOUDS_GROUP,
  SceneryStage,
} from '../render/scenery/scenery-stage';
import { SceneryViewerPanel, type SceneryViewerSettings } from '../ui/scenery-viewer-panel';
import { StatsTile } from '../ui/stats-tile';
import { SCENERY_VIEWER_CONFIG as CFG } from '../config/scenery-viewer';
import { RateMeter } from './rate-meter';

/** Options of {@link startSceneryViewer}. */
export interface SceneryViewerOptions {
  /** Generated textures, sky lighting, shadows and glow. Needs a real WebGL engine. */
  readonly environment: boolean;
  readonly doc: Pick<Document, 'createElement'>;
  /** Where the controls go. */
  readonly panelParent: HTMLElement;
  /** Where the FPS / polygons tile goes. No tile when omitted. */
  readonly statsParent?: HTMLElement;
  /** Where keyboard shortcuts are listened to. No shortcuts when omitted. */
  readonly keyboardTarget?: Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;
  /** Seconds elapsed since the previous frame. Defaults to the engine's frame time. */
  readonly frameSeconds?: () => number;
  /** Starts the engine's render loop (off in unit tests, which call `frame()`). */
  readonly renderLoop: boolean;
  /** Phase 15 (P15-R10, `?tiles=1`): the grid of tiles drawn over the districts. */
  readonly tileGrid?: boolean;
}

/** Handle on a running viewer. */
export interface RunningSceneryViewer {
  readonly scene: Scene;
  readonly stage: SceneryStage;
  readonly track: ScrollTrack;
  readonly panel: SceneryViewerPanel;
  /** Advances and draws one frame of `dt` seconds. */
  frame(dt: number): void;
  /** Applies a keyboard shortcut, if `key` is one. */
  key(key: string): void;
  dispose(): void;
}

function firstLevel(game: GameDefinition<GameView>): { level: SceneryLevel; look: SceneryLook } {
  const level = game.sceneryLevels[0];
  if (!level) throw new Error('The game has no scenery level');
  const look = game.view.scenery.looks[level.id];
  if (!look) throw new Error(`No look for scenery level "${level.id}"`);
  return { level, look };
}

const percent = (v: number): number => Math.round(v * 100);

/** The pieces of a running viewer; see {@link startSceneryViewer}. */
class SceneryViewer {
  readonly scene: Scene;
  readonly stage: SceneryStage;
  readonly track: ScrollTrack;
  readonly panel: SceneryViewerPanel;
  readonly #clock = new FixedStepClock(CFG.stepHz, CFG.maxStepsPerFrame);
  readonly #ship: TransformNode;
  readonly #frame: TransformNode;
  readonly #stats: StatsTile | undefined;
  readonly #fps = new RateMeter(CFG.stats.fpsWindow);
  #frames = 0;
  #previous = 0;

  constructor(
    engine: AbstractEngine,
    private readonly game: GameDefinition<GameView>,
    options: SceneryViewerOptions,
  ) {
    const { level, look } = firstLevel(game);
    this.scene = new Scene(engine);
    const glow = options.environment
      ? applyShowcaseEnvironment(this.scene, {
          cubeSize: CFG.environmentCubeSize,
          intensity: look.sky.environmentIntensity,
          stops: look.sky.stops,
          glow: look.glow,
        })
      : undefined;
    this.stage = new SceneryStage(this.scene, {
      screen: game.screen,
      camera: game.view.scenery.camera,
      level,
      look,
      propModels: game.view.scenery.propModels,
      kit: options.environment ? createSceneryKit : createPlainSceneryKit,
      config: CFG.stage,
      ...(options.tileGrid ? { atmosphere: { tileGrid: true } } : {}),
    });
    for (const mesh of this.stage.glowingMeshes) glow?.addIncludedOnlyMesh(mesh);
    // The glow is composed before the clouds are drawn, so it does not shine through them.
    if (glow) glow.renderingGroupId = BELOW_CLOUDS_GROUP;
    this.track = new ScrollTrack(level.scrollSpeed, levelLength(level));
    this.#ship = this.#buildShip();
    this.#frame = this.#buildFrame();
    this.#stats = options.statsParent
      ? new StatsTile(options.doc, options.statsParent, CFG.stats.refresh)
      : undefined;
    this.panel = this.#buildPanel(options, level.name);
    this.#apply(this.panel.settings);
    this.frame(0);
  }

  #buildPanel(options: SceneryViewerOptions, levelName: string): SceneryViewerPanel {
    return new SceneryViewerPanel({
      doc: options.doc,
      parent: options.panelParent,
      levelName,
      duration: this.track.duration,
      hasSea: this.stage.hasSea,
      initial: {
        paused: false,
        fastForward: false,
        sea: this.stage.hasSea,
        frame: false,
        clouds: this.stage.clouds.map((c) => ({
          enabled: c.enabled,
          coverage: percent(c.coverage),
          opacity: percent(c.opacity),
        })),
      },
      onChange: (settings) => {
        this.#apply(settings);
      },
      onSeek: (time) => {
        this.#seek(time);
      },
      onRestart: () => {
        this.#seek(0);
      },
      onNewSeed: () => {
        this.stage.setSeed(this.stage.seed + 1);
      },
    });
  }

  frame(dt: number): void {
    const { steps, alpha } = this.#clock.advance(dt);
    for (let i = 0; i < steps; i++) {
      this.#previous = this.track.distance;
      this.track.step(this.#clock.stepSeconds);
    }
    const distance = this.#previous + (this.track.distance - this.#previous) * alpha;
    this.stage.update(distance, dt);
    const { width, height } = this.game.screen;
    this.#ship.position = this.stage.playfieldPoint(width / 2, CFG.shipY, distance);
    stepModelAnimations(this.#ship, dt);
    this.#frame.position = this.stage.playfieldPoint(0, 0, distance);
    this.panel.showReadout({
      time: this.track.time,
      section: this.stage.field.sectionAt(distance + height / 2).section.name,
      props: this.stage.stats.props,
      seed: this.stage.seed,
      ended: this.track.ended,
    });
    this.#fps.add(dt, ++this.#frames);
    this.#stats?.update(dt, { fps: this.#fps.rate, polygons: this.scene.getActiveIndices() / 3 });
  }

  key(key: string): void {
    const k = key.toLowerCase();
    const s = this.panel.settings;
    const cloud = /^[1-9]$/.test(k) ? Number(k) - 1 : -1;
    if (cloud >= 0 && cloud < s.clouds.length) {
      this.panel.updateCloud(cloud, { enabled: !s.clouds[cloud]?.enabled });
      return;
    }
    const actions: Readonly<Record<string, () => void>> = {
      p: () => {
        this.panel.update({ paused: !s.paused });
      },
      f: () => {
        this.panel.update({ fastForward: !s.fastForward });
      },
      s: () => {
        this.panel.update({ sea: !s.sea });
      },
      o: () => {
        this.panel.update({ frame: !s.frame });
      },
      r: () => {
        this.#seek(0);
      },
      n: () => {
        this.stage.setSeed(this.stage.seed + 1);
      },
      arrowleft: () => {
        this.#seek(this.track.time - CFG.seekStep);
      },
      arrowright: () => {
        this.#seek(this.track.time + CFG.seekStep);
      },
    };
    actions[k]?.();
  }

  #seek(time: number): void {
    this.track.seek(time);
    this.#previous = this.track.distance;
  }

  #apply(settings: SceneryViewerSettings): void {
    this.track.timeScale = settings.paused ? 0 : settings.fastForward ? CFG.fastForward : 1;
    this.stage.setSeaEnabled(settings.sea);
    this.#frame.setEnabled(settings.frame);
    settings.clouds.forEach((cloud, i) => {
      const layer = this.stage.clouds[i];
      if (!layer) return;
      layer.enabled = cloud.enabled;
      layer.coverage = cloud.coverage / 100;
      layer.opacity = cloud.opacity / 100;
    });
  }

  /** The game's first ship, flying at the bottom of the playfield to show the scale. */
  #buildShip(): TransformNode {
    const ship = new TransformNode('scenery-ship', this.scene);
    const first = this.game.playerShips.ships[0];
    const model = first && this.game.view.playerShipModels[first.id];
    if (model) {
      // Models face +Z with +Y up, like the level: no turn needed.
      const holder = model(this.scene);
      holder.parent = ship;
      ship.scaling.setAll(this.game.view.playerShipScale);
    }
    // Drawn after the ground's glow and the clouds, which it flies above.
    for (const mesh of ship.getChildMeshes()) mesh.renderingGroupId = ABOVE_CLOUDS_GROUP;
    return ship;
  }

  /** Outline of the playfield on the flight plane (P04-R05 check). */
  #buildFrame(): TransformNode {
    const { width, height } = this.game.screen;
    const corners = [
      new Vector3(0, 0, 0),
      new Vector3(width, 0, 0),
      new Vector3(width, 0, height),
      new Vector3(0, 0, height),
      new Vector3(0, 0, 0),
    ];
    const frame = new TransformNode('playfield-frame', this.scene);
    const lines = CreateLines('playfield-frame-lines', { points: corners }, this.scene);
    lines.color = new Color3(...CFG.frameColor);
    lines.parent = frame;
    lines.isPickable = false;
    return frame;
  }

  dispose(): void {
    this.panel.root.remove();
    this.#stats?.root.remove();
    this.scene.dispose();
  }
}

/**
 * Starts the generated level viewer (`level_zero/`, P04): the game's first scenery level
 * scrolls under the tilted playfield camera for its whole duration, with a ship to show the
 * scale, and controls to pause, fast-forward, seek, change the seed, and switch the sea and
 * the cloud layers.
 */
export function startSceneryViewer(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  options: SceneryViewerOptions,
): RunningSceneryViewer {
  const viewer = new SceneryViewer(engine, game, options);
  const onKey = (event: Event): void => {
    viewer.key((event as KeyboardEvent).key);
  };
  options.keyboardTarget?.addEventListener('keydown', onKey);
  const frameSeconds = options.frameSeconds ?? (() => engine.getDeltaTime() / 1000);
  if (options.renderLoop) {
    engine.runRenderLoop(() => {
      viewer.frame(Math.min(frameSeconds(), CFG.maxFrameSeconds));
      viewer.scene.render();
    });
  }
  return {
    scene: viewer.scene,
    stage: viewer.stage,
    track: viewer.track,
    panel: viewer.panel,
    frame: (dt) => {
      viewer.frame(dt);
    },
    key: (key) => {
      viewer.key(key);
    },
    dispose: () => {
      engine.stopRenderLoop();
      options.keyboardTarget?.removeEventListener('keydown', onKey);
      viewer.dispose();
    },
  };
}
