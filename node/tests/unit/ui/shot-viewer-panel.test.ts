// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { ShotViewerPanel, type ShotViewerSelection } from '../../../src/ui/shot-viewer-panel';

function panel() {
  const changes: ShotViewerSelection[] = [];
  const p = new ShotViewerPanel({
    doc: document,
    parent: document.body,
    ships: ['A', 'B'],
    weapons: ['Gun', 'Beam'],
    levelCounts: [2, 3],
    initial: { ship: 0, weapon: 0, level: 1, guides: false, targets: true },
    onChange: (s) => changes.push(s),
  });
  const buttons = (row: string) => [
    ...p.root.querySelectorAll<HTMLButtonElement>(`.shot-${row} button`),
  ];
  const selected = (row: string) =>
    buttons(row)
      .filter((b) => b.classList.contains('selected'))
      .map((b) => b.textContent);
  return { p, changes, buttons, selected };
}

describe('ShotViewerPanel', () => {
  it('P03-R10: shows a button per ship, weapon and level, the selected ones marked', () => {
    const { buttons, selected } = panel();
    expect(buttons('ship').map((b) => b.textContent)).toEqual(['A', 'B']);
    expect(buttons('weapon').map((b) => b.textContent)).toEqual(['Gun', 'Beam']);
    expect(buttons('level').map((b) => b.textContent)).toEqual(['L1', 'L2']);
    expect(selected('ship')).toEqual(['A']);
    expect(selected('toggles')).toEqual(['Targets (T)']);
    expect(buttons('ship')[0]?.getAttribute('aria-pressed')).toBe('true');
  });

  it('P03-R10: clicking a button changes the selection and reports it', () => {
    const { p, changes, buttons, selected } = panel();
    buttons('weapon')[1]?.click();
    expect(p.selection.weapon).toBe(1);
    // The level row follows the weapon's level count.
    expect(buttons('level')).toHaveLength(3);
    buttons('level')[2]?.click();
    buttons('toggles')[0]?.click();
    expect(selected('level')).toEqual(['L3']);
    expect(changes.at(-1)).toMatchObject({ weapon: 1, level: 3, guides: true, targets: true });
  });

  it('keeps the level within the selected weapon', () => {
    const { p } = panel();
    p.update({ weapon: 1, level: 3 });
    p.update({ weapon: 0 });
    expect(p.selection.level).toBe(2);
    p.update({ level: 0 });
    expect(p.selection.level).toBe(1);
  });

  it('shows the live readouts', () => {
    const { p } = panel();
    p.showReadout({ summary: 'Gun L1', shots: 3, damagePerSecond: 12.345, kills: 2 });
    const text = p.root.textContent;
    expect(text).toContain('Gun L1');
    expect(text).toContain('Shots in flight: 3');
    expect(text).toContain('Damage/s: 12.3');
    expect(text).toContain('Targets destroyed: 2');
  });
});
