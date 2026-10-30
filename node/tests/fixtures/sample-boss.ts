import { Boss, type BossStats } from '../../src/core/entities/boss';
import type { EnemyContext, EnemySpawnArea } from '../../src/core/entities/enemy';
import { approach } from '../../src/core/systems/enemy-motion';
import type { BossKindDefinition } from '../../src/core/systems/boss-fights';
import { BossPattern, type BossPatternSpec } from '../../src/core/systems/boss-pattern';

const BULLET = { speed: 60, radius: 2, style: 'dot' };

/** A sample boss: a core shielded by a gun, and a plate that does not shield it. */
export const SAMPLE_BOSS_STATS: BossStats = {
  model: 'cube',
  name: 'Big Cube',
  radius: 40,
  coreRadius: 10,
  health: 30,
  points: 100,
  groundSpeed: 0.5,
  stagePause: 1,
  death: { seconds: 1, every: 0.25 },
  coreDropChance: 1,
  parts: [
    { id: 'gun', x: -20, y: 0, radius: 8, health: 20, shieldsCore: true, dropChance: 1 },
    { id: 'plate', x: 20, y: 0, radius: 8, health: 10, shieldsCore: false, dropChance: 0 },
  ],
};

/** Stage 0: the gun and the core fire; then the core fires faster; then a ring. */
export const SAMPLE_BOSS_STAGES: readonly BossPatternSpec[] = [
  [
    { from: 'gun', every: 1, shape: { kind: 'aimed', count: 1, spacingDeg: 0, bullet: BULLET } },
    {
      from: 'core',
      every: 2,
      shape: { kind: 'fan', headingDeg: 0, count: 3, spacingDeg: 10, bullet: BULLET },
    },
  ],
  [
    {
      from: 'core',
      every: 1,
      shape: { kind: 'fan', headingDeg: 0, count: 3, spacingDeg: 10, bullet: BULLET },
    },
  ],
  [{ from: 'core', every: 1, shape: { kind: 'ring', count: 4, turnDeg: 10, bullet: BULLET } }],
];

/** Comes down to 3/4 of the height in 1 s, then stays and fires its stage's pattern. */
export class SampleBoss extends Boss {
  readonly stopY: number;
  #pattern = new BossPattern(SAMPLE_BOSS_STAGES[0] ?? []);

  constructor(area: EnemySpawnArea, stats: BossStats = SAMPLE_BOSS_STATS) {
    super(area.width / 2, area.height + 40, stats);
    this.stopY = area.height * 0.75;
  }

  protected override enter(_ctx: EnemyContext, dt: number): boolean {
    this.y = approach(this.y, this.stopY, 140 * dt);
    return this.y === this.stopY;
  }

  protected override move(): void {
    // It stays where it stopped.
  }

  protected override updatePattern(ctx: EnemyContext, dt: number): void {
    this.#pattern.step(ctx, dt, (from) => {
      if (from === 'core') return this.core;
      return this.parts.find((p) => p.spec.id === from && !p.destroyed);
    });
  }

  protected override onStageChange(stage: number): void {
    this.#pattern = new BossPattern(SAMPLE_BOSS_STAGES[stage] ?? []);
  }
}

export const SAMPLE_BOSS_KINDS: readonly BossKindDefinition[] = [
  { id: 'big-cube', name: 'Big Cube', spawn: (area) => new SampleBoss(area) },
];
