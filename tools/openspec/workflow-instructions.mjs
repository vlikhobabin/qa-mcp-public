// Read unchanged stock workflow instructions from this installed pinned package.
// The caller supplies a sanitized Node environment; no downloads or global import.
import './check-install.mjs';
import { readFileSync, realpathSync } from 'node:fs';
import { dirname, relative, resolve, sep } from 'node:path';
import { pathToFileURL } from 'node:url';

const workflows = {
  apply: ['apply-change', 'getApplyChangeSkillTemplate'],
  sync: ['sync-specs', 'getSyncSpecsSkillTemplate'],
  verify: ['verify-change', 'getVerifyChangeSkillTemplate'],
};
try {
  if (process.argv.length !== 3 || !Object.hasOwn(workflows, process.argv[2])) {
    throw new Error('expected exactly one workflow: apply, sync, verify');
  }
  const dependency = dirname(resolve(process.argv[1]));
  const packageRoot = realpathSync(resolve(dependency, 'node_modules/@fission-ai/openspec'));
  const manifest = JSON.parse(readFileSync(resolve(packageRoot, 'package.json'), 'utf8'));
  if (manifest.version !== '1.3.1') throw new Error('unsupported workflow package');
  const [file, factory] = workflows[process.argv[2]];
  const source = realpathSync(resolve(packageRoot, `dist/core/templates/workflows/${file}.js`));
  const offset = relative(packageRoot, source);
  if (offset === '..' || offset.startsWith(`..${sep}`)) {
    throw new Error('workflow source escapes installed package');
  }
  const module = await import(pathToFileURL(source).href);
  const instructions = module[factory]().instructions;
  if (typeof instructions !== 'string' || !instructions.trim()) {
    throw new Error('missing stock workflow instructions');
  }
  process.stdout.write(instructions);
} catch (error) {
  console.error(`openspec workflow: ${error.message}`);
  process.exitCode = 1;
}
