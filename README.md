# sanskrit-util

One **canonical** implementation of the Sanskrit string helpers that were being re-typed in
~20+ Sanskrit-Lexicon / CDSL repos: IAST ⇄ SLP1 ⇄ Devanāgarī transcoding plus the
normalization keys used for search, indexing and form comparison.

Python and JavaScript ports are **behaviour-identical**, proved on every commit by a shared
golden-vector set ([`vectors/vectors.json`](vectors/vectors.json)) that both test suites
assert against. The Python functions are extracted verbatim from
`WhitneyRoots/scripts/sanskrit_util.py` (regression-locked against that donor); the JS-origin
helpers (`deva_to_iast`, `iast_to_devanagari`, `normalize_sanskrit`) come from WhitneyRoots
`reader.js` / `src/utils/linguistics.js`.

## Why this exists

A file-name census across the GitHub root found `transcoder.py` in **62 copies / 7 versions**
and a dozen independently hand-rolled `to_slp1` / `norm` / `form_key` / `slug` / `hwnorm`
functions. Every one re-derives the same SLP1 table and re-hits the same Unicode traps
(`ś` = `s` + U+0301 collides with the pitch accent; NFD-then-strip destroys vowel length and
retroflex dots). This package ends that. See [`../SHARED_CODE.md`](../SHARED_CODE.md) for the
full cross-repo dedup map.

## API (identical in Python and JS)

| Function | Does |
|---|---|
| `to_slp1(iast)` | IAST → SLP1 (longest-key-first: `ai`→`E`, `kh`→`K`, `ṣ`→`z`) |
| `from_slp1(slp1)` | SLP1 → IAST |
| `to_roman(nums)` | `[1,4,10]` gaṇa numbers → `['I','IV','X']` |
| `deva_to_iast(s)` | Devanāgarī → IAST (inherent-`a` + virāma aware) |
| `iast_to_devanagari(s)` | IAST → Devanāgarī (**approximate, display only** — no conjunct shaping) |
| `norm(s)` | **exact** diacritic-insensitive key — Devanāgarī-aware; lookup/index |
| `nfold(s)` | `norm()` + every nasal folded to `n` — recall fallback only |
| `form_key(s)` | **length-preserving** compare key (`ā`≠`a`) — generated-vs-recorded forms |
| `normalize_sanskrit(s)` | **lossy** ASCII fold (`ā`→`a`, `ś`→`s`, `ṃ`→`m`) — v3-explorer parity |

### SLP1-side API (the CDSL dictionaries are SLP1-native)

The functions above are IAST/Devanāgarī-centric, but CDSL dictionary headwords are stored in
**SLP1**, where case is *phonemic* (`S`=ś ≠ `s`, `T`=th ≠ `t`). These work on SLP1 directly:

| Symbol | Does |
|---|---|
| `SLP1_VOWELS` `SLP1_MARKS` `SLP1_CONSONANTS` `SLP1_ALPHABET` | valid SLP1 character classes (strings; `set(...)` for membership) |
| `strip_slp1_accents(slp1)` | drop the SLP1 accent/candrabindu marks `/ \ ^ ~` |
| `slp1_norm(slp1)` | **headword key**: strip accents + trailing homonym digits, collapse space; **case preserved** |
| `slp1_form_key(slp1)` | **length-preserving compare key** for SLP1 forms = `form_key(from_slp1(…))` |

### Which key do I want?

- **Search / index lookup** → `norm` (and `nfold` as a fallback alias). Reversible-ish,
  diacritic-insensitive, keeps `am`/`an` distinct on the exact key.
- **Comparing two word forms** (vidyut output vs warnemyr vs DCS) → `form_key`. Length is
  meaningful: `krānta` (PPP) ≠ `kranta`; anusvāra folds to its homorganic nasal; the nom-sg
  visarga is stripped; pitch accents on vowels drop but `ś` and the retroflex dots survive.
- **A crude ASCII bucket** (you explicitly want no diacritics at all) → `normalize_sanskrit`.
  This is *lossy* and not the same as `norm`; prefer `norm` unless you really need bare ASCII.
- **A CDSL SLP1 headword key** (align `<k1>` across dictionaries) → `slp1_norm`. Strips accents
  and the trailing homonym index, keeps SLP1 case. The shared form of the per-repo
  `normalize_lemma` / `normalizeSlp1Lemma` headword normalizers. Use `slp1_form_key` to compare
  SLP1 *forms* (folds nasals/visarga like `form_key`).

## Use it

### Python
```bash
pip install -e py            # from this directory; editable install
```
```python
from sanskrit_util import to_slp1, form_key, norm
to_slp1('aiśvarya')   # 'ESvarya'
form_key('krāṃta')    # 'krānta'   (anusvāra → homorganic n, length kept)
norm('धर्म')           # 'dharma'   (Devanāgarī-aware)
```

### JavaScript (ESM)
```js
import { to_slp1, form_key, norm } from '@sanskrit-lexicon/sanskrit-util'; // or '../sanskrit-util/js/index.mjs'
to_slp1('aiśvarya'); // 'ESvarya'
```

### In a sibling repo without publishing (this GitHub-root layout)
Drop a 12-line re-export shim named `sanskrit_util.py` that loads
`../../sanskrit-util/py/sanskrit_util/__init__.py` by relative path — see the working example at
[`../WhitneyRoots/scripts/sanskrit_util.py`](../WhitneyRoots/scripts/sanskrit_util.py).

## Test

```bash
python tools/gen_vectors.py           # regenerate vectors.json + regression-check vs donor
python py/tests/test_units.py         # pitfall unit tests
python py/tests/test_vectors.py       # Python == golden
node   js/test/vectors.test.mjs       # JS == golden  (== Python)
```

## Layout

```
sanskrit-util/
  py/sanskrit_util/__init__.py   Python implementation (importable as `sanskrit_util`)
  py/tests/                      unit + vector tests
  js/index.mjs                   JS implementation (ESM)
  js/test/vectors.test.mjs       cross-language vector test
  vectors/vectors.json           golden outputs, shared by both test suites
  tools/gen_vectors.py           regenerate vectors + donor regression
```
