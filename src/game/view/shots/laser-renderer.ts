import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { BeamSegment } from '../../../core/systems/beam';
import { createRng } from '../../../core/math/rng';
import { NodePool } from '../../../render/node-pool';
import type { ShotRenderer } from '../../../render/game-view';
import { SHOT_LOOK } from '../../config/shot-look';
import { flicker } from '../reactor-flame';
import { buildGlowBar, buildGlowDisc } from '../shot-geometry';
import { LaserParticles, type ParticleSpot } from './laser-particles';
import { additiveTemplate } from './shot-meshes';
import type { ColoredGeometry } from '../../../render/geometry/gradient-shapes';

const LOOK = SHOT_LOOK.laser;
/** Length used to spread the particles along the beam before it first fires. */
const INITIAL_LENGTH = 600;
const DISC_SEGMENTS = 10;

/** A disabled additive template and a pool of its clones. */
function glowPool(scene: Scene, name: string, geo: ColoredGeometry) {
  const template = additiveTemplate(name, geo, scene);
  const pool = new NodePool((i) => template.clone(`${name}-${String(i)}`));
  return { template, pool };
}

type Pool = NodePool<Mesh>;

/** One bar per segment, as wide as the segment's level (times the glow), from y0 to y1. */
function placeBars(bars: Pool, beam: readonly BeamSegment[], wobble: number): void {
  bars.show(beam.length).forEach((mesh, i) => {
    const s = beam[i];
    if (!s) return;
    mesh.position.set(s.x, s.y0, 0);
    mesh.scaling.set(s.width * LOOK.glowWidth * wobble, Math.max(0, s.y1 - s.y0), 1);
  });
}

/** A glow at the end of each segment that stops on a target. */
function placeContacts(contacts: Pool, beam: readonly BeamSegment[], wobble: number): void {
  const hits = beam.filter((s) => s.hit);
  contacts.show(hits.length).forEach((mesh, i) => {
    const s = hits[i];
    if (!s) return;
    const r = LOOK.contact.radius * wobble * (0.5 + s.width / 16);
    mesh.position.set(s.x, s.y1, -0.5);
    mesh.scaling.set(r, r, 1);
  });
}

/** A pulsing glow where the beam leaves the ship, bigger for wider (higher level) beams. */
function placeMuzzle(muzzle: Pool, beam: readonly BeamSegment[], time: number): void {
  const [first] = beam;
  const [mesh] = muzzle.show(first ? 1 : 0);
  if (!first || !mesh) return;
  const look = LOOK.muzzle;
  const pulse = 1 + look.pulse * flicker(time, 1, look.pulseHz);
  const r = look.radius * (look.baseScale + first.width / look.widthDivisor) * pulse;
  mesh.position.set(first.x, first.y0, -0.6);
  mesh.scaling.set(r, r * look.stretch, 1);
}

function placeSparks(sparks: Pool, spots: readonly ParticleSpot[]): void {
  sparks.show(spots.length).forEach((mesh, i) => {
    const p = spots[i];
    if (!p) return;
    mesh.position.set(p.x, p.y, -0.2);
    mesh.scaling.set(p.radius, p.radius * 2, 1);
  });
}

/**
 * P03-R02: a bright blue beam per segment, thinner at each lower level, a glow at its base and
 * where it touches a target, and particles flowing up along it.
 */
export function createLaserRenderer(scene: Scene): ShotRenderer {
  const bars = glowPool(scene, 'laser', buildGlowBar(LOOK.colors));
  const contacts = glowPool(
    scene,
    'laser-contact',
    buildGlowDisc(DISC_SEGMENTS, LOOK.contact.colors),
  );
  const sparks = glowPool(
    scene,
    'laser-particle',
    buildGlowDisc(DISC_SEGMENTS, LOOK.particles.colors),
  );
  const muzzle = glowPool(
    scene,
    'laser-muzzle',
    buildGlowDisc(LOOK.muzzle.segments, LOOK.muzzle.colors),
  );
  const particles = new LaserParticles(
    LOOK.particles,
    createRng(LOOK.particles.seed),
    INITIAL_LENGTH,
  );
  let time = 0;

  return {
    sync: ({ beam, dtSeconds }) => {
      time += dtSeconds;
      const wobble = 1 + LOOK.flicker * flicker(time, 0, [LOOK.flickerHz]);
      placeBars(bars.pool, beam, wobble);
      placeContacts(contacts.pool, beam, wobble);
      placeMuzzle(muzzle.pool, beam, time);
      placeSparks(sparks.pool, particles.step(beam, dtSeconds));
    },
    dispose: () => {
      for (const { pool, template } of [bars, contacts, muzzle, sparks]) {
        pool.dispose();
        template.dispose();
      }
    },
  };
}
