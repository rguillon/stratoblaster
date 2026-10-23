import { describe, expect, it } from 'vitest';
import { GAME } from '../../../src/game/index';
import { HeightField } from '../../../src/core/scenery/height-field';
import { PropPlacer } from '../../../src/core/scenery/prop-placement';
import { levelRoads } from '../../../src/core/scenery/road-network';
import { levelDuration } from '../../../src/core/scenery/scenery-level';
import { LEVEL_ZERO, SCENERY_LEVELS } from '../../../src/game/sim/scenery-levels';
import { LEVEL_ZERO_LOOK, PLAYFIELD_CAMERA } from '../../../src/game/config/scenery-look';
import { framePlayfield, visibleGround } from '../../../src/render/scenery/playfield-framing';
import { GAME_CONFIG } from '../../../src/game/config/game';
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

  it('P04-R03 (review): the cloud layers fly above every peak and under the ships', () => {
    expect(LEVEL_ZERO_LOOK.clouds.length).toBeGreaterThan(0);
    for (const cloud of LEVEL_ZERO_LOOK.clouds) {
      expect(cloud.altitude).toBeGreaterThan(field.ceiling);
      expect(cloud.altitude).toBeLessThan(PLAYFIELD_CAMERA.flightAltitude);
    }
  });

  it('P04 review: roads start and end beyond what the camera can see', () => {
    const { width, height } = GAME_CONFIG.screen;
    const framing = framePlayfield(GAME_CONFIG.screen, PLAYFIELD_CAMERA);
    const cameraY = PLAYFIELD_CAMERA.flightAltitude + framing.height;
    const seen = visibleGround(framing, width / height, cameraY, LEVEL_ZERO.sea?.level ?? 0, 0);
    const { offscreenX, mainWidth, junction } = LEVEL_ZERO.roads;
    const shoulder = LEVEL_ZERO_LOOK.roads.shoulder;
    expect(offscreenX).toBeGreaterThan(
      seen.halfWidth + Math.max(mainWidth, junction.width) / 2 + shoulder,
    );
    for (const road of levelRoads(field, LEVEL_ZERO.roads, LEVEL_ZERO.seed).roads) {
      const last = road.points.at(-1);
      const onLevel = last && last.z > 0 && last.z < field.length;
      if (onLevel) expect(Math.abs(last.x)).toBeGreaterThanOrEqual(offscreenX);
    }
  });

  it('P04 review: ends with green meadows, an industrial zone and a city centre', () => {
    const names = LEVEL_ZERO.sections.map((s) => s.name);
    expect(names.slice(-3)).toEqual(['meadows', 'industrial zone', 'city centre']);
    const [meadows, industry, city] = field.sections.slice(-3);
    if (!meadows || !industry || !city) throw new Error('missing sections');
    const middle = (p: { start: number; end: number }) => (p.start + p.end) / 2;
    expect(field.surface(middle(meadows)).lush).toBe(1);
    expect(field.surface(middle(city)).paved).toBe(1);
    expect(industry.section.streets).toBeDefined();
    expect(city.section.streets).toBeDefined();
    const roads = levelRoads(field, LEVEL_ZERO.roads, LEVEL_ZERO.seed);
    const placer = new PropPlacer(field, LEVEL_ZERO.props, LEVEL_ZERO.seed, roads);
    const kindsIn = (p: { start: number; end: number }) =>
      new Set(
        placer
          .place({ xMin: -500, xMax: 500, zMin: p.start + 300, zMax: p.end - 300 })
          .map((q) => q.kind),
      );
    const green = kindsIn(meadows);
    expect(['conifer', 'broadleaf-tree', 'bush'].every((k) => green.has(k))).toBe(true);
    expect(green.has('dead-tree')).toBe(false);
    const industrial = kindsIn(industry);
    expect(industrial.has('industrial-plant-1') || industrial.has('industrial-plant-2')).toBe(true);
    expect([...industrial].some((k) => k.startsWith('industrial-works'))).toBe(true);
    expect(industrial.has('glass-tower')).toBe(false);
    const downtown = kindsIn(city);
    expect([...downtown].some((k) => k.startsWith('city-block'))).toBe(true);
    expect(downtown.has('factory')).toBe(false);
    // Dense: many more buildings per unit of length in the city than on the plains.
    const count = (zMin: number, zMax: number) =>
      placer
        .place({ xMin: -400, xMax: 400, zMin, zMax })
        .filter((q) => !q.kind.includes('tree') && q.kind !== 'bush' && q.kind !== 'conifer')
        .length;
    expect(count(middle(city) - 300, middle(city) + 300)).toBeGreaterThan(3 * count(200, 800));
  });

  it('P04 review: matte props and fixed, texel-snapped shadows (no blinking while scrolling)', () => {
    expect(LEVEL_ZERO_LOOK.props.specular).toBe(0);
    expect(LEVEL_ZERO_LOOK.terrain.specular).toBe(0);
    expect(LEVEL_ZERO_LOOK.sun.shadow.frustum).toBeGreaterThan(1000);
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
    const roads = levelRoads(field, LEVEL_ZERO.roads, LEVEL_ZERO.seed);
    const placer = new PropPlacer(field, LEVEL_ZERO.props, LEVEL_ZERO.seed, roads);
    const props = placer.place({ xMin: -500, xMax: 500, zMin: 0, zMax: field.length });
    const kinds = new Set(props.map((p) => p.kind));
    expect([...kinds].sort()).toEqual(Object.keys(PROP_MODELS).sort());
    for (const p of props) expect(p.y).toBeGreaterThanOrEqual(LEVEL_ZERO.props.minHeight);
  });

  it('P04-R07: has roads and paths over the level, with buildings only along them', () => {
    const roads = levelRoads(field, LEVEL_ZERO.roads, LEVEL_ZERO.seed);
    expect(roads.roads.filter((r) => r.kind === 'main').length).toBeGreaterThanOrEqual(2);
    expect(roads.roads.filter((r) => r.kind === 'cross').length).toBeGreaterThan(20);
    const placer = new PropPlacer(field, LEVEL_ZERO.props, LEVEL_ZERO.seed, roads);
    const trees = new Set(LEVEL_ZERO.props.trees.map((t) => t.id));
    const buildings = placer
      .place({ xMin: -500, xMax: 500, zMin: 0, zMax: 3000 })
      .filter((p) => !trees.has(p.kind));
    expect(buildings.length).toBeGreaterThan(50);
    const widest = Math.max(
      ...LEVEL_ZERO.props.groups.flatMap((g) => g.kinds.map((k) => k.footprint)),
    );
    for (const b of buildings) {
      expect(roads.edgeDistance(b.x, b.z)).toBeLessThanOrEqual(
        widest + LEVEL_ZERO.roads.setback + 1,
      );
    }
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
