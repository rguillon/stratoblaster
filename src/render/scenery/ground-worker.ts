// P13-R03: generates levels' grounds and scenery textures off the main thread.
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { generateInTwo } from './level-ground';
import { texturePixels, type TextureJob } from './procedural-textures';

/** A job for the worker. */
export type GroundWorkerJob =
  | {
      readonly id: number;
      readonly kind: 'ground';
      readonly level: SceneryLevel;
      readonly seed: number;
    }
  | { readonly id: number; readonly kind: 'texture'; readonly job: TextureJob };

const scope = self as unknown as {
  onmessage: ((event: MessageEvent<GroundWorkerJob>) => void) | null;
  postMessage(message: unknown, transfer?: Transferable[]): void;
};

scope.onmessage = ({ data }) => {
  if (data.kind === 'ground') {
    const made = generateInTwo(data.level, data.seed);
    scope.postMessage({ id: data.id, ground: made.ground });
    // Reviewer, 2026-10-28: the runout after the jobs already waiting (the level's textures), as
    // the level can start without it.
    setTimeout(() => {
      scope.postMessage({ id: data.id, runout: made.runout() });
    }, 0);
    return;
  }
  const pixels = texturePixels(data.job);
  scope.postMessage({ id: data.id, pixels }, [pixels.buffer]);
};
