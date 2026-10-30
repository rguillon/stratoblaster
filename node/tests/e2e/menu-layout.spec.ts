import { test, expect } from './fixtures';
import { expectState, openGame } from './menu-helpers';

for (const [width, height] of [
  [800, 600],
  [1920, 1080],
  [390, 844],
] as const) {
  test(`P01-R13: at ${String(width)}×${String(height)} the menu is fully visible, not cropped, not stretched`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height });
    await openGame(page);
    for (const selector of ['#stage', '#menu']) {
      const box = await page.locator(selector).boundingBox();
      if (!box) throw new Error(`${selector} has no box`);
      expect(box.x).toBeGreaterThanOrEqual(0);
      expect(box.y).toBeGreaterThanOrEqual(0);
      expect(box.x + box.width).toBeLessThanOrEqual(width + 1);
      expect(box.y + box.height).toBeLessThanOrEqual(height + 1);
      expect(box.width / box.height).toBeCloseTo(480 / 640, 2);
      expect(Math.max(box.width / width, box.height / height)).toBeGreaterThan(0.99);
    }
    await expect(page.locator('.title-version')).toBeInViewport({ ratio: 1 });
  });
}

test('P01-R13: the menu follows window resizes', async ({ page }) => {
  await page.setViewportSize({ width: 800, height: 600 });
  await openGame(page);
  await page.setViewportSize({ width: 390, height: 844 });
  await expect
    .poll(async () => (await page.locator('#menu').boundingBox())?.width)
    .toBeCloseTo(390, 0);
});

test('P01-R13: the selected entry is marked by more than colour (markers, frame)', async ({
  page,
}) => {
  await openGame(page);
  const marker = (selector: string, pseudo: string, property: string) =>
    page
      .locator(selector)
      .evaluate((el, [p, prop]) => getComputedStyle(el, p).getPropertyValue(prop), [
        pseudo,
        property,
      ] as const);
  expect(await marker('.title-start.selected', '::before', 'content')).toContain('▶');
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select' });
  expect(await marker('.ship-card.selected', '::before', 'visibility')).toBe('visible');
  expect(await marker('.ship-card:not(.selected) >> nth=0', '::before', 'visibility')).toBe(
    'hidden',
  );
  await page.locator('.ship-card.selected').click();
  await expectState(page, { screen: 'level-select' });
  expect(await marker('.level-cell.selected', '', 'outline-style')).toBe('dashed');
});

test('P01-R11: touch targets are at least 44×44 CSS px on a phone', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await openGame(page);
  await page.locator('.title-start').click();
  await expectState(page, { screen: 'ship-select' });
  await page.locator('.ship-card.selected').click();
  await expectState(page, { screen: 'level-select' });
  for (const target of await page.locator('.menu-entry, .menu-back').all()) {
    const box = await target.boundingBox();
    expect(box?.width).toBeGreaterThanOrEqual(44);
    expect(box?.height).toBeGreaterThanOrEqual(44);
  }
});
