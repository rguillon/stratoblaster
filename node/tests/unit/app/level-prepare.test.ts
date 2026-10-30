import { afterEach, describe, expect, it } from 'vitest';
import { LevelPrefetcher, prepareLevel } from '../../../src/app/level-prepare';
import { BackgroundLoader, type WorkerPort } from '../../../src/render/scenery/background-loader';
import { generateGroundsWith } from '../../../src/render/scenery/level-ground';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

function port(): WorkerPort & { jobs: unknown[] } {
  const jobs: unknown[] = [];
  return {
    jobs,
    onmessage: null,
    onerror: null,
    postMessage: (job) => jobs.push(job),
  };
}

afterEach(() => {
  generateGroundsWith(undefined);
});

describe('LevelPrefetcher', () => {
  it('P13-R03: prefetches the highlighted level once the highlight rests on it', () => {
    const worker = port();
    // Level a gets a scenery of its own, so its ground is not the one asked for c.
    const game = {
      ...SAMPLE_GAME,
      gameLevels: SAMPLE_GAME.gameLevels.map((l) =>
        l.id === 'a' ? { ...l, scenery: { ...l.scenery, seed: l.scenery.seed + 1 } } : l,
      ),
    };
    const prefetcher = new LevelPrefetcher(game, new BackgroundLoader(worker));
    prefetcher.update(0.1, 'a');
    // Passed over: nothing asked yet.
    prefetcher.update(0.1, 'c');
    expect(worker.jobs).toHaveLength(0);
    prefetcher.update(0.3, 'c');
    const asked = worker.jobs.length;
    expect(asked).toBeGreaterThan(0);
    // Once per level; none for a cell that is not a level, nor without a level select.
    prefetcher.update(1, 'c');
    prefetcher.update(1, 'back');
    prefetcher.update(1, null);
    expect(worker.jobs).toHaveLength(asked);
    // A level started without its highlight resting first is prefetched at once.
    prefetcher.start('a');
    expect(worker.jobs.length).toBeGreaterThan(asked);
  });

  it('P13-R03: without a worker, a level ground is ready at once', () => {
    expect(prepareLevel(SAMPLE_GAME, 'a')).toBe(true);
    const prefetcher = new LevelPrefetcher(SAMPLE_GAME, undefined);
    prefetcher.update(1, 'a');
  });
});
