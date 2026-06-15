# -*- coding: utf-8 -*-
"""Adversarial 3-way equivalence check: package-Python vs JS-port vs original donor, over a
large/arbitrary input set (real corpus words + exotic Unicode). Catches divergences the curated
golden vectors miss.

Usage:
  python tools/crosscheck.py [corpus_file ...]
Each corpus_file is newline-delimited test strings (e.g. real IAST headwords). Built-in exotic
cases are always included. Exit 0 iff package==JS on all 9 functions AND package==donor on the 6
donor-origin functions (norm/nfold compared on non-Devanāgarī inputs only — the package unifies
those to be Devanāgarī-aware by design)."""
import sys
import os
import json
import subprocess
import importlib.util

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'py'))
import sanskrit_util as su  # noqa: E402

STR_FNS = ['to_slp1', 'from_slp1', 'deva_to_iast', 'iast_to_devanagari', 'norm', 'nfold', 'form_key', 'normalize_sanskrit']
DONOR_STR_FNS = ['to_slp1', 'from_slp1', 'form_key']           # always comparable
DONOR_NORM_FNS = ['norm', 'nfold']                            # compare on non-Devanāgarī only

ACUTE, GRAVE, SVAR, ANUD = '́', '̀', '॑', '॒'
ZWJ, ZWNJ, NBSP = '‍', '‌', ' '
EXOTIC = [
    '', ' ', '\t', NBSP, ZWJ, ZWNJ,
    'a' + ACUTE, 'ā' + ACUTE, 'i' + GRAVE, 's' + ACUTE, 'ś', 'ṣ' + ACUTE,
    'agni' + SVAR, 'devá'.replace('á', 'a' + ACUTE), 'índra'.replace('í', 'i' + ACUTE),
    'kṛṣṇa' + ANUD, 'धर्मं', 'अग्निः', 'क्ष्म्य', 'श्री', 'ॐ', 'a‍b', 'ṛṝḷḹ',
    'AÁBC', 'XYZ123', 'saṃskṛtam', 'kāṃkṣ', 'tat tvam asi', 'kó',
]


def load_donor():
    p = os.path.abspath(os.path.join(ROOT, '..', 'WhitneyRoots', 'scripts', 'sanskrit_util.py'))
    if not os.path.exists(p):
        return None
    # load by file path under a private name so it doesn't collide with the package
    src = open(p, encoding='utf-8').read()
    if 'spec_from_file_location(\'_sanskrit_util_shared\'' in src or '_sanskrit_util_shared' in src:
        return 'SHIM'   # the donor file has been turned into the shim → no independent donor here
    spec = importlib.util.spec_from_file_location('_donor_su', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def collect_inputs(argv):
    strs = list(EXOTIC)
    for fpath in argv:
        if os.path.exists(fpath):
            with open(fpath, encoding='utf-8') as f:
                for line in f:
                    w = line.rstrip('\n')
                    if w:
                        strs.append(w)
    # dedupe, keep order
    seen, out = set(), []
    for s in strs:
        if s not in seen:
            seen.add(s); out.append(s)
    nums = [[], [1], [1, 4, 10], [11], [0, 3, 7, 10], list(range(1, 12))]
    return {'str': out, 'num': nums}


def js_outputs(inp):
    inpath = os.path.join(HERE, '_xcheck_in.json')
    outpath = os.path.join(HERE, '_xcheck_out.json')
    with open(inpath, 'w', encoding='utf-8') as f:
        json.dump(inp, f, ensure_ascii=False)
    subprocess.run(['node', os.path.join(HERE, 'crosscheck_js.mjs'), inpath, outpath],
                   check=True, cwd=HERE)
    with open(outpath, encoding='utf-8') as f:
        res = json.load(f)
    os.remove(inpath); os.remove(outpath)
    return res


def main():
    inp = collect_inputs(sys.argv[1:])
    strs, nums = inp['str'], inp['num']
    py = {fn: [getattr(su, fn)(s) for s in strs] for fn in STR_FNS}
    py['to_roman'] = [su.to_roman(n) for n in nums]
    js = js_outputs(inp)

    fails = []
    for fn in STR_FNS + ['to_roman']:
        for i, (a, b) in enumerate(zip(py[fn], js[fn])):
            if a != b:
                key = strs[i] if fn != 'to_roman' else nums[i]
                fails.append(('py!=js', fn, key, a, b))

    donor = load_donor()
    donor_note = ''
    if donor in (None, 'SHIM'):
        donor_note = 'donor unavailable (file is the shim or missing) — skipped package-vs-donor'
    else:
        for fn in DONOR_STR_FNS:
            for s in strs:
                a, b = getattr(su, fn)(s), getattr(donor, fn)(s)
                if a != b:
                    fails.append(('py!=donor', fn, s, a, b))
        for fn in DONOR_NORM_FNS:
            for s in strs:
                if su._DEVA_RE.search(s):
                    continue
                a, b = getattr(su, fn)(s), getattr(donor, fn)(s)
                if a != b:
                    fails.append(('py!=donor', fn, s, a, b))
        for n in nums:
            if su.to_roman(n) != donor.to_roman(n):
                fails.append(('py!=donor', 'to_roman', n, su.to_roman(n), donor.to_roman(n)))

    n_checks = len(strs) * len(STR_FNS) + len(nums)
    print(f'inputs: {len(strs)} strings + {len(nums)} number-lists | ~{n_checks} cross-language checks')
    if donor_note:
        print('NOTE:', donor_note)
    if fails:
        print(f'DIVERGENCES: {len(fails)}')
        for kind, fn, key, a, b in fails[:40]:
            print(f'  [{kind}] {fn}({key!r}): {a!r}  vs  {b!r}')
        return 1
    print('OK: package-Python == JS-port on all 9 functions'
          + ('' if donor_note else ' AND == donor on the 6 donor-origin functions'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
