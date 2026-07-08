# Changelog

## Unreleased

### Added — `tools/epistemic/` — seven builders for the epistemic sibling registries (H356)

Seven scripts that seed / generate the epistemic sibling registries that sit next to each
`FINDINGS.md` (ASSUMPTIONS · CONTRADICTIONS · GAPS · DEAD_ENDS · RECIPES · STALENESS · GLOSSARY),
mirrored across the `SanskritLexicography` (Sanskrit-data) and `Uprava` (infra/process) sides.
Housed here so both sides run the same code; re-vendor via `/cologne-sanskrit-util-sync`.
`derive_staleness.py` fully generates the STALENESS decay table from a FINDINGS file (date passed
in via `--today`, never `Date.now()`, so re-runs are byte-identical); `seed_recipes.py` /
`seed_gaps.py` / `seed_contradictions.py` / `seed_dead_ends.py` / `scan_assumptions.py` emit
`⚙️ auto` candidate rows a human confirms or deletes. `seed_contradictions.py` reuses `form_key`
when the package is importable. See [`tools/epistemic/README.md`](tools/epistemic/README.md).

## 0.4.0 — 2026-07-04

### Added — `source_line_to_iast` / `source_text_to_iast` (CDSL raw source line → readable IAST)

A display layer over `from_slp1`: a raw `csl-orig` line is SLP1 inside CDSL markup
(`{#aBAga#}¦, <lex>f.</lex> {#A#} <ls>…</ls>`) and unreadable to a human. These render it to IAST,
honoring each dictionary's own encoding — MW `<s>…</s>`; PW/PWG/AP/WIL `{#…#}` (with the meaning
language in `{%…%}` left as-is); VCP/SKD whole-line SLP1 prose — and strip the markup shell (tags,
`[Page…]` markers, the `¦` headword separator). `code` is the csl-orig dict code. Example:
`{#aBAga#}¦, <lex>f.</lex> {#A#}` → `abhāga, f. ā`. Python and JS byte-identical, locked by new
unit tests in both suites. First extracted in `csl-atlas` (PRs #205/#206/#209); upstreamed here so
every CDSL reader/web frontend renders source entries the same way instead of re-parsing markup.
SLP1 is a machine key — the guidance is IAST for readers, raw SLP1 behind an opt-in toggle.

## 0.3.0 — 2026-07-03

First real SLP1-side release from `main`. Completes the SLP1 surface (roadmap Cross-Pollination
Wave-1 / D1): the CDSL-native (SLP1-keyed) consumers can now migrate off their per-repo helpers.

> **Note on `v0.2.0`:** a `v0.2.0` tag was pushed to origin pointing at an off-`main` commit
> (`11dd18b`) that was never merged or released; it carried the SLP1 API + `deva_to_slp1` (below)
> plus a Python-only `slp1_simplify`. This `0.3.0` supersedes it — it merges that work into `main`
> **and** gives `slp1_simplify` its missing JS port / golden vectors / docs, so the whole SLP1
> surface is finally cross-language and released properly. (The stray `v0.2.0` tag is left for the
> maintainer to retarget or delete.)

### Added — `slp1_to_devanagari` (SLP1 → Devanāgarī, real round-trip partner of `deva_to_slp1`)
A **real** transcode (not a display-only replace like `iast_to_devanagari`): it supplies the
virāma between clustered consonants and renders each vowel as an independent sign or a mātrā by
position, so the output is well-formed Devanāgarī. It is the round-trip partner of `deva_to_slp1`:
`deva_to_slp1(slp1_to_devanagari(s)) == s` for canonical SLP1, proved by a new **property test** in
`tools/gen_vectors.py` over the full alphabet **plus 1000 real MW `<k1>` headwords**
(`vectors/slp1_roundtrip_sample.txt`). The vowel/mātrā/consonant maps are inverted from the same
Devanāgarī→SLP1 maps `deva_to_slp1` uses (kept in lock-step); the 3 marks (M→anusvāra, H→visarga,
~→candrabindu) are explicit because anusvāra and candrabindu both map back to `M`. Candrabindu
(`~`→ँ→`M`) and avagraha (`'`→ऽ, dropped) are documented as **not** round-trip stable, matching
`deva_to_slp1`'s own behaviour. This closes the "_Still deferred:_ a real SLP1→Devanāgarī
round-trip" note from the previous SLP1 batch.

### Added — `slp1_simplify` (lossy MW fuzzy-match key), now cross-language
Fold **every** SLP1 distinction to plain ASCII — the lossy extreme of the SLP1 key family
(`slp1_norm` keeps case+everything but accents/digits; `slp1_form_key` keeps length + `ś` +
retroflex dots; `slp1_simplify` keeps almost nothing). For building/querying MW headword indexes
(`mw_en_tm.json`). Critical `R`→`n` (`guṇa` = `guRa` → `guna`, not `gūna`). Was Python-only on an
unmerged branch; this ships the matching **JS port**, golden vectors, and README/`Which key` docs.

### `ṁ` (U+1E41) → `M` on the IAST→SLP1 side
Locked with golden vectors + unit tests in both languages (`to_slp1('saṁskṛta') == 'saMskfta'`,
and `form_key` folds it like anusvāra `ṃ`). This is the named blocker for dropping `sanscript` from
SamudraManthanam's IAST→SLP1 path — `to_slp1` already handled it; it is now regression-covered.

Golden vectors grow 418 → **482** across **15** functions (`JS == Python` still asserted every
commit; the browser global build re-checked non-stale). Purely additive — existing exports and
their behaviour are unchanged.

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

### Added — `deva_to_slp1` (Devanāgarī → SLP1, direct)
`deva_to_slp1(s)` transcodes Devanāgarī straight to SLP1 (inherent-`a` + virāma aware), replacing
the lossy `to_slp1(deva_to_iast(s))` chain that consumers had to hand-roll. The crux is the
**`ळ`→`L` vs `x` decision** that 0.1.0 deferred: `deva_to_iast` collapses `ळ` (U+0933, retroflex ḻa)
onto vocalic `ḷ` — both render as IAST `ḷ` (U+1E37) — so the chained form mis-maps `ळ` to `x`
(vocalic ḷ), and that can't be recovered after the IAST step. `deva_to_slp1` makes the decision
directly: `ळ`→`L` (the round-trip partner of `from_slp1('L')`→`ḻ`) while `ऌ` / the `◌ॢ` mātrā stay
`x`. The Devanāgarī→SLP1 maps are derived from the existing Devanāgarī→IAST maps (so they track
`to_slp1` exactly) with the one `ळ`→`L` override, and the traversal mirrors `deva_to_iast`. Golden
vectors **403 → 418** across **13** functions; +3 Python and matching JS unit tests lock the
`ळ`/`ऌ` distinction cross-language. Purely additive — existing exports unchanged.

_Since resolved:_ the real SLP1→Devanāgarī round-trip landed in **0.3.0** above
(`slp1_to_devanagari`). Still deferred: proper virāma/conjunct shaping for `iast_to_devanagari`
(still approximate, display-only) — a separate change.

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
