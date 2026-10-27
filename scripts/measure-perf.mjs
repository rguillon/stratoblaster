// P13-R01: measures the menu buttons, the level loading times and the frames of every level, on
// the e2e build (`make e2e-build`, then `npx vite preview --mode e2e --outDir dist-e2e`).
// Usage: node scripts/measure-perf.mjs [--seconds 120] [--levels 1-1,4-5] [--gpu] [--warm]
//   [--out file]
import { chromium } from '@playwright/test';
import { writeFileSync } from 'node:fs';
import process from 'node:process';

const args = process.argv.slice(2);
const arg = (name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : fallback;
};
const seconds = Number(arg('seconds', '120'));
const renderEvery = Number(arg('render-every', '6'));
const base = arg('url', 'http://localhost:4173/');
const levels = arg('levels', '').split(',').filter(Boolean);
const allLevels = [1, 2, 3, 4].flatMap((w) => [1, 2, 3, 4, 5].map((l) => `${w}-${l}`));
const out = arg('out', '');
const gpu = args.includes('--gpu');
const warm = args.includes('--warm');
const warmMs = Number(arg('warm-ms', '3000'));

const browser = await chromium.launch({
  args: gpu
    ? ['--enable-gpu', '--ignore-gpu-blocklist']
    : ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
});

/** Times `sendAction(action)` and the frame after it, in the page. */
const press = (page, action) =>
  page.evaluate((a) => {
    const api = window.__GAME_TEST__;
    const t = performance.now();
    api.sendAction(a);
    api.step(1);
    return performance.now() - t;
  }, action);

const settle = (page) =>
  page.evaluate(() => {
    const api = window.__GAME_TEST__;
    for (let i = 0; i < 120 && api.getState().transitioning; i++) api.step(1, false);
    api.step(1);
  });

async function open(page) {
  await page.goto(base);
  await page.waitForFunction(() => window.__GAME_TEST__?.getState().screen === 'title', undefined, {
    timeout: 120000,
  });
  await settle(page);
}

async function measureMenus() {
  const page = await browser.newPage();
  await open(page);
  const rows = [];
  const time = async (label, action) => {
    rows.push({ label, ms: await press(page, action) });
    await settle(page);
  };
  await time('title: down', 'down');
  await time('title: up', 'up');
  await time('title: confirm (ship select)', 'confirm');
  await time('ship select: right', 'right');
  await time('ship select: confirm (level select)', 'confirm');
  await time('level select: right', 'right');
  await time('level select: left', 'left');
  await time('level select: confirm (1-1)', 'confirm');
  await page.evaluate(() => window.__GAME_TEST__.step(30));
  await time('game: pause', 'pause');
  await time('pause: down', 'down');
  await time('pause: up', 'up');
  await time('pause: resume', 'confirm');
  await page.close();
  return rows;
}

/** Goes from the title screen to level `id` on the level select screen. */
async function goToLevel(page, id) {
  await open(page);
  for (const action of ['confirm', 'confirm']) {
    await press(page, action);
    await settle(page);
  }
  const [world, index] = id.split('-').map(Number);
  const moves = [...Array(world - 1).fill('down'), ...Array(index - 1).fill('right')];
  for (const action of moves) {
    await press(page, action);
    await settle(page);
  }
}

/** Confirms the level selected and steps until it is loaded, timing each step. */
const confirmLevel = (page) =>
  page.evaluate(async () => {
    const api = window.__GAME_TEST__;
    // One frame per task, as in the browser: the worker's messages come in between.
    const nextTask = () => new Promise((resolve) => setTimeout(resolve, 0));
    const t = performance.now();
    api.sendAction('confirm');
    const press = performance.now() - t;
    const steps = [];
    // Builds without the perf numbers (before P13): loaded once the level has drawn a frame.
    const loaded = () => {
      const state = api.getState();
      return state.perf ? state.perf.lastLoad !== null : state.game != null && steps.length > 0;
    };
    while (!loaded() && steps.length < 600) {
      const s = performance.now();
      api.step(1);
      steps.push(Math.round(performance.now() - s));
      await nextTask();
    }
    const total = performance.now() - t;
    const perf = api.getState().perf ?? {
      lastLoad: total,
      longestLoadStep: Math.max(press, ...steps),
    };
    return { press, lastLoad: perf.lastLoad, step: perf.longestLoadStep, steps };
  });

/** Plays `seconds` with no input, timing each frame; one in `renderEvery` is drawn. */
const playLevel = (page) =>
  page.evaluate(
    ({ seconds, renderEvery }) => {
      const api = window.__GAME_TEST__;
      const [sim, drawn] = [[], []];
      for (let i = 0; i < Math.round(seconds * 60); i++) {
        const render = i % renderEvery === renderEvery - 1;
        const t = performance.now();
        api.step(1, render);
        (render ? drawn : sim).push({ ms: performance.now() - t, at: i / 60 });
      }
      return { sim, drawn, time: api.getState().game?.time ?? 0 };
    },
    { seconds, renderEvery },
  );

/** Count over 50 and 100 ms, median and longest of the frames after the first second. */
function stats(frames) {
  const list = frames.filter((f) => f.at >= 1).map((f) => f.ms);
  const sorted = [...list].sort((a, b) => a - b);
  return {
    max: sorted[sorted.length - 1] ?? 0,
    median: sorted[Math.floor(sorted.length / 2)] ?? 0,
    over50: list.filter((m) => m > 50).length,
    over100: list.filter((m) => m > 100).length,
  };
}

/** The five longest frames after the first second, as `ms@time`. */
const worst = (frames) =>
  frames
    .filter((f) => f.at >= 1)
    .sort((a, b) => b.ms - a.ms)
    .slice(0, 5)
    .map((f) => `${f.ms.toFixed(0)}@${f.at.toFixed(1)}s`);

async function measureLevel(id) {
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(String(e)));
  await goToLevel(page, id);
  // --warm: the highlight rests on the level a moment, as a player's would, so its ground and
  // textures are prepared in the background (P13-R03) before it is confirmed.
  if (warm) {
    await page.evaluate(() => window.__GAME_TEST__.step(30));
    await page.waitForTimeout(warmMs);
  }
  const confirm = await confirmLevel(page);
  const run = await playLevel(page);
  await page.close();
  return {
    id,
    pressMs: confirm.press,
    loadMs: confirm.lastLoad,
    loadStepMs: confirm.step,
    loadSteps: confirm.steps,
    levelTime: run.time,
    sim: stats(run.sim),
    drawn: stats(run.drawn),
    simWorst: worst(run.sim),
    drawnWorst: worst(run.drawn),
    errors,
  };
}

const result = { menus: [], levels: [] };
if (!levels.length || args.includes('--menus')) result.menus = await measureMenus();
for (const r of result.menus) console.log(`${r.label.padEnd(40)} ${r.ms.toFixed(0)} ms`);
for (const id of levels.length ? levels : allLevels) {
  const r = await measureLevel(id);
  result.levels.push(r);
  console.log(
    `${id} press ${r.pressMs.toFixed(0)} load ${r.loadMs?.toFixed(0)} step ${r.loadStepMs?.toFixed(0)} [${r.loadSteps.join(',')}] t=${r.levelTime.toFixed(0)}s ` +
      `sim max ${r.sim.max.toFixed(0)} med ${r.sim.median.toFixed(1)} >50:${r.sim.over50} >100:${r.sim.over100} ` +
      `| drawn max ${r.drawn.max.toFixed(0)} med ${r.drawn.median.toFixed(0)} | worst sim ${r.simWorst.join(' ')} drawn ${r.drawnWorst.join(' ')}` +
      (r.errors.length ? ` ERR ${r.errors.join(';')}` : ''),
  );
}
if (out) writeFileSync(out, JSON.stringify(result, null, 2));
await browser.close();
