import { describe, expect, it } from 'vitest';
import { renderCaptionRow } from '../../../src/ui/caption-row';
import { FAKE_DOCUMENT, FakeElement } from '../../helpers/fake-dom';

describe('renderCaptionRow', () => {
  it('renders one caption per entry with a title and stat lines', () => {
    const parent = new FakeElement('body');
    const row = renderCaptionRow(
      FAKE_DOCUMENT as unknown as Document,
      parent as unknown as HTMLElement,
      [
        { title: 'A', lines: ['one', 'two'] },
        { title: 'B', lines: [] },
      ],
      90,
    ) as unknown as FakeElement;
    expect(parent.children).toEqual([row]);
    expect(row.className).toBe('caption-row');
    expect(row.style.width).toBe('90%');
    const [a, b] = row.children;
    expect(a?.className).toBe('caption');
    expect(a?.children.map((c) => c.textContent)).toEqual(['A', 'one', 'two']);
    expect(a?.children[0]?.className).toBe('caption-title');
    expect(b?.children.map((c) => c.textContent)).toEqual(['B']);
  });
});
