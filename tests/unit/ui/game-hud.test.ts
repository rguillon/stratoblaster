// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { GameHud, type HudFrame } from '../../../src/ui/game-hud';

const FRAME: HudFrame = {
  health: 100,
  maxHealth: 100,
  lives: 3,
  weapon: 'Bullet',
  weaponLevel: 1,
  weaponLevels: 5,
  progress: 0.25,
  score: 0,
  highScore: 12_340,
  bombs: 3,
};

const pad = (score: number): string => String(score).padStart(7, '0');

function setup(onBomb?: () => void) {
  const parent = document.createElement('div');
  const hud = new GameHud(document, parent, {
    ship: 'Heavy',
    texts: {
      health: 'HP',
      weapon: (name, level, levels) => `${name} · Lv ${String(level)}/${String(levels)}`,
      bombs: (count) => `Bombs ${String(count)}`,
      lives: (count) => `Lives ${String(count)}`,
      score: pad,
      highScore: (score) => `HI ${pad(score)}`,
      bomb: (bombs) => `Bomb ${String(bombs)}`,
    },
    ...(onBomb ? { onBomb } : {}),
  });
  const $ = (selector: string) => parent.querySelector<HTMLElement>(selector);
  return { parent, hud, $ };
}

describe('GameHud', () => {
  it('phase 6 review: shows the ship and its health, the weapon level and the progress', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    expect($('.hud-ship')?.textContent).toBe('Heavy');
    expect($('.hud-health-text')?.textContent).toBe('HP 100 / 100');
    expect($('.hud-bar-fill')?.style.width).toBe('100%');
    expect($('.hud-weapon')?.textContent).toBe('Bullet · Lv 1/5');
    expect($('.hud-progress-fill')?.style.width).toBe('25%');
    expect($('.game-hud')?.getAttribute('aria-hidden')).toBe('true');
  });

  it('reviewer, 2026-10-28: one bar at the bottom, without the enemies destroyed', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    const panel = $('.hud-panel');
    for (const part of ['.hud-progress', '.hud-health', '.hud-score', '.hud-weapon']) {
      expect(panel?.querySelector(part), part).not.toBeNull();
    }
    expect($('.hud-destroyed')).toBeNull();
    expect($('.game-hud')?.textContent).not.toMatch(/destroyed/i);
  });

  it('updates what changed, keeps the bars within 0..100 %', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    hud.update({ ...FRAME, health: 39.2, weaponLevel: 3, progress: 1.4 });
    expect($('.hud-health-text')?.textContent).toBe('HP 40 / 100');
    expect($('.hud-bar-fill')?.style.width).toBe('39.2%');
    expect($('.hud-weapon')?.textContent).toBe('Bullet · Lv 3/5');
    hud.update({ ...FRAME, weapon: 'Laser', weaponLevels: 4 });
    expect($('.hud-weapon')?.textContent).toBe('Laser · Lv 1/4');
    hud.update({ ...FRAME, health: 39.2, weaponLevel: 3, progress: 1.4 });
    expect($('.hud-progress-fill')?.style.width).toBe('100%');
    const text = $('.hud-weapon')?.firstChild;
    hud.update({ ...FRAME, health: 39.2, weaponLevel: 3, progress: 1.4 });
    expect($('.hud-weapon')?.firstChild).toBe(text);
  });

  it('phase 6 review: shows the lives left, and the health bar turns red when low (GD-20)', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    expect($('.hud-lives')?.textContent).toBe('Lives 3');
    expect($('.hud-bar-fill')?.classList.contains('low')).toBe(false);
    hud.update({ ...FRAME, health: 20, lives: 1 });
    expect($('.hud-lives')?.textContent).toBe('Lives 1');
    expect($('.hud-bar-fill')?.classList.contains('low')).toBe(true);
    expect($('.hud-health-text')?.textContent).toBe('HP 20 / 100');
  });

  it('is removed on dispose', () => {
    const { hud, parent } = setup();
    hud.dispose();
    expect(parent.children).toHaveLength(0);
  });

  it('P11-R02: shows the score, zero-padded, and the high score under it', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    expect($('.hud-score-value')?.textContent).toBe('0000000');
    expect($('.hud-high-score')?.textContent).toBe('HI 0012340');
    hud.update({ ...FRAME, score: 20_000, highScore: 20_000 });
    expect($('.hud-score-value')?.textContent).toBe('0020000');
    expect($('.hud-high-score')?.textContent).toBe('HI 0020000');
  });

  it('P11-R05: shows the bombs left, as a count (reviewer, 2026-10-28: they have no limit)', () => {
    const { hud, $ } = setup();
    hud.update(FRAME);
    expect($('.hud-bombs')?.textContent).toBe('Bombs 3');
    hud.update({ ...FRAME, bombs: 12 });
    expect($('.hud-bombs')?.textContent).toBe('Bombs 12');
    hud.update({ ...FRAME, bombs: undefined });
    expect($('.hud-bombs')?.textContent).toBe('');
  });

  it('P11-R06: the touch bomb button sets a bomb off and is dimmed with no bomb left', () => {
    let presses = 0;
    const { hud, $ } = setup(() => presses++);
    hud.update(FRAME);
    const button = $('.hud-bomb-button');
    expect(button?.textContent).toBe('Bomb 3');
    button?.dispatchEvent(new Event('pointerdown'));
    expect(presses).toBe(1);
    hud.update({ ...FRAME, bombs: 0 });
    expect(button?.classList.contains('empty')).toBe(true);
    expect(setup().$('.hud-bomb-button')).toBeNull();
  });
});
