// no-comments-in-functions.js

export default {
  meta: {
    type: "suggestion",
    docs: {
      description: "Disallow comments inside functions and TypeScript interfaces",
    },
    messages: {
      avoidComments:
        "Comments are not allowed here. Prefer self-explanatory code.",
    },
    schema: [],
  },

  create(context) {
    const sourceCode = context.sourceCode;

    const forbiddenParents = new Set([
      "FunctionDeclaration",
      "FunctionExpression",
      "ArrowFunctionExpression",
      "TSInterfaceBody",
    ]);

    return {
      Program() {
        const comments = sourceCode.getAllComments();

        for (const comment of comments) {
          let node = sourceCode.getNodeByRangeIndex(comment.range[0]);

          while (node) {
            if (forbiddenParents.has(node.type)) {
              context.report({
                loc: comment.loc,
                messageId: "avoidComments",
              });
              break;
            }

            node = node.parent;
          }
        }
      },
    };
  },
};
