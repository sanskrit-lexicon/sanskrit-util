# Changelog

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2026-09-02

### Fixed

- **`form_key`: word-final anusvāra now folds to `m`, so the two spellings of a Sanskrit
  word-final nasal finally collide** (H3911). ⚠️ **This changes emitted keys — see the
  migration note below.** Sanskrit writes word-final `-m` as anusvāra before a consonant and
  as `-m` in pausa or before a vowel, so `rasaṃ` and `rasam` are one word in two spellings.
  `form_key` folded `[ṃṁṅñṇ] → n` at every position while never touching a literal `m`, so
  `rasaṃ → rasan` but `rasam → rasam`: the two spellings could never match, and **every
  anusvāra-final attestation read as un-generated**. The new rule runs *before* the general
  homorganic fold and applies only word-finally, so medial behaviour is unchanged
  (`saṃskṛta == sanskṛta`, `krāṃta == krānta`) and final `-n` stays distinct from final `-m`
  (`rājan != rājam` — the fold is deliberately not widened to merge two different endings).
  Both ports changed together; `vectors.json` regenerated (3 vectors move:
  `form_key('saṃ')` `san→sam`, `form_key('ṁ')` `n→m`, `slp1_form_key("aDo'MSukaM")`
  `adho'nśukan→adho'nśukam` — the medial `M` stays `n`, which is the rule being positional).
  The `WhitneyRoots/scripts/sanskrit_util.py` regression donor is updated in the same pass so
  package and donor stay byte-identical.

  **Migration.** Any stored `form_key`/`slp1_form_key` value computed before 0.11.0 and
  compared against a freshly computed one will mismatch for anusvāra-final forms; rebuild
  derived keys rather than mixing eras. Measured on the one consumer with a published figure
  — kosha's A3 generated-vs-attested audit — **24,149 of its 196,378
  "attested-never-generated" keys (12.30% of rows, 16.86% by corpus weight) stop being gaps**
  under the fixed key (`rūpaṃ`, `duḥkhaṃ`, `vijñānaṃ` … standard `-am` neuters written with
  anusvāra), so that dataset's A¬G figure is an upper bound until it is rebuilt. Other known
  consumers: csl-observatory (`headword_linkage.py`, `error_recapture.py`,
  `corrector_recapture.py`), csl-atlas (`adjudicate-h4-agent.mjs`,
  `build-h4-review-packet.mjs`), kosha's concordance builders.

## [0.10.0] - 2026-08-24

### Added

- **linkid: `TYPED_LINK_ID_GRAMMAR.md` build/parse/validate** (H3341): `linkid_build_anchor_id` /
  `linkid_parse_anchor_id` / `linkid_build_target_locus` / `linkid_parse_target_locus` /
  `linkid_validate_link_record` in both ports, implementing Uprava's cross-repo Type-D
  (grammar ↔ non-grammar) link-ID grammar — grammar-anchor ids (`gra:<L>`, `whitney-root:<n>`,
  `whitney-sec:<§>`, `root:<slp1>`, `sutra:<a.p.n>`) and target-locus ids (`dcs:<sent_id>`,
  `vedaweb:<RV-locus>:<resource-id>`, `commentary:<work>:<cite>`, `subject:<index>:<category>`),
  plus the `LINKID_ANCHOR_PREFIXES` / `LINKID_TARGET_PREFIXES` / `LINKID_LINK_TYPES` /
  `LINKID_MATCH_METHODS` constant lists. 53 shared golden vectors pin Py==JS. The prefix/pattern/
  tier constants are locked against the spec's canonical validator,
  [kosha/scripts/typed_link_lint.py](https://github.com/gasyoun/kosha/blob/main/scripts/typed_link_lint.py)
  + `concordance_core.py`, by `tools/gen_vectors.py`'s new `linkid_donor_regression()` (skipped
  gracefully if the sibling checkout is absent). Library package versions bumped to **0.10.0**
  in `py/pyproject.toml`, `js/package.json`, and `__version__` (resyncing them with the git tag
  sequence — they had drifted to the 0.6.0 they were resynced to for v0.9.0 while tags moved on
  to v0.9.0).

### Changed

- **tools/KeySwap** — default input is **cycle only** (letter then `=`). Smart digraphs (`aa`→ā, `ll`→ḷ, `ss`→ṣ, …) and Writer-scheme marks no longer fire unless the tray / PWA / Mac / iOS **smart** toggle is on. Restores the original Yes Vedanta Keyswap model.

- **tools/KeySwap docs** — smart mode is documented as **English-hostile**: `ll`/`ss`/`tt`/`nn`/`sh`/`ng`/`aa` rewrite ordinary words (*call*, *class*, *letter*, *English*). Cycle only for mixed typing. H3279.

- [CLAUDE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/CLAUDE.md): dated header (`_Created: 03-07-2026 · Last updated: 20-08-2026_`), full-URL SHARED_CODE / WhitneyRoots / KeySwap architecture links, H2876 German-apparatus API note, `changelog-lint.yml` in the CI table (H3042).

## [0.9.0] - 2026-08-16

### Added

- **German lexicographic-apparatus (metalanguage) detection** (H2876):
  `classify_german_metalanguage(text) -> [{start, end, text, category}]` in
  both ports, categories `grammar_label` / `recurring_formula` /
  `function_word` / `uncertain`, plus the exported harvested inventories
  (`GERMAN_GRAMMAR_AB`, `GERMAN_GRAMMAR_BARE`, `GERMAN_FORMULA_AB`,
  `GERMAN_FORMULA_PHRASES`, `GERMAN_FUNCTION_WORDS`,
  `GERMAN_AMBIGUOUS_TOKENS`). Tokens are harvested — not invented — from the
  pwg_ru sources that owned them
  ([pwg_tm_fragmentize.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_tm_fragmentize.py),
  [compile_translatable.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/compile_translatable.py),
  [microstructure.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/microstructure.py),
  [pwg_mask.py](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_mask.py)),
  the H2684 repair extras (`demin.`, `personif.`, `Uebertr.`), and the H2787
  arm-B defect formulae (`eines`, `im Comp. vorangehend`, `so`, `Ergänzung`).
  34 shared golden vectors pin Py==JS. Library versions resynced to **0.6.0**
  in both `py/pyproject.toml` and `js/package.json` (they had drifted to
  0.4.1 / 0.5.1).

### Fixed

- **tools/KeySwap Windows AHK** — two startup defects on AutoHotkey v2.0:
  the tray "Reload config (F6)" fat-arrow used `=> { stmts }`, which v2.0
  parses as an object literal (`Missing "propertyname" in object literal`)
  and exits; writer-scheme `~` was registered as `Hotkey("~*" "~")` =
  `~*~`, which AHK reports as `~^` and warns *will not be active* on
  layouts that have no tilde (JCUKEN). Reload is now the named
  `ReloadConfig`; the tilde mark is `{ ~ }` via `TryHotkey`.

## [0.8.11] - 2026-07-26

### Added

- **tools/KeySwap v4 paid SKU brief** (H1640, closes child C3 of the
  keyswap-v2-v3-v4 programme):
  [docs/V4_PAID_SKU_BRIEF.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/V4_PAID_SKU_BRIEF.md)
  (+ metadoc) — V4-A pricing/SKU options (one-time per platform vs subscription
  vs à-la-carte packs, options only, human rules), ordered V4-B Mac and V4-C
  iOS execution checklists scoped from
  [SIMILARS_COMPARISON.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/SIMILARS_COMPARISON.md),
  V4-D forms/morphology rights assessment naming
  [`vidyut-prakriya`](https://github.com/ambuda-org/vidyut) (MIT code + MIT
  ashtadhyayi.com Dhātupāṭha, verified against the repo 26-07-2026) as the
  rights-clear primary candidate with Heritage/in-house fallbacks, and a V4-E
  free→paid bridge note. Docs only — no v4 code, no builds; the two `@DECIDE`
  rows (SKU shape · forms data source) land in Uprava
  [GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md).
  ROADMAP v4 section links the brief.

## [0.8.10] - 2026-07-25

### Added

- **tools/KeySwap V3 free-heavy residual** (H1639, closes child C2 of the
  keyswap-v2-v3-v4 programme):
  - **Tray opt-in for V3-2/V3-7 plugins** — a "Plugins (opt-in; off by
    default)" submenu (Windows `windows/KeySwap.ahk` tray menu, Mac
    `apple/macos/KeySwapMacApp.swift` status-bar menu) toggles
    `offline_fuzzy` / `network_autocomplete` on and off. Persistence is a new
    `plugins/tray_state.py` (`%APPDATA%\KeySwap\plugins.ini` on Windows /
    `UserDefaults` on Mac — never inside the repo tree); the tray click
    writes the exact same `KEYSWAP_PLUGINS` env surface the CLI/env path
    already reads, never a parallel enable mechanism. Still one explicit
    click; still absent from default Startup.
  - **Full-MW pack docs** — `plugins/offline_fuzzy/README.md` now documents
    pointing `KEYSWAP_WORDLIST` (or `build_local_wordlist.py --out`, sent
    outside the repo tree) at the org's existing
    `SanskritLexicography/HeadwordLists/` MW key1 exports (~194k entries),
    instead of the ~1k shipped seed. Nothing vendored into git.
  - **V3-1/V3-3/V3-4/V3-5/V3-6 link-out polish** — the Windows tray
    "Ecosystem" submenu gained two real links that were missing (Sanskrit
    Text-to-Speech at SRI Auroville for V3-5, replacing a vague "SRI TTS
    etc." mention; the Sanskrit Heritage Site at INRIA for V3-6) and a
    clarified label for V3-1/V3-4 (Aksharamukha's converter page covers both
    script conversion *and* OCR upload — one tool, not two). Doc rows in
    `ROADMAP_KEYSWAP_V2_V3.md`, `docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md`,
    and `SIMILARS_COMPARISON.md` updated to match. No new integrations.
  - Tests: `test_tray_state.py` (persistence round trip + CLI).

- **tools/KeySwap 2.9 — v2 free-portable residual** (H1638, closes the v2 tier):
  - **#7 iOS Writer digraph parity** — `KeyboardViewController` resolved smart-digraph
    substitution from the active profile (`SmartTables.forProfile`) instead of a
    hardcoded classic table; Writer-profile users now get `-a`→ā, not `aa`→ā, matching
    the cycle engine (already profile-correct) and the Mac app (already correct).
  - **#8 live Deva, in place (Windows)** — `Ctrl+Alt+Shift+D` converts the current text
    selection to Devanāgarī and pastes it back without a manual clipboard round trip.
    Opt-in (nothing changes unless pressed); continuous per-keystroke auto-flip was
    considered and parked — see [ROADMAP_KEYSWAP_V2_V3.md](tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md)
    § "Residual free backlog" for the reason. Mac/iOS parked with the same reason.
  - **Portable packaging** — audited `packaging/INSTALL.md` / `VENDOR_PE.md`; already
    one clear path per platform, no changes needed.
  - Swift `KeySwapVersion.current` and its stale test assertion ("2.3.0" vs the actual
    "2.7.0") were both out of sync with the shipped product version; both now read "2.9.0".

### Changed

- **tools/KeySwap product tiers** — [SIMILARS_COMPARISON.md](tools/KeySwap/SIMILARS_COMPARISON.md)
  and [ROADMAP_KEYSWAP_V2_V3.md](tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md) refreshed:
  **v2 free portable** · **v3 free heavy (not max)** · **v4 paid full** (Mac/iOS + forms).
  Umbrella handoff H1619.

## [0.8.9] - 2026-07-24

### Added

- **tools/KeySwap V3-7 network_autocomplete** — opt-in offline-first then Cologne
  Simple Search when the local fuzzy index is not confident
  (`plugins/network_autocomplete/`; `--plugin network_autocomplete` /
  `KEYSWAP_PLUGINS`). Never always-on; never default Startup AHK.
  Tests: `test_network_autocomplete_plugin.py`.

### Changed

- **Registration surfaces for KeySwap v3 plugins** (H1583 `/artifact-propagate`):
  root README “Related tools”, `CLAUDE.md` KeySwap agent rules + table rows,
  `.ai_state.md` completed entry, architecture
  [metadoc](tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.meta.md).

## [0.8.8] - 2026-07-24

### Added

- **tools/KeySwap 2.8** (`2.8.0`) — non-US **cycle trigger presets**
  (`equals` / `bracket` / `slash` / `backtick`): tray submenu, `windows/trigger.ini`,
  env `KEYSWAP_TRIGGER`, shared table [`trigger_presets.py`](tools/KeySwap/trigger_presets.py);
  PWA trigger select + Mac `KEYSWAP_TRIGGER` keycode. Shift+trigger = literal.

## [0.8.7] - 2026-07-24

### Added

- **tools/KeySwap V3-2 offline_fuzzy** — real fuzzy index over the local SLP1
  wordlist (exact → prefix → Levenshtein); enable only via
  `typing_check --plugin offline_fuzzy` or `KEYSWAP_PLUGINS=offline_fuzzy`.
  Full MW remains opt-in through `KEYSWAP_WORDLIST` /
  `build_local_wordlist.py`. Still **never** loaded by default Startup AHK.

## [0.8.6] - 2026-07-24

### Added

- **tools/KeySwap v3 design (H1581)** — plugin/sibling architecture memo
  ([`docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md`](tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md));
  first-pick **V3-2** scaffold [`plugins/offline_fuzzy/`](tools/KeySwap/plugins/offline_fuzzy/)
  (`never_autoload`, seed exact-match only; no SQLite pack / no default AHK load);
  ROADMAP Version 3 status rows updated.

## [0.8.5] - 2026-07-24

### Added

- **tools/KeySwap 2.7** (`2.7.0`) — v2 highest-leverage pack: SLP1+normkey copy (Ctrl+Alt+K), Ecosystem tray, Shift+= literal equals, pali-lite profile, SIMILARS refresh + ROADMAP_KEYSWAP_V2_V3, classroom pack doc.

## [0.8.4] - 2026-07-24

### Added

- **tools/KeySwap 2.6** (`2.6.0`) — beat-Sanskrit-Writer roadmap (all five):
  1. **Writer-scheme** profile + digraphs (`-a` for long a, `~n`, `'s`, `h.`)
  2. **Script mode** Ctrl+Alt+D / V (IAST / Devanagari clipboard)
  3. **Gloss** Ctrl+Alt+G / `--open-gloss` opens Cologne webtc full entry
  4. **One install** `packaging/install-windows.ps1`, `install-macos.sh`, INSTALL.md
  5. README landing blurb + comparison table vs Sanskrit Writer

## [0.8.3] - 2026-07-24

### Added

- **tools/KeySwap 2.5** (`2.5.0`) — optional **DCS-2026** frequency mode
  (`--dcs-freq` / `KEYSWAP_DCS_FREQ=1`): `data/dcs_freq.txt` (csl-apidev
  `simple-search/wf1`), HUD `dcs=N`, Cologne `--freqsrc wf1|wf0` for ranking
  table selection after server Fix I. Default remains off.

## [0.8.2] - 2026-07-23

### Added

- **tools/KeySwap 2.4** (`2.4.0`) — offline headword check via local SLP1
  wordlist (`data/local_headwords.txt` seed ~1k keys): `typing_check` falls
  back when Cologne API fails or with `--local-only`;
  `local_wordlist.py` + `build_local_wordlist.py --from-spellcheck` to expand
  from sibling SanskritSpellCheck `HeadwordLists/MW-unique-key1-*.txt`.
  Not a full detector stack — existence check only.

## [0.8.1] - 2026-07-23

### Fixed

- **tools/KeySwap** `typing_check` / `cologne_search.format_api_error`: map Cologne
  Simple Search **HTTP 429** to HUD text `rate-limited — try browser (Ctrl+Alt+C)`
  instead of opaque `api: HTTPError` (H1545).

## [0.8.0] - 2026-07-23

### Added

- **tools/KeySwap 2.3** (`2.3.0`) — typing-tool port for light Cologne headword
  check: `typing_check.py` (last token → Simple Search API → ✓/✗ HUD), AHK
  Ctrl+Alt+S, Mac menu; no local dict / no SanskritSpellCheck embed.
- **tools/KeySwap 2.2** (`2.2.0`) — Cologne Simple Search integration:
  `cologne_search.py` ports csl-apidev `Dalnorm::normalize` + multi-scheme→SLP1
  query prep, builds Simple Search UI/API URLs (`--open` / `--api`), AHK
  Ctrl+Alt+C, PWA Cologne button, Mac menu item. Builds on 2.1 (scheme_bridge,
  convert `--from`, guards, HUD) and 2.0 (smart/long-press/PWA). Not part of
  the PyPI/npm library API.
- **tools/KeySwap** — peer-tool survey + lean roadmap:
  [`SIMILARS_COMPARISON.md`](tools/KeySwap/SIMILARS_COMPARISON.md) (Lexilogos,
  Keyman/Heidelberg, EasyUnicode, SanskritTypist, Sanscript, Aksharamukha, …)
  with Tier A light-next features and explicit heavy-skips.
- **tools/KeySwap** — upstream page + **80-comment** analysis
  ([`UPSTREAM_KEYSWAP_ANALYSIS.md`](tools/KeySwap/UPSTREAM_KEYSWAP_ANALYSIS.md));
  README hero, Word/`=` troubleshooting, config recipes (danda, ॐ, svara),
  first-60-seconds launch path.

### Fixed

- `iast_to_devanagari` re-implemented as the `to_slp1` -> `slp1_to_devanagari`
  composition — the previous naive character-substitution was wrong on 9 of 9
  basic words (bare `ka` -> `कअ` instead of `क`); now correct on all 9 plus the
  D1 `ṁ` round-trip vector (H1394).

## [0.7.0] - 2026-07-14

### Removed — `csl_pyutil` package (superseded by a standalone repo, H925)

The `csl_pyutil/` package added in v0.6.0 below is **removed** — its own H925
handoff got filled in with a more complete spec (by a concurrent session)
partway through that work, requiring a standalone repo (explicitly not this
one — "thematic mismatch", the exact concern that motivated this sibling-
package compromise in the first place) and a byte-identical port from the
real donor (`build_h180_review_sheets.py`) rather than an independent
reimplementation. Real home now:
[sanskrit-lexicon/csl-pyutil](https://github.com/sanskrit-lexicon/csl-pyutil).
Both packages were briefly named `csl-pyutil` on PyPI-style naming, which
would have conflicted at install time — removing this one resolves that.

## [0.6.0] - 2026-07-14

### Added — `csl_pyutil` package: `render_review_sheet()` HTML emitter (H925)

New sibling package [`csl_pyutil/`](csl_pyutil/) (own `pyproject.toml`, own version
track `0.1.0`, no shared code with `sanskrit_util`) — generic, non-Sanskrit-specific
CDSL/Sanskrit-Lexicon tooling. First (and so far only) export:
`render_review_sheet(items, *, sheet_id, title, ...)`, extracting the interactive
approve/reject/defer HTML review-sheet the `/review-sheet` Claude Code skill
previously hand-wrote from scratch on every invocation into one deterministic,
tested emitter (12 pytest cases; browser-verified end to end with Playwright —
voting, keyboard shortcuts a/r/d, `localStorage` persistence across reload, the
download button producing valid decisions JSON, light+dark theme — no console
errors). Same exported decisions-JSON shape as before, so
[`Uprava/tools/review_decisions_watcher.py`](https://github.com/gasyoun/Uprava/blob/main/tools/review_decisions_watcher.py)
needs no changes. `~/.claude/commands/review-sheet.md` updated to call it instead
of hand-writing HTML. Closes the "lift into `sanskrit-util` or a `csl-pyutil`"
placeholder that [`SHARED_CODE.md`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md)
had carried since before this repo existed — `csl-pyutil` is now real, living here
rather than as a new repo (H925 originally named a standalone `csl-pyutil` repo;
this repo's existing publish/CI infrastructure made that unnecessary).

## [0.5.0] - 2026-07-08

### Added — `tools/epistemic/build_epistemic_dashboard.py` — the epistemic dashboard generator (H356)

Parses whichever of the seven registries live in `--dir` into one `epistemic.json`
(per-layer rows, importance 🔴🟠🟡, ⚙️ auto / ✍️ human origin split, STALENESS flag summary,
grand totals). Feeds a self-contained dashboard: published on the Sanskrit-data side
(<https://gasyoun.github.io/SanskritLexicography/episteme/>), local-only on the private
Uprava side. The Sanskrit-data repo vendors a byte-identical copy into its `epistemic_dashboard/`
so CI self-builds. No `Date.now()` in any derived count.

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

## [0.4.0] - 2026-07-04

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

## [0.3.0] - 2026-07-03

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

## [0.1.0] - 2026-06-14

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
