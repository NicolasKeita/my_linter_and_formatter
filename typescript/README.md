# eslint-config-nicolaskeita

Shared ESLint flat config for JavaScript and TypeScript projects, with formatting preferences and custom code rules. The package also provides a separate command for directory checks.

## Use in another project

Install the published package from [npm](https://www.npmjs.com/package/eslint-config-nicolaskeita):

```sh
npm install --save-dev eslint-config-nicolaskeita eslint typescript
```

For local development, install this package directory with `npm install --save-dev ../my_linter_and_formatter/typescript` from a sibling project. To share an unpublished change as an archive, run `npm pack` from `typescript/` and install the generated `.tgz` file in the other project.

Create `eslint.config.mjs` in the consuming project (this works with or without `"type": "module"` in its `package.json`):

```js
import config from 'eslint-config-nicolaskeita';

export default [
  ...config,
  { ignores: ['dist/', 'coverage/'] },
];
```

Add scripts to the consuming project's `package.json`:

```json
{
  "scripts": {
    "lint": "eslint src/ && nk-lint-structure src/",
    "format": "eslint src/ --fix"
  }
}
```

Append another config object after `...config` to override rules for a project. For example, `{ rules: { 'nk/no-french-comments': 'off' } }` disables that rule.

## Directory checks

`nk-lint-structure <directory>` reports empty directories and directories containing more than 10 direct files. It counts all files, including assets and files that ESLint does not parse. It ignores `.git`, `.next`, `node_modules`, `dist`, `build`, and `coverage` by name. It exits successfully on warnings, matching the ESLint rule severity used in the portfolio.

Use `--max-files N` to change the threshold, `--ignore NAME` to skip another directory name, or `--strict` to exit with code 1 when warnings exist.

## Development

From the `typescript/` directory, install dependencies and run the checks:

```sh
npm ci
npm run lint
npm test
```

Use `npm run format` to apply automatic formatting fixes. This repository uses its own ESLint configuration and does not depend on a consuming project.

## Publishing

Source code is maintained in [NicolasKeita/my_linter_and_formatter](https://github.com/NicolasKeita/my_linter_and_formatter/tree/main/typescript). Consuming projects install releases from npm.

From the package directory, inspect the archive before publishing:

```sh
npm pack --dry-run
```

For a new release, update the version in `package.json` and `plugin.js`, then refresh `package-lock.json` with `npm install --package-lock-only`. Published versions cannot be overwritten.

When ready to publish, use `npm publish` from this directory with an npm account that can publish the package name. The `prepublishOnly` script runs `npm test` first and aborts publication if the tests fail. `npm pack --dry-run` checks the archive contents but does not run that hook.

## License

This package is licensed under the MIT License; see [LICENSE](./LICENSE).
