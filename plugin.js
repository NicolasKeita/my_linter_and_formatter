import noCommentsInFunctions from './rules/no-comments-in-functions.js';
import noEmptyFile from './rules/no-empty-file.js';
import noFrenchComments from './rules/no-french-comments.js';

const plugin = {
  meta: {
    name: 'eslint-config-nicolaskeita',
    version: '0.1.0',
  },
  rules: {
    'no-comments-in-functions': noCommentsInFunctions,
    'no-empty-file': noEmptyFile,
    'no-french-comments': noFrenchComments,
  },
};

export default plugin;
