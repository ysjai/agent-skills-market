import { test, expect } from '@playwright/test';

test.describe('Page Loading Tests', () => {
  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/.*/);
    await expect(page.locator('body')).toBeVisible();
  });

  test('login page loads successfully', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('body')).toBeVisible();
  });

  test('skills page loads successfully', async ({ page }) => {
    await page.goto('/skills');
    await expect(page.locator('body')).toBeVisible();
  });
});
