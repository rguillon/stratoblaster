import { beatSeconds, trackSeconds, type Note, type Track } from './audio-types';

/** A note to play, with its time in seconds since the track started (counting loops). */
export interface ScheduledNote {
  readonly note: Note;
  readonly at: number;
  readonly seconds: number;
}

/**
 * Walks a track's notes ahead of time (P12-R05): each call hands out the notes that start
 * before a given point of the track, once each, looping at the track's end. Pure: the player
 * turns track time into audio time, so the music keeps time when frames are slow, and pausing is
 * only a matter of where it stands.
 */
export class Sequencer {
  /** Seconds into the track (counting loops) up to which the notes were handed out. */
  #position = 0;
  /** Index of the next note in the track, and the loop it is in. */
  #index = 0;
  #loop = 0;
  readonly #beat: number;
  readonly #length: number;

  constructor(readonly track: Track) {
    this.#beat = beatSeconds(track.bpm);
    this.#length = trackSeconds(track);
  }

  /** Seconds into the track (counting loops) handed out so far. */
  get position(): number {
    return this.#position;
  }

  /** Whether a track that does not loop has handed out all its notes. */
  get done(): boolean {
    return !this.track.loop && this.#position >= this.#length;
  }

  /** The notes starting before `until` seconds into the track that were not handed out yet. */
  advance(until: number): ScheduledNote[] {
    const out: ScheduledNote[] = [];
    if (until <= this.#position || this.#length <= 0) return out;
    const { notes, loop } = this.track;
    while (notes.length > 0) {
      const note = notes[this.#index];
      if (!note) {
        if (!loop) break;
        this.#index = 0;
        this.#loop++;
        continue;
      }
      const at = this.#loop * this.#length + note.beat * this.#beat;
      if (at >= until) break;
      out.push({ note, at, seconds: note.beats * this.#beat });
      this.#index++;
    }
    this.#position = loop ? until : Math.min(until, this.#length);
    return out;
  }

  /**
   * Goes back (or on) to `seconds` into the track: the notes from there are handed out again.
   * Used when the game pauses, as the notes scheduled ahead are cancelled (P12-R11).
   */
  seek(seconds: number): void {
    const time = Math.max(0, seconds);
    const length = this.#length;
    this.#loop = length > 0 && this.track.loop ? Math.floor(time / length) : 0;
    const inLoop = time - this.#loop * length;
    const index = this.track.notes.findIndex((n) => n.beat * this.#beat >= inLoop);
    this.#index = index < 0 ? this.track.notes.length : index;
    this.#position = time;
  }
}
