/** A titled block of text lines. */
export interface Caption {
  readonly title: string;
  readonly lines: readonly string[];
}

/**
 * Renders captions side by side in a row (styled by the page's `.caption-row` CSS) and
 * appends it to `parent`. `widthPercent` sets the row width, centred on the page.
 */
export function renderCaptionRow(
  doc: Pick<Document, 'createElement'>,
  parent: HTMLElement,
  captions: readonly Caption[],
  widthPercent: number,
): HTMLElement {
  const row = doc.createElement('div');
  row.className = 'caption-row';
  row.style.width = `${String(widthPercent)}%`;
  for (const caption of captions) {
    const block = doc.createElement('div');
    block.className = 'caption';
    const title = doc.createElement('div');
    title.className = 'caption-title';
    title.textContent = caption.title;
    block.append(title);
    for (const line of caption.lines) {
      const el = doc.createElement('div');
      el.textContent = line;
      block.append(el);
    }
    row.append(block);
  }
  parent.append(row);
  return row;
}
