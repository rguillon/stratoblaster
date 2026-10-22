import { execSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
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
  },
}));
