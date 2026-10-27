import type { AbstractEngine } from '@babylonjs/core/Engines/abstractEngine';
import { Scene } from '@babylonjs/core/scene';
import type { GameDefinition } from '../core/content/game-definition';
import type { MenuScreen } from '../core/menu/menu-screen';
import type { LoadingTask } from '../assets/loading-tasks';
import type { GameView, MenuBackdrop, ModelFactory } from '../render/game-view';
import { ShipSelectStage } from '../render/ship-select-stage';
import { applyShowcaseEnvironment } from '../render/environment/showcase-environment.visual';
import { MENU_CONFIG } from '../config/menu';

/** The 3D scenes behind the menus: the game's backdrop, and the ship select stage over it. */
export interface MenuScenes {
  readonly backdropScene: Scene;
  readonly backdrop: MenuBackdrop;
  readonly shipScene: Scene;
  readonly stage: ShipSelectStage;
}

function shipModels(game: GameDefinition<GameView>): ModelFactory[] {
  return game.playerShips.ships.map(({ id }) => {
    const factory = game.view.playerShipModels[id];
    if (!factory) throw new Error(`No model for player ship "${id}"`);
    return factory;
  });
}

function environmentOptions(): Parameters<typeof applyShowcaseEnvironment>[1] {
  return { ...MENU_CONFIG.environment, glow: MENU_CONFIG.glow };
}

/**
 * Splits the creation of the menu scenes into loading steps (P01-R02): build the backdrop,
 * build the ships, then compile each scene's shaders. `result()` is available once every
 * task has run. `environment` (image-based lighting, glow) needs a real WebGL engine.
 */
export function prepareMenuScenes(
  engine: AbstractEngine,
  game: GameDefinition<GameView>,
  environment: boolean,
): { tasks: LoadingTask[]; result: () => MenuScenes } {
  let backdropScene: Scene | undefined;
  let backdrop: MenuBackdrop | undefined;
  let shipScene: Scene | undefined;
  let stage: ShipSelectStage | undefined;
  const tasks: LoadingTask[] = [
    () => {
      backdropScene = new Scene(engine);
      backdropScene.metadata = { gameId: game.id };
      backdrop = game.view.menuBackdrop(backdropScene);
      if (!environment) return;
      const glow = applyShowcaseEnvironment(backdropScene, environmentOptions());
      for (const mesh of backdrop.glowExcludedMeshes) glow.addExcludedMesh(mesh);
    },
    () => {
      shipScene = new Scene(engine);
      // Drawn over the backdrop: keep its colours, clear only depth.
      shipScene.autoClear = false;
      stage = new ShipSelectStage(shipScene, shipModels(game), MENU_CONFIG.shipSelect);
      if (environment) applyShowcaseEnvironment(shipScene, environmentOptions());
    },
    () => backdropScene?.whenReadyAsync(),
    () => shipScene?.whenReadyAsync(),
    // P13-R02: each ship highlighted once (the spot light lights other meshes), so moving the
    // highlight on the ship select screen does not compile shaders.
    async () => {
      if (!shipScene || !stage) return;
      const ships = game.playerShips.ships.length;
      for (let i = ships - 1; i >= 0; i--) {
        stage.select(i);
        await shipScene.whenReadyAsync();
      }
    },
  ];
  return {
    tasks,
    result: () => {
      if (!backdropScene || !backdrop || !shipScene || !stage) {
        throw new Error('The menu scenes are not loaded yet');
      }
      return { backdropScene, backdrop, shipScene, stage };
    },
  };
}

/** Renders the scenes of `screen`: the backdrop, plus the ships on the ship select screen. */
export function renderMenuScenes(scenes: MenuScenes, screen: MenuScreen): void {
  if (screen === 'loading') return;
  scenes.backdropScene.render();
  if (screen === 'ship-select') scenes.shipScene.render();
}
