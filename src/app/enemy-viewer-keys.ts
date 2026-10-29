import type { EnemyViewerSelection } from '../ui/enemy-viewer-panel';

// The keys of the enemies page (P05-R11).

/** Shortcuts: N / B next / previous enemy, M model, V wireframe, X weapon, 1-9 level, F, P, L, H. */
export function shortcut(
  key: string,
  s: EnemyViewerSelection,
  counts: { kinds: number; weapons: number },
) {
  const k = key.toLowerCase();
  const wrap = (i: number, n: number): number => (i + n) % Math.max(1, n);
  if (/^[1-9]$/.test(k)) return { level: Number(k) };
  const changes: Readonly<Record<string, Partial<EnemyViewerSelection>>> = {
    n: { kind: wrap(s.kind + 1, counts.kinds) },
    b: { kind: wrap(s.kind - 1, counts.kinds) },
    m: { view: s.view === 'model' ? 'behaviour' : 'model' },
    v: { view: s.view === 'wireframe' ? 'behaviour' : 'wireframe' },
    x: { weapon: wrap(s.weapon + 1, counts.weapons), level: 1 },
    f: { fire: !s.fire },
    p: { paused: !s.paused },
    l: { living: !s.living },
    h: { hitbox: !s.hitbox },
  };
  return changes[k];
}

/** In the model and wireframe views, ← / → (by key position) show the previous / next enemy. */
export const SWITCH_KEYS: Readonly<Record<string, number>> = { ArrowLeft: -1, ArrowRight: 1 };

export const HELP =
  'Move: arrows / WASD · N / B: next / previous enemy · M: model · V: wireframe (← / →: switch enemy) · X: weapon · 1-5: level · F: fire · P: pause · L: motion · H: hitbox';

/** What listens to a viewer page's keys. */
type KeyTarget = Pick<EventTarget, 'addEventListener' | 'removeEventListener'>;

/**
 * Sends `target`'s key presses to `viewer` (and lets go of held keys when it loses focus).
 * Returns what stops listening.
 */
export function listenToKeys(
  target: KeyTarget | undefined,
  viewer: {
    key(key: string, code: string, down: boolean): void;
    readonly held: { clear(): void };
  },
): () => void {
  const onKey = (event: Event): void => {
    const e = event as KeyboardEvent;
    viewer.key(e.key, e.code, e.type === 'keydown');
  };
  const onBlur = (): void => {
    viewer.held.clear();
  };
  target?.addEventListener('keydown', onKey);
  target?.addEventListener('keyup', onKey);
  target?.addEventListener('blur', onBlur);
  return () => {
    for (const type of ['keydown', 'keyup']) target?.removeEventListener(type, onKey);
    target?.removeEventListener('blur', onBlur);
  };
}
