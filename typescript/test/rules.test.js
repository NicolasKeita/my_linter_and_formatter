import assert from 'node:assert/strict';
import test from 'node:test';

import { Linter } from 'eslint';
import tseslint from 'typescript-eslint';

import plugin from '../plugin.js';

function verify(code, ruleId) {
  const linter = new Linter();

  return linter.verify(code, [
    {
      files: ['**/*.ts'],
      languageOptions: { parser: tseslint.parser },
      plugins: { nk: plugin },
      rules: { [`nk/${ruleId}`]: 'warn' },
    },
  ], { filename: 'example.ts' });
}

test('comments inside functions and interfaces are reported', () => {
  const functionMessages = verify('const answer = () => {\n  // explain\n  return 42;\n};', 'no-comments-in-functions');
  const interfaceMessages = verify('interface Answer {\n  // explain\n  value: number;\n}', 'no-comments-in-functions');
  const outsideMessages = verify('// explain\nconst answer = () => 42;', 'no-comments-in-functions');

  assert.equal(functionMessages.length, 1);
  assert.equal(interfaceMessages.length, 1);
  assert.equal(outsideMessages.length, 0);
});

test('empty files are reported', () => {
  assert.equal(verify('   \n', 'no-empty-file').length, 1);
  assert.equal(verify('const answer = 42;', 'no-empty-file').length, 0);
});

test('French comments are reported but English comments are accepted', () => {
  const french = '// Ce commentaire explique clairement pourquoi cette fonction existe dans ce programme.\nconst answer = 42;';
  const english = '// This comment clearly explains why this function exists in the program.\nconst answer = 42;';

  assert.equal(verify(french, 'no-french-comments').length, 1);
  assert.equal(verify(english, 'no-french-comments').length, 0);
});
