import { element, type MenuDocument } from './screens/elements';

/** Texts of the in-game HUD, provided by the game. */
export interface HudTexts {
  /** Label of the health bar. */
  readonly health: string;
  /** The weapon and its level, e.g. `Bullet · Lv 1/5`. */
  readonly weapon: (name: string, level: number, levels: number) => string;
  /** How many enemies were destroyed so far. */
  readonly destroyed: (count: number) => string;
  /** The lives left (GD-20). */
  readonly lives: (count: number) => string;
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
  readonly destroyed: number;
}

/** The fixed parts of a HUD: the ship and the texts. */
export interface HudSetup {
  readonly ship: string;
  readonly texts: HudTexts;
}

/** Under this share of its health the bar turns red. */
const LOW_HEALTH = 0.3;

const percent = (share: number): string =>
  `${String(Math.round(Math.min(1, Math.max(0, share)) * 1000) / 10)}%`;

/**
 * The in-game HUD (phase 6 review): the ship, its lives and health bar (red when low), the
 * weapon and its level, how far the level has gone, and the enemies destroyed. Laid out at the logical resolution over the
 * playfield; it never takes clicks or taps. Text and bars change only when their value does.
 */
export class GameHud {
  readonly root: HTMLElement;
  readonly #healthBar: HTMLElement;
  readonly #healthText: HTMLElement;
  readonly #lives: HTMLElement;
  readonly #weapon: HTMLElement;
  readonly #progressBar: HTMLElement;
  readonly #destroyed: HTMLElement;
  #shown = '';

  constructor(
    doc: MenuDocument,
    parent: HTMLElement,
    private readonly setup: HudSetup,
  ) {
    this.root = element(doc, 'div', 'game-hud');
    this.root.setAttribute('aria-hidden', 'true');
    const health = element(doc, 'div', 'hud-health');
    const bar = element(doc, 'div', 'hud-bar');
    this.#healthBar = element(doc, 'div', 'hud-bar-fill');
    this.#healthText = element(doc, 'div', 'hud-health-text');
    bar.append(this.#healthBar);
    this.#lives = element(doc, 'div', 'hud-lives');
    const name = element(doc, 'div', 'hud-name');
    name.append(element(doc, 'div', 'hud-ship', setup.ship), this.#lives);
    health.append(name, bar, this.#healthText);
    this.#weapon = element(doc, 'div', 'hud-weapon');
    const progress = element(doc, 'div', 'hud-progress');
    this.#progressBar = element(doc, 'div', 'hud-progress-fill');
    progress.append(this.#progressBar);
    this.#destroyed = element(doc, 'div', 'hud-destroyed');
    this.root.append(health, this.#weapon, progress, this.#destroyed);
    parent.append(this.root);
  }

  /** Shows `frame`, touching the page only when something visible changed. */
  update(frame: HudFrame): void {
    const { texts } = this.setup;
    const health = `${texts.health} ${String(Math.ceil(frame.health))} / ${String(frame.maxHealth)}`;
    const shown = [
      health,
      percent(frame.health / frame.maxHealth),
      texts.weapon(frame.weapon, frame.weaponLevel, frame.weaponLevels),
      percent(frame.progress),
      texts.destroyed(frame.destroyed),
      texts.lives(frame.lives),
      frame.health < LOW_HEALTH * frame.maxHealth ? 'low' : '',
    ];
    const key = shown.join('|');
    if (key === this.#shown) return;
    this.#shown = key;
    const [text = '', healthWidth = '', weaponText = '', progressWidth = '', destroyed = ''] =
      shown;
    this.#lives.textContent = shown[5] ?? '';
    this.#healthBar.classList.toggle('low', shown[6] === 'low');
    this.#healthText.textContent = text;
    this.#healthBar.style.width = healthWidth;
    this.#weapon.textContent = weaponText;
    this.#progressBar.style.width = progressWidth;
    this.#destroyed.textContent = destroyed;
  }

  dispose(): void {
    this.root.remove();
  }
}
