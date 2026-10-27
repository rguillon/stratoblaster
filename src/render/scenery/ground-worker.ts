// P13-R03: generates levels' grounds and scenery textures off the main thread.
import type { SceneryLevel } from '../../core/scenery/scenery-level';
import { groundSnapshot } from './level-ground';
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
    scope.postMessage({ id: data.id, ground: groundSnapshot(data.level, data.seed) });
    return;
  }
  const pixels = texturePixels(data.job);
  scope.postMessage({ id: data.id, pixels }, [pixels.buffer]);
};
