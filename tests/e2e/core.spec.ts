import { test, expect } from '@playwright/test';

test.describe('VibeWine Core Flows', () => {
  test('homepage has correct title and manifest', async ({ page }) => {
    await page.goto('/');

    // Expect a title
    await expect(page).toHaveTitle(/VibeWine/);

    // Expect the hero title to be visible
    const heroTitle = page.locator('h1', { hasText: 'Drop Snobberiet.' });
    await expect(heroTitle).toBeVisible();

    // Expect manifest section to be visible
    const manifestHeading = page.locator('h2', { hasText: 'Hvad er VibeWine?' });
    await expect(manifestHeading).toBeVisible();
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

  test('search input exists and renders', async ({ page }) => {
    await page.goto('/');

    // Check if pagefind UI input exists
    const searchInput = page.locator('.pagefind-ui__search-input');
    await expect(searchInput).toBeVisible();
  });
});
