import { defineConfig } from 'vitest/config';

const CORE_THRESHOLDS = { lines: 90, branches: 85, functions: 90, statements: 90 };

export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify('test'),
    __APP_COMMIT__: JSON.stringify('test'),
    __E2E__: JSON.stringify(false),
  },
  test: {
    include: ['tests/unit/**/*.test.ts'],
    environment: 'node',
    // The level-generation tests take about 2 s here and over 5 s (Vitest's default) on the
    // low-CPU shared CI runners.
    testTimeout: 30_000,
    hookTimeout: 30_000,
    coverage: {
      provider: 'v8',
      include: ['src/**/*.ts'],
      // ENG-45 exclusions. Pure GPU/visual setup files in render/ and fx/ use the *.visual.ts suffix.
      exclude: [
        'src/main.ts',
        'src/debug/**',
        'src/render/**/*.visual.ts',
        'src/fx/**/*.visual.ts',
        'src/**/*.d.ts',
      ],
      reporter: ['text', 'text-summary', 'html', 'json-summary'],
      // ENG-43 / ENG-146. Never lower these to get a green gate.
      thresholds: {
        lines: 70,
        'src/core/**': CORE_THRESHOLDS,
        'src/game/sim/**': CORE_THRESHOLDS,
      },
    },
  },
});
