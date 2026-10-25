// @vitest-environment happy-dom
import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { startBossViewer, type RunningBossViewer } from '../../../src/app/start-boss-viewer';
import { BOSS_VIEWER_CONFIG as CFG } from '../../../src/config/boss-viewer';
import { SAMPLE_GAME } from '../../fixtures/sample-game';
import { SampleBoss, SAMPLE_BOSS_STATS } from '../../fixtures/sample-boss';

/** The sample game with two bosses: Big Cube, of level a, and Small Cube, of no level. */
const GAME = {
  ...SAMPLE_GAME,
  bossKinds: [
    ...SAMPLE_GAME.bossKinds,
    {
      id: 'small-cube',
      name: 'Small Cube',
      spawn: (area: ConstructorParameters<typeof SampleBoss>[0]) =>
        new SampleBoss(area, { ...SAMPLE_BOSS_STATS, name: 'Small Cube' }),
    },
  ],
  gameLevels: SAMPLE_GAME.gameLevels.map((level) =>
    level.id === 'a'
      ? { ...level, bosses: [{ kind: 'big-cube', rank: 'final', at: 400 }] as const }
      : level,
  ),
};

function start(keyboardTarget?: EventTarget): RunningBossViewer {
  return startBossViewer(new NullEngine(), GAME, {
    environment: false,
    doc: document,
    panelParent: document.body,
    statsParent: document.body,
    renderLoop: false,
    ...(keyboardTarget ? { keyboardTarget } : {}),
  });
}

const text = (selector: string): string => document.querySelector(selector)?.textContent ?? '';

function frames(viewer: RunningBossViewer, seconds: number): void {
  for (let t = 0; t < seconds; t += 1 / 60) viewer.frame(1 / 60);
}

describe('startBossViewer', () => {
  let viewer: RunningBossViewer | undefined;
  afterEach(() => {
    viewer?.dispose();
    viewer = undefined;
    document.body.replaceChildren();
  });

  it('P07-R09: lists the bosses and brings the first one in, with the debug tile', () => {
    viewer = start();
    expect(text('.enemy-title')).toBe('Bosses');
    const names = [...document.querySelectorAll('.enemy-kind button')].map((b) => b.textContent);
    expect(names).toEqual(['Big Cube', 'Small Cube']);
    expect(viewer.state().boss).toMatchObject({ name: 'Big Cube', state: 'entering', stage: 0 });
    expect(document.querySelector('.stats-tile')).not.toBeNull();
  });

  it('P07-R09: the ground eases to the boss speed; K destroys a part and the stage shows', () => {
    viewer = start();
    frames(viewer, 2);
    expect(viewer.state().groundSpeed).toBeCloseTo(0.5);
    viewer.key('k', 'KeyK', true);
    viewer.key('k', 'KeyK', false);
    frames(viewer, 0.1);
    expect(viewer.state().boss).toMatchObject({ stage: 1, partsLeft: 1 });
    expect(text('.enemy-stage')).toMatch(/^Big Cube: stage 1 \/ 2/);
  });

  it('P07-R09: a destroyed boss comes again; the player cannot die', () => {
    viewer = start();
    frames(viewer, 2);
    for (let i = 0; i < 3; i++) {
      viewer.key('k', 'KeyK', true);
      frames(viewer, 0.1);
    }
    frames(viewer, 1.2);
    expect(viewer.state().kills).toBe(1);
    expect(viewer.state().boss).toBeNull();
    frames(viewer, CFG.respawnDelay + 0.1);
    expect(viewer.state().boss?.state).toBe('entering');
  });

  it('P07-R09: picking another boss (of another level) brings it in; N / B switch', () => {
    viewer = start();
    viewer.key('n', 'KeyN', true);
    expect(viewer.state().boss?.name).toBe('Small Cube');
    viewer.key('b', 'KeyB', true);
    expect(viewer.state().boss?.name).toBe('Big Cube');
  });

  it('P07-R09: the model and wireframe views show the boss alone; ← / → switch it', () => {
    viewer = start();
    viewer.key('m', 'KeyM', true);
    expect(viewer.activeScene).toBe(viewer.closeUp.scene);
    expect(viewer.state().boss).toBeNull();
    viewer.key('ArrowRight', 'ArrowRight', true);
    expect(viewer.panel.selection.kind).toBe(1);
    viewer.key('v', 'KeyV', true);
    expect(viewer.closeUp.wireframe).toBe(true);
    // A circle for the core and for each part.
    const circles = viewer.closeUp.scene.meshes.filter((m) =>
      m.name.startsWith('close-up-hitbox-'),
    );
    expect(circles).toHaveLength(3);
    frames(viewer, 0.2);
  });

  it('listens to the keyboard target until disposed', () => {
    const target = new EventTarget();
    viewer = start(target);
    target.dispatchEvent(new KeyboardEvent('keydown', { key: 'n', code: 'KeyN' }));
    expect(viewer.panel.selection.kind).toBe(1);
    target.dispatchEvent(new Event('blur'));
    viewer.dispose();
    viewer = undefined;
    document.body.replaceChildren();
  });
});
