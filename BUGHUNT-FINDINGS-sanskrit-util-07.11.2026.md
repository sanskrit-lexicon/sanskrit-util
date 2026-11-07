# BUGHUNT-FINDINGS — sanskrit-util — 07-11-2026

_Created: 07-11-2026 · Last updated: 07-11-2026_

Nightly one-repo bug hunt (MG ruling 26-09-2026: nightly, one repo, auto-fix HIGH). Executor: GLM 5.3 Flash (zai-coding-plan/glm-5.3-flash). Scope: CODE only — [py/](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py), [js/](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/js), [tools/](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools) (incl. KeySwap core + plugins + PWA), [scripts/](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/scripts); vendored copies, lockfiles, node_modules, data giants skipped. Every finding below carries a live probe I actually ran on the 67e04e1 tree.

**Elapsed:** 03:01:00 → 03:33 +0300 (~32 min) · hunt ~29 min, landing ~3 min.

**Verdict: 0 HIGH · 2 MEDIUM · 5 LOW.** No HIGH code bugs → nothing auto-fixed this run (MEDIUM/LOW are report-only per the night rules). No committed secrets or credential/infra HIGHs → no GTD `@DO` row minted.

---

## Findings (ranked)

### M1 · MEDIUM — Python linkid/sidecar validators accept trailing-newline tails the JS twin rejects (broken twin contract; CLASS)

- **Where:** [`py/sanskrit_util/__init__.py` lines 695–717](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py#L695) (`_LINKID_ANCHOR_RE`, `_LINKID_TARGET_RE`, `_LINKID_DATE_RE` — all `$`-anchored), [`py/sanskrit_util/sidecar.py` line 79](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/sidecar.py#L79) → [blob](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/sidecar.py#L79) (`_HANDOFF_RE`, `_DATE_RE` — same `$` class); JS twin: [`js/index.mjs` lines 464–484](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/js/index.mjs#L464).
- **Bug:** Python `$` matches **before a trailing `\n`**; JS `$` does not. Both ports are documented as behaviour-identical ("proved by vectors"), but any tail carrying a trailing newline passes Python validation and is rejected by the JS twin. The vector set has no newline case, so the cross-language lock never sees it. A Python-side builder reading a TSV row without `rstrip()` (exactly the trap [tools/crosscheck.py line 78](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/crosscheck.py#L78) guards against manually) can mint `whitney-root:5\n` link-IDs or a sidecar `handoff: "H6979\n"` that Python gates accept.
- **Live evidence (ran this session):**
  - `linkid_parse_anchor_id('whitney-root:5\n')` → PY `{'type': 'whitney-root', 'tail': '5\n', 'valid': True}` vs JS `valid:false`.
  - `linkid_build_anchor_id({'type':'whitney-root','tail':'5\n'})` → PY `'whitney-root:5\n'` vs JS `null`.
  - `linkid_parse_target_locus('dcs:588488\n')` → PY `valid: True` vs JS `valid:false`.
  - `linkid_validate_link_record({... 'date':'07-11-2026\n'})` → PY `valid: True` vs JS `valid:false`.
  - `validate_sidecar({..., 'handoff':'H6979\n'})` → `[]` (accepted).
- **Class:** the `$`-anchor mechanism, all sites in this repo: the 3 linkid RE dicts + `_LINKID_DATE_RE` in `__init__.py`, `_HANDOFF_RE`/`_DATE_RE` in `sidecar.py`. Fix shape (when scheduled): anchor with `\Z` / `re.fullmatch` instead of `$`; JS side already correct. Sibling watch: kosha `typed_link_lint.py` (the canonical validator this module mirrors) almost certainly has the same `$` shape — check before fixing here.

### M2 · MEDIUM — `detect_scheme()` misroutes canonical ITRANS to Velthuis; `--from auto` silently emits wrong transliteration (CLASS)

- **Where:** [`tools/KeySwap/scheme_bridge.py` lines 240–244](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/scheme_bridge.py#L240) — the Velthuis marker regex (`\.[a-zA-Z]|"n|"s|~n`) is tested **before** the ITRANS regex, while both schemes share `.n/.m/.h/.t/.d/.s`; the ITRANS-only decisive tokens (`RRi`, `RRI`, `LLi`, `~N`, `sh`, `Sh`) are never consulted first. Consumers: [`scheme_to_iast(..., 'auto')`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/scheme_bridge.py#L202) and [`cologne_search.to_slp1()` auto branch lines 179–194](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/cologne_search.py#L179) — so Cologne query keys are also wrong for ITRANS input under auto.
- **Bug:** the function's own docstring example — `python scheme_bridge.py --from itrans "sa.nskRRitam"` — misroutes under `--from auto`.
- **Live evidence (ran this session):**
  - `detect_scheme('sa.nskRRitam')` → `'velthuis'` (should be `itrans`).
  - `scheme_to_iast('sa.nskRRitam', 'auto')` → `'saṇskRRitam'`; correct `itrans` path → `'saṇskṛtam'`.
  - Minor sibling: `detect_scheme` can return `'deva'`, but `scheme_to_iast(text, 'deva')` raises `ValueError: unknown scheme: 'deva'` (only `main()` special-cases it) — probed live.
- **Class:** shared-marker ordering; one fix site (reorder: test ITRANS-only tokens before the Velthuis marker regex, or make the Velthuis regex exclude ITRANS-only tokens).

### L1 · LOW — dead wiring: Cologne `"default"` scheme branch is unreachable

- **Where:** [`tools/KeySwap/cologne_search.py` line 209](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/cologne_search.py#L209) vs [line 179](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/cologne_search.py#L179).
- `to_slp1()`'s auto branch already consumes `"default"` (`s in ("auto","detect","default","simple")`), so the dedicated `if s == "default":` fuzzy-input path six lines later can never execute — the "Cologne default fuzzy input" behaviour its comment promises is silently the auto path instead. Evidence: code-read + the branch order; no runtime probe possible on an unreachable line.

### L2 · LOW — `derive_staleness.py`: a future-dated finding is flagged 🟢 but counted in no snapshot bucket

- **Where:** [`tools/epistemic/derive_staleness.py` lines 105–110](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py#L105) (`flag_for`) vs [lines 170–173](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py#L170) (snapshot counts).
- A typo'd future date gives `age < 0`: `flag_for(-5)` returns 🟢 (probed live), but the snapshot's green bucket is `0 <= age < 91`, so the row is counted nowhere and 🔴+🟡+🟢+⬜ no longer sum to `total`. Denominator-only; the table row itself still renders.

### L3 · LOW — PWA service worker never purges old caches and never warms the cache on successful fetch

- **Where:** [`tools/KeySwap/pwa/sw.js` lines 1–14](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/pwa/sw.js#L2).
- Installs cache `keyswap-2.1.0` but has no `activate` handler, so caches from previous version strings are never deleted; the fetch handler is pure cache-first (`caches.match … || fetch`) and never `cache.put`s successful responses. Old-version cache growth + a renamed asset stays stale until the CACHE string bumps. Dev-grade surface; report only.

### L4 · LOW — `crosscheck.py` would silently truncate if the JS runner returned fewer outputs

- **Where:** [`tools/crosscheck.py` line 112](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/crosscheck.py#L112).
- `zip(py[fn], js[fn])` pairs element-wise; if a future edit of [`crosscheck_js.mjs`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/crosscheck_js.mjs) dropped an input, the shorter side silently truncates the comparison and the missing case reads as agreement. A `len(a) != len(b)` guard would make the adversarial harness fail loud. Defensive-only today (both sides map the same arrays).

### L5 · LOW — Python `_gm_token_pattern` lacks the backslash hardening its JS twin carries (parity note)

- **Where:** [`py/sanskrit_util/__init__.py` lines 593–596](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/__init__.py#L593) vs the hardened [`js/index.mjs` lines 377–379](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/js/index.mjs#L377).
- The JS side escapes `\` before `.` (CodeQL incomplete-string-escaping hardening, comment cites it); the Python side escapes only `.`. All tokens today are compile-time constants with no backslash, so this is not exploitable — parity note so a future dynamic token doesn't reopen the injection surface on one side only.

---

## Checked and clean (negative results, probed)

- **No committed secrets.** [`tools/KeySwap/vendor/key.bin`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/vendor/key.bin) is a 4-byte third-party vendor blob (`bb 00 00 00`, part of the upstream KeySwap reference bundle documented in [THIRD_PARTY_NOTICE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/THIRD_PARTY_NOTICE.md)), not a credential; `keyswap.exe` is the documented vendored upstream binary. No keys/tokens in tracked sources.
- **No build-artifact leakage:** `py/dist/`, `*.egg-info/`, `__pycache__/`, `.pytest_cache/` are gitignored and untracked (`git ls-files` verified) — the 0.12.0 wheel on disk is local residue only.
- **verify-gate anti-tamper** ([scripts/verify.sh](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/scripts/verify.sh)): audit-trail replay + tamper detection is sound; hand-editing `feature_list.json` cannot self-certify.
- Swallowed-error sites ([sidecar.py:264](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/py/sanskrit_util/sidecar.py#L264), [convert_bridge.py:131](https://github.com/sanskrit-util/blob/main/tools/KeySwap/convert_bridge.py#L131), changelog guards' `git_show` excepts) are all deliberate cleanup/skip paths that re-raise or return sentinel values — no silent failure.
- Plugin opt-in discipline ([discovery.py](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/discovery.py), both `manifest.json` `never_autoload` guards) and the network plugin's offline-first policy hold under test.

## What verified green (ran this session, tree 67e04e1)

| Gate | Result |
|---|---|
| `python3 -m pytest py/tests -q` | 54 passed |
| `node --test js/test/*.test.mjs` | 3 passed, 0 failed |
| `python3 -m pytest tools/KeySwap -q` | 120 passed |
| `python3 tools/crosscheck.py` | 546 cross-language checks OK (py == js == donor) |
| `python3 tools/gen_vectors.py` + `git diff` | vectors.json byte-identical (no drift) |
| `bash scripts/verify.sh --check` | VCR 3/3 verified/passing, full checks green |
| `node js/build-global.mjs --check` | global build current (717 vectors) |

## Disposition

- **Auto-fix (HIGH code):** none applicable — 0 HIGH. M1/M2 and the LOWs stay report-only per the night rules; M1 is the strongest candidate for a follow-up fix lane (`\Z`-anchors, class-wide, JS untouched) if promoted.
- **Credential/infra HIGH → GTD `@DO`:** none found — no row minted.

_Dr. Mārcis Gasūns_
