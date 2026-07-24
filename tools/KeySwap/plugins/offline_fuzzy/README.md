# Plugin: `offline_fuzzy` (V3-2)

_Created: 24-07-2026 · Last updated: 24-07-2026_

Optional **offline fuzzy** headword lookup over the KeySwap local SLP1 wordlist
(exact → prefix → edit-distance). First v3 capability pick per
[KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](../../docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

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

Expand the index (optional full MW, not vendored):

```bash
python tools/KeySwap/build_local_wordlist.py --from-spellcheck
# or
set KEYSWAP_WORDLIST=path\to\MW-unique-key1.txt
```

## Status

| Piece | State |
|-------|--------|
| Manifest + `never_autoload` | Yes |
| Exact + prefix + Levenshtein | **Yes** |
| `typing_check --plugin` / `KEYSWAP_PLUGINS` | **Yes** |
| SQLite pack | Not required (wordlist index is enough) |
| AHK / install wiring | **None** (by design) |

## Do not

- Import this package from `windows/KeySwap.ahk` or `install-windows.ps1`.  
- Treat fuzzy-unique as morphologically “correct forms” — existence/near-key only.

_Dr. Mārcis Gasūns_
