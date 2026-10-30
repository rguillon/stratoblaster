import { BossBar, type BossBarFrame } from './boss-bar';
import { element, type MenuDocument } from './screens/elements';

/** Texts of the in-game HUD, provided by the game. */
export interface HudTexts {
  /** Label of the health bar. */
  readonly health: string;
  /** The weapon and its level, e.g. `Bullet · Lv 1/5`. */
  readonly weapon: (name: string, level: number, levels: number) => string;
  /** The lives left (GD-20). */
  readonly lives: (count: number) => string;
  /** The bombs left (P11-R05). */
  readonly bombs: (count: number) => string;
  /** The score, and the high score line under it (P11-R02). */
  readonly score: (score: number) => string;
  readonly highScore: (score: number) => string;
  /** Label of the touch bomb button, with the bombs left (P11-R06). */
  readonly bomb: (bombs: number) => string;
}

/** What the HUD shows on one frame. */
export interface HudFrame {
  readonly health: number;
  readonly maxHealth: number;
  readonly lives: number;
  /** The weapon fired (it can be switched) and its level, out of `weaponLevels`. */
  readonly weapon: string;
  readonly weaponLevel: number;
  readonly weaponLevels: number;
  /** Share of the level flown, 0..1. */
  readonly progress: number;
  /** The score, and the best of it and the saved high score (P11-R02). */
  readonly score: number;
  readonly highScore: number;
  /** The bombs left (P11-R05); no bombs shown when omitted. */
  readonly bombs?: number | undefined;
  /** The boss being fought, for its health bar (P07-R02); none when omitted. */
  readonly boss?: BossBarFrame | undefined;
}

/** The fixed parts of a HUD: the ship and the texts. */
export interface HudSetup {
  readonly ship: string;
  readonly texts: HudTexts;
  /** The touch bomb button was pressed (P11-R06). No button when omitted. */
  readonly onBomb?: () => void;
}

/** Under this share of its health the bar turns red. */
const LOW_HEALTH = 0.3;

const percent = (share: number): string =>
  `${String(Math.round(Math.min(1, Math.max(0, share)) * 1000) / 10)}%`;

/**
 * The in-game HUD (reworked at the reviewer's request, 2026-10-28): one bar along the bottom of
 * the playfield, the level's progress along its top edge; on the left the ship, its lives, bombs
 * (P11-R05) and health bar (red when low); the score and high score in the middle (P11-R02); the
 * weapon and its level on the right. While a boss is fought, its health bar (P07-R02). Laid out
 * at the logical resolution over the playfield; it takes no clicks or taps but on its touch bomb
 * button (P11-R06). Text and bars change only when their value does.
 */
export class GameHud {
  readonly root: HTMLElement;
  readonly #healthBar: HTMLElement;
  readonly #healthText: HTMLElement;
  readonly #lives: HTMLElement;
  readonly #weapon: HTMLElement;
  readonly #progressBar: HTMLElement;
  readonly #score: HTMLElement;
  readonly #highScore: HTMLElement;
  readonly #bombs: HTMLElement;
  readonly #bombButton: HTMLElement | undefined;
  readonly #boss: BossBar;
  #shown = '';
  #shownScore = '';

  constructor(
    doc: MenuDocument,
    parent: HTMLElement,
    private readonly setup: HudSetup,
  ) {
    this.root = element(doc, 'div', 'game-hud');
    this.root.setAttribute('aria-hidden', 'true');
    const panel = element(doc, 'div', 'hud-panel');
    const progress = element(doc, 'div', 'hud-progress');
    this.#progressBar = element(doc, 'div', 'hud-progress-fill');
    progress.append(this.#progressBar);
    this.#lives = element(doc, 'div', 'hud-lives');
    this.#bombs = element(doc, 'div', 'hud-bombs');
    const name = element(doc, 'div', 'hud-name');
    name.append(element(doc, 'div', 'hud-ship', setup.ship), this.#lives, this.#bombs);
    const bar = element(doc, 'div', 'hud-bar');
    this.#healthBar = element(doc, 'div', 'hud-bar-fill');
    bar.append(this.#healthBar);
    this.#healthText = element(doc, 'div', 'hud-health-text');
    const meter = element(doc, 'div', 'hud-meter');
    meter.append(bar, this.#healthText);
    const health = element(doc, 'div', 'hud-health');
    health.append(name, meter);
    const score = element(doc, 'div', 'hud-score');
    this.#score = element(doc, 'div', 'hud-score-value');
    this.#highScore = element(doc, 'div', 'hud-high-score');
    score.append(this.#score, this.#highScore);
    this.#weapon = element(doc, 'div', 'hud-weapon');
    panel.append(progress, health, score, this.#weapon);
    this.root.append(panel);
    this.#bombButton = setup.onBomb && this.#newBombButton(doc, setup.onBomb);
    this.#boss = new BossBar(doc, this.root);
    parent.append(this.root);
  }

  /** The touch bomb button (P11-R06): the only part of the HUD that takes taps. */
  #newBombButton(doc: MenuDocument, onBomb: () => void): HTMLElement {
    const button = element(doc, 'div', 'hud-bomb-button');
    button.setAttribute('role', 'button');
    button.addEventListener('pointerdown', (event) => {
      event.stopPropagation();
      onBomb();
    });
    this.root.append(button);
    return button;
  }

  /** Shows `frame`, touching the page only when something visible changed. */
  update(frame: HudFrame): void {
    this.#boss.update(frame.boss);
    this.#updateScore(frame);
    const { texts } = this.setup;
    const health = `${texts.health} ${String(Math.ceil(frame.health))} / ${String(frame.maxHealth)}`;
    const shown = [
      health,
      percent(frame.health / frame.maxHealth),
      texts.weapon(frame.weapon, frame.weaponLevel, frame.weaponLevels),
      percent(frame.progress),
      texts.lives(frame.lives),
      frame.health < LOW_HEALTH * frame.maxHealth ? 'low' : '',
    ];
    const key = shown.join('|');
    if (key === this.#shown) return;
    this.#shown = key;
    const [text = '', healthWidth = '', weaponText = '', progressWidth = '', lives = '', low] =
      shown;
    this.#lives.textContent = lives;
    this.#healthBar.classList.toggle('low', low === 'low');
    this.#healthText.textContent = text;
    this.#healthBar.style.width = healthWidth;
    this.#weapon.textContent = weaponText;
    this.#progressBar.style.width = progressWidth;
  }

  /** The score, the high score, and the bombs left, by the lives and on the touch button. */
  #updateScore({ score, highScore, bombs }: HudFrame): void {
    const key = `${String(score)}|${String(highScore)}|${String(bombs)}`;
    if (key === this.#shownScore) return;
    this.#shownScore = key;
    const { texts } = this.setup;
    this.#score.textContent = texts.score(score);
    this.#highScore.textContent = texts.highScore(Math.max(score, highScore));
    this.#bombs.textContent = bombs === undefined ? '' : texts.bombs(bombs);
    const button = this.#bombButton;
    if (!button) return;
    button.textContent = texts.bomb(bombs ?? 0);
    button.classList.toggle('empty', (bombs ?? 0) <= 0);
  }

  dispose(): void {
    this.root.remove();
  }
}
