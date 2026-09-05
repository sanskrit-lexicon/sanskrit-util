# tools/epistemic — auto-derivation builders for the seven epistemic sibling registries

_Created: 08-07-2026 · Last updated: 05-09-2026_

Seven builders that seed / generate the **epistemic sibling registries** minted under
[H356](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H356-Opus_csl-corrections_epistemic-sibling-registries_08.07.26.md).
Each registry occupies one epistemic slot that `FINDINGS.md` (measured-fact-only) structurally
cannot hold. The registries are **mirrored across two sides** — a Sanskrit-data copy next to
[`SanskritLexicography/FINDINGS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/FINDINGS.md)
and an infra/process copy next to
[`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md).

These builders live here (in `sanskrit-util`, the shared toolkit) so both sides run the **same**
code; re-vendor to any consumer on a version bump via
[`/cologne-sanskrit-util-sync`](https://github.com/gasyoun/github-spine/blob/main/SHARED_CODE.md).

| Script | Layer | Automation | What it emits |
|--------|-------|-----------|---------------|
| [`derive_staleness.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/derive_staleness.py) | STALENESS | **full** (regenerate, never hand-edit) | the whole confidence-decay table over a FINDINGS file |
| [`seed_recipes.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_recipes.py) | RECIPES | high | recipe stubs from manifest builders + FINDINGS command-citations |
| [`seed_gaps.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_gaps.py) | GAPS | high | set-difference candidates (manifest datasets with no FINDINGS row) |
| [`seed_contradictions.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_contradictions.py) | CONTRADICTIONS | medium | crosswalk-mismatch candidates (two TSVs, shared key, differing value) |
| [`seed_dead_ends.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/seed_dead_ends.py) | DEAD_ENDS | medium | QUESTIONS_LOG refuted rows + SERVER_OUTAGES permanent-dead hosts |
| [`scan_assumptions.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/scan_assumptions.py) | ASSUMPTIONS | low | `# ASSUMES:` / `# INVARIANT:` / builder-`assert` tag grep |
| (glossary) | GLOSSARY | none | hand-curated; token-frequency assist only |
| [`build_epistemic_dashboard.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/build_epistemic_dashboard.py) | (all 7) | full | `epistemic.json` for the dashboard — per-layer row/importance/origin counts + STALENESS flags |
| [`normalize_provenance.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/normalize_provenance.py) | (all 6 entry) | — | finishing pass: clickable repo tags, bare model version id, commits-by-date link in every `> **Source:**` line (idempotent) |
| [`_provenance.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/_provenance.py) | — | — | shared helpers (verified repo→URL map, `repo_link`, `date_link`, `strip_model_tier`) used by the seeders + normalizer |

### The lifecycle — read [`PROTOCOL.md`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/PROTOCOL.md)

[`PROTOCOL.md`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/PROTOCOL.md) is the algorithm for moving a row along: **confirm** an `⚙️ auto`
candidate to `✍️ human` (or delete it), **graduate** a vouched row into `FINDINGS` /
`CROSS_REPO_DECISIONS`, or **delete** it — with the per-layer exit conditions. The registries are
staging areas, not archives; that doc is how they stay live.

### The dashboard

[`build_epistemic_dashboard.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/epistemic/build_epistemic_dashboard.py) parses whichever of the seven
registries exist in `--dir` into one `epistemic.json`. It feeds a small self-contained
dashboard published on the **Sanskrit-data** side (public Pages,
<https://gasyoun.github.io/SanskritLexicography/episteme/>) and generated locally on the
**infra** side (Uprava is private — local-only, no Pages). The Sanskrit-data side vendors a
byte-identical copy of this script into its `epistemic_dashboard/` so CI self-builds; re-vendor
on version bump via `/cologne-sanskrit-util-sync`.

## Conventions (all builders)

- `sys.stdout/stderr.reconfigure(encoding='utf-8')`; write files with `encoding='utf-8'` (**no BOM**).
- **No `Date.now()` / no system clock in the derivation math** — `--today DD-MM-YYYY` is passed
  in, so a re-run on the same inputs is byte-identical and diffable (this is what makes
  `derive_staleness.py` a regenerate-not-edit artifact).
- Auto-emitted rows carry the `⚙️ auto` origin marker and are **candidates** until a human
  confirms (⚙️→✍️), fills the blanks, or deletes them. `STALENESS` is the exception — it is
  fully generated and not hand-edited.
- Every row of every registry opens with the shared FINDINGS traffic-light dot
  (🔴 3 · 🟠 2 · 🟡 1); what the dot rates varies by layer (blast radius, impact, value,
  re-attempt cost) but the three-tier scale never changes.

## Examples

```sh
# STALENESS — regenerate both sides (run on every FINDINGS change)
python derive_staleness.py --findings ../../SanskritLexicography/FINDINGS.md \
  --today 08-07-2026 --side sanskrit \
  --repo-url https://github.com/gasyoun/SanskritLexicography/blob/master \
  --out ../../SanskritLexicography/STALENESS.md

# GAPS — which kosha datasets have no FINDINGS row yet?
python seed_gaps.py --manifest ../../kosha/data/manifest/datasets.json \
  --findings ../../SanskritLexicography/FINDINGS.md --today 08-07-2026

# DEAD_ENDS — harvest refuted hypotheses + dead hosts
python seed_dead_ends.py --questions-log ../../Uprava/QUESTIONS_LOG.md \
  --server-outages ../../Uprava/SERVER_OUTAGES.md --today 08-07-2026
```

_Dr. Mārcis Gasūns_
