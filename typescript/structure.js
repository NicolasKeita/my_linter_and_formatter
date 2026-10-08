import fs from 'node:fs';
import path from 'node:path';

export const defaultIgnoredNames = [
  '.git',
  '.next',
  'node_modules',
  'dist',
  'build',
  'coverage',
];

export function scanStructure(rootDirectory, { maxFiles = 10, ignore = defaultIgnoredNames } = {}) {
  if (!Number.isInteger(maxFiles) || maxFiles < 0) {
    throw new TypeError('maxFiles must be a non-negative integer.');
  }

  const root = path.resolve(rootDirectory);
  const ignoredNames = new Set(ignore);
  const diagnostics = [];

  function visit(directory) {
    const entries = fs.readdirSync(directory, { withFileTypes: true })
      .filter((entry) => !ignoredNames.has(entry.name))
      .sort((left, right) => left.name.localeCompare(right.name));

    if (entries.length === 0) {
      diagnostics.push({ directory, kind: 'empty-directory' });
      return;
    }

    const fileCount = entries.filter((entry) => entry.isFile()).length;

    if (fileCount > maxFiles) {
      diagnostics.push({ directory, kind: 'too-many-files', fileCount, maxFiles });
    }

    for (const entry of entries) {
      if (entry.isDirectory()) {
        visit(path.join(directory, entry.name));
      }
    }
  }

  visit(root);
  return diagnostics;
}
