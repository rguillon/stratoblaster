import type { Scene } from '@babylonjs/core/scene';
import { CreateBox } from '@babylonjs/core/Meshes/Builders/boxBuilder';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Enemy, type EnemyContext, type EnemyKindDefinition } from '../../src/core/entities/enemy';
import type {
  BlastRenderer,
  EnemyBindings,
  EnemyModel,
  EnemyShotFrame,
  EnemyShotRenderer,
} from '../../src/render/game-view';
import type { EnemyBlast } from '../../src/core/systems/enemy-world';

const BULLET = { speed: 50, radius: 2, style: 'dot' };

/** A sample enemy: drops straight down and fires a bullet straight down every second. */
export class Dropper extends Enemy {
  #cooldown = 1;

  constructor(x: number, y: number) {
    super(x, y, { model: 'cube', radius: 10, health: 5, points: 7 });
  }

  override update(ctx: EnemyContext, dt: number): void {
    this.y -= 100 * dt;
    this.#cooldown -= dt;
    if (this.#cooldown <= 0) {
      this.#cooldown += 1;
      ctx.fireBullet(this.x, this.y, Math.PI, BULLET);
    }
  }
}

/** A sample enemy that splits into two Droppers when destroyed. */
export class Twin extends Dropper {
  override onDestroyed(ctx: EnemyContext): void {
    ctx.spawn(new Dropper(this.x - 10, this.y));
    ctx.spawn(new Dropper(this.x + 10, this.y));
  }
}

export const SAMPLE_ENEMY_KINDS: readonly EnemyKindDefinition[] = [
  {
    id: 'dropper',
    name: 'Dropper',
    spawn: (area) => [new Dropper(area.width / 2, area.height + 20)],
  },
  {
    id: 'pair',
    name: 'Pair',
    spawn: (area) => [
      new Twin(area.width / 3, area.height + 20),
      new Dropper(area.width / 2, area.height + 20),
    ],
  },
];

/** What the sample renderers were given, most recent last. */
export const SAMPLE_ENEMY_FRAMES: EnemyShotFrame[] = [];
export const SAMPLE_BLASTS: EnemyBlast[] = [];

function cubeModel(scene: Scene): EnemyModel {
  const root = new TransformNode('sample-enemy', scene);
  CreateBox('sample-enemy-box', { size: 10 }, scene).parent = root;
  return { root, sync: () => undefined };
}

function shotRenderer(): EnemyShotRenderer {
  return {
    sync: (frame) => {
      SAMPLE_ENEMY_FRAMES.push(frame);
    },
    dispose: () => undefined,
  };
}

function blastRenderer(): BlastRenderer {
  return {
    sync: (blasts) => {
      SAMPLE_BLASTS.push(...blasts);
    },
    dispose: () => undefined,
  };
}

export const SAMPLE_ENEMIES: EnemyBindings = {
  models: { cube: cubeModel },
  shots: shotRenderer,
  blasts: blastRenderer,
  glow: { intensity: 0.5, blurKernelSize: 8 },
};
