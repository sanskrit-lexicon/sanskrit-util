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
    # H1394 iast_to_devanagari regression set (9 basic words wrong under the old naive
    # substitution; the rest of this word already appear above/below): ka, kṣa, rāma, tvam,
    # śrī, dharma (agni, buddha, saṃskṛta already present; saṁskṛta/ṁ added further below).
    'ka', 'kṣa', 'rāma', 'tvam', 'śrī', 'dharma',
    'jñāna', 'aiśvarya', 'auṣadha', 'ṭīkā', 'ḍamaru', 'buddha', 'kāṅkṣ', 'aṃśa',
    'saṃ', 'am', 'an', 'kram', 'gacchan', '  Agni  ', 'vāc', 'sañjaya',
    # ṁ (U+1E41, m-with-dot-above) -> M on the IAST->SLP1 side: the named blocker for dropping
    # sanscript from SamudraManthanam. NFD/form_key must also treat it like anusvāra ṃ.
    'saṁskṛta', 'ṁ',
    # accent / visarga / placeholder edge cases for form_key
    'krānta', 'krāṃta', 'kranta', 'rāmaḥ', 'devá'.replace('á', 'a' + A),
    'agniḥ'.replace('i', 'i' + A), 'śas', 'ā' + A, 'sá'.replace('á', 'a' + A) + 's',
    '-', '–', '—',
    # Devanāgarī (norm/nfold/deva_to_iast are Devanāgarī-aware)
    'धर्म', 'कृष्ण', 'सञ्जय', 'गच्छति', 'अग्नि', 'राजन्', 'सुखं', 'विद्या', 'अऽपि',
]
# Devanāgarī inputs for deva_to_slp1 — the Devanāgarī subset of STR_INPUTS plus the retroflex-ḻa
# (ळ) cases that motivate the direct transcode: ळ → 'L' must NOT collapse onto vocalic ḷ (ऌ /
# the ◌ॢ mātrā), which is 'x'. 'अग्निमीळे' = RV 1.1.1 incipit; 'खेळ' = Marathi; 'कॢप्त' = kḷpta.
DEVA_SLP1_INPUTS = [
    '', 'धर्म', 'कृष्ण', 'सञ्जय', 'गच्छति', 'अग्नि', 'राजन्', 'सुखं', 'विद्या', 'अऽपि',
    'ळ', 'खेळ', 'अग्निमीळे', 'ऌ', 'कॢप्त',
]
# SLP1 inputs for from_slp1
SLP1_INPUTS = ['', 'Siva', 'kfzRa', 'jYAna', 'saMskftam', 'EkSvarya', 'OzaDa', 'aMSa', 'BAva', 'rAjan']
# SLP1 inputs for the SLP1-side helpers: accents (/ \ ^ ~), trailing homonym digits, whitespace,
# avagraha, the Vedic L, case (S=ś), visarga/anusvāra for the compare key.
SLP1_NORM_INPUTS = [
    '', 'agni', 'agni2', 'aMSa', 'a/MSa', 'aMSa3', 'kf/zRa', 'Si^va', 'a~Nga', 'rAma\\',
    '  agni  ', 'deva 2', "aDo'MSukaM", 'mfL', 'saMskftam2', 'BAvaH', 'Siva', 'aMSaH', 'anSa',
]
# SLP1 inputs for slp1_to_devanagari — alphabet coverage + conjuncts, inherent 'a', mātrās,
# independent vowels, marks (M/H anusvāra/visarga), the Vedic L, avagraha ('), and the two
# documented not-round-trip-stable cases (candrabindu ~, avagraha) so their output is pinned.
SLP1_TO_DEVA_INPUTS = [
    '', 'agni', 'Darma', 'kfzRa', 'saMskftam', 'rAmaH', 'budDa', 'jYAna', 'aMSa', 'La',
    'agnimILe', 'sarva', 'veda', 'k', 'kya', 'tsya', 'a', 'A',
    'i', 'I', 'f', 'F', 'x', 'X', 'e', 'E', 'o', 'O', 'M', 'H', "ta'", 'a~', 'aMga',
]
# SLP1 inputs for slp1_simplify — the fuzzy-match key; guRa/kaRa pin the critical R->n (guṇa,
# NOT gūna); the rest exercise every fold branch (aspirates, sibilants, nasals, long/vocalic).
SLP1_SIMPLIFY_INPUTS = [
    '', 'guRa', 'kaRa', 'kfzRa', 'aMSa', 'BAva', 'jYAna', 'EkSvarya', 'OzaDa', 'saMskftam',
    'DarmakzetraM', 'buDa', 'pfTivI', 'agniH', 'La', 'WIkA', 'QAmara',
]
# gaṇa-number lists for to_roman
NUM_INPUTS = [[], [1], [1, 2, 3], [4, 9, 10], [11], [0, 1, 10, 99], [5, 5, 6]]
# German-apparatus inputs for classify_german_metalanguage — the H2787 defect tokens
# (eines, im Comp., so, Ergänzung), the H2684 repair extras (demin., personif.,
# Uebertr.), the harvested grammar/formula inventories, and the negative cases that
# pin mid-text function words / ordinary gloss prose to [] (Name eines Baumes).
GERMAN_META_INPUTS = [
    '', 'eines', 'die', 'so', 'so wie', 'Ergänzung',
    'im Comp. vorangehend', 'im Comp.', 'im Comp., vorangehend',
    'demin.', 'personif.', 'Uebertr.', 'uebertr.', 'vgl.', 's. u. d. W.',
    'adj.', 'm. f. n.', 'comp.', 'Akk', 'Subst mfn', 'dass.',
    'am Ende eines Comp.', 'am Anf. eines Comp.', 'an der Spitze eines Comp.',
    'mit Ergänzung von', 'in Verbindung mit', 'u.s.w.',
    'Name eines Baumes', 'gewachsen', 'Gabe, Geschenk', 'das Nichthandeln',
    'Die Ergänzung geht im Comp. voran', '  eines  ', 'vgl. das Vorhergehende',
]


def build():
    v = {}
    v['to_slp1'] = [{'in': s, 'out': su.to_slp1(s)} for s in STR_INPUTS]
    v['from_slp1'] = [{'in': s, 'out': su.from_slp1(s)} for s in SLP1_INPUTS]
    v['to_roman'] = [{'in': n, 'out': su.to_roman(n)} for n in NUM_INPUTS]
    v['deva_to_iast'] = [{'in': s, 'out': su.deva_to_iast(s)} for s in STR_INPUTS]
    v['deva_to_slp1'] = [{'in': s, 'out': su.deva_to_slp1(s)} for s in DEVA_SLP1_INPUTS]
    v['iast_to_devanagari'] = [{'in': s, 'out': su.iast_to_devanagari(s)} for s in STR_INPUTS]
    v['norm'] = [{'in': s, 'out': su.norm(s)} for s in STR_INPUTS]
    v['nfold'] = [{'in': s, 'out': su.nfold(s)} for s in STR_INPUTS]
    v['form_key'] = [{'in': s, 'out': su.form_key(s)} for s in STR_INPUTS]
    v['normalize_sanskrit'] = [{'in': s, 'out': su.normalize_sanskrit(s)} for s in STR_INPUTS]
    v['strip_slp1_accents'] = [{'in': s, 'out': su.strip_slp1_accents(s)} for s in SLP1_NORM_INPUTS]
    v['slp1_norm'] = [{'in': s, 'out': su.slp1_norm(s)} for s in SLP1_NORM_INPUTS]
    v['slp1_form_key'] = [{'in': s, 'out': su.slp1_form_key(s)} for s in SLP1_NORM_INPUTS]
    v['slp1_to_devanagari'] = [{'in': s, 'out': su.slp1_to_devanagari(s)} for s in SLP1_TO_DEVA_INPUTS]
    v['slp1_simplify'] = [{'in': s, 'out': su.slp1_simplify(s)} for s in SLP1_SIMPLIFY_INPUTS]
    v['classify_german_metalanguage'] = [
        {'in': s, 'out': su.classify_german_metalanguage(s)} for s in GERMAN_META_INPUTS]
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


def slp1_set_regression():
    """Lock the SLP1 character-class constants against the INDEPENDENT donor definition in
    SanskritSpellCheck/detectors/slp1util.py. The donor now imports these from sanskrit-util at
    runtime, so comparing the live module would be tautological — instead extract the hardcoded
    literals from the donor's `except ImportError:` fallback branch (its own source of truth) and
    compare verbatim. Returns [] if the donor sibling is absent (skipped), else a list of failures."""
    p = os.path.abspath(os.path.join(ROOT, '..', 'SanskritSpellCheck', 'detectors', 'slp1util.py'))
    if not os.path.exists(p):
        return None
    src = open(p, encoding='utf-8').read()
    import re as _re
    donor = {}
    for name, key in (('VOWELS', 'SLP1_VOWELS'), ('MARKS', 'SLP1_MARKS'), ('CONSONANTS', 'SLP1_CONSONANTS')):
        m = _re.search(name + r'\s*=\s*set\("([^"]*)"\)', src)   # the fallback-branch literal
        if m:
            donor[key] = m.group(1)
    fails = []
    for key, lit in donor.items():
        if set(getattr(su, key)) != set(lit):
            fails.append((key, getattr(su, key), lit))
    return fails


def roundtrip_check():
    """Property test: for canonical SLP1, deva_to_slp1(slp1_to_devanagari(s)) == s. Runs over the
    full alphabet (minus candrabindu ~ / avagraha, which are documented as not round-trip stable)
    plus the real-lemma sample in vectors/slp1_roundtrip_sample.txt (1000 MW <k1> headwords)."""
    alpha = su.SLP1_VOWELS + 'MH' + su.SLP1_CONSONANTS
    fails = [c for c in alpha if su.deva_to_slp1(su.slp1_to_devanagari(c)) != c]
    sample_path = os.path.join(ROOT, 'vectors', 'slp1_roundtrip_sample.txt')
    n = 0
    if os.path.exists(sample_path):
        with open(sample_path, encoding='utf-8') as f:
            for line in f:
                w = line.rstrip('\n')
                if not w or w.startswith('#'):
                    continue
                n += 1
                if su.deva_to_slp1(su.slp1_to_devanagari(w)) != w:
                    fails.append(w)
    return fails, len(alpha), n


def main():
    vectors = build()
    out = os.path.join(ROOT, 'vectors', 'vectors.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(vectors, f, ensure_ascii=False, indent=1)
    total = sum(len(x) for x in vectors.values())
    print(f'wrote {out}: {total} vectors across {len(vectors)} functions')

    rc = 0

    # SLP1 set constants locked against the SanskritSpellCheck donor's independent literals
    set_fails = slp1_set_regression()
    if set_fails is None:
        print('SLP1-set donor NOT FOUND (SanskritSpellCheck/detectors/slp1util.py) — skipped')
    elif set_fails:
        print(f'SLP1-SET MISMATCH vs donor ({len(set_fails)}):')
        for key, got, lit in set_fails:
            print(f'  {key}: pkg={got!r} donor={lit!r}')
        rc = 1
    else:
        print('SLP1-set OK: SLP1_VOWELS/MARKS/CONSONANTS set-equal to slp1util.py donor literals')

    # SLP1 <-> Devanāgarī round-trip property test (alphabet + real MW headwords)
    rt_fails, nalpha, nlemmas = roundtrip_check()
    if rt_fails:
        print(f'ROUND-TRIP FAIL ({len(rt_fails)}): deva_to_slp1(slp1_to_devanagari(s)) != s')
        for s in rt_fails[:20]:
            print(f'  {s!r} -> {su.slp1_to_devanagari(s)!r} -> {su.deva_to_slp1(su.slp1_to_devanagari(s))!r}')
        rc = 1
    else:
        print(f'round-trip OK: {nalpha} alphabet chars + {nlemmas} real MW headwords survive SLP1->Deva->SLP1')

    # WhitneyRoots donor regression on the six donor-origin functions
    donor = load_donor()
    if donor is None:
        print('DONOR NOT FOUND (WhitneyRoots/scripts/sanskrit_util.py) — skipped regression')
    elif donor == 'SHIM':
        print('donor is now the re-export shim — regression already locked at extraction; skipped')
    else:
        fails = regression(donor)
        if fails:
            print(f'REGRESSION MISMATCH vs donor ({len(fails)}):')
            for fn, s in fails[:20]:
                print(f'  {fn}({s!r}): pkg={getattr(su, fn)(s)!r} donor={getattr(donor, fn)(s)!r}')
            rc = 1
        else:
            print('regression OK: package reproduces donor on all 6 donor-origin functions')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
