/**
 * Lowers `el`'s font size, 1 px at a time, until it fits the width of its parent (or
 * `minPx` is reached). The CSS sizes are tuned for condensed fonts; this keeps whole letters
 * when the system falls back to a wider one. Does nothing while the element is not laid out.
 */
export function shrinkToFit(el: HTMLElement, minPx = 12): void {
  const room = el.parentElement?.clientWidth ?? 0;
  const style = el.ownerDocument.defaultView?.getComputedStyle(el);
  if (room === 0 || !style) return;
  let size = Number.parseFloat(style.fontSize);
  while (el.scrollWidth > room && size > minPx) {
    size -= 1;
    el.style.fontSize = `${String(size)}px`;
  }
}
