import { test as base, expect, type Page } from '@playwright/test';

/**
 * ENG-53: every e2e test fails on a console error or an uncaught exception; P12-R05: and on any
 * warning from the audio (an autoplay warning, a context that could not start).
 */
export const test = base.extend<{ consoleErrors: string[] }>({
  consoleErrors: [
    async ({ page }, use) => {
      const errors: string[] = [];
      page.on('console', (msg) => {
        if (msg.type() === 'error') errors.push(msg.text());
        if (msg.type() === 'warning' && /audio|autoplay/i.test(msg.text())) errors.push(msg.text());
      });
      page.on('pageerror', (err) => errors.push(err.message));
      await use(errors);
      expect(errors, 'browser console errors').toEqual([]);
    },
    { auto: true },
  ],
});

/** Resolves after `count` animation frames, so the render loop has drawn that many frames. */
export async function waitForFrames(page: Page, count = 10): Promise<void> {
  await page.evaluate(
    (n) =>
      new Promise<void>((resolve) => {
        let left = n;
        const tick = () => {
          if (--left <= 0) resolve();
          else requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      }),
    count,
  );
}

export { expect };
