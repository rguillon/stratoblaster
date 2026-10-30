import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import type { GameDefinition } from '../core/content/game-definition';
import type { GameLevel } from '../core/content/game-level';
import type { Boss } from '../core/entities/boss';
import type { WeaponDefinition } from '../core/entities/weapon';
import type { Random } from '../core/math/rng';
import { withRunout, type SceneryLevel } from '../core/scenery/scenery-level';
import type { BossKindDefinition } from '../core/systems/boss-fights';
import { EnemyWorld } from '../core/systems/enemy-world';
import { ShotWorld } from '../core/systems/shot-world';
import { EnemyLayer } from '../render/enemy-layer';
import type { GameView } from '../render/game-view';
import { playfieldEye, visibleHalfWidth } from '../render/scenery/playfield-framing';
import { BOSS_VIEWER_CONFIG as CFG } from '../config/boss-viewer';
import type { BossViewerState } from '../debug/boss-viewer-test-api';
import type { HitCircle } from './enemy-close-up';
import { EnemyViewerShots } from './enemy-viewer-shots';
import { buildLevelScene, type LevelScene } from './level-scene';
import { PlayfieldShip } from './shot-viewer-scene';

/** The level a boss belongs to (P07-R09: it is fought over that level's scenery). */
export function levelOfBoss(
  game: GameDefinition<GameView>,
  kind: BossKindDefinition,
): GameLevel | undefined {
  return game.gameLevels.find((level) => level.bosses?.some((b) => b.kind === kind.id));
}

/**
 * Headings of the boss buttons (P08-R12): a world's bosses come after the ones before, under
 * `World N`, from the level each boss is fought in (its id's first part).
 */
export function bossGroups(game: GameDefinition<GameView>): { label: string; from: number }[] {
  const groups: { label: string; from: number }[] = [];
  game.bossKinds.forEach((kind, i) => {
    const world = levelOfBoss(game, kind)?.id.split('-')[0];
    const label = world === undefined ? 'Other' : `World ${world}`;
    if (groups.at(-1)?.label !== label) groups.push({ label, from: i });
  });
  return groups;
}

/** The scenery a boss is fought over: its level's (and its extra ground), or the first level's. */
function sceneryOf(game: GameDefinition<GameView>, level: GameLevel | undefined): SceneryLevel {
  if (level) return withRunout(level.scenery, level.runout ?? 0);
  const first = game.gameLevels[0]?.scenery;
  if (!first) throw new Error('The game has no level');
  return first;
}

/**
 * What the `bosses/` page shows of one level (P07-R09): its scenery under the playfield camera,
 * the enemies (the boss, and what it launches) and the player's shots, all drawn on the
 * playfield layer, and the player ship. Rebuilt when a boss of another level is picked.
 */
export class BossViewerStage {
  readonly view: LevelScene;
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly ship: PlayfieldShip;
  readonly layer: EnemyLayer;
  readonly drawn: EnemyViewerShots;
  /** Where the ship can reach at the bottom of the screen: bosses keep their parts within it. */
  readonly reach: readonly [number, number];
  /** Shots leave this far above the ship's centre. */
  readonly muzzle: number;

  constructor(
    engine: AbstractEngine,
    readonly game: GameDefinition<GameView>,
    readonly level: GameLevel | undefined,
    options: {
      readonly environment: boolean;
      readonly random: Random;
      readonly weapon: WeaponDefinition;
    },
  ) {
    this.view = buildLevelScene(engine, game, {
      level: sceneryOf(game, level),
      environment: options.environment,
      glow: game.view.enemies.glow,
      environmentCubeSize: CFG.environmentCubeSize,
      stage: CFG.stage,
    });
    const { width, height } = game.screen;
    const area = { width, height, cullMargin: CFG.cullMargin };
    const difficulty = level?.difficulty ?? { bulletSpeed: 1, fireRate: 1 };
    this.enemies = new EnemyWorld(
      {
        ...area,
        maxEnemyAge: CFG.maxEnemyAge,
        eye: playfieldEye(game.screen, this.view.stage.framing),
      },
      options.random,
      difficulty,
    );
    this.shots = new ShotWorld(area, options.weapon);
    this.shots.targets = this.enemies.targets;
    const pf = this.view.playfield;
    this.layer = pf.run(() => new EnemyLayer(this.view.scene, game.view.enemies.models));
    this.drawn = new EnemyViewerShots(game, pf, this.view.look.shotStyle);
    const first = game.playerShips.ships[0];
    const model = first && game.view.playerShipModels[first.id];
    let nose = 0;
    this.ship = pf.run(() => {
      const ship = new PlayfieldShip(this.view.scene, game.view.playerShipScale, 0, 0);
      if (model) nose = ship.show(model);
      return ship;
    });
    this.muzzle = Math.max(0, nose - CFG.muzzleInset);
    const half = this.halfWidthAt(CFG.shipMargin.bottom);
    this.reach = [width / 2 - half, width / 2 + half];
  }

  /** Half the width the ship may fly in at height `y` (inside what the camera shows). */
  halfWidthAt(y: number): number {
    const { width, height } = this.game.screen;
    return visibleHalfWidth(this.view.stage.framing, width / height, y) - CFG.shipMargin.side;
  }

  /** A new boss of `kind`, coming in from the top. */
  spawn(kind: BossKindDefinition, random: Random): Boss {
    const { width, height } = this.game.screen;
    const boss = kind.spawn({ width, height, random, topRange: this.reach });
    this.enemies.add(boss);
    return boss;
  }

  dispose(): void {
    this.layer.dispose();
    this.drawn.dispose();
    this.view.scene.dispose();
  }
}

export type { BossViewerState } from '../debug/boss-viewer-test-api';

/** The hit circles of a boss for the wireframe view: core, shielding parts, other parts. */
export function circlesOf(boss: Boss): HitCircle[] {
  const { circles } = CFG;
  return [
    { x: 0, y: 0, radius: boss.core.radius, color: circles.core },
    ...boss.parts.map((part) => ({
      x: part.spec.x,
      y: part.spec.y,
      radius: part.radius,
      color: part.shieldsCore ? circles.shield : circles.part,
    })),
  ];
}

/** What the bosses page reports (its e2e test API, the readout). */
export function bossViewerState(
  stage: BossViewerStage,
  shown: Boss | undefined,
  player: { readonly x: number; readonly y: number },
): BossViewerState {
  const boss = shown && !shown.gone ? shown : undefined;
  const { enemies, view } = stage;
  const alive = (list: readonly { alive: boolean }[]): number => list.filter((s) => s.alive).length;
  return {
    boss: boss
      ? {
          id: boss.model,
          name: boss.name,
          state: boss.state,
          stage: boss.stage,
          parts: boss.parts.length,
          partsLeft: boss.parts.filter((p) => !p.destroyed).length,
          health: boss.remainingHealth,
          fullHealth: boss.fullHealth,
        }
      : null,
    kills: enemies.kills,
    bullets: alive(enemies.shots.bullets),
    missiles: alive(enemies.shots.missiles),
    lasers: enemies.shots.lasers.length,
    groundSpeed: view.track.speedFactor,
    player: { ...player },
  };
}
