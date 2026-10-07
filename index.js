import js from '@eslint/js';
import stylistic from '@stylistic/eslint-plugin';
import tseslint from 'typescript-eslint';

import plugin from './plugin.js';

const config = tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    plugins: {
      '@stylistic': stylistic,
      nk: plugin,
    },
    rules: {
      'no-console': 'warn',
      'nk/no-comments-in-functions': 'warn',
      'nk/no-empty-file': 'warn',
      'nk/no-french-comments': 'warn',

      'max-len': ['warn', { code: 140 }],
      '@stylistic/indent': ['warn', 2],
      '@stylistic/semi': ['warn', 'always'],
      '@stylistic/eol-last': ['warn', 'always'],
      '@stylistic/space-infix-ops': 'warn',
      'linebreak-style': ['warn', 'unix'],
      '@stylistic/object-curly-spacing': ['warn', 'always'],
      '@stylistic/comma-spacing': [
        'warn',
        {
          before: false,
          after: true,
        },
      ],
      '@stylistic/space-before-blocks': ['warn', 'always'],
      '@stylistic/no-trailing-spaces': 'warn',
    },
  },
);

export { plugin };
export default config;
