# Plugin: `offline_fuzzy` (V3-2)

_Created: 24-07-2026 · Last updated: 24-07-2026_

Optional **offline fuzzy / full-index** headword lookup — the first v3 capability
pick per [KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](../../docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Why not core?

KeySwap **2.4** already ships a **seed** exact-match list
(`data/local_headwords.txt`, ~1k). A full MW / hwnorm1c-class index is multi-MB
and was an explicit 2.x skip. This plugin is the opt-in home for that weight.

## Status (H1581)

| Piece | State |
|-------|--------|
| Manifest + discovery | Present |
| `fuzzy_lookup.lookup` API | Stub (exact seed via core `local_wordlist` only) |
| SQLite / full MW pack | **Not** shipped |
| AHK / install wiring | **None** (by design) |

## Enable (when a future PR wires typing_check)

```bash
# Planned — not yet hooked in core CLI:
set KEYSWAP_PLUGINS=offline_fuzzy
python tools/KeySwap/typing_check.py --local-only --plugin offline_fuzzy --hud "rAma"
```

Until that hook lands, call the module directly for smoke:

```bash
python -c "from tools.KeySwap.plugins.offline_fuzzy.fuzzy_lookup import lookup; print(lookup('rAma'))"
# or from tools/KeySwap as cwd — see fuzzy_lookup.py docstring
```

## Data packs (later)

- Prefer building with existing `build_local_wordlist.py --from-spellcheck`.  
- Large packs: gitignore + download instructions; do not force into default clone.  
- Fuzzy rankers must document false-positive risk in the HUD string.

_Dr. Mārcis Gasūns_
