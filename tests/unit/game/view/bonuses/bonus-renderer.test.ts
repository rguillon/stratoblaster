import { describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { Bonus } from '../../../../../src/core/systems/bonus-world';
import { BONUS_LOOK } from '../../../../../src/game/config/bonus-look';
import {
  buildBombBadge,
  buildBonusBadge,
  buildLifeBadge,
} from '../../../../../src/game/view/bonuses/bonus-geometry';
import { createBonusRenderer } from '../../../../../src/game/view/bonuses/bonus-renderer';

const shown = (scene: Scene, prefix: string) =>
  scene.meshes.filter((m) => m.name.startsWith(`${prefix}-`) && m.isEnabled());

describe('bonus look (phase 6 review)', () => {
  it('the badge is a framed hexagon of radius 1 with chevrons in front of it', () => {
    const colors = { frame: [1, 1, 0], face: [0, 0, 0], chevrons: [0, 1, 1], inset: 0.8 } as const;
    const geo = buildBonusBadge(colors);
    for (let i = 0; i < geo.positions.length; i += 3) {
      const [x = 0, y = 0, z = 0] = geo.positions.slice(i, i + 3);
      expect(Math.hypot(x, y)).toBeLessThanOrEqual(1 + 1e-9);
      expect(z).toBeLessThanOrEqual(0);
    }
    expect(geo.indices.length % 3).toBe(0);
    expect(Math.max(...geo.indices)).toBe(geo.positions.length / 3 - 1);
    // The chevrons (cyan) stand in front (-Z) of the face.
    const cyan = geo.colors.findIndex((c, i) => i % 4 === 0 && c === 0 && geo.colors[i + 1] === 1);
    expect(geo.positions[(cyan / 4) * 3 + 2]).toBeLessThan(0);
  });

  it('draws each bonus as a swinging badge over a halo, and a flash where one is picked up', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createBonusRenderer(scene);
    const bonus: Bonus = { id: 1, x: 40, y: 300, age: 0.25, kind: 'weapon' };
    renderer.sync({ bonuses: [bonus], picked: [], dtSeconds: 0.1 });
    const [badge] = shown(scene, 'bonus-badge');
    expect(badge?.position.x).toBe(40);
    expect(badge?.position.y).toBe(300);
    expect(badge?.position.z).toBe(BONUS_LOOK.depth);
    const { amplitude, hz } = BONUS_LOOK.swing;
    expect(badge?.rotation.y).toBeCloseTo(amplitude * Math.sin(2 * Math.PI * hz * 0.25));
    expect(shown(scene, 'bonus-halo')).toHaveLength(1);
    expect(shown(scene, 'bonus-flash')).toHaveLength(0);
    // Picked up: the badge goes, a ring flashes out there, then fades.
    renderer.sync({ bonuses: [], picked: [bonus], dtSeconds: 0.1 });
    expect(shown(scene, 'bonus-badge')).toHaveLength(0);
    const [flash] = shown(scene, 'bonus-flash');
    expect(flash?.position.x).toBe(40);
    renderer.sync({ bonuses: [], picked: [], dtSeconds: BONUS_LOOK.flash.life / 2 });
    expect(flash?.visibility).toBeCloseTo(0.5);
    expect(flash?.scaling.x).toBeGreaterThan(BONUS_LOOK.size);
    renderer.sync({ bonuses: [], picked: [], dtSeconds: BONUS_LOOK.flash.life });
    expect(shown(scene, 'bonus-flash')).toHaveLength(0);
    renderer.dispose();
    expect(scene.meshes.filter((m) => m.name.startsWith('bonus-'))).toHaveLength(0);
  });

  it('P11-R07: life and bomb badges fit in radius 1, their marks in front', () => {
    for (const geo of [buildLifeBadge(BONUS_LOOK.life), buildBombBadge(BONUS_LOOK.bomb)]) {
      for (let i = 0; i < geo.positions.length; i += 3) {
        const [x = 0, y = 0, z = 0] = geo.positions.slice(i, i + 3);
        expect(Math.hypot(x, y)).toBeLessThanOrEqual(1 + 1e-9);
        expect(z).toBeLessThanOrEqual(0);
      }
      expect(geo.indices.length % 3).toBe(0);
      expect(Math.max(...geo.indices)).toBe(geo.positions.length / 3 - 1);
      expect(Math.min(...geo.positions.filter((_, i) => i % 3 === 2))).toBeLessThan(0);
    }
  });

  it('P11-R07: each kind of bonus is drawn with its own badge and halo', () => {
    const scene = new Scene(new NullEngine());
    const renderer = createBonusRenderer(scene);
    const bonuses: Bonus[] = [
      { id: 1, x: 10, y: 100, age: 0, kind: 'weapon' },
      { id: 2, x: 20, y: 100, age: 0, kind: 'life' },
      { id: 3, x: 30, y: 100, age: 0, kind: 'bomb' },
      { id: 4, x: 40, y: 100, age: 0, kind: 'bomb' },
    ];
    renderer.sync({ bonuses, picked: [], dtSeconds: 0.1 });
    expect(shown(scene, 'bonus-badge').map((m) => m.position.x)).toEqual([10]);
    expect(shown(scene, 'bonus-heart').map((m) => m.position.x)).toEqual([20]);
    expect(shown(scene, 'bonus-sphere').map((m) => m.position.x)).toEqual([30, 40]);
    expect(shown(scene, 'bonus-glow-life')).toHaveLength(1);
    expect(shown(scene, 'bonus-glow-bomb')).toHaveLength(2);
    expect(shown(scene, 'bonus-halo')).toHaveLength(1);
    renderer.dispose();
    expect(scene.meshes.filter((m) => m.name.startsWith('bonus-'))).toHaveLength(0);
  });
});
