// @vitest-environment happy-dom
import { afterEach, describe, expect, it, vi } from 'vitest';
import {
  formatTime,
  SceneryViewerPanel,
  type SceneryViewerPanelOptions,
  type SceneryViewerSettings,
} from '../../../src/ui/scenery-viewer-panel';

const INITIAL: SceneryViewerSettings = {
  paused: false,
  fastForward: false,
  sea: true,
  frame: false,
  clouds: [{ enabled: true, coverage: 30, opacity: 75 }],
};

function panel(overrides: Partial<SceneryViewerPanelOptions> = {}) {
  const calls = { change: vi.fn(), seek: vi.fn(), restart: vi.fn(), seed: vi.fn() };
  const p = new SceneryViewerPanel({
    doc: document,
    parent: document.body,
    levelName: 'Test level',
    duration: 180,
    hasSea: true,
    initial: INITIAL,
    onChange: calls.change,
    onSeek: calls.seek,
    onRestart: calls.restart,
    onNewSeed: calls.seed,
    ...overrides,
  });
  return { p, calls };
}

const click = (selector: string) => document.querySelector<HTMLElement>(selector)?.click();

describe('SceneryViewerPanel', () => {
  afterEach(() => {
    document.body.replaceChildren();
  });

  it('formats times as m:ss', () => {
    expect(formatTime(0)).toBe('0:00');
    expect(formatTime(65.7)).toBe('1:05');
    expect(formatTime(-3)).toBe('0:00');
  });

  it('P04-R06: shows the time out of the level duration, the section and the end banner', () => {
    const { p } = panel();
    p.showReadout({ time: 42, section: 'canyon', props: 12, seed: 7, ended: false });
    expect(document.querySelector('.scenery-time')?.textContent).toBe('Time: 0:42 / 3:00');
    expect(document.querySelector('.scenery-section')?.textContent).toBe('Section: canyon');
    expect(document.querySelector<HTMLInputElement>('.scenery-time-slider')?.value).toBe('42');
    expect(document.querySelector<HTMLElement>('.scenery-end')?.hidden).toBe(true);
    p.showReadout({ time: 180, section: 'plains', props: 3, seed: 7, ended: true });
    expect(document.querySelector<HTMLElement>('.scenery-end')?.hidden).toBe(false);
  });

  it('P04-R06: buttons pause, fast-forward, restart and change the seed; the slider seeks', () => {
    const { p, calls } = panel();
    click('.scenery-pause');
    expect(p.settings.paused).toBe(true);
    expect(document.querySelector('.scenery-pause')?.getAttribute('aria-pressed')).toBe('true');
    click('.scenery-fast');
    expect(calls.change).toHaveBeenLastCalledWith(expect.objectContaining({ fastForward: true }));
    click('.scenery-restart');
    click('.scenery-new-seed');
    expect(calls.restart).toHaveBeenCalledOnce();
    expect(calls.seed).toHaveBeenCalledOnce();
    const slider = document.querySelector<HTMLInputElement>('.scenery-time-slider');
    if (!slider) throw new Error('no slider');
    slider.value = '90';
    slider.dispatchEvent(new Event('input'));
    expect(calls.seek).toHaveBeenCalledWith(90);
  });

  it('P04-R02, P04-R03: toggles the sea and the playfield outline, and sets each cloud layer', () => {
    const { p } = panel();
    click('.scenery-sea');
    click('.scenery-frame');
    expect(p.settings).toMatchObject({ sea: false, frame: true });
    click('.scenery-cloud-toggle');
    expect(p.settings.clouds[0]?.enabled).toBe(false);
    const opacity = document.querySelector<HTMLInputElement>('.scenery-opacity');
    if (!opacity) throw new Error('no slider');
    opacity.value = '20';
    opacity.dispatchEvent(new Event('input'));
    expect(p.settings.clouds[0]).toEqual({ enabled: false, coverage: 30, opacity: 20 });
    expect(document.querySelector<HTMLInputElement>('.scenery-coverage')?.value).toBe('30');
  });

  it('P04-R02: a level without a sea cannot show one', () => {
    const { p } = panel({ hasSea: false, initial: { ...INITIAL, sea: false } });
    expect(document.querySelector<HTMLButtonElement>('.scenery-sea')?.disabled).toBe(true);
    p.update({ sea: true });
    expect(p.settings.sea).toBe(false);
  });
});
