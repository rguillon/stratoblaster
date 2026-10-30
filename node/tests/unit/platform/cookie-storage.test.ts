import { describe, expect, it } from 'vitest';
import { CookieStorage } from '../../../src/platform/cookie-storage';
import { MemoryStorage } from '../../../src/platform/key-value-storage';

/** Mimics `document.cookie`: reading returns `name=value` pairs, writing sets one cookie. */
class FakeCookieJar {
  readonly writes: string[] = [];
  readonly #values = new Map<string, string>();

  get cookie(): string {
    return [...this.#values].map(([k, v]) => `${k}=${v}`).join('; ');
  }

  set cookie(text: string) {
    this.writes.push(text);
    const [pair = ''] = text.split(';');
    const eq = pair.indexOf('=');
    this.#values.set(pair.slice(0, eq), pair.slice(eq + 1));
  }
}

describe('CookieStorage', () => {
  it('GD-51: reads and writes cookies that last cookie_max_age days', () => {
    const jar = new FakeCookieJar();
    const storage = new CookieStorage(jar, 365);
    expect(storage.get('stratoblaster_high_score')).toBeNull();
    storage.set('stratoblaster_last_ship', 'light ship');
    expect(jar.writes[0]).toBe(
      'stratoblaster_last_ship=light%20ship; max-age=31536000; SameSite=Lax',
    );
    expect(storage.get('stratoblaster_last_ship')).toBe('light ship');
  });

  it('finds a cookie among others and ignores names that only share a prefix', () => {
    const storage = new CookieStorage({ cookie: 'a_b=1; a=2; other=3' }, 1);
    expect(storage.get('a')).toBe('2');
    expect(storage.get('other')).toBe('3');
  });

  it('P01-R04: returns null for a cookie that cannot be decoded', () => {
    const storage = new CookieStorage({ cookie: 'stratoblaster_high_score=%E0%A4%A' }, 1);
    expect(storage.get('stratoblaster_high_score')).toBeNull();
  });
});

describe('MemoryStorage', () => {
  it('stores strings in memory', () => {
    const storage = new MemoryStorage();
    expect(storage.get('k')).toBeNull();
    storage.set('k', 'v');
    expect(storage.get('k')).toBe('v');
  });
});
