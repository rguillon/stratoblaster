import { Boss, type BossPart } from '../../../core/entities/boss';
import type { EnemyContext, EnemySpawnArea } from '../../../core/entities/enemy';
import {
  BossPattern,
  CORE,
  type BossPatternSpec,
  type BossVolley,
  type VolleySource,
} from '../../../core/systems/boss-pattern';
import { approach } from '../../../core/systems/enemy-motion';
import { BOSS_TIMING, type BossDesign } from '../../config/bosses/boss-kit';
import { launchVolley } from './boss-launches';

/** How far its hit circles reach left and right of its centre (orbiting parts all around). */
export function bossHalfWidth(design: BossDesign): number {
  const { parts, coreRadius } = design.stats;
  return parts.reduce(
    (most, p) => Math.max(most, (p.orbits ? Math.hypot(p.x, p.y) : Math.abs(p.x)) + p.radius),
    coreRadius,
  );
}

/** How far its hit circles reach above its centre. */
function bossTop(design: BossDesign): number {
  const { parts, coreRadius } = design.stats;
  return parts.reduce(
    (most, p) => Math.max(most, (p.orbits ? Math.hypot(p.x, p.y) : p.y) + p.radius),
    coreRadius,
  );
}

/**
 * A World 1 boss (P07-R05), from its {@link BossDesign}: it comes down from above the top edge,
 * braking into its place in the upper part of the screen, then sways left and right (never
 * taking its parts out of the ship's reach at the bottom of the screen, D-048) and bobs. Each
 * stage fires its pattern; its parts' launches go on while they stand.
 */
export class WorldBoss extends Boss {
  readonly centerX: number;
  readonly stopY: number;
  /** How far it sways: its design's, or less to keep its parts within reach. */
  readonly swayAmplitude: number;
  #pattern: BossPattern;
  #fighting = 0;
  readonly #launches: readonly BossVolley[];
  readonly #byId: ReadonlyMap<string, BossPart>;
  readonly #ringed = new Set<string>();

  constructor(
    readonly design: BossDesign,
    area: EnemySpawnArea,
  ) {
    const [min, max] = area.topRange ?? [0, area.width];
    super((min + max) / 2, area.height + bossTop(design) + BOSS_TIMING.spawnMargin, design.stats);
    this.centerX = (min + max) / 2;
    this.stopY = design.stopFraction * area.height;
    this.swayAmplitude = Math.max(
      0,
      Math.min(design.sway.amplitude, (max - min) / 2 - bossHalfWidth(design)),
    );
    this.#byId = new Map(this.parts.map((p) => [p.spec.id, p]));
    this.#launches = (design.launches ?? []).map((launch) =>
      launchVolley(launch, Math.sign(this.#byId.get(launch.from)?.spec.x ?? 1)),
    );
    this.#pattern = new BossPattern(this.#stage(0));
  }

  /** The pattern of stage `stage`: its design's volleys and the parts' launches. */
  #stage(stage: number): BossPatternSpec {
    const { stages } = this.design;
    return [...(stages[Math.min(stage, stages.length - 1)] ?? []), ...this.#launches];
  }

  protected override enter(_ctx: EnemyContext, dt: number): boolean {
    const { entrySpeed, brakeDistance } = BOSS_TIMING;
    const left = this.y - this.stopY;
    // Full speed, then braking into its place over the last `brakeDistance`.
    const speed = Math.max(entrySpeed * 0.2, entrySpeed * Math.min(1, left / brakeDistance));
    this.y = approach(this.y, this.stopY, speed * dt);
    this.spin += (this.design.spinRate ?? 0) * dt;
    return this.y === this.stopY;
  }

  protected override move(_ctx: EnemyContext, dt: number): void {
    this.#fighting += dt;
    const { sway, bob } = this.design;
    const t = this.#fighting;
    this.x = this.centerX + this.swayAmplitude * Math.sin((2 * Math.PI * t) / sway.period);
    this.y = this.stopY + bob.amplitude * Math.sin((2 * Math.PI * t) / bob.period);
    this.spin += (this.design.spinRate ?? 0) * dt;
  }

  protected override updatePattern(ctx: EnemyContext, dt: number): void {
    this.#pattern.step(ctx, dt, (from) => this.#source(from));
    this.charge = this.#pattern.charge;
  }

  protected override onStageChange(stage: number, ctx: EnemyContext): void {
    this.#pattern = new BossPattern(this.#stage(stage));
    for (const [id, ring] of Object.entries(this.design.breakRings ?? {})) {
      const part = this.#byId.get(id);
      if (!part?.destroyed || this.#ringed.has(id)) continue;
      // A fuel tank bursts into a ring of bullets (P07-R05).
      this.#ringed.add(id);
      for (let k = 0; k < ring.count; k++) {
        ctx.fireBullet(part.x, part.y, (2 * Math.PI * k) / ring.count, ring.bullet);
      }
    }
  }

  /** The piece a volley fires from: the core, or its part while that part stands. */
  #source(from: string): VolleySource | undefined {
    if (from === CORE) return this.core;
    const part = this.#byId.get(from);
    return part && !part.destroyed ? part : undefined;
  }
}
