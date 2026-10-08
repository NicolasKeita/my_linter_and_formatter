import { franc } from 'franc';

const IGNORED_TOKENS = /\b(TODO|FIXME|NOTE|XXX)\b/gi;
const MIN_LENGTH = 20;

export default {
  meta: {
    type: 'problem',
    docs: {
      description: 'Warn when comments are written in French instead of English',
    },
    schema: [],
  },

  create(context) {
    return {
      Program() {
        const comments = context.sourceCode.getAllComments();

        for (const comment of comments) {
          const text = comment.value
            .replace(IGNORED_TOKENS, '')
            .trim();

          if (text.length < MIN_LENGTH) {
            continue;
          }

          const language = franc(text);

          if (language === 'fra') {
            context.report({
              loc: comment.loc,
              message: 'Comment must be written in English.',
            });
          }
        }
      },
    };
  },
};
