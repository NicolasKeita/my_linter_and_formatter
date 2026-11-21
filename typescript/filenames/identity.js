import path from 'node:path';

const separators = /[_\s\-\u2010-\u2015\u2212]+/gu;
const invisible = /[\u200b-\u200d\u2060\ufeff]/gu;
const numberedEnd = /(?:(?:part|chunk|split)[_\s-]*)?\p{Decimal_Number}+$/iu;
const roles = ['.test', '.spec', '.stories', '.d'];

export function nameParts(name) {
  const extension = path.extname(name);
  const stem = name.slice(0, -extension.length);
  const suffix = roles.find((role) => stem.toLowerCase().endsWith(role));

  return suffix ? [stem.slice(0, -suffix.length), suffix + extension.toLowerCase()] : [stem, extension.toLowerCase()];
}

export function nameBody(stem) {
  let value = stem.normalize('NFKC').replace(invisible, '').replace(separators, '_');

  for (;;) {
    const previous = value;

    value = value.replace(/^_+|_+$/gu, '').replace(numberedEnd, '').replace(/^_+|_+$/gu, '');
    if (value === previous) {
      return value;
    }
  }
}

export function baseName(stem) {
  return nameBody(stem).replaceAll('_', '').toLowerCase();
}
