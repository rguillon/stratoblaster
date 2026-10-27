import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import type { EnemyLaser } from '../../../core/systems/enemy-shots';
import { NodePool } from '../../../render/node-pool';
import { BOSS_LOOK } from '../../config/boss-look';
import { foldIntoFamily } from '../../../core/math/color';
import { ENEMY_LOOK, laserPalette } from '../../config/enemy-look';
import { READABILITY } from '../../config/readability';
import { flicker } from '../reactor-flame';
import { buildGlowBar, buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from '../shots/shot-meshes';

const LOOK = ENEMY_LOOK.laser;

/** The warning lines, beams and base flares of the lasers of one colour. */
interface LaserPools {
  readonly warning: NodePool<Mesh>;
  readonly beam: NodePool<Mesh>;
  readonly emitter: NodePool<Mesh>;
  readonly templates: readonly Mesh[];
}

/**
 * The colour of the lasers of `style`: a boss's neon, or the Lancer's (phase 8 review), moved
 * into the enemy shots' colour family (P14-R02).
 */
function colorOf(style: string): Rgb {
  return foldIntoFamily(BOSS_LOOK.neon[style] ?? LOOK.color, READABILITY.families.enemyShot);
}

type Rgb = readonly [number, number, number];

/** A warning line with a white core, standing out over red grounds (P10-R07). */
function contrastWarning([r, g, b]: Rgb): readonly Rgb[] {
  const t = ENEMY_LOOK.contrast.warningCore;
  return [
    [r + (1 - r) * t, g + (1 - g) * t, b + (1 - b) * t],
    [r, g, b],
    [r * 0.5, g * 0.5, b * 0.5],
    [0, 0, 0],
  ];
}

function lasersOf(scene: Scene, style: string, contrast: boolean): LaserPools {
  const base = laserPalette(colorOf(style));
  const palette = contrast ? { ...base, warning: contrastWarning(colorOf(style)) } : base;
  const name = (part: string): string => `enemy-laser-${part}-${style}`;
  // Drawn over the models: a beam leaves its emitter's lens, not from under the hull around it.
  const templates = [
    additiveTemplate(name('warning'), buildGlowBar(palette.warning), scene, true),
    additiveTemplate(name('beam'), buildGlowBar(palette.beam), scene, true),
    additiveTemplate(
      name('emitter'),
      buildGlowDisc(LOOK.flare.segments, palette.emitter),
      scene,
      true,
    ),
  ] as const;
  const pool = (template: Mesh): NodePool<Mesh> =>
    new NodePool((i) => template.clone(`${template.name}-${String(i)}`));
  return {
    warning: pool(templates[0]),
    beam: pool(templates[1]),
    emitter: pool(templates[2]),
    templates,
  };
}

function syncWarnings(
  pool: NodePool<Mesh>,
  warnings: readonly EnemyLaser[],
  [time, width]: readonly [number, number],
): void {
  // The warning line blinks: drawn at full or half width.
  const blink = Math.sin(2 * Math.PI * LOOK.warning.blinkHz * time) > 0 ? 1 : 0.5;
  pool.show(warnings.length).forEach((mesh, i) => {
    const l = warnings[i];
    if (!l) return;
    mesh.position.set(l.x, l.y, -0.8);
    mesh.rotation.z = -l.heading;
    mesh.scaling.set(width * blink, l.length, 1);
  });
}

function syncBeams(pools: LaserPools, beams: readonly EnemyLaser[], time: number): void {
  const wobble = 1 + LOOK.beam.flicker * flicker(time, 0, [LOOK.beam.flickerHz]);
  pools.beam.show(beams.length).forEach((mesh, i) => {
    const l = beams[i];
    if (!l) return;
    mesh.position.set(l.x, l.y, -0.9);
    mesh.rotation.z = -l.heading;
    mesh.scaling.set(l.spec.width * LOOK.beam.glowWidth * wobble, l.length, 1);
  });
  // A pulsing flare where the beam leaves, as the player's laser's: bigger for wider beams,
  // stretched along the beam.
  const flare = LOOK.flare;
  const pulse = 1 + flare.pulse * flicker(time, 1, flare.pulseHz);
  pools.emitter.show(beams.length).forEach((mesh, i) => {
    const l = beams[i];
    if (!l) return;
    const r = flare.radius * (flare.baseScale + l.spec.width / flare.widthDivisor) * pulse;
    mesh.position.set(l.x, l.y, -1.2);
    mesh.rotation.z = -l.heading;
    mesh.scaling.set(r, r * flare.stretch, 1);
  });
}

/**
 * The enemies' lasers (GD-43): a blinking warning line, then a beam with a flare at its base,
 * in the colour of their style (phase 8 review: each boss's lasers in its neon colour).
 */
export class EnemyLasers {
  /** The pools of each style drawn so far. */
  readonly #styles = new Map<string, LaserPools>();

  /** `contrast`: warning lines with a white core, wider (P10-R07). */
  constructor(
    private readonly scene: Scene,
    private readonly contrast = false,
  ) {}

  sync(lasers: readonly EnemyLaser[], time: number): void {
    for (const style of new Set(lasers.map((l) => l.spec.style))) {
      if (!this.#styles.has(style))
        this.#styles.set(style, lasersOf(this.scene, style, this.contrast));
    }
    const scale = this.contrast ? ENEMY_LOOK.contrast.warningWidth : 1;
    for (const [style, pools] of this.#styles) {
      const own = lasers.filter((l) => l.spec.style === style);
      syncWarnings(
        pools.warning,
        own.filter((l) => l.phase === 'warning'),
        [time, LOOK.warning.width * scale],
      );
      syncBeams(
        pools,
        own.filter((l) => l.phase === 'firing'),
        time,
      );
    }
  }

  dispose(): void {
    for (const pools of this.#styles.values()) {
      for (const pool of [pools.warning, pools.beam, pools.emitter]) pool.dispose();
      for (const template of pools.templates) template.dispose();
    }
    this.#styles.clear();
  }
}
