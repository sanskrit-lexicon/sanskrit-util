# KeySwap plugins (v3)

_Created: 24-07-2026 · Last updated: 05-09-2026_

Optional heavy capabilities live here. **Nothing under this tree loads on
default Startup** (`install-windows.ps1` → `KeySwap.lnk` → `windows/KeySwap.ahk`).

Contract (full): [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Discovery

| Rule | Detail |
|------|--------|
| Layout | `plugins/<id>/manifest.json` with `"id"` == directory name |
| Autoload | Forbidden for heavy packs (`"never_autoload": true`) |
| Enable | CLI `--plugin <id>` and/or env `KEYSWAP_PLUGINS=id1,id2`, **or** the tray "Plugins" submenu (Windows/Mac, H1639) — the tray click just sets the same env var, never a parallel mechanism |
| Core imports | Do not import `plugins.*` from core modules at import time |

## Plugins

| id | V3 item | Status |
|----|---------|--------|
| [offline_fuzzy](offline_fuzzy/) | V3-2 | **Implemented** — exact + prefix + edit-distance; enable with `--plugin offline_fuzzy`, `KEYSWAP_PLUGINS`, or the tray toggle. [Full-MW pack docs](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/offline_fuzzy/README.md#full-mw-pack-opt-in-not-vendored). |
| [network_autocomplete](network_autocomplete/) | V3-7 | **Implemented** — offline first, Cologne only when local is not confident; `--plugin network_autocomplete`, `KEYSWAP_PLUGINS`, or the tray toggle. |

Tray opt-in state is persisted by [`tray_state.py`](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/tray_state.py) —
`%APPDATA%\KeySwap\plugins.ini` on Windows / `UserDefaults` on Mac, both
**outside** this repo tree. See `windows/KeySwap.ahk`'s "Plugins (opt-in; off
by default)" tray submenu, and `apple/macos/KeySwapMacApp.swift`'s equivalent
status-bar submenu.

## Do not

- Wire plugins into the default tray menu without an explicit user opt-in path.
  (The Plugins **submenu itself** is fine — see above — the ban is on
  default-*on* wiring, i.e. loading a plugin without a click.)
- Vendor multi-MB dictionaries into the default git tree without a separate pack story.  
- Dual-run Keyman + KeySwap hooks “because a plugin asked”.

_Dr. Mārcis Gasūns_
