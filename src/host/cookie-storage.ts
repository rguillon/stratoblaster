import type { KeyValueStorage } from './key-value-storage';

const SECONDS_PER_DAY = 86_400;

/** Cookie-backed storage (GD-51, vision: persistence uses cookies). */
export class CookieStorage implements KeyValueStorage {
  constructor(
    private readonly doc: { cookie: string },
    private readonly maxAgeDays: number,
  ) {}

  get(key: string): string | null {
    const prefix = `${encodeURIComponent(key)}=`;
    for (const part of this.doc.cookie.split(';')) {
      const cookie = part.trim();
      if (!cookie.startsWith(prefix)) continue;
      try {
        return decodeURIComponent(cookie.slice(prefix.length));
      } catch {
        return null;
      }
    }
    return null;
  }

  set(key: string, value: string): void {
    const maxAge = Math.round(this.maxAgeDays * SECONDS_PER_DAY);
    this.doc.cookie =
      `${encodeURIComponent(key)}=${encodeURIComponent(value)}; ` +
      `max-age=${String(maxAge)}; SameSite=Lax`;
  }
}
