# Changelog

## Unreleased

### Added — SLP1-side API
The original 0.1.0 surface was IAST/Devanāgarī-centric, but the CDSL dictionaries are
**SLP1-native** (case is phonemic there), so every dict repo had re-rolled its own SLP1
alphabet + headword normalizer. New, behaviour-identical in Python and JS:

- `SLP1_VOWELS`, `SLP1_MARKS`, `SLP1_CONSONANTS`, `SLP1_ALPHABET` — valid SLP1 character classes.
- `strip_slp1_accents(slp1)` — drop the SLP1 accent/candrabindu marks `/ \ ^ ~`.
- `slp1_norm(slp1)` — canonical CDSL **headword** key (strip accents + trailing homonym digits,
  collapse whitespace; **case preserved**). The shared form of the per-repo `normalize_lemma` /
  `normalizeSlp1Lemma`.
- `slp1_form_key(slp1)` — length-preserving **compare** key for SLP1 forms (`form_key ∘ from_slp1`).

Golden vectors grow 346 → **403** across **12** functions (`JS == Python` still asserted on every
commit); +4 Python unit tests and a new JS unit suite (`js/test/units.test.mjs`) lock the
constants' cross-language parity. Purely additive — existing exports unchanged.

_Deferred:_ a proper `deva_to_slp1` / SLP1→Devanāgarī round-trip (the `ळ`→`L` vs `x` decision and
real virāma/conjunct shaping need their own change).

## 0.1.0 — 2026-06-14

Initial extraction. Consolidates the Sanskrit string helpers that were duplicated across the
CDSL / Sanskrit-Lexicon repos into one Python + JS package.

- **Python**: `to_slp1`, `from_slp1`, `to_roman`, `form_key`, `norm`, `nfold` extracted
  verbatim from `WhitneyRoots/scripts/sanskrit_util.py` and regression-locked against that
  donor (`tools/gen_vectors.py` fails if they ever diverge).
- **JS-origin helpers** folded in from WhitneyRoots `reader.js` (`deva_to_iast`) and
  `src/utils/linguistics.js` (`iast_to_devanagari`, `normalize_sanskrit`).
- **JS port** (`js/index.mjs`) is behaviour-identical to Python; 346 shared golden vectors
  assert `JS == Python` in CI.
- **One intentional unification:** `norm()` is now Devanāgarī-aware in **both** languages
  (it transliterates Devanāgarī via `deva_to_iast` before folding). The original Python
  `norm()` was IAST-only; the original JS `norm()` already did this. For IAST input the
  behaviour is unchanged (the donor regression confirms it), so existing Python consumers are
  unaffected; Devanāgarī input now yields IAST keys instead of raw Devanāgarī.
- `normalize_sanskrit` is kept **distinct** from `norm` (it is the lossy ASCII-folding
  v3-explorer key) rather than silently merged — they had different semantics in the donor.

### First consumer
`WhitneyRoots/scripts/sanskrit_util.py` is now a thin re-export shim pointing at this package;
its six importing scripts are unchanged.

### Not consolidated (deliberately)
- Dhaval Patel's `transcoder.py` (the 62-copy Cologne engine) — that is the dictionary-build
  toolchain's own vendored dependency; reuse it from `csl-pywork`, don't fold it here.
- `scripts/dcs/` Roman↔Arabic + fold helpers in WhitneyRoots — a separate corpus-class
  pipeline, intentionally kept apart upstream.
