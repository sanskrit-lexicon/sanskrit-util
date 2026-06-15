// Assert the browser global build (sanskrit-util.global.js) exposes window.SanskritUtil and
// reproduces the golden vectors — i.e. global == ESM == Python. Run: node test/global.test.mjs
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const code = readFileSync(join(here, '..', 'sanskrit-util.global.js'), 'utf8');
(0, eval)(code); // indirect eval → global scope → sets globalThis.SanskritUtil
const SU = globalThis.SanskritUtil;
if (!SU) { console.error('FAIL: global build did not define SanskritUtil'); process.exit(1); }

const vectors = JSON.parse(readFileSync(join(here, '..', '..', 'vectors', 'vectors.json'), 'utf8'));
let pass = 0;
const fails = [];
for (const [fn, cases] of Object.entries(vectors)) {
  if (typeof SU[fn] !== 'function') { fails.push(`missing global export: ${fn}`); continue; }
  for (const { in: input, out: expected } of cases) {
    const got = SU[fn](input);
    if (JSON.stringify(got) === JSON.stringify(expected)) pass += 1;
    else fails.push(`${fn}(${JSON.stringify(input)}): global=${JSON.stringify(got)} expected=${JSON.stringify(expected)}`);
  }
}
if (fails.length) {
  console.error(`FAIL: ${fails.length} mismatch(es), ${pass} passed`);
  for (const f of fails.slice(0, 20)) console.error('  ' + f);
  process.exit(1);
}
console.log(`OK: global build matches ${pass} vectors (window.SanskritUtil == ESM == Python)`);
