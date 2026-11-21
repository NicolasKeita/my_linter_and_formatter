import { editDistance } from './distance.js';
import { nameBody } from './identity.js';

export function splitWords(stem) {
  return nameBody(stem)
    .replace(/([\p{Ll}\p{Nd}])(\p{Lu})/gu, '$1_$2')
    .replace(/(\p{Lu})(\p{Lu}\p{Ll})/gu, '$1_$2')
    .split('_').filter(Boolean).map((word) => word.toLowerCase());
}

export function differingWordsMatch(left, right) {
  const first = splitWords(left);
  const second = splitWords(right);

  if (first.length !== second.length) {
    return false;
  }
  return first.length > 0 && first.every((word, index) => {
    const other = second[index];
    const lengths = [Array.from(word).length, Array.from(other).length];
    const length = Math.max(...lengths);

    return word === other || (Math.abs(lengths[0] - lengths[1]) * 100 <= length * 15
      && editDistance(word, other) * 100 <= length * 15);
  });
}
