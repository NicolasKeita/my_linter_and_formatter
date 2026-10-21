import path from 'node:path';

import { editDistance } from './distance.js';

const separators = /[_\s\-\u2010-\u2015\u2212]+/gu;
const invisible = /[\u200b-\u200d\u2060\ufeff]/gu;
const numberedEnd = /(?:(?:part|chunk|split)[_\s-]*)?\p{Decimal_Number}+$/u;
const roles = ['.test', '.spec', '.stories', '.d'];

export function nameParts(name) {
  const extension = path.extname(name);
  const stem = name.slice(0, -extension.length);
  const suffix = roles.find((role) => stem.toLowerCase().endsWith(role));

  return suffix ? [stem.slice(0, -suffix.length), suffix + extension.toLowerCase()] : [stem, extension.toLowerCase()];
}

function normalized(stem) {
  return stem.normalize('NFKC').toLowerCase().replace(invisible, '');
}

export function baseName(stem) {
  let value = normalized(stem).replace(separators, '_');

  for (;;) {
    const previous = value;

    value = value.replace(/^_+|_+$/gu, '').replace(numberedEnd, '').replace(/^_+|_+$/gu, '');
    if (value === previous) {
      return value.replaceAll('_', '');
    }
  }
}

export function comparisonReason(left, right) {
  const [leftStem, leftRole] = nameParts(left);
  const [rightStem, rightRole] = nameParts(right);
  const first = baseName(leftStem);
  const second = baseName(rightStem);

  if (leftRole !== rightRole || !first || !second) {
    return undefined;
  }
  if (first === second) {
    return 'same normalized base (numbering, separators or case)';
  }
  const lengths = [Array.from(first).length, Array.from(second).length];
  const length = Math.max(...lengths);

  if (Math.min(...lengths) < 6 || Math.abs(lengths[0] - lengths[1]) * 100 > length * 15) {
    return undefined;
  }
  const distance = editDistance(first, second);

  return distance * 100 <= length * 15
    ? `similarity ${(100 * (length - distance) / length).toFixed(1)}% (threshold 85%)`
    : undefined;
}
