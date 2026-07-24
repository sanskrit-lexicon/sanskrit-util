# KeySwap plugins (v3)

_Created: 24-07-2026 · Last updated: 24-07-2026_

Optional heavy capabilities live here. **Nothing under this tree loads on
default Startup** (`install-windows.ps1` → `KeySwap.lnk` → `windows/KeySwap.ahk`).

Contract (full): [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](../docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Discovery

| Rule | Detail |
|------|--------|
| Layout | `plugins/<id>/manifest.json` with `"id"` == directory name |
| Autoload | Forbidden for heavy packs (`"never_autoload": true`) |
| Enable | CLI `--plugin <id>` and/or env `KEYSWAP_PLUGINS=id1,id2` only |
| Core imports | Do not import `plugins.*` from core modules at import time |

## Plugins

| id | V3 item | Status |
|----|---------|--------|
| [offline_fuzzy](offline_fuzzy/) | V3-2 | Scaffold only (no SQLite pack yet) |

## Do not

- Wire plugins into the default tray menu without an explicit user opt-in path.  
- Vendor multi-MB dictionaries into the default git tree without a separate pack story.  
- Dual-run Keyman + KeySwap hooks “because a plugin asked”.

_Dr. Mārcis Gasūns_
