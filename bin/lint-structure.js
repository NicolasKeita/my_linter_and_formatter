#!/usr/bin/env node

import path from 'node:path';
import process from 'node:process';

import { defaultIgnoredNames, scanStructure } from '../structure.js';

const args = process.argv.slice(2);
const ignoredNames = [...defaultIgnoredNames];
let rootDirectory;
let maxFiles = 10;
let strict = false;

try {
  for (let index = 0; index < args.length; index += 1) {
    const argument = args[index];

    if (argument === '--strict') {
      strict = true;
    } else if (argument === '--max-files') {
      maxFiles = Number(args[++index]);
    } else if (argument === '--ignore') {
      const name = args[++index];

      if (!name || name.startsWith('-')) {
        throw new Error('--ignore requires a directory name.');
      }

      ignoredNames.push(name);
    } else if (argument.startsWith('-')) {
      throw new Error(`Unknown option: ${argument}`);
    } else if (rootDirectory) {
      throw new Error('Provide only one root directory.');
    } else {
      rootDirectory = argument;
    }
  }

  if (!rootDirectory) {
    throw new Error('Usage: nk-lint-structure <directory> [--max-files N] [--ignore NAME] [--strict]');
  }

  const diagnostics = scanStructure(rootDirectory, { maxFiles, ignore: ignoredNames });

  for (const diagnostic of diagnostics) {
    const directory = path.relative(process.cwd(), diagnostic.directory) || '.';

    if (diagnostic.kind === 'empty-directory') {
      process.stdout.write(`${directory}: empty directory\n`);
    } else {
      process.stdout.write(`${directory}: ${diagnostic.fileCount} files (maximum ${diagnostic.maxFiles})\n`);
    }
  }

  if (strict && diagnostics.length > 0) {
    process.exitCode = 1;
  }
} catch (error) {
  process.stderr.write(`${error.message}\n`);
  process.exitCode = 2;
}
