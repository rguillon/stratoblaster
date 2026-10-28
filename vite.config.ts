import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { defineConfig } from 'vite';

const pkg = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8')) as {
  version: string;
};

function commitHash(): string {
  try {
    return execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim();
  } catch {
    return 'unknown';
  }
}

// ENG-82: relative base so the build works under any GitHub Pages sub-path.
// ENG-83: version + commit injected at build time.
export default defineConfig(({ mode }) => ({
  base: './',
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
    __APP_COMMIT__: JSON.stringify(commitHash()),
    __E2E__: JSON.stringify(mode === 'e2e'),
  },
  server: { port: 5173, strictPort: true },
  preview: { port: 4173, strictPort: true },
  build: {
    outDir: mode === 'e2e' ? 'dist-e2e' : 'dist',
    target: 'es2023',
    sourcemap: mode === 'e2e',
    // Babylon alone exceeds Vite's 500 kB default; the real budget is ENG-107 (1.5 MB gzip).
    chunkSizeWarningLimit: 1500,
    // Multi-page: the game, the player ship viewer at `player_ship/` (phase 02), the
    // player shots viewer at `player_shots/` (phase 03), the generated level viewer at
    // `level_zero/` (phase 04), the enemies viewer at `enemies/` (phase 05) and the bosses viewer
    // at `bosses/` and `boss/` (phase 07).
    rolldownOptions: {
      input: {
        main: fileURLToPath(new URL('./index.html', import.meta.url)),
        playerShip: fileURLToPath(new URL('./player_ship/index.html', import.meta.url)),
        playerShots: fileURLToPath(new URL('./player_shots/index.html', import.meta.url)),
        levelZero: fileURLToPath(new URL('./level_zero/index.html', import.meta.url)),
        enemies: fileURLToPath(new URL('./enemies/index.html', import.meta.url)),
        bosses: fileURLToPath(new URL('./bosses/index.html', import.meta.url)),
        boss: fileURLToPath(new URL('./boss/index.html', import.meta.url)),
        // The props viewer at `props/` (reviewer, 2026-10-28).
        props: fileURLToPath(new URL('./props/index.html', import.meta.url)),
      },
    },
  },
}));
