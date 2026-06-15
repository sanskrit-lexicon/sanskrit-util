// Cross-language equivalence test: assert the JS port reproduces vectors/vectors.json
// (which is generated from the Python package). Any divergence between the two ports
// fails here. Run: node test/vectors.test.mjs   (or: npm test)
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import * as su from '../index.mjs';

const here = dirname(fileURLToPath(import.meta.url));
const vectors = JSON.parse(readFileSync(join(here, '..', '..', 'vectors', 'vectors.json'), 'utf8'));

let pass = 0;
const fails = [];
for (const [fn, cases] of Object.entries(vectors)) {
  if (typeof su[fn] !== 'function') { fails.push(`missing export: ${fn}`); continue; }
  for (const { in: input, out: expected } of cases) {
    const got = su[fn](input);
    const g = JSON.stringify(got), e = JSON.stringify(expected);
    if (g === e) { pass += 1; }
    else fails.push(`${fn}(${JSON.stringify(input)}): js=${g} expected=${e}`);
  }
}

if (fails.length) {
  console.error(`FAIL: ${fails.length} mismatch(es), ${pass} passed`);
  for (const f of fails.slice(0, 30)) console.error('  ' + f);
  process.exit(1);
}
console.log(`OK: ${pass} vectors match across ${Object.keys(vectors).length} functions (JS == Python)`);
