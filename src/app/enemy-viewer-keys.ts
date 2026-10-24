import type { EnemyViewerSelection } from '../ui/enemy-viewer-panel';

// The keys of the enemies page (P05-R11).

/** Shortcuts: N / B next / previous enemy, M model, V wireframe, X weapon, 1-9 level, F, P. */
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
  };
  return changes[k];
}

/** In the model and wireframe views, ← / → (by key position) show the previous / next enemy. */
export const SWITCH_KEYS: Readonly<Record<string, number>> = { ArrowLeft: -1, ArrowRight: 1 };

export const HELP =
  'Move: arrows / WASD · N / B: next / previous enemy · M: model · V: wireframe (← / →: switch enemy) · X: weapon · 1-5: level · F: fire · P: pause';
