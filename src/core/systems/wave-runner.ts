import type { EnemyEntry } from '../entities/enemy';

/**
 * One wave of a level's script (GD-40, P06-R07): when the level has scrolled `at` world units,
 * `count` groups of the enemy kind `kind` come in at `entry`, one every `interval` seconds.
 */
export interface Wave {
  /** Distance scrolled (world units, from the start of the level) that triggers the wave. */
  readonly at: number;
  /** Id of an `EnemyKindDefinition`; each group is one call of its `spawn`. */
  readonly kind: string;
  readonly count: number;
  /** Seconds between two groups of the wave. */
  readonly interval: number;
  readonly entry: EnemyEntry;
  /**
   * Added to the entry position for each group after the first (e.g. a line of Scouts coming in
   * across the screen), wrapped back into 0..1.
   */
  readonly spread?: number;
}

/** A level's waves. The runner sorts them by distance. */
export type WaveScript = readonly Wave[];

/** Calls the runner makes to bring a group in. */
export type WaveSpawner = (kind: string, entry: EnemyEntry) => void;

interface QueuedGroup {
  readonly time: number;
  readonly kind: string;
  readonly entry: EnemyEntry;
}

/** Throws a descriptive error for a wave with an unknown kind or impossible numbers. */
export function validateWaveScript(script: WaveScript, kindIds: readonly string[]): void {
  for (const wave of script) {
    const where = `Wave "${wave.kind}" at ${String(wave.at)}`;
    if (!kindIds.includes(wave.kind)) throw new Error(`${where}: unknown enemy kind`);
    if (!Number.isInteger(wave.count) || wave.count < 1) throw new Error(`${where}: bad count`);
    if (!(wave.at >= 0) || !(wave.interval >= 0)) throw new Error(`${where}: bad timing`);
    const { position } = wave.entry;
    if (!(position >= 0 && position <= 1)) throw new Error(`${where}: bad entry position`);
  }
}

/** The entry of group `index` of `wave`. */
function groupEntry(wave: Wave, index: number): EnemyEntry {
  const shifted = wave.entry.position + (wave.spread ?? 0) * index;
  return { side: wave.entry.side, position: shifted - Math.floor(shifted) };
}

/**
 * Runs a wave script (P06-R07): waves start when the level scrolls past their distance, and not
 * before; the groups of a wave come in one by one, so several waves can be on screen at once.
 * The runner knows enemy kinds only by id: the spawner brings the groups in. Pure and
 * deterministic.
 */
export class WaveRunner {
  readonly #waves: Wave[];
  readonly #queue: QueuedGroup[] = [];
  #next = 0;
  #time = 0;
  #stopped = false;

  constructor(
    script: WaveScript,
    private readonly spawn: WaveSpawner,
  ) {
    this.#waves = [...script].sort((a, b) => a.at - b.at);
  }

  /** Waves triggered so far. */
  get triggered(): number {
    return this.#next;
  }

  /** Whether no group will come in any more: stopped, or every wave triggered and spawned. */
  get finished(): boolean {
    return this.#stopped || (this.#next >= this.#waves.length && this.#queue.length === 0);
  }

  /**
   * Advances by `dt` seconds, the level having scrolled `distance`: triggers the waves passed
   * and brings in the groups due.
   */
  step(dt: number, distance: number): void {
    if (this.#stopped) return;
    this.#time += dt;
    for (let wave = this.#waves[this.#next]; wave && wave.at <= distance;) {
      for (let i = 0; i < wave.count; i++) {
        const time = this.#time + i * wave.interval;
        this.#queue.push({ time, kind: wave.kind, entry: groupEntry(wave, i) });
      }
      wave = this.#waves[++this.#next];
    }
    this.#queue.sort((a, b) => a.time - b.time);
    while (this.#queue[0] && this.#queue[0].time <= this.#time) {
      const group = this.#queue.shift();
      if (group) this.spawn(group.kind, group.entry);
    }
  }

  /** No group comes in after this, not even the rest of a started wave (P06-R03). */
  stop(): void {
    this.#stopped = true;
    this.#queue.length = 0;
  }

  /**
   * Starts again at `distance`, as if the level began there: the waves before it are skipped,
   * the groups waiting are dropped, and the later waves trigger as usual (P06-R09).
   */
  skipTo(distance: number): void {
    this.#queue.length = 0;
    this.#stopped = false;
    const next = this.#waves.findIndex((wave) => wave.at >= distance);
    this.#next = next < 0 ? this.#waves.length : next;
  }
}
