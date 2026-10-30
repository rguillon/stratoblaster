/** Small string storage, so app code does not depend on cookies and tests use a fake. */
export interface KeyValueStorage {
  /** The stored value, or null when missing or unreadable. */
  get(key: string): string | null;
  set(key: string, value: string): void;
}

/** In-memory storage, for tests and as a fallback. */
export class MemoryStorage implements KeyValueStorage {
  readonly #values = new Map<string, string>();

  get(key: string): string | null {
    return this.#values.get(key) ?? null;
  }

  set(key: string, value: string): void {
    this.#values.set(key, value);
  }
}
