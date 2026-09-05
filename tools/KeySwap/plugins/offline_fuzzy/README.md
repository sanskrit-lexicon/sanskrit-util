# Plugin: `offline_fuzzy` (V3-2)

_Created: 24-07-2026 · Last updated: 05-09-2026_

Optional **offline fuzzy** headword lookup over the KeySwap local SLP1 wordlist
(exact → prefix → edit-distance). First v3 capability pick per
[KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Why not core?

KeySwap **2.4** already ships a **seed** exact-match list
(`data/local_headwords.txt`, ~1k). Fuzzy ranking adds false-positive risk and
scan cost over a full MW key1 (~200k). This plugin is **opt-in only**.

## Enable

```bash
# CLI
python tools/KeySwap/typing_check.py --local-only --plugin offline_fuzzy --hud "rAm"

# Env (same session)
set KEYSWAP_PLUGINS=offline_fuzzy
python tools/KeySwap/typing_check.py --local-only --hud "rAm"
```

Direct module smoke:

```bash
python tools/KeySwap/plugins/offline_fuzzy/fuzzy_lookup.py rAm
```

## Behaviour

| Status | Meaning | `found` / HUD |
|--------|---------|----------------|
| `exact` | Key in wordlist | ✓ known |
| `fuzzy-unique` | Single prefix or dist≤1 edit | ~ known (soft) |
| `fuzzy-multi` | Several near matches | ~ not known; `near: a, b, c` |
| `not-found` | No near hit | ✗ |

## Full-MW pack (opt-in, not vendored)

The shipped seed (`data/local_headwords.txt`, ~1k) is exact-match only, by
design — see "Why not core?" above. A user who wants the fuzzy ranker to
cover the **full MW key1** (~194k entries, ~2 MB) can point at the org's
existing `HeadwordLists/` exports instead of re-deriving anything. **Nothing
here is vendored into this git tree** — the pack lives in a sibling repo you
already have checked out, or fetch it separately.

**Fastest path — no build step.** `local_wordlist.py` loads any one-key-per-line
SLP1 file directly (BOM-safe), so `KEYSWAP_WORDLIST` can point straight at the
export:

```bash
# Windows (persists for the current user; PowerShell)
setx KEYSWAP_WORDLIST "C:\Users\<you>\Documents\GitHub\SanskritLexicography\HeadwordLists\now-2026\MW-unique-key1-194084.txt"

# Same session only (any shell)
set KEYSWAP_WORDLIST=C:\Users\<you>\Documents\GitHub\SanskritLexicography\HeadwordLists\now-2026\MW-unique-key1-194084.txt

python tools/KeySwap/typing_check.py --local-only --plugin offline_fuzzy --hud "rAm"
```

Use **key1** (not key2) — key1 is the normalized computational key meant for
matching/dedup; key2 retains accent/hyphen marks from the printed source and
is not what the fuzzy index wants (see
[`SanskritLexicography/CLAUDE.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/CLAUDE.md)
"key1 vs key2"). Either the frozen
[`then-2014/MW-unique-key1-193978.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/then-2014/MW-unique-key1-193978.txt)
or the current
[`now-2026/MW-unique-key1-194084.txt`](https://github.com/gasyoun/SanskritLexicography/blob/master/HeadwordLists/now-2026/MW-unique-key1-194084.txt)
works; prefer `now-2026` unless you specifically need the frozen snapshot.

**Merged-copy path** — if you'd rather have `build_local_wordlist.py` write a
deduped copy, send `--out` **outside the repo tree** (its default,
`data/local_headwords.txt`, is the tracked ~1k seed — never point a ~194k
`--out` at a tracked path, that would vendor the full pack into git on the
next commit):

```bash
python tools/KeySwap/build_local_wordlist.py \
  --from-file "..\SanskritLexicography\HeadwordLists\now-2026\MW-unique-key1-194084.txt" \
  --out "%APPDATA%\KeySwap\local_headwords_full.txt"
set KEYSWAP_WORDLIST=%APPDATA%\KeySwap\local_headwords_full.txt

# or, if SanskritSpellCheck/HeadwordLists is checked out as a sibling repo
# (its MW-unique-key1-*.txt is the same export, mirrored for spellcheck tooling):
python tools/KeySwap/build_local_wordlist.py --from-spellcheck --out "%APPDATA%\KeySwap\local_headwords_full.txt"
```

Either path is **manual, one-time, and per-user** — no install script or
default Startup path reads `HeadwordLists/` or writes `KEYSWAP_WORDLIST` for
you; it stays exactly as opt-in as the plugin itself.

## Status

| Piece | State |
|-------|--------|
| Manifest + `never_autoload` | Yes |
| Exact + prefix + Levenshtein | **Yes** |
| `typing_check --plugin` / `KEYSWAP_PLUGINS` | **Yes** |
| SQLite pack | Not required (wordlist index is enough) |
| Full-MW pack docs (this section) | **Yes** (H1639) |
| Tray opt-in (Windows menu / Mac status-bar menu) | **Yes** (H1639) — toggles `KEYSWAP_PLUGINS`, still one explicit click, still off by default |
| AHK / install wiring of plugin *code* | **None** (by design — the tray only sets an env var, never imports `plugins.*`) |

## Do not

- Import this package from `windows/KeySwap.ahk` or `install-windows.ps1`.  
- Treat fuzzy-unique as morphologically “correct forms” — existence/near-key only.
- Point `build_local_wordlist.py --out` (or any full-MW copy) at a path tracked by git — see "Full-MW pack" above.

_Dr. Mārcis Gasūns_
