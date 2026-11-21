import { editDistance } from './distance.js';
import { baseName, nameParts } from './identity.js';
import { differingWordsMatch } from './words.js';

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

  return distance * 100 <= length * 15 && differingWordsMatch(leftStem, rightStem)
    ? `similarity ${(100 * (length - distance) / length).toFixed(1)}% (global and differing words >=85%)`
    : undefined;
}
