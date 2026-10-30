// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { shrinkToFit } from '../../../src/ui/shrink-to-fit';

/** A 46 px element whose content is `pxPerFontPx × font size` wide, in a `room` px parent. */
function setup(room: number, pxPerFontPx: number) {
  const parent = document.createElement('div');
  const el = document.createElement('h1');
  el.style.fontSize = '46px';
  parent.append(el);
  document.body.append(parent);
  Object.defineProperty(parent, 'clientWidth', { value: room });
  Object.defineProperty(el, 'scrollWidth', {
    get: () => Number.parseFloat(el.style.fontSize) * pxPerFontPx,
  });
  return el;
}

describe('shrinkToFit', () => {
  it('P01-R04: shrinks the title logo until it fits the screen width', () => {
    const el = setup(480, 11);
    shrinkToFit(el);
    expect(el.style.fontSize).toBe('43px');
  });

  it('leaves an element that already fits untouched', () => {
    const el = setup(480, 10);
    shrinkToFit(el);
    expect(el.style.fontSize).toBe('46px');
  });

  it('stops at the minimum font size', () => {
    const el = setup(100, 11);
    shrinkToFit(el, 40);
    expect(el.style.fontSize).toBe('40px');
  });

  it('does nothing while the parent is not laid out', () => {
    const el = setup(0, 11);
    shrinkToFit(el);
    expect(el.style.fontSize).toBe('46px');
  });
});
