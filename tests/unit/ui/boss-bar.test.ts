// @vitest-environment happy-dom
import { describe, expect, it } from 'vitest';
import { BossBar } from '../../../src/ui/boss-bar';
import { GameHud } from '../../../src/ui/game-hud';

const FRAME = { name: 'Reef Warden', rank: 'Mini boss', share: 0.5, notches: [0.25, 0.5] };

function setup() {
  const parent = document.createElement('div');
  const bar = new BossBar(document, parent);
  const $ = (selector: string) => parent.querySelector<HTMLElement>(selector);
  return { parent, bar, $ };
}

describe('BossBar', () => {
  it('P07-R02: hidden while no boss is fought', () => {
    const { bar, $ } = setup();
    expect(bar.root.hidden).toBe(true);
    bar.update(undefined);
    expect($('.boss-bar')?.hidden).toBe(true);
  });

  it('P07-R02: shows the boss name, its kind, the share of health left and a notch per part', () => {
    const { bar, $, parent } = setup();
    bar.update(FRAME);
    expect(bar.root.hidden).toBe(false);
    expect($('.boss-name')?.textContent).toBe('Reef Warden');
    expect($('.boss-rank')?.textContent).toBe('Mini boss');
    expect($('.boss-fill')?.style.height).toBe('50%');
    const notches = [...parent.querySelectorAll<HTMLElement>('.boss-notch')];
    expect(notches.map((n) => n.style.bottom)).toEqual(['25%', '50%']);
    bar.update({ ...FRAME, share: 0.4 });
    expect($('.boss-fill')?.style.height).toBe('40%');
    expect(parent.querySelectorAll('.boss-notch')).toHaveLength(2);
    bar.update(undefined);
    expect(bar.root.hidden).toBe(true);
  });

  it('P07-R02: the HUD shows the bar of the boss in its frame', () => {
    const parent = document.createElement('div');
    const hud = new GameHud(document, parent, {
      ship: 'Heavy',
      texts: {
        health: 'HP',
        weapon: () => 'w',
        destroyed: () => 'd',
        lives: () => 'l',
        score: () => 's',
        highScore: () => 'h',
        bomb: () => 'b',
      },
    });
    const frame = {
      health: 100,
      maxHealth: 100,
      lives: 3,
      weapon: 'Bullet',
      weaponLevel: 1,
      weaponLevels: 5,
      progress: 0.5,
      destroyed: 0,
      score: 0,
      highScore: 0,
    };
    hud.update({ ...frame, boss: FRAME });
    expect(parent.querySelector<HTMLElement>('.boss-bar')?.hidden).toBe(false);
    hud.update(frame);
    expect(parent.querySelector<HTMLElement>('.boss-bar')?.hidden).toBe(true);
  });
});
