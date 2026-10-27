import { describe, expect, it } from 'vitest';
import {
  foldIntoFamily,
  hueSaturation,
  inFamily,
  relativeLuminance,
  veiled,
  type ColorFamily,
  type Rgb,
} from '../../../../src/core/math/color';
import { BOMB_LOOK } from '../../../../src/game/config/bomb-look';
import { BONUS_LOOK } from '../../../../src/game/config/bonus-look';
import { BOSS_LOOK } from '../../../../src/game/config/boss-look';
import { VETERAN_NEON } from '../../../../src/game/config/enemies-veteran';
import { ELITE_NEON } from '../../../../src/game/config/enemy-look-elite';
import { ENEMY_LOOK, laserPalette } from '../../../../src/game/config/enemy-look';
import { READABILITY } from '../../../../src/game/config/readability';
import { SHIP_LOOK } from '../../../../src/game/config/ship-look';
import { SHOT_LOOK } from '../../../../src/game/config/shot-look';
import { SCENERY_BINDINGS } from '../../../../src/game/view/scenery-bindings';
import { enemyColor } from '../../../../src/game/view/enemies/enemy-mesh';

const FAMILIES = READABILITY.families;

/** Every RGB triple (3 numbers in 0..1) found anywhere in `value`, but under `skip` keys. */
function colorsIn(value: unknown, skip?: RegExp): Rgb[] {
  if (Array.isArray(value)) {
    if (value.length === 3 && value.every((v) => typeof v === 'number' && v >= 0 && v <= 1)) {
      return [value as unknown as Rgb];
    }
    return value.flatMap((v) => colorsIn(v, skip));
  }
  if (typeof value === 'object' && value !== null) {
    return Object.entries(value)
      .filter(([key]) => !skip?.test(key))
      .flatMap(([, v]) => colorsIn(v, skip));
  }
  return [];
}

/**
 * Colours of a look that are not seen on the ground as such: the sun's and the lights' (their
 * colour tints what they light), the sky gradient used for reflections only.
 */
const NOT_SEEN = /^(sun|ambient|stops)$|light/i;

/** Colours that read as a colour (not a grey, a pale tint or a near black). */
function vivid(colors: readonly Rgb[]): Rgb[] {
  const saturated = FAMILIES.player.minSaturation;
  return colors.filter((c) => Math.max(...c) >= 0.3 && hueSaturation(c).saturation >= saturated);
}

function expectAllIn(colors: readonly Rgb[], family: ColorFamily): void {
  expect(colors.length).toBeGreaterThan(0);
  for (const c of colors) expect({ c, in: inFamily(c, family) }).toEqual({ c, in: true });
}

describe('P14-R02: reserved gameplay colours', () => {
  it('P14-R02: the colour families do not overlap', () => {
    const all = Object.values(FAMILIES);
    for (let hue = 0; hue < 360; hue += 0.5) {
      // A fully saturated colour of that hue.
      const k = (n: number) => {
        const t = (n + hue / 60) % 6;
        return 1 - Math.max(0, Math.min(t, 4 - t, 1));
      };
      const color: Rgb = [k(5), k(3), k(1)];
      expect(all.filter((f) => inFamily(color, f)).length).toBeLessThanOrEqual(1);
    }
  });

  it('P14-R02: every enemy shot (bullets, missiles, lasers) is in the enemy shots family', () => {
    const { bullets, missile } = ENEMY_LOOK;
    // As `enemy-lasers.ts` draws them: each colour folded into the family.
    const lasers = [ENEMY_LOOK.laser.color, ...Object.values(BOSS_LOOK.neon)].map((c) =>
      foldIntoFamily(c, FAMILIES.enemyShot),
    );
    expectAllIn(vivid(colorsIn([bullets.styles, missile.tip, missile.flame])), FAMILIES.enemyShot);
    expectAllIn(vivid(colorsIn(lasers.map(laserPalette))), FAMILIES.enemyShot);
  });

  it('P14-R02: player shots and ship lights are in the player family', () => {
    expectAllIn(vivid(colorsIn(SHOT_LOOK)), FAMILIES.player);
    expectAllIn(vivid(colorsIn(SHIP_LOOK)), FAMILIES.player);
    expectAllIn(
      vivid(colorsIn([READABILITY.playerOutline, READABILITY.hitboxMarker])),
      FAMILIES.player,
    );
    expectAllIn(vivid(colorsIn(BOMB_LOOK.wave)), FAMILIES.player);
  });

  it('P14-R02: every enemy and boss neon is drawn in the enemy family', () => {
    const neons = [
      ...Object.values(ENEMY_LOOK.neon),
      ...Object.values(ELITE_NEON),
      ...Object.values(VETERAN_NEON),
      ...Object.values(BOSS_LOOK.neon),
      ENEMY_LOOK.reactor.color,
    ];
    expectAllIn(vivid(neons.map(enemyColor)), FAMILIES.enemy);
    // They stay different from each other.
    const keys = new Set(Object.values(ENEMY_LOOK.neon).map((c) => enemyColor(c).join()));
    expect(keys.size).toBe(new Set(Object.values(ENEMY_LOOK.neon).map((c) => c.join())).size);
  });

  it('P14-R02: every bonus is in the pickups family', () => {
    expectAllIn(vivid(colorsIn(BONUS_LOOK)), FAMILIES.pickup);
  });

  it('P14-R01, R02: no ground colour of the enemy shots family is brighter than the cap', () => {
    for (const [id, look] of Object.entries(SCENERY_BINDINGS.looks)) {
      const veil = look.veil;
      expect({ id, veil: veil !== undefined }).toEqual({ id, veil: true });
      if (!veil) continue;
      const palette = Object.fromEntries(Object.entries(look).filter(([key]) => key !== 'veil'));
      for (const c of colorsIn(palette, NOT_SEEN)) {
        if (!inFamily(c, FAMILIES.enemyShot)) continue;
        const seen = veiled(c, veil);
        expect({
          id,
          c,
          ok: relativeLuminance(seen) <= READABILITY.backgroundMaxLuminance,
        }).toEqual({
          id,
          c,
          ok: true,
        });
      }
    }
  });
});
