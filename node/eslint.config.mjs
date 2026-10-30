// ESLint flat config. Layering rules: specs/01-engineering.md ENG-11, ENG-18, ENG-142.
import js from '@eslint/js';
import { config as defineConfig, configs as tsConfigs } from 'typescript-eslint';
import { importX, createNodeResolver } from 'eslint-plugin-import-x';
import { createTypeScriptImportResolver } from 'eslint-import-resolver-typescript';
import prettier from 'eslint-config-prettier';
import globals from 'globals';

const ENGINE_LAYERS = [
  'app',
  'core',
  'render',
  'fx',
  'audio',
  'input',
  'ui',
  'assets',
  'config',
  'platform',
  'debug',
];

// Pure code (core/, game/sim/): no engine, no DOM, deterministic (ENG-11, ENG-18).
const PURE_RULES = {
  'no-restricted-imports': [
    'error',
    {
      patterns: [
        { group: ['@babylonjs/*'], message: 'Pure simulation code must not import Babylon.' },
      ],
    },
  ],
  'no-restricted-globals': [
    'error',
    ...[
      'window',
      'document',
      'performance',
      'navigator',
      'localStorage',
      'requestAnimationFrame',
    ].map((name) => ({ name, message: 'Pure simulation code must not touch browser globals.' })),
  ],
  'no-restricted-properties': [
    'error',
    { object: 'Math', property: 'random', message: 'Use the seeded RNG (ENG-18).' },
    { object: 'Date', property: 'now', message: 'Use the injected dt / clock (ENG-18).' },
    { object: 'performance', property: 'now', message: 'Use the injected dt / clock (ENG-18).' },
  ],
};

const layerZones = [
  // core/ imports only core/ and config/.
  { target: './src/core', from: './src', except: ['./core', './config'] },
  // game/sim/ imports only core/, config/, game/sim/, game/config/.
  {
    target: './src/game/sim',
    from: './src',
    except: ['./core', './config', './game/sim', './game/config'],
  },
  // game/view/ may not import app/, input/, platform/, debug/, config/, main.ts.
  {
    target: './src/game/view',
    from: [
      './src/app',
      './src/input',
      './src/platform',
      './src/debug',
      './src/config',
      './src/main.ts',
    ],
  },
  // game/config/ is plain data.
  { target: './src/game/config', from: './src', except: ['./game/config', './core'] },
  // Engine never imports game/ (main.ts may import game/index.ts only).
  ...ENGINE_LAYERS.map((layer) => ({ target: `./src/${layer}`, from: './src/game' })),
  { target: './src/main.ts', from: './src/game', except: ['./index.ts'] },
  // Only app/ and main.ts wire layers: nothing else imports app/.
  {
    target: ENGINE_LAYERS.filter((l) => l !== 'app').map((l) => `./src/${l}`),
    from: './src/app',
  },
];

export default defineConfig(
  {
    ignores: [
      'dist/',
      'dist-e2e/',
      'coverage/',
      'playwright-report/',
      'test-results/',
      'node_modules/',
    ],
  },
  js.configs.recommended,
  ...tsConfigs.strictTypeChecked,
  ...tsConfigs.stylisticTypeChecked,
  importX.flatConfigs.recommended,
  importX.flatConfigs.typescript,
  {
    languageOptions: {
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
      globals: { ...globals.browser },
    },
    settings: {
      'import-x/resolver-next': [createTypeScriptImportResolver(), createNodeResolver()],
    },
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/ban-ts-comment': [
        'error',
        { 'ts-ignore': true, 'ts-expect-error': 'allow-with-description' },
      ],
      'import-x/no-default-export': 'error',
      // TypeScript (`make typecheck`, in every hook and gate) already reports unresolved modules
      // and missing default, named or namespace exports: these rules only added a third of the
      // lint time (typescript-eslint performance guide, D-094).
      'import-x/no-unresolved': 'off',
      'import-x/namespace': 'off',
      'import-x/default': 'off',
      'import-x/no-named-as-default-member': 'off',
      'import-x/no-restricted-paths': ['error', { zones: layerZones }],
      'max-lines-per-function': ['warn', { max: 50, skipBlankLines: true, skipComments: true }],
      'max-lines': ['warn', { max: 300, skipBlankLines: true, skipComments: true }],
      complexity: ['warn', 10],
    },
  },
  { files: ['src/core/**/*.ts', 'src/game/sim/**/*.ts'], rules: PURE_RULES },
  {
    files: ['tests/**/*.ts'],
    rules: { 'max-lines-per-function': 'off' },
  },
  {
    // Tool configs must use default exports.
    files: ['*.config.ts', '*.config.mjs', 'eslint.config.mjs'],
    languageOptions: { globals: { ...globals.node } },
    rules: { 'import-x/no-default-export': 'off' },
  },
  {
    files: ['**/*.mjs'],
    ...tsConfigs.disableTypeChecked,
  },
  prettier,
);
