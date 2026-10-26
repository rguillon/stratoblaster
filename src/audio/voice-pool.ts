/** A sound effect voice the pool counts. */
export interface PoolVoice {
  readonly id: number;
  readonly name: string;
  readonly priority: number;
  readonly start: number;
  /** When it is over (Infinity for a looping sound, until released). */
  end: number;
}

/** What the pool decided for a sound: play it (in place of `evicted`), or not. */
export type PoolDecision =
  | { readonly play: true; readonly id: number; readonly evicted?: PoolVoice }
  | { readonly play: false; readonly retrigger: boolean };

/**
 * Mixing limits of the sound effects (P12-R10): at most `maxVoices` at once; when they are all
 * taken, a new sound replaces the oldest one of lower or equal priority (or is dropped); the
 * same sound started again within `retriggerSeconds` is not played twice. Pure: time is given.
 */
export class VoicePool {
  readonly #voices: PoolVoice[] = [];
  readonly #lastStart = new Map<string, number>();
  #nextId = 1;

  constructor(
    private readonly maxVoices: number,
    private readonly retriggerSeconds: number,
  ) {}

  /** The voices playing at the last request. */
  get voices(): readonly PoolVoice[] {
    return this.#voices;
  }

  /** Asks to play `name` at `now` for `seconds`. */
  request(name: string, priority: number, now: number, seconds: number): PoolDecision {
    this.#expire(now);
    const last = this.#lastStart.get(name);
    if (last !== undefined && now - last < this.retriggerSeconds) {
      return { play: false, retrigger: true };
    }
    let evicted: PoolVoice | undefined;
    if (this.#voices.length >= this.maxVoices) {
      evicted = this.#victim(priority);
      if (!evicted) return { play: false, retrigger: false };
      this.#voices.splice(this.#voices.indexOf(evicted), 1);
    }
    const voice: PoolVoice = { id: this.#nextId++, name, priority, start: now, end: now + seconds };
    this.#voices.push(voice);
    this.#lastStart.set(name, now);
    return evicted ? { play: true, id: voice.id, evicted } : { play: true, id: voice.id };
  }

  /** A voice stopped early (a looping sound let go, or every sound stopped). */
  release(id: number): void {
    const index = this.#voices.findIndex((v) => v.id === id);
    if (index >= 0) this.#voices.splice(index, 1);
  }

  /** Forgets every voice (the game paused: they were all stopped, P12-R11). */
  clear(): void {
    this.#voices.length = 0;
    this.#lastStart.clear();
  }

  #expire(now: number): void {
    for (let i = this.#voices.length - 1; i >= 0; i--) {
      if ((this.#voices[i]?.end ?? 0) <= now) this.#voices.splice(i, 1);
    }
  }

  /** The oldest voice whose priority is not above `priority`. */
  #victim(priority: number): PoolVoice | undefined {
    let oldest: PoolVoice | undefined;
    for (const voice of this.#voices) {
      if (voice.priority <= priority && (!oldest || voice.start < oldest.start)) oldest = voice;
    }
    return oldest;
  }
}
