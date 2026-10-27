import { defineConfig, devices } from '@playwright/test';

// ENG-50, ENG-51, ENG-57: runs against the e2e build served by `vite preview`.
export default defineConfig({
  testDir: 'tests/e2e',
  // Tests share no state: run them in parallel, within a file too (one CI job, D-018 amended).
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['html', { open: 'never' }], ['github']] : [['list']],
  use: {
    baseURL: 'http://localhost:4173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        launchOptions: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] },
      },
    },
  ],
  webServer: {
    command: 'npx vite preview --mode e2e --outDir dist-e2e',
    url: 'http://localhost:4173',
    reuseExistingServer: !process.env.CI,
  },
});
