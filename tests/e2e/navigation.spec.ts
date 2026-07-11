import { test, expect } from '@playwright/test';

test.describe('Navigation and Content Verification', () => {
  test('has title and hero content', async ({ page }) => {
    await page.goto('/');

    // Expect a title "to contain" a substring.
    await expect(page).toHaveTitle(/Wine Price Aggregator/);

    // Expect the hero section to be present
    const heroHeading = page.locator('h1', { hasText: 'Din Personlige Sommelier' });
    await expect(heroHeading).toBeVisible();
    
    // Expect at least one wine card to be present
    const firstWineCard = page.locator('article').first();
    await expect(firstWineCard).toBeVisible();
  });

  test('can navigate to wine detail page and see key elements', async ({ page }) => {
    await page.goto('/');

    // Click the first wine link
    const firstWineLink = page.locator('a.group').first();
    await firstWineLink.click();

    // Verify detail page elements
    // The h1 should be the wine title, which is visible
    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();

    // Check for specific UI elements
    await expect(page.getByText('Pris', { exact: true })).toBeVisible();
    await expect(page.getByText('Anbefaling')).toBeVisible();
    await expect(page.getByText('Værdi-Index')).toBeVisible();
    
    // Check components
    await expect(page.getByText('Smagsnoter & Fordele')).toBeVisible();
    await expect(page.getByText('Den Musikalske Pairing')).toBeVisible();
  });
});
