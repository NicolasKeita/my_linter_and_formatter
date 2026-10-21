import path from 'node:path';

import { comparisonReason, nameParts } from './comparison.js';

const extensions = new Set(['.ts', '.tsx', '.js', '.jsx', '.mts', '.cts', '.mjs', '.cjs']);

export function findSimilar(files, scope = 'directory') {
  if (!['directory', 'project'].includes(scope)) {
    throw new TypeError('similarity scope must be directory or project');
  }
  const groups = new Map();
  const matches = new Map();

  for (const file of [...new Set(files.map((entry) => path.resolve(entry)))].sort()) {
    if (!extensions.has(path.extname(file).toLowerCase())) {
      continue;
    }
    const key = JSON.stringify([scope === 'directory' ? path.dirname(file) : '', nameParts(path.basename(file))[1]]);

    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key).push(file);
  }
  for (const group of groups.values()) {
    for (let index = 0; index < group.length; index += 1) {
      const left = group[index];

      for (const right of group.slice(index + 1)) {
        if (path.dirname(left) !== path.dirname(right) && path.basename(left) === path.basename(right)) {
          continue;
        }
        const reason = comparisonReason(path.basename(left), path.basename(right));

        if (reason) {
          for (const [file, peer] of [[left, right], [right, left]]) {
            if (!matches.has(file)) {
              matches.set(file, []);
            }
            matches.get(file).push(`${path.relative(path.dirname(file), peer)} (${reason})`);
          }
        }
      }
    }
  }
  return [...matches].sort(([left], [right]) => left < right ? -1 : Number(left > right)).map(([file, peers]) => ({
    directory: path.dirname(file), file, kind: 'similar-filename',
    message: `Similar filename(s): ${peers.sort().join('; ')}. Prefer responsibility-based names.`,
  }));
}
