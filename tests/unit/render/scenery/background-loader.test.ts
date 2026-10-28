import { afterEach, describe, expect, it } from 'vitest';
import { runoutStart, withRunout } from '../../../../src/core/scenery/scenery-level';
import { GAME } from '../../../../src/game/index';
import type { GroundWorkerJob } from '../../../../src/render/scenery/ground-worker';
import {
  BackgroundLoader,
  type WorkerPort,
} from '../../../../src/render/scenery/background-loader';
import {
  generateGroundsWith,
  generateInTwo,
  levelGround,
  requestLevelGround,
} from '../../../../src/render/scenery/level-ground';
import {
  hasTexture,
  sceneryTextureJobs,
  texturePixels,
} from '../../../../src/render/scenery/procedural-textures';
import { SAMPLE_SCENERY_LEVEL, SAMPLE_SCENERY_LOOK } from '../../../fixtures/sample-scenery';

/**
 * A worker run by hand: jobs wait in `jobs` until `run` answers them as the real one would (a
 * ground job twice: its ground, then its runout). `run(false)` keeps the runouts for later.
 */
function fakeWorker(): WorkerPort & {
  jobs: GroundWorkerJob[];
  terminated: boolean;
  run(runouts?: boolean): void;
  fail(): void;
} {
  const later: (() => void)[] = [];
  const send = (data: object) => {
    port.onmessage?.({ data: structuredClone(data) } as MessageEvent<never>);
  };
  const port = {
    jobs: [] as GroundWorkerJob[],
    onmessage: null as WorkerPort['onmessage'],
    onerror: null as WorkerPort['onerror'],
    terminated: false,
    postMessage(job: GroundWorkerJob) {
      port.jobs.push(structuredClone(job));
    },
    run(runouts = true) {
      for (const job of port.jobs.splice(0)) {
        if (job.kind === 'texture') {
          send({ id: job.id, pixels: texturePixels(job.job) });
          continue;
        }
        const made = generateInTwo(job.level, job.seed);
        send({ id: job.id, ground: made.ground });
        later.push(() => {
          send({ id: job.id, runout: made.runout() });
        });
      }
      if (runouts) for (const answer of later.splice(0)) answer();
    },
    fail() {
      port.jobs.splice(0);
      later.splice(0);
      port.onerror?.({} as ErrorEvent);
    },
    terminate() {
      port.terminated = true;
    },
  };
  return port;
}

afterEach(() => {
  generateGroundsWith(undefined);
});

describe('BackgroundLoader', () => {
  it('P13-R03: a level ground comes from the worker, ready once it is back', () => {
    const worker = fakeWorker();
    const loader = new BackgroundLoader(worker);
    const level = { ...SAMPLE_SCENERY_LEVEL };
    expect(requestLevelGround(level)).toBe(false);
    // Asked again while on its way: not posted twice.
    expect(requestLevelGround(level)).toBe(false);
    expect(worker.jobs).toHaveLength(1);
    worker.run();
    expect(requestLevelGround(level)).toBe(true);
    loader.stop();
    expect(worker.terminated).toBe(true);
  });

  it('P13-R05: the ground made from what the worker sent is the one made on the main thread', () => {
    const scenery = GAME.gameLevels.find((l) => l.id === '3-3')?.scenery;
    if (!scenery) throw new Error('no level 3-3');
    const worker = fakeWorker();
    new BackgroundLoader(worker);
    const level = { ...scenery };
    requestLevelGround(level);
    worker.run();
    const fromWorker = levelGround(level, level.seed);
    generateGroundsWith(undefined);
    const here = levelGround({ ...scenery }, scenery.seed);
    expect(fromWorker.placer.roads.roads).toEqual(here.placer.roads.roads);
    for (const zMin of [0, 900, 4000, 9000]) {
      const area = { xMin: -400, xMax: 400, zMin, zMax: zMin + 300 };
      expect(fromWorker.placer.place(area)).toEqual(here.placer.place(area));
      expect(fromWorker.placer.roads.edgeDistance(10, zMin + 50)).toBe(
        here.placer.roads.edgeDistance(10, zMin + 50),
      );
    }
  });

  it('reviewer, 2026-10-28: a level is ready with its ground; its runout comes after, as made here', () => {
    const scenery = GAME.gameLevels.find((l) => l.id === '4-4')?.scenery;
    if (!scenery) throw new Error('no level 4-4');
    const level = withRunout(scenery, 60);
    const from = runoutStart(level) ?? 0;
    const worker = fakeWorker();
    new BackgroundLoader(worker);
    requestLevelGround(level);
    worker.run(false);
    expect(requestLevelGround(level)).toBe(true);
    const ground = levelGround(level, level.seed);
    const before = ground.placer.roads.roads;
    const past = (roads: readonly { points: readonly { z: number }[] }[]) =>
      roads.some((r) => r.points.some((p) => p.z > from + 1));
    expect(past(before)).toBe(false);
    worker.run();
    expect(ground.placer.roads.roads.length).toBeGreaterThan(before.length);
    expect(past(ground.placer.roads.roads)).toBe(true);
    generateGroundsWith(undefined);
    const here = levelGround(withRunout(scenery, 60), level.seed);
    expect(ground.placer.roads.roads).toEqual(here.placer.roads.roads);
    for (const zMin of [0, from - 300, from, from + 2000]) {
      const area = { xMin: -400, xMax: 400, zMin, zMax: zMin + 300 };
      expect(ground.placer.place(area)).toEqual(here.placer.place(area));
    }
  });

  it('reviewer, 2026-10-28: a worker broken after the ground leaves its runout to the main thread', () => {
    const level = withRunout(SAMPLE_SCENERY_LEVEL, 30);
    const worker = fakeWorker();
    new BackgroundLoader(worker);
    requestLevelGround(level);
    worker.run(false);
    const ground = levelGround(level, level.seed);
    const before = ground.placer.place({ xMin: -400, xMax: 400, zMin: 0, zMax: 1e6 }).length;
    worker.fail();
    const after = ground.placer.place({ xMin: -400, xMax: 400, zMin: 0, zMax: 1e6 }).length;
    expect(after).toBeGreaterThan(before);
    generateGroundsWith(undefined);
    const here = levelGround(withRunout(SAMPLE_SCENERY_LEVEL, 30), level.seed);
    expect(ground.placer.roads.roads).toEqual(here.placer.roads.roads);
  });

  it('P13-R03: a broken worker leaves the grounds to the main thread', () => {
    const worker = fakeWorker();
    new BackgroundLoader(worker);
    const level = { ...SAMPLE_SCENERY_LEVEL };
    expect(requestLevelGround(level)).toBe(false);
    worker.fail();
    expect(requestLevelGround(level)).toBe(true);
  });

  it('P13-R03: prefetched textures are kept for the scenery kit', () => {
    const worker = fakeWorker();
    const loader = new BackgroundLoader(worker);
    const jobs = sceneryTextureJobs(SAMPLE_SCENERY_LOOK, 991);
    loader.prefetchTextures(jobs);
    loader.prefetchTextures(jobs);
    expect(worker.jobs).toHaveLength(jobs.length);
    worker.run();
    expect(jobs.every(hasTexture)).toBe(true);
  });
});
