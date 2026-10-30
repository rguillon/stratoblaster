import { describe, expect, it } from 'vitest';
import { runLoadingTasks } from '../../../src/assets/loading-tasks';

describe('runLoadingTasks', () => {
  it('P01-R02: reports real progress from 0 to 1, yielding before each task', async () => {
    const log: string[] = [];
    await runLoadingTasks(
      [() => void log.push('a'), () => Promise.resolve().then(() => void log.push('b'))],
      (p) => log.push(String(p)),
      () => {
        log.push('yield');
        return Promise.resolve();
      },
    );
    expect(log).toEqual(['0', 'yield', 'a', '0.5', 'yield', 'b', '1']);
  });

  it('reports 0 then 1 when there is nothing to load', async () => {
    const progress: number[] = [];
    await runLoadingTasks(
      [],
      (p) => progress.push(p),
      () => Promise.resolve(),
    );
    expect(progress).toEqual([0, 1]);
  });
});
