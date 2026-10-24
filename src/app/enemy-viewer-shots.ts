import type { GameDefinition } from '../core/content/game-definition';
import type { EnemyWorld, EnemyBlast } from '../core/systems/enemy-world';
import type { ShotImpact, ShotWorld } from '../core/systems/shot-world';
import type { BlastRenderer, EnemyShotRenderer, GameView, ShotRenderer } from '../render/game-view';
import type { NodeAdopter } from '../render/node-adopter';

/** What {@link EnemyViewerShots.sync} draws. */
export interface ShotsToDraw {
  readonly enemies: EnemyWorld;
  readonly shots: ShotWorld;
  readonly blasts: readonly EnemyBlast[];
  readonly impacts: readonly ShotImpact[];
  readonly dt: number;
}

/**
 * The shots and explosions of the enemies page, all drawn on the playfield layer: the player's
 * shots (one renderer per weapon, as on `player_shots/`, hits included), the enemies' shots and
 * the explosions (GD-62).
 */
export class EnemyViewerShots {
  readonly #player: Map<string, ShotRenderer>;
  readonly #enemy: EnemyShotRenderer;
  readonly #blasts: BlastRenderer;

  constructor(
    game: GameDefinition<GameView>,
    private readonly playfield: NodeAdopter,
  ) {
    const scene = playfield.root.getScene();
    [this.#player, this.#enemy, this.#blasts] = playfield.run(() => {
      const player = new Map(
        game.playerWeapons.map((weapon) => {
          const factory = game.view.playerShotRenderers[weapon.id];
          if (!factory) throw new Error(`No shot renderer for weapon "${weapon.id}"`);
          return [weapon.id, factory(scene)] as const;
        }),
      );
      return [player, game.view.enemies.shots(scene), game.view.enemies.blasts(scene)] as const;
    });
  }

  sync({ enemies, shots, blasts, impacts, dt }: ShotsToDraw): void {
    this.playfield.run(() => {
      const flying = shots.projectiles.filter((p) => p.alive);
      for (const [id, renderer] of this.#player) {
        renderer.sync({
          projectiles: flying.filter((p) => p.weapon.id === id),
          beam: shots.weapon.id === id ? shots.beam : [],
          impacts: impacts.filter((impact) => impact.weaponId === id),
          dtSeconds: dt,
        });
      }
      const s = enemies.shots;
      this.#enemy.sync({
        bullets: s.bullets.filter((b) => b.alive),
        missiles: s.missiles.filter((m) => m.alive),
        lasers: s.lasers,
        dtSeconds: dt,
      });
      this.#blasts.sync(blasts, dt);
    });
  }

  dispose(): void {
    for (const renderer of this.#player.values()) renderer.dispose();
    this.#enemy.dispose();
    this.#blasts.dispose();
  }
}
