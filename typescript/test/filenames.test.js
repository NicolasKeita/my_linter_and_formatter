import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import test from 'node:test';
import { fileURLToPath, URL } from 'node:url';

import { comparisonReason } from '../filenames/comparison.js';
import { editDistance } from '../filenames/distance.js';
import { findSimilar } from '../filenames/index.js';
import { scanStructure } from '../structure.js';

const cases = JSON.parse(fs.readFileSync(new URL('../../testdata/filename_cases.json', import.meta.url), 'utf8'));
const cli = fileURLToPath(new URL('../bin/lint-structure.js', import.meta.url));

test('shared filename policy including course/source, Unicode and the exact threshold', () => {
  for (const sample of cases) {
    assert.equal(Boolean(comparisonReason(`${sample.left}.ts`, `${sample.right}.ts`)), sample.match, JSON.stringify(sample));
  }
  assert.equal(editDistance('CA', 'ABC'), 2);
  assert.equal(comparisonReason('utility.ts', 'utility.test.ts'), undefined);
  assert.equal(comparisonReason('utility.ts', 'utility.d.ts'), undefined);
  assert.equal(comparisonReason('utility.ts', 'utility.js'), undefined);
  assert.ok(comparisonReason('utility_1.test.ts', 'utility-2.test.ts'));
});

test('directory and project scopes preserve exclusions and report each file once', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'filename-policy-'));

  assert.equal(path.dirname(root), path.resolve(os.tmpdir()));
  try {
    for (const name of ['Utility_1.ts', 'nested/Utility-2.ts', 'dist/Utility_3.ts', 'Utility_4.json']) {
      const file = path.join(root, name);

      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.writeFileSync(file, 'export {};\n');
    }
    assert.deepEqual(scanStructure(root), []);
    assert.equal(scanStructure(root, { similarityScope: 'project' }).length, 2);
    for (const options of [[], ['--strict']]) {
      const result = spawnSync(process.execPath, [cli, root, '--similarity-scope', 'project', ...options], { encoding: 'utf8' });

      assert.equal(result.status, options.length ? 1 : 0, result.stderr);
      assert.equal(result.stdout.match(/\[similar-filename\]/gu).length, 2);
    }
    assert.equal(fs.readFileSync(path.join(root, 'Utility_1.ts'), 'utf8'), 'export {};\n');
    const invalid = spawnSync(process.execPath, [cli, root, '--similarity-scope', 'invalid'], { encoding: 'utf8' });

    assert.equal(invalid.status, 2);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});

test('direct matches are deduplicated without transitive grouping or cross-directory identical names', () => {
  const root = path.join(os.tmpdir(), 'filename-policy');
  const files = ['abcdefghijklmnopqrst.ts', 'xyzdefghijklmnopqrst.ts', 'xyzabcghijklmnopqrst.ts']
    .map((name) => path.join(root, name));
  const matches = findSimilar([...files, files[0]]);

  assert.equal(matches.length, 3);
  assert.ok(!matches.find(({ file }) => file === files[0]).message.includes(path.basename(files[2])));
  assert.deepEqual(findSimilar([path.join(root, 'one/index.ts'), path.join(root, 'two/index.ts')], 'project'), []);
  assert.deepEqual(findSimilar([files[0]]), []);
  assert.throws(() => findSimilar([], 'invalid'), /scope/u);
});
