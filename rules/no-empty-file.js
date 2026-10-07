export default {
  meta: {
    type: 'problem',
    docs: {
      description: 'Disallow empty files',
    },
    schema: [],
  },

  create(context) {
    return {
      Program(node) {
        const sourceCode = context.sourceCode;
        const text = sourceCode.getText().trim();

        if (text.length === 0) {
          context.report({
            node,
            message: 'Empty file.',
          });
        }
      },
    };
  },
};
