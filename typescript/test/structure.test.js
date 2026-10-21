import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import test from 'node:test';
import { fileURLToPath, URL } from 'node:url';

import { scanStructure } from '../structure.js';

const cliPath = fileURLToPath(new URL('../bin/lint-structure.js', import.meta.url));

function withTemporaryDirectory(run) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'nk-lint-'));

  if (path.dirname(path.resolve(root)) !== path.resolve(os.tmpdir())) {
    throw new Error('Refusing to use a directory outside the system temporary directory.');
  }

  try {
    run(root);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
}

test('scans every directory and respects the file limit and ignored names', () => {
  withTemporaryDirectory((root) => {
    fs.mkdirSync(path.join(root, 'empty'));
    fs.mkdirSync(path.join(root, 'nested'));
    fs.mkdirSync(path.join(root, 'node_modules'));
    fs.writeFileSync(path.join(root, 'nested', 'one.ts'), 'export {};');
    fs.writeFileSync(path.join(root, 'nested', 'two.json'), '{}');

    const diagnostics = scanStructure(root, { maxFiles: 1 });

    assert.deepEqual(diagnostics.map(({ directory, kind }) => [path.basename(directory), kind]), [
      ['empty', 'empty-directory'],
      ['nested', 'too-many-files'],
    ]);

    fs.writeFileSync(path.join(root, 'empty', 'one.ts'), 'export {};');
    assert.equal(scanStructure(root, { maxFiles: 2 }).length, 0);
  });
});

test('the CLI warns by default and can fail in strict mode', () => {
  withTemporaryDirectory((root) => {
    const warning = spawnSync(process.execPath, [cliPath, root], { encoding: 'utf8' });
    const strict = spawnSync(process.execPath, [cliPath, root, '--strict'], { encoding: 'utf8' });

    assert.equal(warning.status, 0);
    assert.match(warning.stdout, /empty directory/);
    assert.equal(strict.status, 1);
  });
});

test('allows eight direct subdirectories and ignores excluded directories at every depth', () => {
  withTemporaryDirectory((root) => {
    fs.writeFileSync(path.join(root, 'root.ts'), 'export {};');

    for (let index = 0; index < 8; index += 1) {
      const nested = path.join(root, `part_${index}`, 'nested');

      fs.mkdirSync(nested, { recursive: true });
      fs.writeFileSync(path.join(nested, 'file.ts'), 'export {};');
    }

    for (const ignored of ['.git', '.next', 'node_modules', 'dist', 'build', 'coverage', 'custom']) {
      fs.mkdirSync(path.join(root, ignored));
    }

    const ignore = ['.git', '.next', 'node_modules', 'dist', 'build', 'coverage', 'custom'];

    assert.equal(scanStructure(root, { ignore }).length, 0);
    fs.mkdirSync(path.join(root, 'part_0', 'node_modules'));
    fs.rmdirSync(path.join(root, 'custom'));
    fs.mkdirSync(path.join(root, 'ninth'));
    const diagnostics = scanStructure(root).filter(({ kind }) => kind === 'too-many-subdirectories');

    assert.deepEqual(diagnostics, [
      { directory: root, kind: 'too-many-subdirectories', directoryCount: 9, maxSubdirectories: 8 },
    ]);
    const warning = spawnSync(process.execPath, [cliPath, root], { encoding: 'utf8' });
    const strict = spawnSync(process.execPath, [cliPath, root, '--strict'], { encoding: 'utf8' });

    assert.equal(warning.status, 0);
    assert.match(warning.stdout, /9 direct subdirectories \(maximum 8\)/);
    assert.equal(strict.status, 1);
  });
});

test('reports nested subdirectory violations without counting descendants in the parent', () => {
  withTemporaryDirectory((root) => {
    const nested = path.join(root, 'src');

    for (let index = 0; index < 9; index += 1) {
      fs.mkdirSync(path.join(nested, `part_${index}`), { recursive: true });
    }

    const diagnostics = scanStructure(root).filter(({ kind }) => kind === 'too-many-subdirectories');

    assert.deepEqual(diagnostics.map(({ directory }) => directory), [nested]);
  });
});
