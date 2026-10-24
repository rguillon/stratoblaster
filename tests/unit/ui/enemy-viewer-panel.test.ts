// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { EnemyViewerPanel, type EnemyViewerSelection } from '../../../src/ui/enemy-viewer-panel';

const INITIAL: EnemyViewerSelection = {
  kind: 0,
  view: 'behaviour',
  weapon: 0,
  level: 1,
  fire: true,
  paused: false,
};

function panel() {
  const changes: EnemyViewerSelection[] = [];
  const p = new EnemyViewerPanel({
    doc: document,
    parent: document.body,
    kinds: ['Gnat', 'Hornet', 'Scout'],
    weapons: ['Gun', 'Beam'],
    levelCounts: [2, 3],
    initial: INITIAL,
    help: 'Keys',
    onChange: (s) => changes.push(s),
  });
  const buttons = (row: string) => [
    ...p.root.querySelectorAll<HTMLButtonElement>(`.enemy-${row} button`),
  ];
  const selected = (row: string) =>
    buttons(row)
      .filter((b) => b.classList.contains('selected'))
      .map((b) => b.textContent);
  return { p, changes, buttons, selected };
}

describe('EnemyViewerPanel', () => {
  it('P05-R11: shows a button per enemy kind, view, weapon and level, the selected ones marked', () => {
    const { p, buttons, selected } = panel();
    expect(p.root.querySelector('.enemy-title')?.textContent).toBe('Enemies');
    expect(buttons('kind').map((b) => b.textContent)).toEqual(['Gnat', 'Hornet', 'Scout']);
    expect(selected('kind')).toEqual(['Gnat']);
    expect(selected('view')).toEqual(['Behaviour']);
    expect(selected('weapon')).toEqual(['Gun']);
    expect(buttons('level').map((b) => b.textContent)).toEqual(['L1', 'L2']);
    expect(selected('toggles')).toEqual(['Fire (F)']);
    expect(p.root.querySelector('.enemy-help')?.textContent).toBe('Keys');
  });

  it('P05-R11: clicks change the selection and report it', () => {
    const { p, changes, buttons, selected } = panel();
    buttons('kind')[2]?.click();
    expect(p.selection.kind).toBe(2);
    buttons('view')[1]?.click();
    expect(p.selection.view).toBe('model');
    buttons('view')[2]?.click();
    expect(p.selection.view).toBe('wireframe');
    buttons('weapon')[1]?.click();
    expect(buttons('level')).toHaveLength(3);
    buttons('level')[2]?.click();
    expect(p.selection.level).toBe(3);
    buttons('toggles')[0]?.click();
    buttons('toggles')[1]?.click();
    expect(selected('toggles')).toEqual(['Pause (P)']);
    // One per click: kind, two views, weapon, level and two toggles.
    expect(changes).toHaveLength(7);
    p.root.querySelector<HTMLElement>('.enemy-kind')?.click();
    expect(changes).toHaveLength(7);
  });

  it('keeps indices and levels in range', () => {
    const { p } = panel();
    p.update({ kind: 9, weapon: -1, level: 7 });
    expect(p.selection).toMatchObject({ kind: 2, weapon: 0, level: 2 });
  });

  it('P05-R11: shows the live numbers', () => {
    const { p } = panel();
    p.showReadout({ enemies: 5, shots: 12, kills: 3, score: 150 });
    const text = (key: string) => p.root.querySelector(`.enemy-${key}`)?.textContent;
    expect(text('enemies')).toBe('Enemies: 5');
    expect(text('shots')).toBe('Enemy shots: 12');
    expect(text('kills')).toBe('Destroyed: 3');
    expect(text('score')).toBe('Score: 150');
  });
});
