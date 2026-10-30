/** Tiny stand-in for the DOM API used by `ui/` code, so unit tests run in Node. */
export class FakeElement {
  className = '';
  textContent: string | null = '';
  readonly children: FakeElement[] = [];
  readonly style: Record<string, string> = {};
  readonly dataset: Record<string, string> = {};
  removed = false;

  constructor(readonly tagName: string) {}

  append(...nodes: FakeElement[]): void {
    this.children.push(...nodes);
  }

  remove(): void {
    this.removed = true;
  }
}

/** Minimal `document` that creates {@link FakeElement}s. */
export const FAKE_DOCUMENT = {
  createElement: (tag: string): FakeElement => new FakeElement(tag),
};
