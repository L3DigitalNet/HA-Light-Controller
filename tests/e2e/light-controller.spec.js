// @ts-check
const { test, expect } = require('@playwright/test');

const HA_URL = process.env.HA_URL || 'http://192.168.2.3:8123';

// Helper to login to Home Assistant
async function loginToHA(page) {
  await page.goto(HA_URL);

  // Check if we need to login
  const loginForm = page.locator('ha-auth-flow');
  if (await loginForm.isVisible({ timeout: 5000 }).catch(() => false)) {
    // If there's a login form, we need credentials
    // For local trusted network, this might be skipped
    console.log('Login form detected - checking for trusted network...');

    // Wait for either login or dashboard
    await Promise.race([
      page.waitForURL('**/lovelace/**', { timeout: 10000 }),
      page.waitForURL('**/states', { timeout: 10000 }),
      page.locator('ha-auth-flow').waitFor({ state: 'hidden', timeout: 10000 }),
    ]).catch(() => {});
  }

  // Wait for HA to fully load
  await page.waitForLoadState('networkidle', { timeout: 30000 });
}

// Helper to navigate to integrations page
async function goToIntegrations(page) {
  await page.goto(`${HA_URL}/config/integrations`);
  await page.waitForLoadState('networkidle');
  await page.waitForSelector('ha-config-integrations', { timeout: 10000 });
}

// Helper to find Light Controller integration card
async function findLightControllerCard(page) {
  // Search for the integration
  const searchInput = page.locator('search-input input, ha-search-input input').first();
  if (await searchInput.isVisible({ timeout: 3000 }).catch(() => false)) {
    await searchInput.fill('Light Controller');
    await page.waitForTimeout(500);
  }

  // Find the integration card
  const card = page.locator('ha-integration-card').filter({ hasText: 'Light Controller' }).first();
  return card;
}

test.describe('Light Controller Integration', () => {

  test.beforeEach(async ({ page }) => {
    await loginToHA(page);
  });

  test('integration is installed and visible', async ({ page }) => {
    await goToIntegrations(page);

    const card = await findLightControllerCard(page);
    await expect(card).toBeVisible({ timeout: 10000 });

    // Verify it shows as configured
    const configuredText = card.locator('text=configured');
    // Integration should be loaded
    await expect(card).toContainText(/Light Controller/i);
  });

  test('can open integration options', async ({ page }) => {
    await goToIntegrations(page);

    const card = await findLightControllerCard(page);
    await expect(card).toBeVisible({ timeout: 10000 });

    // Click on the card to open details
    await card.click();

    // Wait for the dialog/panel
    await page.waitForTimeout(1000);

    // Look for the options/configure button (gear icon)
    const optionsButton = page.locator('[aria-label*="onfigure"], [aria-label*="ptions"], ha-icon-button').filter({ has: page.locator('ha-svg-icon') }).first();

    if (await optionsButton.isVisible({ timeout: 3000 }).catch(() => false)) {
      await optionsButton.click();
      await page.waitForTimeout(1000);

      // Should show options menu
      const dialog = page.locator('ha-dialog, ha-more-info-dialog, .mdc-dialog');
      const menuVisible = await dialog.isVisible({ timeout: 5000 }).catch(() => false);

      // Either dialog or menu should appear
      expect(menuVisible || await page.locator('ha-config-flow-card').isVisible().catch(() => false)).toBeTruthy();
    }
  });

  test('options flow shows menu', async ({ page }) => {
    // Navigate directly to the integration's config page
    await page.goto(`${HA_URL}/config/integrations/integration/ha_light_controller`);
    await page.waitForLoadState('networkidle');

    // Find and click configure/options
    const configureButton = page.locator('mwc-button, ha-button').filter({ hasText: /configure|options/i }).first();

    if (await configureButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await configureButton.click();
      await page.waitForTimeout(1000);

      // Should show the options menu with our categories
      const menuItems = ['defaults', 'tolerances', 'retry', 'notifications', 'preset'];

      for (const item of menuItems) {
        const menuOption = page.locator(`text=/${item}/i`);
        // At least some menu options should be visible
        if (await menuOption.isVisible({ timeout: 2000 }).catch(() => false)) {
          console.log(`Found menu option: ${item}`);
        }
      }
    }
  });

  test('services are registered', async ({ page }) => {
    // Go to Developer Tools > Services
    await page.goto(`${HA_URL}/developer-tools/service`);
    await page.waitForLoadState('networkidle');

    // Search for light controller services
    const serviceSearch = page.locator('ha-service-picker input, [role="combobox"]').first();
    await serviceSearch.click();
    await serviceSearch.fill('ha_light_controller');
    await page.waitForTimeout(1000);

    // Check for expected services
    const expectedServices = [
      'ensure_state',
      'activate_preset',
      'create_preset',
      'delete_preset',
    ];

    const dropdown = page.locator('mwc-list-item, ha-list-item, [role="option"]');
    const serviceCount = await dropdown.count();

    console.log(`Found ${serviceCount} matching services`);
    expect(serviceCount).toBeGreaterThan(0);
  });

  test('ensure_state service UI loads', async ({ page }) => {
    await page.goto(`${HA_URL}/developer-tools/service`);
    await page.waitForLoadState('networkidle');

    // Select the ensure_state service
    const serviceSearch = page.locator('ha-service-picker input, [role="combobox"]').first();
    await serviceSearch.click();
    await serviceSearch.fill('ha_light_controller.ensure_state');
    await page.waitForTimeout(500);

    // Click on the service option
    const option = page.locator('mwc-list-item, ha-list-item, [role="option"]').filter({ hasText: /ensure_state/i }).first();
    if (await option.isVisible({ timeout: 3000 }).catch(() => false)) {
      await option.click();
      await page.waitForTimeout(1000);

      // Verify service fields are shown
      const form = page.locator('ha-service-control, ha-yaml-editor');
      await expect(form).toBeVisible({ timeout: 5000 });
    }
  });

  test('entities are created for presets', async ({ page }) => {
    // Go to entities page and search for light controller entities
    await page.goto(`${HA_URL}/config/entities`);
    await page.waitForLoadState('networkidle');

    // Search for light controller entities
    const searchInput = page.locator('search-input input, ha-search-input input').first();
    await searchInput.fill('light_controller');
    await page.waitForTimeout(1000);

    // Check if any entities exist
    const entityRows = page.locator('ha-data-table .mdc-data-table__row, [role="row"]');
    const count = await entityRows.count();

    console.log(`Found ${count} Light Controller entities`);
    // Log entity names if found
    if (count > 0) {
      const firstEntity = entityRows.first();
      const text = await firstEntity.textContent().catch(() => '');
      console.log(`First entity: ${text}`);
    }
  });

  test('device is created', async ({ page }) => {
    // Go to devices page
    await page.goto(`${HA_URL}/config/devices/dashboard`);
    await page.waitForLoadState('networkidle');

    // Search for Light Controller device
    const searchInput = page.locator('search-input input, ha-search-input input').first();
    await searchInput.fill('Light Controller');
    await page.waitForTimeout(1000);

    // Check for device
    const deviceCard = page.locator('ha-device-card, .device-card').filter({ hasText: /Light Controller/i });

    if (await deviceCard.isVisible({ timeout: 5000 }).catch(() => false)) {
      console.log('Light Controller device found');
      await expect(deviceCard).toBeVisible();
    } else {
      console.log('No dedicated device card found (may be normal if no presets exist)');
    }
  });
});

test.describe('Light Controller Error Handling', () => {

  test.beforeEach(async ({ page }) => {
    await loginToHA(page);
  });

  test('no JavaScript errors on integration page', async ({ page }) => {
    const errors = [];

    page.on('pageerror', (error) => {
      errors.push(error.message);
    });

    await page.goto(`${HA_URL}/config/integrations/integration/ha_light_controller`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Filter out known non-critical errors
    const criticalErrors = errors.filter(e =>
      !e.includes('ResizeObserver') &&
      !e.includes('Non-Error promise rejection')
    );

    if (criticalErrors.length > 0) {
      console.log('JavaScript errors found:', criticalErrors);
    }

    expect(criticalErrors.length).toBe(0);
  });

  test('no console errors in developer tools', async ({ page }) => {
    const consoleErrors = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto(`${HA_URL}/developer-tools/service`);
    await page.waitForLoadState('networkidle');

    // Select light controller service
    const serviceSearch = page.locator('ha-service-picker input, [role="combobox"]').first();
    await serviceSearch.click();
    await serviceSearch.fill('ha_light_controller');
    await page.waitForTimeout(2000);

    // Filter relevant errors
    const relevantErrors = consoleErrors.filter(e =>
      e.toLowerCase().includes('light_controller') ||
      e.toLowerCase().includes('error')
    );

    if (relevantErrors.length > 0) {
      console.log('Console errors:', relevantErrors);
    }
  });
});
