import type { Scene } from '@babylonjs/core/scene';
import type { ActiveBomb } from '../../../core/systems/player-bombs';
import type { BombRenderer } from '../../../render/game-view';
import { BOMB_LOOK as LOOK } from '../../config/bomb-look';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from '../shots/shot-meshes';

/** How far out the shockwave is, 0..1, `t` (0..1) into the bomb: fast, then slowing. */
export function waveReach(t: number): number {
  const clamped = Math.min(1, Math.max(0, t));
  return 1 - (1 - clamped) ** 2;
}

/** How bright the flash is, `age` seconds into the bomb: full at once, gone after its time. */
export function flashStrength(age: number): number {
  return Math.max(0, 1 - age / LOOK.flash.seconds);
}

/**
 * A bomb going off (P11-R05), in playfield space: a shockwave ring growing from where the ship
 * was over the whole playfield, and a flash there that fades in a fraction of a second.
 */
export function createBombRenderer(scene: Scene): BombRenderer {
  const { wave, flash, depth } = LOOK;
  const ring = additiveTemplate('bomb-wave', buildGlowDisc(wave.segments, wave.colors), scene);
  const glow = additiveTemplate('bomb-flash', buildGlowDisc(flash.segments, flash.colors), scene);
  const show = (bomb: ActiveBomb | undefined): void => {
    ring.setEnabled(bomb !== undefined);
    glow.setEnabled(bomb !== undefined && flashStrength(bomb.age) > 0);
    if (!bomb) return;
    const t = bomb.age / bomb.seconds;
    const radius = Math.max(1, wave.radius * waveReach(t));
    ring.position.set(bomb.x, bomb.y, depth);
    ring.scaling.set(radius, radius, 1);
    ring.visibility = 1 - t * t;
    glow.position.set(bomb.x, bomb.y, depth + 0.5);
    glow.scaling.set(flash.radius, flash.radius, 1);
    glow.visibility = flashStrength(bomb.age);
  };
  return {
    sync: ({ bomb }) => {
      show(bomb);
    },
    dispose: () => {
      ring.dispose();
      glow.dispose();
    },
  };
}
