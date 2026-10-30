import type { AudioBindings, MusicRequest } from '../../../audio/audio-bindings';
import type { Track } from '../../../audio/audio-types';
import { composeTrack, seedOf } from './compose-track';
import { INSTRUMENTS } from './instruments';
import { JINGLES } from './jingles';
import { MENU_STYLE, WORLD_STYLES, type MusicStyle } from './music-styles';
import { SOUND_DESIGNS } from './sound-designs';

/** Explosions of enemies at least this big (hit radius, logical pixels) sound large. */
const LARGE_BLAST_RADIUS = 18;

/**
 * Levels of the music and sound effect buses at full volume: the loudest sound effects stay
 * within `loudest_sfx` (+6 dB) of the music at equal volume settings (P12-R10).
 */
const MIX = { music: 0.8, sfx: 1 };

/** The synthwave echo (a dotted eighth) and reverb the instruments send to. */
const EFFECTS = { echoBeats: 0.75, echoFeedback: 0.35, reverbSeconds: 2.2 };

/** The world of a level id such as `2-3`. */
export function worldOf(levelId: string): number {
  return Number.parseInt(levelId, 10);
}

function styleOf(levelId: string): MusicStyle | undefined {
  return WORLD_STYLES[worldOf(levelId)];
}

const made = new Map<string, Track>();

/** Composes a track once, then keeps it (a track is a few thousand notes). */
function cached(id: string, style: MusicStyle | undefined, boss = false): Track | undefined {
  if (!style) return undefined;
  let track = made.get(id);
  if (!track) {
    track = composeTrack({ id, style, seed: seedOf(id), boss });
    made.set(id, track);
  }
  return track;
}

/**
 * The track for a request (P12-R06..R08): each level its own, from its id; one boss track per
 * world; the menu theme; the jingles.
 */
export function gameMusic(request: MusicRequest): Track | undefined {
  switch (request.kind) {
    case 'menu':
      return cached('menu', MENU_STYLE);
    case 'level':
      return cached(`level-${request.levelId}`, styleOf(request.levelId));
    case 'boss': {
      const world = worldOf(request.levelId);
      return cached(`boss-${String(world)}`, WORLD_STYLES[world], true);
    }
    case 'jingle':
      return JINGLES[request.jingle];
  }
}

/** The game's generated music and sound effects (P12-R05..R10, GD-70, GD-71). */
export const GAME_AUDIO: AudioBindings = {
  music: gameMusic,
  instruments: INSTRUMENTS,
  sounds: SOUND_DESIGNS,
  largeBlastRadius: LARGE_BLAST_RADIUS,
  mix: MIX,
  effects: EFFECTS,
};
