// Helper for tools/crosscheck.py — read inputs JSON, emit JS-port outputs JSON.
// argv: <inputs.json> <outputs.json>   inputs = { str: [...], num: [[...],...] }
import { readFileSync, writeFileSync } from 'node:fs';
import * as su from '../js/index.mjs';

const STR_FNS = ['to_slp1', 'from_slp1', 'deva_to_iast', 'iast_to_devanagari', 'norm', 'nfold', 'form_key', 'normalize_sanskrit'];
const inp = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const fn of STR_FNS) out[fn] = inp.str.map((s) => su[fn](s));
out.to_roman = inp.num.map((n) => su.to_roman(n));
writeFileSync(process.argv[3], JSON.stringify(out));
