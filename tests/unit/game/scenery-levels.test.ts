import { describe, expect, it } from 'vitest';
import { GAME } from '../../../src/game/index';
import { HeightField } from '../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../src/core/scenery/prop-placement';
import { levelDuration } from '../../../src/core/scenery/scenery-level';
import { LEVEL_ZERO, SCENERY_LEVELS } from '../../../src/game/sim/scenery-levels';
import { PLAYFIELD_CAMERA } from '../../../src/game/config/scenery-look';
import { PROP_MODELS } from '../../../src/game/view/props/prop-models';

describe('Level Zero', () => {
  const field = new HeightField(LEVEL_ZERO);

  it('P04-R06: lasts about 3 minutes', () => {
    expect(levelDuration(LEVEL_ZERO)).toBe(180);
    expect(field.length).toBe(180 * LEVEL_ZERO.scrollSpeed);
  });

  it('P04-R01: shows every terrain tool: mountains, canyon, plateau, coast, flat ground', () => {
    const s = LEVEL_ZERO.sections;
    expect(s.some((x) => x.relief.style === 'ridged')).toBe(true);
    expect(s.some((x) => x.channel)).toBe(true);
    expect(s.some((x) => x.flatten)).toBe(true);
    expect(s.some((x) => x.shore)).toBe(true);
    expect(s.some((x) => x.relief.amplitude < 20 && x.relief.style === 'smooth')).toBe(true);
  });

  it('P04-R01: no peak rises into the flight plane', () => {
    let highest = -Infinity;
    for (let z = 0; z <= field.length; z += 40) {
      for (let x = -600; x <= 600; x += 40) highest = Math.max(highest, field.height(x, z));
    }
    expect(highest).toBeLessThan(PLAYFIELD_CAMERA.flightAltitude - 50);
    expect(highest).toBeGreaterThan(150);
  });

  it('P04-R02: has a sea, with ground under it in the coast and open sea sections', () => {
    expect(LEVEL_ZERO.sea?.level).toBe(0);
    const sea = field.sections.find((p) => p.section.name === 'open sea');
    if (!sea) throw new Error('no open sea');
    const z = (sea.start + sea.end) / 2;
    const heights = Array.from({ length: 30 }, (_, i) => field.height(-600 + i * 40, z));
    expect(heights.filter((h) => h < 0).length).toBeGreaterThan(15);
  });

  it('P04-R04: places every kind of prop over the level, on flat ground above the sea', () => {
    const placer = new PropPlacer(field, LEVEL_ZERO.props, LEVEL_ZERO.seed);
    const props = placer.place({ xMin: -500, xMax: 500, zMin: 0, zMax: field.length });
    const kinds = new Set(props.map((p) => p.kind));
    expect([...kinds].sort()).toEqual(Object.keys(PROP_MODELS).sort());
    for (const p of props) expect(p.y).toBeGreaterThanOrEqual(LEVEL_ZERO.props.minHeight);
  });

  it('P04: is registered in the game with a look and a model per prop', () => {
    expect(GAME.sceneryLevels).toBe(SCENERY_LEVELS);
    expect(SCENERY_LEVELS[0]).toBe(LEVEL_ZERO);
    expect(GAME.view.scenery.looks[LEVEL_ZERO.id]).toBeDefined();
    expect(GAME.view.scenery.camera.tiltDeg).toBe(35);
    const ids = [...LEVEL_ZERO.props.groups.flatMap((g) => g.kinds), ...LEVEL_ZERO.props.trees].map(
      (k) => k.id,
    );
    for (const id of ids) expect(GAME.view.scenery.propModels[id]).toBeTypeOf('function');
  });
});
