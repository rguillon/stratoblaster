// Same ESLint cache as `make check-fast` (pre-push): files linted at commit are not linted again
// at push unless they changed (D-094).
const ESLINT_CACHE =
  '--cache --cache-strategy content --cache-location node_modules/.cache/eslint/';

export default {
  '*.{ts,mts,mjs}': ['prettier --write --cache', `eslint --fix --max-warnings 0 ${ESLINT_CACHE}`],
  '*.{json,md,yml,yaml,css,html}': ['prettier --write --cache'],
};
