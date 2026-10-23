import { afterEach, describe, expect, it, vi } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import type { Scene } from '@babylonjs/core/scene';
import { prepareMenuScenes, renderMenuScenes, type MenuScenes } from '../../../src/app/menu-scenes';
import { SAMPLE_GAME } from '../../fixtures/sample-game';

async function load(): Promise<MenuScenes> {
  const prepared = prepareMenuScenes(new NullEngine(), SAMPLE_GAME, false);
  expect(() => prepared.result()).toThrow(/not loaded/);
  for (const task of prepared.tasks) await task();
  return prepared.result();
}

describe('menu scenes', () => {
  let scenes: MenuScenes | undefined;
  afterEach(() => {
    scenes?.backdropScene.dispose();
    scenes?.shipScene.dispose();
    scenes = undefined;
  });

  it('P01-R02: are built in several loading steps', () => {
    const prepared = prepareMenuScenes(new NullEngine(), SAMPLE_GAME, false);
    expect(prepared.tasks).toHaveLength(4);
  });

  it('P01-R06: put every player ship on the ship select stage, drawn over the backdrop', async () => {
    scenes = await load();
    expect(scenes.stage.showcase.pivots).toHaveLength(2);
    expect(scenes.shipScene.autoClear).toBe(false);
  });

  it('render the backdrop, plus the ships on ship-select only', async () => {
    scenes = await load();
    const spy = (scene: Scene) => vi.spyOn(scene, 'render').mockImplementation(() => undefined);
    const backdrop = spy(scenes.backdropScene);
    const ships = spy(scenes.shipScene);
    renderMenuScenes(scenes, 'loading');
    expect(backdrop).not.toHaveBeenCalled();
    renderMenuScenes(scenes, 'title');
    expect(backdrop).toHaveBeenCalledTimes(1);
    expect(ships).not.toHaveBeenCalled();
    renderMenuScenes(scenes, 'ship-select');
    expect(backdrop).toHaveBeenCalledTimes(2);
    expect(ships).toHaveBeenCalledTimes(1);
  });

  it('fail clearly when a ship has no model', async () => {
    const game = { ...SAMPLE_GAME, view: { ...SAMPLE_GAME.view, playerShipModels: {} } };
    const prepared = prepareMenuScenes(new NullEngine(), game, false);
    const [buildBackdrop, buildShips] = prepared.tasks;
    await buildBackdrop?.();
    await expect(async () => buildShips?.()).rejects.toThrow(/no model for player ship "cube"/i);
  });
});
