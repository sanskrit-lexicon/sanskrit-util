# -*- coding: utf-8 -*-
"""Generate vectors/vectors.json from the sanskrit_util package, and regression-check the
extracted package against the ORIGINAL donor (WhitneyRoots/scripts/sanskrit_util.py) for the
six functions that came from there.

Run:  python tools/gen_vectors.py
The JSON is the single golden-output set asserted by BOTH the Python and the JS test suites,
so a mismatch in either language is a test failure (cross-language equivalence lock).
"""
import sys
import os
import json
import importlib.util

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'py'))
import sanskrit_util as su  # noqa: E402

# ---- curated inputs (edge cases first) -------------------------------------
A = '́'   # combining acute  (pitch accent on a vowel; also the codepoint inside ś)
G = '̀'   # combining grave
STR_INPUTS = [
    '', ' ', 'agni', 'rama', 'śiva', 'Śiva', 'KṚṢṆA', 'kṛṣṇa', 'rājan', 'saṃskṛta',
    'jñāna', 'aiśvarya', 'auṣadha', 'ṭīkā', 'ḍamaru', 'buddha', 'kāṅkṣ', 'aṃśa',
    'saṃ', 'am', 'an', 'kram', 'gacchan', '  Agni  ', 'vāc', 'sañjaya',
    # accent / visarga / placeholder edge cases for form_key
    'krānta', 'krāṃta', 'kranta', 'rāmaḥ', 'devá'.replace('á', 'a' + A),
    'agniḥ'.replace('i', 'i' + A), 'śas', 'ā' + A, 'sá'.replace('á', 'a' + A) + 's',
    '-', '–', '—',
    # Devanāgarī (norm/nfold/deva_to_iast are Devanāgarī-aware)
    'धर्म', 'कृष्ण', 'सञ्जय', 'गच्छति', 'अग्नि', 'राजन्', 'सुखं', 'विद्या', 'अऽपि',
]
# SLP1 inputs for from_slp1
SLP1_INPUTS = ['', 'Siva', 'kfzRa', 'jYAna', 'saMskftam', 'EkSvarya', 'OzaDa', 'aMSa', 'BAva', 'rAjan']
# SLP1 inputs for the SLP1-side helpers: accents (/ \ ^ ~), trailing homonym digits, whitespace,
# avagraha, the Vedic L, case (S=ś), visarga/anusvāra for the compare key.
SLP1_NORM_INPUTS = [
    '', 'agni', 'agni2', 'aMSa', 'a/MSa', 'aMSa3', 'kf/zRa', 'Si^va', 'a~Nga', 'rAma\\',
    '  agni  ', 'deva 2', "aDo'MSukaM", 'mfL', 'saMskftam2', 'BAvaH', 'Siva', 'aMSaH', 'anSa',
]
# gaṇa-number lists for to_roman
NUM_INPUTS = [[], [1], [1, 2, 3], [4, 9, 10], [11], [0, 1, 10, 99], [5, 5, 6]]


def build():
    v = {}
    v['to_slp1'] = [{'in': s, 'out': su.to_slp1(s)} for s in STR_INPUTS]
    v['from_slp1'] = [{'in': s, 'out': su.from_slp1(s)} for s in SLP1_INPUTS]
    v['to_roman'] = [{'in': n, 'out': su.to_roman(n)} for n in NUM_INPUTS]
    v['deva_to_iast'] = [{'in': s, 'out': su.deva_to_iast(s)} for s in STR_INPUTS]
    v['iast_to_devanagari'] = [{'in': s, 'out': su.iast_to_devanagari(s)} for s in STR_INPUTS]
    v['norm'] = [{'in': s, 'out': su.norm(s)} for s in STR_INPUTS]
    v['nfold'] = [{'in': s, 'out': su.nfold(s)} for s in STR_INPUTS]
    v['form_key'] = [{'in': s, 'out': su.form_key(s)} for s in STR_INPUTS]
    v['normalize_sanskrit'] = [{'in': s, 'out': su.normalize_sanskrit(s)} for s in STR_INPUTS]
    v['strip_slp1_accents'] = [{'in': s, 'out': su.strip_slp1_accents(s)} for s in SLP1_NORM_INPUTS]
    v['slp1_norm'] = [{'in': s, 'out': su.slp1_norm(s)} for s in SLP1_NORM_INPUTS]
    v['slp1_form_key'] = [{'in': s, 'out': su.slp1_form_key(s)} for s in SLP1_NORM_INPUTS]
    return v


def load_donor():
    """Load the original WhitneyRoots donor module by file path (not import name)."""
    p = os.path.join(ROOT, '..', 'WhitneyRoots', 'scripts', 'sanskrit_util.py')
    p = os.path.abspath(p)
    if not os.path.exists(p):
        return None
    if '_sanskrit_util_shared' in open(p, encoding='utf-8').read():
        return 'SHIM'   # donor file is now the re-export shim → no independent donor to compare
    spec = importlib.util.spec_from_file_location('_donor_su', p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def regression(donor):
    """Assert the extracted package reproduces the donor for the six donor-origin functions.
    norm/nfold are compared only on non-Devanāgarī inputs: the package intentionally unifies
    those to be Devanāgarī-aware (matching reader.js), which the IAST-only donor lacks."""
    fails = []
    for s in STR_INPUTS:
        if su.to_slp1(s) != donor.to_slp1(s):
            fails.append(('to_slp1', s))
        if su.form_key(s) != donor.form_key(s):
            fails.append(('form_key', s))
        if not su._DEVA_RE.search(s):
            if su.norm(s) != donor.norm(s):
                fails.append(('norm', s))
            if su.nfold(s) != donor.nfold(s):
                fails.append(('nfold', s))
    for s in SLP1_INPUTS:
        if su.from_slp1(s) != donor.from_slp1(s):
            fails.append(('from_slp1', s))
    for n in NUM_INPUTS:
        if su.to_roman(n) != donor.to_roman(n):
            fails.append(('to_roman', tuple(n)))
    return fails


def main():
    vectors = build()
    out = os.path.join(ROOT, 'vectors', 'vectors.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(vectors, f, ensure_ascii=False, indent=1)
    total = sum(len(x) for x in vectors.values())
    print(f'wrote {out}: {total} vectors across {len(vectors)} functions')

    donor = load_donor()
    if donor is None:
        print('DONOR NOT FOUND (WhitneyRoots/scripts/sanskrit_util.py) — skipped regression')
        return 0
    if donor == 'SHIM':
        print('donor is now the re-export shim — regression already locked at extraction; skipped')
        return 0
    fails = regression(donor)
    if fails:
        print(f'REGRESSION MISMATCH vs donor ({len(fails)}):')
        for fn, s in fails[:20]:
            print(f'  {fn}({s!r}): pkg={getattr(su, fn)(s)!r} donor={getattr(donor, fn)(s)!r}')
        return 1
    print('regression OK: package reproduces donor on all 6 donor-origin functions')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
