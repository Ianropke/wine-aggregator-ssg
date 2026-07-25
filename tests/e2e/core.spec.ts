import { test, expect } from '@playwright/test';

test.describe('VibeWine Core Flows', () => {
  test('homepage has correct title, hero and search UI', async ({ page }) => {
    await page.goto('/');

    // Expect a title
    await expect(page).toHaveTitle(/VibeWine/);

    // Expect the hero title to be visible
    const heroTitle = page.locator('h1', { hasText: 'Find vinen der matcher din vibe' });
    await expect(heroTitle).toBeVisible();

    // Check if pagefind UI input exists
    const searchInput = page.locator('.pagefind-ui__search-input');
    await expect(searchInput).toBeVisible();
  });

  test('navigation to Hall of Fame works', async ({ page }) => {
    await page.goto('/');

    // Click the Hall of Fame link
    await page.click('text=Hall of Fame 🔥');

    // Wait for URL to change
    await expect(page).toHaveURL(/.*hall-of-fame/);

    // Expect Hall of Fame heading
    const heading = page.locator('h1', { hasText: 'Hall of Fame' });
    await expect(heading).toBeVisible();
  });

  test('navigation to Forhandlere & Presse works', async ({ page }) => {
    await page.goto('/');

    // Click the Forhandlere link
    await page.click('text=Forhandlere & Presse');

    // Wait for URL to change
    await expect(page).toHaveURL(/.*forhandlere/);

    // Expect Forhandlere heading
    const heading = page.locator('h1', { hasText: 'Sælg flere flasker med' });
    await expect(heading).toBeVisible();
  });

  test('wine detail page renders retailer tools', async ({ page }) => {
    await page.goto('/wines/w-m-100');

    // Expect title
    const heading = page.locator('h1');
    await expect(heading).toBeVisible();

    // Expect retailer tools section
    const toolsHeading = page.locator('h3', { hasText: 'Brug denne anmeldelse i din butik' });
    await expect(toolsHeading).toBeVisible();

    // Expect print button
    const printBtn = page.locator('button', { hasText: 'Print Halsskilt' });
    await expect(printBtn).toBeVisible();
  });

  test('embed page renders compact widget', async ({ page }) => {
    await page.goto('/embed/w-m-100');

    // Expect vibe score element
    const scoreLabel = page.locator('.score-label');
    await expect(scoreLabel).toBeVisible();
  });
});
