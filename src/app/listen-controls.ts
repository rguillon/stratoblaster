import type { GameControls } from '../input/game-controls';
import type { GamePlay } from './game-play';

export type ListenTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/** Keys go to the level's debug keys first (when on), then to the in-game controls. */
export function listenControls(
  target: ListenTarget | undefined,
  controls: GameControls,
  game: () => GamePlay | undefined,
): () => void {
  if (!target) return () => undefined;
  const onKey = (event: Event): void => {
    const { code, type } = event as KeyboardEvent;
    const down = type === 'keydown';
    if (!game()?.debugKey(code, down)) controls.key(code, down);
  };
  const onBlur = (): void => {
    controls.clear();
  };
  target.addEventListener('keydown', onKey);
  target.addEventListener('keyup', onKey);
  target.addEventListener('blur', onBlur);
  return () => {
    target.removeEventListener('keydown', onKey);
    target.removeEventListener('keyup', onKey);
    target.removeEventListener('blur', onBlur);
  };
}
