// Verify the pinned project-local entrypoint before executing upstream code.
import { readFileSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, relative, resolve, sep } from 'node:path';

const dependencyRoot = dirname(resolve(process.argv[1]));
const packageRoot = resolve(dependencyRoot, 'node_modules/@fission-ai/openspec');

function contained(candidate, parent) {
  const offset = relative(parent, candidate);
  return offset !== '..' && !offset.startsWith(`..${sep}`) && !isAbsolute(offset);
}

try {
  const [major, minor] = process.versions.node.split('.').map(Number);
  if (major < 20 || (major === 20 && minor < 19)) {
    throw new Error('Node.js >=20.19.0 is required');
  }
  const expected = JSON.parse(readFileSync(resolve(dependencyRoot, 'package.json'), 'utf8'))
    .dependencies['@fission-ai/openspec'];
  if (expected !== '1.3.1') {
    throw new Error('adapter compatibility is pinned to OpenSpec 1.3.1');
  }
  for (const candidate of [packageRoot, resolve(packageRoot, 'package.json'),
    resolve(packageRoot, 'bin/openspec.js')]) {
    if (!contained(realpathSync(candidate), realpathSync(dependencyRoot))) {
      throw new Error('OpenSpec dependency must remain inside tools/openspec');
    }
  }
  const installed = JSON.parse(readFileSync(resolve(packageRoot, 'package.json'), 'utf8'));
  if (installed.name !== '@fission-ai/openspec' || installed.version !== expected) {
    throw new Error(`expected @fission-ai/openspec ${expected}; found ${installed.name} ${installed.version}`);
  }
} catch (error) {
  const reason = error.code === 'ENOENT' ? 'project-local OpenSpec dependency is missing' : error.message;
  console.error(`openspec: ${reason}. Run tools/openspec/bootstrap.sh --offline after preparing the npm cache.`);
  process.exit(1);
}
