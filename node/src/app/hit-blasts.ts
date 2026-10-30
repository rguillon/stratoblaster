import type { EnemyBlast } from '../core/systems/enemy-world';
import type { LandedHit } from '../core/systems/level-run';
import { GAME_PLAY_CONFIG as CFG } from '../config/game-play';

/** A spark where a hit landed; a blast at the ship when it cost a life (phase 6 review). */
export function hitBlasts(
  hits: readonly LandedHit[],
  ship: { readonly x: number; readonly y: number },
): EnemyBlast[] {
  const { hitSpark, shipBlast } = CFG.damage;
  return hits.map((hit) =>
    hit.event === 'hit'
      ? { kind: 'missile', x: hit.x, y: hit.y, radius: hitSpark }
      : { kind: 'enemy', x: ship.x, y: ship.y, radius: shipBlast },
  );
}
