import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import type { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { Enemy } from '../../../../../src/core/entities/enemy';
import { ENEMY_CONFIG } from '../../../../../src/game/config/enemies';
import { ELITE_CONFIG } from '../../../../../src/game/config/enemies-elite';
import { VETERAN_CONFIG } from '../../../../../src/game/config/enemies-veteran';
import { ENEMY_LOOK } from '../../../../../src/game/config/enemy-look';
import { BOSS_DESIGNS } from '../../../../../src/game/sim/boss-kinds';
import { BOSS_MODELS } from '../../../../../src/game/view/bosses/boss-models';
import { ENEMY_BINDINGS } from '../../../../../src/game/view/enemies/enemy-bindings';
import {
  breathScale,
  buildEnemyModel,
  flutterAngle,
  glowLevel,
  isLivingMotion,
  newBreath,
  setLivingMotion,
} from '../../../../../src/game/view/enemies/enemy-mesh';
import { ENEMY_MODELS } from '../../../../../src/game/view/enemies/enemy-models';
import { countTriangles } from '../../../../../src/render/mesh-stats';

const scene = (): Scene => new Scene(new NullEngine());
const IDLE = { charge: 0 } as unknown as Enemy;
const B = ENEMY_LOOK.budget;
const LIVING = ENEMY_LOOK.living;

/** The tier budget of each model key (P16-R09). */
function budgets(): [string, number][] {
  const of = (configs: object, budget: number): [string, number][] =>
    Object.values(configs).map((c: { stats: { model: string } }) => [c.stats.model, budget]);
  const bosses = BOSS_DESIGNS.map((d, i): [string, number] => [
    d.id,
    // Mini boss, then final boss, level after level.
    i % 2 === 0 ? B.miniBoss : B.finalBoss,
  ]);
  return [
    ...of(ENEMY_CONFIG, B.basic),
    ...of(VETERAN_CONFIG, B.veteran),
    ...of(ELITE_CONFIG, B.elite),
    ...bosses,
  ];
}

/** The world positions of the muzzle markers under `root`, by name. */
function muzzles(root: TransformNode): Map<string, string> {
  root.computeWorldMatrix(true);
  const found = new Map<string, string>();
  for (const node of root.getDescendants<TransformNode>(false)) {
    if (!node.name.includes('-muzzle-')) continue;
    node.computeWorldMatrix(true);
    const p = node.getAbsolutePosition();
    found.set(node.name, [p.x, p.y, p.z].map((v) => v.toFixed(4)).join(','));
  }
  return found;
}

describe('Cyber-Organic enemies (P16)', () => {
  afterEach(() => {
    setLivingMotion(true);
  });

  it('P16-R09: every model is within its tier’s triangle budget', () => {
    const s = scene();
    const keys = budgets();
    expect(keys.length).toBe(Object.keys(ENEMY_BINDINGS.models).length);
    for (const [key, budget] of keys) {
      const build = ENEMY_MODELS[key] ?? BOSS_MODELS[key];
      expect(build, key).toBeDefined();
      const root = build?.(s).root;
      expect(root ? countTriangles(root) : Infinity, key).toBeLessThanOrEqual(budget);
    }
  });

  it('P16-R01, R03..R06: every enemy and boss has a flesh body and metal grafts', () => {
    const s = scene();
    for (const [key, build] of Object.entries(ENEMY_BINDINGS.models)) {
      const names = build(s)
        .root.getChildMeshes()
        .map((m) => m.material?.name);
      expect(names, key).toContain('enemy-flesh');
      expect(names, key).toContain('enemy-hull');
    }
  });

  it('P16-R01: the flesh shades are dark, so enemies keep their contrast (P14-R04)', () => {
    const { crimson, purple, teal, sinew, bone, membrane } = ENEMY_LOOK.flesh;
    for (const shade of [crimson, purple, teal, sinew, bone, membrane]) {
      expect(Math.max(...shade)).toBeLessThan(0.2);
    }
    expect(ENEMY_LOOK.flesh.metallic).toBeLessThan(ENEMY_LOOK.hull.metallic);
  });

  it('P16-R07: the body breathes, its veins pulse and its wings flutter, from the sim time', () => {
    const model = buildEnemyModel('living', scene(), [1, 0.1, 0.1], (p) => {
      p.flesh.box([4, 2, 4], ENEMY_LOOK.flesh.crimson);
      p.vein.box([1, 1, 1], [1, 0.1, 0.1]);
      p.flap([2, 0, 0], 1, 6, (w) => w.flesh.box([6, 0.2, 2], ENEMY_LOOK.flesh.membrane));
    });
    const body = model.root.getChildTransformNodes(true).find((n) => n.name === 'living-body');
    const wing = model.root.getChildTransformNodes(false).find((n) => n.name === 'living-wing-0');
    const vein = model.root.getChildMeshes().find((m) => m.name === 'living-living-vein');
    if (!body || !wing || !vein) throw new Error('living model parts');
    const glow = vein.material as StandardMaterial;
    const scales = new Set<string>();
    const rolls = new Set<string>();
    const glows = new Set<string>();
    for (let i = 0; i < 30; i++) {
      model.sync(IDLE, 0.1);
      scales.add(body.scaling.x.toFixed(4));
      rolls.add(wing.rotation.z.toFixed(4));
      glows.add(glow.emissiveColor.r.toFixed(4));
    }
    expect(scales.size).toBeGreaterThan(5);
    expect(rolls.size).toBeGreaterThan(5);
    expect(glows.size).toBeGreaterThan(5);
    // A paused game steps nothing: it holds still.
    const held = body.scaling.x;
    model.sync(IDLE, 0);
    expect(body.scaling.x).toBe(held);
  });

  it('P16-R07: breathing, glow and flutter stay within their tunables', () => {
    const breath = newBreath();
    const { amplitude, period, spread } = LIVING.breathing;
    expect(breath.period).toBeGreaterThanOrEqual(period * (1 - spread) - 1e-9);
    expect(breath.period).toBeLessThanOrEqual(period * (1 + spread) + 1e-9);
    expect(newBreath().phase).not.toBe(breath.phase);
    for (let t = 0; t < 5; t += 0.05) {
      expect(Math.abs(breathScale(breath, t) - 1)).toBeLessThanOrEqual(amplitude + 1e-9);
      expect(glowLevel(breath, t)).toBeGreaterThanOrEqual(LIVING.glow.low - 1e-9);
      expect(glowLevel(breath, t)).toBeLessThanOrEqual(1 + 1e-9);
      expect(Math.abs(flutterAngle(1, 5, t))).toBeLessThanOrEqual(LIVING.flutter.angle + 1e-9);
    }
    // Big wings beat slower: a quarter beat of a small wing is far from a big wing's peak.
    const quarter = 1 / (4 * LIVING.flutter.hz);
    expect(Math.abs(flutterAngle(1, 5, quarter))).toBeCloseTo(LIVING.flutter.angle);
    expect(Math.abs(flutterAngle(1, LIVING.flutter.bigSpan + 1, quarter))).toBeLessThan(
      LIVING.flutter.angle * 0.7,
    );
    // Left and right wings of a pair flap opposite ways in roll (both up together).
    expect(flutterAngle(-1, 5, quarter)).toBeCloseTo(-flutterAngle(1, 5, quarter));
  });

  it('P16-R07, R08: shot origins are the same with and without the living motion', () => {
    const s = scene();
    for (const [key, build] of Object.entries(ENEMY_BINDINGS.models)) {
      setLivingMotion(false);
      const still = build(s);
      still.sync(IDLE, 0);
      const before = muzzles(still.root);
      setLivingMotion(true);
      const living = build(s);
      for (let i = 0; i < 7; i++) living.sync(IDLE, 0.13);
      const after = muzzles(living.root);
      // Names carry the model's instance-free name: compare by position, in order.
      expect([...after.values()], key).toEqual([...before.values()]);
    }
  });

  it('P16-R10: the living motion can be turned off, bodies then hold still at rest', () => {
    setLivingMotion(false);
    expect(isLivingMotion()).toBe(false);
    const model = buildEnemyModel('still', scene(), [1, 1, 0], (p) => {
      p.flesh.box([2, 2, 2], ENEMY_LOOK.flesh.teal);
    });
    for (let i = 0; i < 5; i++) model.sync(IDLE, 0.3);
    const body = model.root.getChildTransformNodes(true).find((n) => n.name === 'still-body');
    expect(body?.scaling.x).toBe(1);
    expect(ENEMY_BINDINGS.setIdleMotion).toBe(setLivingMotion);
  });

  it('P16-R05: a destroyed boss part leaves a wound of torn flesh, not a hole', () => {
    const s = scene();
    for (const design of BOSS_DESIGNS) {
      const root = BOSS_MODELS[design.id]?.(s).root;
      const flesh = root
        ?.getChildMeshes()
        .filter((m) => m.name.includes('-stump-') && m.material?.name === 'enemy-flesh');
      expect(flesh?.length, design.id).toBeGreaterThanOrEqual(design.stats.parts.length);
    }
  });
});
