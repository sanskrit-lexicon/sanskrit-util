# sanskrit-util

_Created: 15-06-2026 · Last updated: 24-08-2026_

One **canonical** implementation of the Sanskrit string helpers that were being re-typed in
~20+ Sanskrit-Lexicon / CDSL repos: IAST ⇄ SLP1 ⇄ Devanāgarī transcoding plus the
normalization keys used for search, indexing and form comparison.

**Current release: v0.10.0** (2026-08-24) — see the
[GitHub releases](https://github.com/sanskrit-lexicon/sanskrit-util/releases) and
[`CHANGELOG.md`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/CHANGELOG.md).
Python and JS carry the same version (`py/pyproject.toml`, `js/package.json`,
`__version__`); npm name is `@sanskrit-lexicon/sanskrit-util`.

Python and JavaScript ports are **behaviour-identical**, proved on every commit by a shared
golden-vector set ([`vectors/vectors.json`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/vectors/vectors.json))
that both test suites assert against. The Python functions are extracted verbatim from
`WhitneyRoots/scripts/sanskrit_util.py` (regression-locked against that donor); the JS-origin
helpers (`deva_to_iast`, `iast_to_devanagari`, `normalize_sanskrit`) come from WhitneyRoots
`reader.js` / `src/utils/linguistics.js`.

## Why this exists

A file-name census across the GitHub root found `transcoder.py` in **62 copies / 7 versions**
and a dozen independently hand-rolled `to_slp1` / `norm` / `form_key` / `slug` / `hwnorm`
functions. Every one re-derives the same SLP1 table and re-hits the same Unicode traps
(`ś` = `s` + U+0301 collides with the pitch accent; NFD-then-strip destroys vowel length and
retroflex dots). This package ends that. See
[`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) §1–2 for
the full cross-repo dedup map.

## Who consumes it

This is the most-vendored shared package in the org. The **authoritative, always-current
consumer list** (with the exact version each repo vendors and the sync PR links) is
[`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md) §1–2 —
consult it rather than trusting a count here. As of v0.4.0 the registered consumers include:

- [WhitneyRoots](https://github.com/sanskrit-lexicon/WhitneyRoots) — the original **donor**, now
  a shim re-exporting the package.
- [csl-apidev](https://github.com/sanskrit-lexicon/csl-apidev) — vendored global build, re-synced to v0.4.0.
- [csl-guides](https://github.com/sanskrit-lexicon/csl-guides) — vendored `.js` copy for SLP1→IAST display.
- [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas) — normalizers delegate to the package + a vendored copy.
- [SanskritSpellCheck](https://github.com/sanskrit-lexicon/SanskritSpellCheck) — SLP1 alphabet/sets delegated via a shim.

After a version bump, re-vendor into every consumer with the
[`/cologne-sanskrit-util-sync`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
batch skill (detect stale copies, re-copy, byte-diff verify, one PR per consumer).

## API (identical in Python and JS)

| Function | Does |
|---|---|
| `to_slp1(iast)` | IAST → SLP1 (longest-key-first: `ai`→`E`, `kh`→`K`, `ṣ`→`z`) |
| `from_slp1(slp1)` | SLP1 → IAST |
| `to_roman(nums)` | `[1,4,10]` gaṇa numbers → `['I','IV','X']` |
| `deva_to_iast(s)` | Devanāgarī → IAST (inherent-`a` + virāma aware) |
| `deva_to_slp1(s)` | Devanāgarī → SLP1 (direct; `ळ`→`L`, not `x`) — round-trip partner of `from_slp1` |
| `iast_to_devanagari(s)` | IAST → Devanāgarī — real transcode (virāma/mātrā aware), implemented as `slp1_to_devanagari(to_slp1(s))` |
| `norm(s)` | **exact** diacritic-insensitive key — Devanāgarī-aware; lookup/index |
| `nfold(s)` | `norm()` + every nasal folded to `n` — recall fallback only |
| `form_key(s)` | **length-preserving** compare key (`ā`≠`a`) — generated-vs-recorded forms |
| `normalize_sanskrit(s)` | **lossy** ASCII fold (`ā`→`a`, `ś`→`s`, `ṃ`→`m`) — v3-explorer parity |

> **`iast_to_devanagari` was broken until H1394 (fixed 21-07-2026).** It used to apply neither
> mātrās nor virāma and emit an independent vowel for every vowel, so it was wrong on all basic
> words — `ka`→`कअ`, `rāma`→`रआमअ`, `dharma`→`धअरमअ`, `kṣa`→`कषअ`. It is now re-implemented as
> the `slp1_to_devanagari(to_slp1(s))` composition and is correct (regression-locked in
> `vectors/vectors.json` and the unit tests). There is still no Cyrillic support in the package.

### SLP1-side API (the CDSL dictionaries are SLP1-native)

The functions above are IAST/Devanāgarī-centric, but CDSL dictionary headwords are stored in
**SLP1**, where case is *phonemic* (`S`=ś ≠ `s`, `T`=th ≠ `t`). These work on SLP1 directly:

| Symbol | Does |
|---|---|
| `SLP1_VOWELS` `SLP1_MARKS` `SLP1_CONSONANTS` `SLP1_ALPHABET` | valid SLP1 character classes (strings; `set(...)` for membership) |
| `strip_slp1_accents(slp1)` | drop the SLP1 accent/candrabindu marks `/ \ ^ ~` |
| `slp1_norm(slp1)` | **headword key**: strip accents + trailing homonym digits, collapse space; **case preserved** |
| `slp1_form_key(slp1)` | **length-preserving compare key** for SLP1 forms = `form_key(from_slp1(…))` |
| `slp1_to_devanagari(slp1)` | SLP1 → Devanāgarī (**real** transcode: virāma conjuncts + mātrās) — round-trip partner of `deva_to_slp1` |
| `slp1_simplify(slp1)` | **lossy** fuzzy-match key: fold every SLP1 distinction to plain ASCII (`R`→`n`, `K`→`kh`, `S`→`s`) — MW index building |

### CDSL raw-source-line display (SLP1-in-markup → readable IAST)

A raw `csl-orig` line is SLP1 wrapped in CDSL markup, unreadable to a human. These render it to
IAST for display, honoring each dictionary's encoding. `code` is the csl-orig dict code (`mw`,
`ap`, `pwg`, `pw`, `wil`, `vcp`, `skd`). SLP1 is a machine key — show IAST to readers; keep raw
SLP1 behind an opt-in toggle for those who edit source.

| Symbol | Does |
|---|---|
| `source_line_to_iast(text, code)` | one raw source line → IAST: MW `<s>…</s>`, PW/PWG/AP/WIL `{#…#}` (meaning `{%…%}` kept), VCP/SKD whole-line prose; strips tags, `[Page…]`, the `¦` separator. `{#aBAga#}¦, <lex>f.</lex>` → `abhāga, f.` |
| `source_text_to_iast(text, code)` | multi-line snippet → IAST, line by line (preserves breaks) |

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
- **A fuzzy MW-index bucket** (match a query token against MW headwords ignoring every
  vowel-length / aspiration / retroflex / sibilant distinction) → `slp1_simplify`. This is the
  **lossy extreme** of the SLP1 key family (`slp1_norm` keeps everything but accents/digits;
  `slp1_form_key` keeps length + `ś` + retroflex dots; `slp1_simplify` keeps almost nothing).
  Critical: MW uses **standard SLP1** where `R`=ṇ, so `guṇa` = `guRa` → `guna` — forgetting
  `R`→`n` mis-reads it as `gūna`.
- **Render an SLP1 headword as Devanāgarī** → `slp1_to_devanagari`. A *real* transcode (supplies
  the virāma between clustered consonants and picks independent-vowel vs mātrā by position), so
  it is the round-trip partner of `deva_to_slp1`: `deva_to_slp1(slp1_to_devanagari(s)) == s` for
  canonical SLP1 (proved on the full alphabet + 1000 real MW headwords). This is also the correct
  IAST→Devanāgarī path: `slp1_to_devanagari(to_slp1(iast))` (the standalone `iast_to_devanagari`
  is broken — see above). Candrabindu (`~`→ँ) folds back to anusvāra and avagraha (`'`→ऽ) is
  dropped by `deva_to_slp1`, so those two are not round-trip stable (matching `deva_to_slp1`'s
  own behaviour).

### German lexicographic apparatus (PWG/PW metalanguage)

The PWG/PW dictionaries write their apparatus in German — grammar labels (`adj.`, `m. f. n.`),
recurring formulae (`vgl.`, `am Ende eines Comp.`, `mit Ergänzung von`, `im Comp. vorangehend`)
and bare function words reused as placeholders (`eines`, `die`). A DE→RU/EN translation pipeline
that renders such a span as an ordinary gloss produces the dominant TM defect class measured by
H2787 (`eines` → «поручать кому-л.»).

| Symbol | Does |
|---|---|
| `classify_german_metalanguage(text)` | → list of `{start, end, text, category}` spans; categories `grammar_label` / `recurring_formula` / `function_word` (whole text is bare function words) / `uncertain` (whole text is an ambiguous token like `so` or `Ergänzung` — consumers treat as **not**-gloss and log) |
| `GERMAN_GRAMMAR_AB` `GERMAN_GRAMMAR_BARE` `GERMAN_FORMULA_AB` `GERMAN_FORMULA_PHRASES` `GERMAN_FUNCTION_WORDS` `GERMAN_AMBIGUOUS_TOKENS` | the harvested token inventories (sets; `GERMAN_FORMULA_PHRASES` = case-insensitive pattern strings), consolidated from the pwg_ru pipeline sources so no consumer keeps a second private token table |

Mid-text function words (`Name eines Baumes`) are **not** flagged — only a span consisting
entirely of function/ambiguous words is apparatus; ordinary German gloss prose returns `[]`.

### linkid — TYPED_LINK_ID_GRAMMAR.md build/parse/validate

Cross-repo **Type-D** (grammar ↔ non-grammar) link-ID grammar per Uprava's
[`TYPED_LINK_ID_GRAMMAR.md`](https://github.com/gasyoun/Uprava/blob/main/TYPED_LINK_ID_GRAMMAR.md):
a grammar-anchor id (`gra:3983`, `whitney-sec:611-641`, `sutra:1.1.1`) linked to a target-locus id
(`dcs:588488`, `vedaweb:1.1.6:668bbf5c1e18769f3d9aafc3`, `commentary:gita-tm:2.47`). Every id is
`<prefix>:<tail>` where the tail is the source's **own** stable id, copied verbatim — never a
fresh synthetic key, never a URL host (spec §0 "reuse, don't mint"). These functions are the
reusable implementation the spec's canonical validator, `kosha/scripts/typed_link_lint.py`, is
locked against (`tools/gen_vectors.py`'s `linkid_donor_regression()`).

| Symbol | Does |
|---|---|
| `linkid_build_anchor_id({type, tail})` | `{type: 'gra', tail: '3983'}` → `'gra:3983'`, or `None`/`null` if `type` isn't a `LINKID_ANCHOR_PREFIXES` member or `tail` fails that prefix's syntax |
| `linkid_parse_anchor_id(anchor_id)` | `'gra:3983'` → `{type, tail, valid}`, or `None`/`null` if there's no known prefix |
| `linkid_build_target_locus({type, tail})` | same shape as the anchor builder, for `LINKID_TARGET_PREFIXES` |
| `linkid_parse_target_locus(target_locus)` | same shape as the anchor parser |
| `linkid_validate_link_record(record)` | validate a full `TYPE_D_RECORD_FIELDS`-shaped record (anchor/target prefix+syntax, the URL-host ban, `link_type`/`match_method` membership, `DD-MM-YYYY` date) → `{valid, errors}` |
| `LINKID_ANCHOR_PREFIXES` `LINKID_TARGET_PREFIXES` `LINKID_LINK_TYPES` `LINKID_MATCH_METHODS` | the known prefix/type/tier lists (tuples/arrays) |

```python
from sanskrit_util import linkid_build_anchor_id, linkid_validate_link_record
linkid_build_anchor_id({'type': 'gra', 'tail': '3983'})   # 'gra:3983'
linkid_validate_link_record({
    'anchor_type': 'id-gra', 'anchor_id': 'gra:3983', 'target_locus': 'vedaweb:1.1.6:668bbf5c1e18769f3d9aafc3',
    'link_type': 'translation-witness', 'source_dataset': '...', 'match_method': 'id-link', 'date': '08-07-2026',
})   # {'valid': True, 'errors': []}
```

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

### Browser, no bundler (plain `<script>`)
For static pages that load plain scripts (no ES-module `import`), use the global build
[`js/sanskrit-util.global.js`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/js/sanskrit-util.global.js) — it exposes `window.SanskritUtil`:
```html
<script src="sanskrit-util.global.js"></script>
<script>
  SanskritUtil.norm('धर्म');        // 'dharma'
  SanskritUtil.to_slp1('aiśvarya'); // 'ESvarya'
</script>
```
The global build is **generated** from `index.mjs` by `node js/build-global.mjs` (single source;
CI fails via `--check` if it goes stale) and is behaviour-identical to the ESM build and Python.

### In a sibling repo without publishing (this GitHub-root layout)
Drop a 12-line re-export shim named `sanskrit_util.py` that loads
`../../sanskrit-util/py/sanskrit_util/__init__.py` by relative path — see the working example at
[`WhitneyRoots/scripts/sanskrit_util.py`](https://github.com/sanskrit-lexicon/WhitneyRoots/blob/main/scripts/sanskrit_util.py).

## Test

```bash
python tools/gen_vectors.py           # regenerate vectors.json + 3 regression checks (see below)
python py/tests/test_units.py         # pitfall unit tests
python py/tests/test_vectors.py       # Python == golden
node   js/test/vectors.test.mjs       # JS == golden  (== Python)
node   js/test/units.test.mjs         # JS unit tests (== Python literals)
node   js/test/global.test.mjs        # window.SanskritUtil global build == ESM
node   js/build-global.mjs --check    # browser global build is not stale
```

`tools/gen_vectors.py` additionally (a) locks the `SLP1_VOWELS/MARKS/CONSONANTS` constants
set-equal to the independent literals in the SanskritSpellCheck `slp1util.py` donor, (b) locks the
`LINKID_*` prefix/type/tier constants against the sibling `kosha/scripts/typed_link_lint.py` +
`concordance_core.py` donors, and (c) runs the **SLP1 ⇄ Devanāgarī round-trip property test** —
`deva_to_slp1(slp1_to_devanagari(s)) == s`
over the full alphabet plus [`vectors/slp1_roundtrip_sample.txt`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/vectors/slp1_roundtrip_sample.txt)
(1000 real MW `<k1>` headwords). All three are skipped gracefully if the sibling repos are absent.

## Related tools (optional, not part of the library API)

- **[tools/KeySwap](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/README.md)**
  (2.8 shell + v3 opt-in plugins) — type IAST (Windows/iPhone/Mac/PWA);
  HK/ITRANS/Velthuis → IAST; **Cologne Simple Search** (`dalnorm` + open/API);
  offline wordlist; **v3 plugins** (never default Startup):
  [`offline_fuzzy`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/offline_fuzzy/)
  (V3-2),
  [`network_autocomplete`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/network_autocomplete/)
  (V3-7, offline-first then Cologne). Architecture:
  [KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).
  Not in PyPI/npm.

## Layout

```
sanskrit-util/
  py/sanskrit_util/__init__.py   Python implementation (importable as `sanskrit_util`)
  py/tests/                      unit + vector tests
  js/index.mjs                   JS implementation (ESM)
  js/sanskrit-util.global.js     generated browser global build (window.SanskritUtil)
  js/build-global.mjs            regenerates the global build from index.mjs (--check in CI)
  js/test/                       cross-language vector + unit + global-build tests
  vectors/vectors.json           golden outputs, shared by both test suites
  vectors/slp1_roundtrip_sample.txt  1000 real MW headwords for the SLP1⇄Devanāgarī round-trip test
  tools/gen_vectors.py           regenerate vectors + donor/set/round-trip regressions
  tools/crosscheck.py + crosscheck_js.mjs  cross-language behaviour crosscheck
  tools/epistemic/               builders for the epistemic sibling registries (H356; re-vendored across repos)
```

The `tools/epistemic/` subtree (seven registry builders + a dashboard generator) is housed here so
the `SanskritLexicography` and `Uprava` sides run the same code; see
[`tools/epistemic/README.md`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/README.md).

_Dr. Mārcis Gasūns_
