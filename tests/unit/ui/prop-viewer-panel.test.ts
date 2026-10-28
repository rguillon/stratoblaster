// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { PropViewerPanel, type PropViewerSelection } from '../../../src/ui/prop-viewer-panel';

const GROUPS = [
  { label: 'Town', ids: ['house', 'shop'] },
  { label: 'Cars', ids: ['car'] },
];

function panel() {
  const changes: PropViewerSelection[] = [];
  const p = new PropViewerPanel({
    doc: document,
    parent: document.body,
    groups: GROUPS,
    initial: { group: 0, prop: 0 },
    onChange: (s) => changes.push(s),
  });
  const buttons = (row: string) => [
    ...p.root.querySelectorAll<HTMLButtonElement>(`.prop-${row} button`),
  ];
  const selected = (row: string) =>
    buttons(row)
      .filter((b) => b.classList.contains('selected'))
      .map((b) => b.textContent);
  return { p, changes, buttons, selected };
}

describe('PropViewerPanel (reviewer, 2026-10-28)', () => {
  it('shows a button per group and per prop of the shown group, the picked ones marked', () => {
    const { buttons, selected } = panel();
    expect(buttons('groups').map((b) => b.textContent)).toEqual(['Town (2)', 'Cars (1)']);
    expect(buttons('kinds').map((b) => b.textContent)).toEqual(['house', 'shop']);
    expect(selected('groups')).toEqual(['Town (2)']);
    expect(selected('kinds')).toEqual(['house']);
  });

  it('picks a prop, or another group starting on its first prop', () => {
    const { p, changes, buttons, selected } = panel();
    buttons('kinds')[1]?.click();
    expect(selected('kinds')).toEqual(['shop']);
    buttons('groups')[1]?.click();
    expect(buttons('kinds').map((b) => b.textContent)).toEqual(['car']);
    expect(changes).toEqual([
      { group: 0, prop: 1 },
      { group: 1, prop: 0 },
    ]);
    p.update({ group: 0, prop: 1 });
    expect(selected('kinds')).toEqual(['shop']);
    expect(changes).toHaveLength(2);
    p.setReadout('house — 4 × 4 × 4');
    expect(p.root.querySelector('.prop-readout')?.textContent).toBe('house — 4 × 4 × 4');
  });
});
