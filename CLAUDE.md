# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

`sanskrit-util` is the **one canonical implementation** of the Sanskrit string
helpers (IAST ⇄ SLP1 ⇄ Devanāgarī transcoding, plus normalization keys for
search/index/form-comparison) that were previously re-typed across ~20+
Sanskrit-Lexicon/CDSL repos (a census found `transcoder.py` in 62 copies /
7 versions). Consumed by other repos as a library, not run standalone. Python
and JavaScript ports are **behaviour-identical**, proved on every commit
against a shared golden-vector set. See [`../SHARED_CODE.md`](../SHARED_CODE.md)
for the full cross-repo dedup map this repo replaces.

## Common commands

```bash
pip install -e py                     # editable Python install, from repo root
python tools/gen_vectors.py           # regenerate vectors/vectors.json + donor/set/round-trip regressions
python py/tests/test_units.py         # Python pitfall unit tests
python py/tests/test_vectors.py       # Python == golden vectors
node   js/test/vectors.test.mjs       # JS == golden vectors (== Python)
node   js/test/units.test.mjs         # JS unit tests (== Python literals)
node   js/build-global.mjs --check    # verify browser global build isn't stale
python tools/crosscheck.py            # adversarial Python == JS check (exotic/BOM/whitespace inputs)
python -m pytest py/tests -q          # full Python suite (as CI runs it)
cd js && npm test                     # full JS suite (as CI runs it)
```

## Key directories / files

| Path | Purpose |
|---|---|
| `py/sanskrit_util/__init__.py` | Python implementation, importable as `sanskrit_util` |
| `py/tests/` | Python unit + golden-vector tests |
| `js/index.mjs` | JS implementation (ESM) |
| `js/sanskrit-util.global.js` | **Generated** browser global build (`window.SanskritUtil`) — do not hand-edit, see below |
| `js/test/` | JS unit + golden-vector tests |
| `vectors/vectors.json` | Golden outputs shared by both test suites — regenerate via `tools/gen_vectors.py`, don't hand-edit |
| `vectors/slp1_roundtrip_sample.txt` | 1000 real MW `<k1>` headwords used for the SLP1⇄Devanāgarī round-trip property test |
| `tools/gen_vectors.py` | Regenerates vectors + locks `SLP1_VOWELS/MARKS/CONSONANTS` against the SanskritSpellCheck `slp1util.py` donor + runs the round-trip test |
| `tools/crosscheck.py` / `tools/crosscheck_js.mjs` | Cross-language adversarial-input parity checks |

## CI workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | push to `main`, PR | Installs both ports, runs Python pitfall+vector tests, regenerates `vectors.json` and the browser global build expecting **no diff** (staleness gate), runs JS tests, runs the cross-language adversarial check |
| `dependabot-auto-merge.yml` | Dependabot PRs | Auto-merges dependency bumps once checks pass |

## Conventions

- **Python functions are extracted verbatim from `WhitneyRoots/scripts/sanskrit_util.py`**
  (regression-locked against that donor) — the JS-origin helpers (`deva_to_iast`,
  `iast_to_devanagari`, `normalize_sanskrit`) come from WhitneyRoots `reader.js` /
  `src/utils/linguistics.js`. Changing shared behavior here without checking the
  donor risks silently diverging from the repo everyone else still points at.
- **Five normalization keys exist on purpose, each for a different job** — do
  not collapse them or add a sixth without reading the README's "Which key do
  I want?" section: `norm` (search/index lookup, diacritic-insensitive but
  exact), `nfold` (recall fallback, nasal-folded), `form_key`
  (length-preserving form comparison), `normalize_sanskrit` (lossy ASCII fold,
  kept only for v3-explorer parity), plus the SLP1-side family
  (`slp1_norm`/`slp1_form_key`/`slp1_simplify`) for CDSL SLP1-native headwords.
- **In standard SLP1, case is phonemic** (`R`=ṇ, `S`=ś, `T`=th — distinct from
  lowercase `r`/`s`/`t`). `slp1_simplify` deliberately folds these for fuzzy
  matching; every other SLP1 function preserves case. Forgetting `R`→`n` in a
  fuzzy match misreads `guṇa` (`guRa`) as `gūna`.
- **`iast_to_devanagari` is now a real transcode** (H1394, 21-07-2026): implemented
  as `slp1_to_devanagari(to_slp1(s))`, so it is virāma/mātrā aware and shares
  `slp1_to_devanagari`'s round-trip properties. It was previously a naive
  character-substitution wrong on 9 of 9 basic words — if you see a comment or
  doc elsewhere still calling it "display-only" or "broken", that's stale.
- **Consumption in a sibling repo without publishing:** drop a small re-export
  shim named `sanskrit_util.py` that loads this package's `py/sanskrit_util/__init__.py`
  by relative path — see the working example at
  [`../WhitneyRoots/scripts/sanskrit_util.py`](../WhitneyRoots/scripts/sanskrit_util.py).
  Do not copy/fork the implementation into a new repo — that's exactly the
  duplication this package exists to end.

## What not to touch

- `js/sanskrit-util.global.js` — generated from `index.mjs` via
  `node js/build-global.mjs`; CI fails (`--check`) if it drifts from source.
- `vectors/vectors.json` — generated by `tools/gen_vectors.py`; hand-editing
  breaks the cross-language parity guarantee both test suites assert against.
