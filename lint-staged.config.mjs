export default {
  '*.{ts,mts,mjs}': ['prettier --write', 'eslint --fix --max-warnings 0'],
  '*.{json,md,yml,yaml,css,html}': ['prettier --write'],
};
