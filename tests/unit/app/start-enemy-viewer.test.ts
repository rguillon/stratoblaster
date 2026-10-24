// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import type { AbstractMesh } from '@babylonjs/core/Meshes/abstractMesh';
import { startEnemyViewer, type RunningEnemyViewer } from '../../../src/app/start-enemy-viewer';
import { ENEMY_VIEWER_CONFIG as CFG } from '../../../src/config/enemy-viewer';
import { ABOVE_CLOUDS_GROUP } from '../../../src/render/scenery/scenery-stage';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { Twin, SAMPLE_BLASTS, SAMPLE_ENEMY_FRAMES } from '../../fixtures/sample-enemies';

function start(keyboardTarget?: EventTarget): RunningEnemyViewer {
  return startEnemyViewer(new NullEngine(), SAMPLE_GAME, {
    environment: false,
    doc: document,
    panelParent: document.body,
    statsParent: document.body,
    renderLoop: false,
    ...(keyboardTarget ? { keyboardTarget } : {}),
  });
}

const text = (selector: string): string => document.querySelector(selector)?.textContent ?? '';

function frames(viewer: RunningEnemyViewer, seconds: number): void {
  for (let t = 0; t < seconds; t += 1 / 60) viewer.frame(1 / 60);
}

/** Flies the player ship sideways until it is under `x`. */
function flyTo(viewer: RunningEnemyViewer, x: number): void {
  const code = viewer.player.x > x ? 'ArrowLeft' : 'ArrowRight';
  viewer.key(code, code, true);
  for (let i = 0; i < 600 && Math.abs(viewer.player.x - x) > 1; i++) viewer.frame(1 / 60);
  viewer.key(code, code, false);
}

describe('startEnemyViewer', () => {
  let viewer: RunningEnemyViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
    document.body.replaceChildren();
  });

  it('P05-R11: shows the game enemy kinds and spawns the first one at once', () => {
    viewer = start();
    const kinds = [...document.querySelectorAll('.enemy-kind button')].map((b) => b.textContent);
    expect(kinds).toEqual(['Dropper', 'Pair']);
    expect(viewer.enemies.enemies).toHaveLength(1);
    expect(text('.enemy-enemies')).toBe('Enemies: 1');
    expect(document.querySelector('.stats-tile')).not.toBeNull();
  });

  it('P05-R11: spawns the picked kind again once the group has gone', () => {
    viewer = start();
    viewer.panel.update({ fire: false });
    const [first] = viewer.enemies.enemies;
    // The Dropper flies down and off the screen.
    for (let i = 0; i < 600 && viewer.enemies.enemies.length > 0; i++) viewer.frame(1 / 60);
    expect(viewer.enemies.enemies).toHaveLength(0);
    frames(viewer, CFG.respawnDelay - 0.1);
    expect(viewer.enemies.enemies).toHaveLength(0);
    frames(viewer, 0.2);
    expect(viewer.enemies.enemies).toHaveLength(1);
    expect(viewer.enemies.enemies[0]).not.toBe(first);
  });

  it('P05-R11: picking another kind starts it over, a whole group', () => {
    viewer = start();
    viewer.panel.update({ kind: 1 });
    expect(viewer.enemies.enemies).toHaveLength(2);
    expect(viewer.enemies.enemies[0]).toBeInstanceOf(Twin);
  });

  it('P05-R11: the model view shows the enemy close up on its own dark scene, turning', () => {
    viewer = start();
    viewer.key('m', 'KeyM', true);
    expect(viewer.panel.selection.view).toBe('model');
    expect(viewer.enemies.enemies).toHaveLength(0);
    const { closeUp } = viewer;
    expect(closeUp.scene).not.toBe(viewer.scene);
    // A dark grey (phase 5 review): neutral, and lighter than the dark hulls.
    const { r, g, b } = closeUp.scene.clearColor;
    expect(Math.max(r, g, b) - Math.min(r, g, b)).toBeLessThan(0.05);
    expect(r).toBeGreaterThan(0.1);
    expect(r).toBeLessThan(0.35);
    expect(closeUp.pivot.getChildMeshes().length).toBeGreaterThan(0);
    // Close up: the camera is a few model sizes away (the sample model is 10 wide).
    expect(closeUp.camera.radius).toBeLessThan(60);
    const turn = closeUp.pivot.rotation.y;
    frames(viewer, 1);
    expect(closeUp.pivot.rotation.y).toBeGreaterThan(turn);
    expect(viewer.enemies.enemies).toHaveLength(0);
    viewer.key('m', 'KeyM', true);
    expect(viewer.enemies.enemies).toHaveLength(1);
  });

  it('P05-R11, phase 5 review: the wireframe view is the model view drawn as lines', () => {
    viewer = start();
    viewer.key('v', 'KeyV', true);
    expect(viewer.panel.selection.view).toBe('wireframe');
    expect(viewer.enemies.enemies).toHaveLength(0);
    expect(viewer.closeUp.scene.forceWireframe).toBe(true);
    viewer.key('ArrowRight', 'ArrowRight', true);
    expect(viewer.panel.selection.kind).toBe(1);
    // The hit circle, as big as the enemy's hit radius, around the model.
    const hitbox = (): AbstractMesh | undefined =>
      viewer?.closeUp.pivot.getChildMeshes().find((m) => m.name === 'close-up-hitbox');
    const circle = hitbox();
    const { radius } = new Twin(0, 0);
    const box = circle?.getBoundingInfo().boundingBox;
    expect((box?.maximum.x ?? 0) - (box?.minimum.x ?? 0)).toBeCloseTo(2 * radius, 1);
    viewer.key('m', 'KeyM', true);
    expect(viewer.closeUp.scene.forceWireframe).toBe(false);
    expect(hitbox()).toBeUndefined();
    viewer.key('v', 'KeyV', true);
    viewer.key('v', 'KeyV', true);
    expect(viewer.panel.selection.view).toBe('behaviour');
    expect(viewer.enemies.enemies.length).toBeGreaterThan(0);
  });

  it('P05-R11: in the model view, ← / → switch the enemy instead of moving the ship', () => {
    viewer = start();
    viewer.key('m', 'KeyM', true);
    const { x } = viewer.player;
    viewer.key('ArrowRight', 'ArrowRight', true);
    expect(viewer.panel.selection.kind).toBe(1);
    viewer.key('ArrowRight', 'ArrowRight', true);
    expect(viewer.panel.selection.kind).toBe(0);
    viewer.key('ArrowLeft', 'ArrowLeft', true);
    expect(viewer.panel.selection.kind).toBe(1);
    viewer.key('ArrowLeft', 'ArrowLeft', false);
    expect(viewer.panel.selection.view).toBe('model');
    frames(viewer, 0.5);
    expect(viewer.player.x).toBe(x);
  });

  it('P05-R11: the player ship flies with arrows / WASD, within what the camera shows', () => {
    viewer = start();
    const { x, y } = viewer.player;
    viewer.key('w', 'KeyW', true);
    frames(viewer, 0.5);
    viewer.key('w', 'KeyW', false);
    expect(viewer.player.y).toBeCloseTo(y + 0.5 * SAMPLE_GAME.playerShips.baseSpeedPxPerSec, -1);
    expect(viewer.player.x).toBe(x);
    viewer.key('ArrowLeft', 'ArrowLeft', true);
    frames(viewer, 20);
    expect(viewer.player.x).toBeGreaterThan(0);
    expect(viewer.shots.centerX).toBe(viewer.player.x);
    expect(viewer.shots.muzzleY).toBeGreaterThan(viewer.player.y);
  });

  it('P05-R11, GD-62: player shots destroy the enemy, score it and blow it up', () => {
    viewer = start();
    const blasts = SAMPLE_BLASTS.length;
    viewer.panel.update({ weapon: 1, level: 2 });
    flyTo(viewer, SAMPLE_GAME.screen.width / 2);
    frames(viewer, 3);
    expect(viewer.enemies.kills).toBeGreaterThan(0);
    expect(text('.enemy-kills')).not.toBe('Destroyed: 0');
    expect(text('.enemy-score')).toBe(`Score: ${String(viewer.enemies.score)}`);
    expect(SAMPLE_BLASTS.length).toBeGreaterThan(blasts);
  });

  it('P05-R11: draws the enemy shots', () => {
    viewer = start();
    viewer.panel.update({ fire: false });
    frames(viewer, 2);
    expect(SAMPLE_ENEMY_FRAMES.at(-1)?.bullets.length).toBeGreaterThan(0);
  });

  it('P05-R11: pause freezes the enemies', () => {
    viewer = start();
    viewer.key('p', 'KeyP', true);
    const y = viewer.enemies.enemies[0]?.y;
    frames(viewer, 1);
    expect(viewer.enemies.enemies[0]?.y).toBe(y);
  });

  it('P05-R11: keyboard shortcuts pick the enemy, the weapon, the level and fire', () => {
    viewer = start();
    const s = () => viewer?.panel.selection;
    viewer.key('n', 'KeyN', true);
    expect(s()?.kind).toBe(1);
    viewer.key('n', 'KeyN', true);
    expect(s()?.kind).toBe(0);
    viewer.key('b', 'KeyB', true);
    expect(s()?.kind).toBe(1);
    viewer.key('x', 'KeyX', true);
    expect(s()).toMatchObject({ weapon: 1, level: 1 });
    viewer.key('2', 'Digit2', true);
    expect(s()?.level).toBe(2);
    viewer.key('f', 'KeyF', true);
    expect(viewer.shots.firing).toBe(false);
    viewer.key('f', 'KeyF', false);
    viewer.key('z', 'KeyZ', true);
    expect(s()?.fire).toBe(false);
  });

  it('P05-R11: draws everything of the playfield above the clouds, in the playfield layer', () => {
    viewer = start();
    frames(viewer, 0.5);
    const playfield = viewer.scene.getTransformNodeByName('playfield');
    const ship = viewer.scene.getTransformNodeByName('playfield-ship');
    expect(ship?.parent).toBe(playfield);
    const shipMeshes = ship?.getChildMeshes() ?? [];
    expect(shipMeshes.length).toBeGreaterThan(0);
    expect(shipMeshes.every((m) => m.renderingGroupId === ABOVE_CLOUDS_GROUP)).toBe(true);
  });

  it('listens to the keyboard target until disposed', () => {
    const target = new EventTarget();
    viewer = start(target);
    target.dispatchEvent(new KeyboardEvent('keydown', { key: 'n', code: 'KeyN' }));
    expect(viewer.panel.selection.kind).toBe(1);
    target.dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowUp', code: 'ArrowUp' }));
    target.dispatchEvent(new Event('blur'));
    const y = viewer.player.y;
    frames(viewer, 0.2);
    expect(viewer.player.y).toBe(y);
    viewer.dispose();
    viewer = undefined;
    expect(document.querySelector('.enemy-panel')).toBeNull();
  });
});
