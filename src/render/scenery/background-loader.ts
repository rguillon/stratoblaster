import type { SceneryLevel } from '../../core/scenery/scenery-level';
import type { GroundWorkerJob } from './ground-worker';
import { generateGroundsWith, type GroundSnapshot } from './level-ground';
import { hasTexture, keepTexture, type TextureJob } from './procedural-textures';

/** What the worker sends back for a job. */
interface Reply {
  readonly id: number;
  readonly ground?: GroundSnapshot;
  readonly pixels?: Uint8Array;
}

/** The worker's side the loader talks to (a `Worker`, or a fake in tests). */
export interface WorkerPort {
  postMessage(job: GroundWorkerJob): void;
  onmessage: ((event: MessageEvent<Reply>) => void) | null;
  onerror: ((event: ErrorEvent) => void) | null;
  terminate?(): void;
}

/**
 * Generates levels' grounds and scenery textures in a worker (P13-R03), so a level can be
 * prepared while the player is still choosing it, without freezing the menus. Unless stopped,
 * every ground the game asks for is generated there ({@link generateGroundsWith}).
 */
export class BackgroundLoader {
  #next = 0;
  readonly #waiting = new Map<number, (reply: Reply | undefined) => void>();
  /** Textures asked for and not back yet, by key. */
  readonly #textures = new Set<string>();

  constructor(private readonly port: WorkerPort) {
    port.onmessage = ({ data }) => {
      this.#waiting.get(data.id)?.(data);
      this.#waiting.delete(data.id);
    };
    // A broken worker: every job waiting fails (the ground is then generated on the main thread).
    port.onerror = () => {
      for (const done of this.#waiting.values()) done(undefined);
      this.#waiting.clear();
    };
    generateGroundsWith((level, seed, done) => {
      this.#post({ kind: 'ground', level, seed }, (reply) => {
        done(reply?.ground);
      });
    });
  }

  /** Generates the textures of `jobs` not kept yet, keeping them when they come back. */
  prefetchTextures(jobs: readonly TextureJob[]): void {
    for (const job of jobs) {
      const key = JSON.stringify(job);
      if (hasTexture(job) || this.#textures.has(key)) continue;
      this.#textures.add(key);
      this.#post({ kind: 'texture', job }, (reply) => {
        this.#textures.delete(key);
        if (reply?.pixels) keepTexture(job, reply.pixels);
      });
    }
  }

  /** Stops generating in the background: the grounds are generated on the main thread again. */
  stop(): void {
    generateGroundsWith(undefined);
    this.port.terminate?.();
  }

  #post(
    job:
      | { readonly kind: 'ground'; readonly level: SceneryLevel; readonly seed: number }
      | { readonly kind: 'texture'; readonly job: TextureJob },
    done: (reply: Reply | undefined) => void,
  ): void {
    const id = this.#next++;
    this.#waiting.set(id, done);
    this.port.postMessage({ ...job, id });
  }
}

/** A loader on the game's worker, if the browser has workers (none in unit tests). */
export function startBackgroundLoader(): BackgroundLoader | undefined {
  if (typeof Worker === 'undefined') return undefined;
  const worker = new Worker(new URL('./ground-worker.ts', import.meta.url), { type: 'module' });
  return new BackgroundLoader(worker);
}
