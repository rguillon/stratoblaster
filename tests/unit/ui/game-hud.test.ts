// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { GameHud, type HudFrame } from '../../../src/ui/game-hud';

const FRAME: HudFrame = {
  health: 100,
  maxHealth: 100,
  weaponLevel: 1,
  progress: 0.25,
  destroyed: 3,
};

function setup() {
  const parent = document.createElement('div');
  const hud = new GameHud(document, parent, {
    ship: 'Heavy',
    weapon: 'Bullet',
    weaponLevels: 5,
    texts: {
      health: 'HP',
      weapon: (name, level, levels) => `${name} · Lv ${String(level)}/${String(levels)}`,
      destroyed: (count) => `Destroyed: ${String(count)}`,
    },
  });
  const $ = (selector: string) => parent.querySelector<HTMLElement>(selector);
  return { parent, hud, $ };
}

describe('GameHud', () => {
  it('phase 6 review: shows the ship and its health, the weapon level, the progress and the kills', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    expect($('.hud-ship')?.textContent).toBe('Heavy');
    expect($('.hud-health-text')?.textContent).toBe('HP 100 / 100');
    expect($('.hud-bar-fill')?.style.width).toBe('100%');
    expect($('.hud-weapon')?.textContent).toBe('Bullet · Lv 1/5');
    expect($('.hud-progress-fill')?.style.width).toBe('25%');
    expect($('.hud-destroyed')?.textContent).toBe('Destroyed: 3');
    expect($('.game-hud')?.getAttribute('aria-hidden')).toBe('true');
  });

  it('updates what changed, keeps the bars within 0..100 %', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    hud.update({ ...FRAME, health: 39.2, weaponLevel: 3, progress: 1.4, destroyed: 4 });
    expect($('.hud-health-text')?.textContent).toBe('HP 40 / 100');
    expect($('.hud-bar-fill')?.style.width).toBe('39.2%');
    expect($('.hud-weapon')?.textContent).toBe('Bullet · Lv 3/5');
    expect($('.hud-progress-fill')?.style.width).toBe('100%');
    const text = $('.hud-destroyed');
    hud.update({ ...FRAME, health: 39.2, weaponLevel: 3, progress: 1.4, destroyed: 4 });
    expect($('.hud-destroyed')).toBe(text);
  });

  it('is removed on dispose', () => {
    const { hud, parent } = setup();
    hud.dispose();
    expect(parent.children).toHaveLength(0);
  });
});
