import { test, expect } from '@playwright/test';

test.describe('Pagefind Search', () => {
  test('search input exists and accepts text', async ({ page }) => {
    await page.goto('/');

    // The search input is injected by Pagefind
    const searchInput = page.locator('.pagefind-ui__search-input');
    await expect(searchInput).toBeVisible();

    // Type into the search input
    await searchInput.fill('Pinot');
    
    // Check that it typed correctly
    await expect(searchInput).toHaveValue('Pinot');
  });
});
