# KeySwap v3 — plugin / sibling architecture

_Created: 24-07-2026 · Last updated: 24-07-2026_  
_Handoff: [H1581](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1581-Sonnet_sanskrit-util_keyswap-v3-former-skips-heavy-wave_24.07.26.md) · [H1583](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1583-Sonnet_sanskrit-util_keyswap-v3-7-network-autocomplete_24.07.26.md) · Model: Grok 4.5 (`grok-4.5`)_  
_Roadmap: [ROADMAP_KEYSWAP_V2_V3.md](../ROADMAP_KEYSWAP_V2_V3.md) · Peers: [SIMILARS_COMPARISON.md](../SIMILARS_COMPARISON.md)_

## Hard principle

> **Core KeySwap stays the typing shell.** Heavy capabilities are **plugins or
> sibling apps**, never forced into the default Startup path
> (`packaging/install-windows.ps1` → `KeySwap.lnk` → `windows/KeySwap.ahk`).

Through 2.x, eight items were **explicit skips** so the tray app would not
become Keyman / Aksharamukha / Sanskrit Writer. v3 reopens them **only** as
opt-in packs. A default install after v3 must still feel like 2.7: hooks +
small data + Cologne link-outs.

## Layers

| Layer | What lives here | Loads on default Startup? |
|-------|-----------------|---------------------------|
| **Core shell** | AHK tray, cycle / smart / writer digraphs, scheme bridge, script mode, Cologne open/API/gloss, seed `local_headwords.txt`, optional DCS | **Yes** |
| **Plugin** | Optional Python (or future) module under `tools/KeySwap/plugins/<id>/` with a manifest; may ship multi-MB data | **No** — explicit env / CLI / tray opt-in only |
| **Sibling app** | Separate product surface (compose companion, OCR tool) that may share `sanskrit-util` code but has its own install entry | **No** — not a KeySwap.lnk target |
| **Link-out** | Static Ecosystem URLs (already 2.7 tray) | Yes (URLs only; no embed) |

## What never loads on default Startup

These must **not** be imported, `Run`, or menu-wired by default in:

- `windows/KeySwap.ahk`
- `packaging/install-windows.ps1` / `install-macos.sh`
- Apple host default menus without a user toggle

| Never by default | Reason |
|------------------|--------|
| Aksharamukha / full script matrix (V3-1) | Weight; 100+ scripts |
| Local MW / hwnorm1c SQLite pack (V3-2) | Multi-MB; server role |
| Keyman dual-hook with KeySwap (V3-3) | Dual-hook hell |
| OCR / TTS engines (V3-4 / V3-5) | Out of typing scope |
| Sanskrit Heritage segmenter process (V3-6) | Heavy grammar engine |
| Always-on network autocomplete (V3-7) | Latency + privacy + false positives |
| Full morphology / forms DB (V3-8) | Product-sized; SW-class |

**Allowed by default (already 2.x):** seed offline list (~1k), one-shot
network headword/gloss when the user presses a hotkey, Ecosystem *open URL*.

## Plugin discovery (folder + opt-in load)

```text
tools/KeySwap/plugins/
  README.md                 # discovery contract (this design’s operator half)
  <plugin_id>/
    manifest.json           # id, title, version, never_autoload, entry
    README.md               # how to enable; license of any data packs
    …                       # implementation (Python package preferred)
```

**Discovery rules:**

1. A directory under `plugins/` is a plugin **iff** it contains `manifest.json`
   with `"id"` matching the directory name.
2. Core code **must not** import `plugins.*` at module import time of
   `typing_check.py`, `cologne_search.py`, or AHK startup.
3. Load path is **opt-in only**, in this priority order:
   - CLI flag, e.g. `--plugin offline_fuzzy`
   - Env `KEYSWAP_PLUGINS=offline_fuzzy` (comma-separated ids)
   - Future: tray “Enable plugin…” that writes a user config **outside** the
     repo tree (e.g. `%APPDATA%\KeySwap\plugins.ini`) — not shipped in 3.0 scaffold
4. `manifest.json` field `"never_autoload": true` is mandatory for every heavy
   plugin; installers ignore plugins entirely unless a future flag is added.
5. Failed / missing plugin data → clear HUD error; never silent fallback that
   pretends the heavy path ran.

### Minimal manifest schema

```json
{
  "id": "offline_fuzzy",
  "title": "Offline fuzzy headword index",
  "version": "0.1.0",
  "never_autoload": true,
  "v3_item": "V3-2",
  "entry": "fuzzy_lookup:lookup",
  "data_note": "SQLite / large wordlist not vendored in git by default"
}
```

## Dependency map (former 2.x skips)

| ID | Capability | External dep | Ship form | Default path |
|----|------------|--------------|-----------|--------------|
| **V3-1** | Full script matrix | [Aksharamukha](https://aksharamukha.com/) (or embed) | Sidecar / optional Python dep; else Ecosystem URL | Link-out only until opt-in module |
| **V3-2** | Offline fuzzy / full MW index | MW key1 export, optional hwnorm1c-class DB | Optional data pack + plugin code | Seed list stays core; full index = plugin |
| **V3-3** | Keyman-class IME | [Keyman](https://keyman.com/) | Dual-install docs; thin bridge if ever | Never dual-hook with KeySwap default |
| **V3-4** | OCR | Aksharamukha OCR / other | Link-out or sibling | Link-out |
| **V3-5** | TTS | e.g. SRI TTS | Link-out | Link-out |
| **V3-6** | Heritage segmenter | [Sanskrit Heritage](https://sanskrit.inria.fr/) | Microservice / link-out | Link-out |
| **V3-7** | Network autocomplete | Cologne API (or other) | **shipped** opt-in plugin after V3-2 | Off by default; offline-first cascade |
| **V3-8** | Morphology / forms dict | SW-class lexical DB | **Sibling app** (“compose companion”) | Not a KeySwap plugin load |

## First plugin pick: **V3-2 offline fuzzy** (not V3-8)

| Criterion | V3-2 offline fuzzy | V3-8 compose companion |
|-----------|--------------------|------------------------|
| Fits typing shell | Yes — improves Ctrl+Alt+S offline path | No — compose/forms is a different job (SIMILARS vs SW) |
| Builds on shipped 2.4 | Yes — exact `local_headwords` → fuzzy / full index | Starts from near-zero product surface |
| Unblocks later items | Unblocks V3-7 (autocomplete needs a local index first) | Orthogonal |
| Weight / rights | Large but **optional** data pack; exact-match core stays tiny | Multi-MB morphology product + UX app |
| Risk to default Startup | Low if discovery rules hold | High if mistaken for “KeySwap core” |

**Recommendation (this memo):** scaffold **V3-2** as `plugins/offline_fuzzy/` for
KeySwap **3.0.0** first capability. Park **V3-8** as a future **sibling** design
doc (not a plugin that loads under the typing tray). V3-1/3–6 remain link-out or
later packs per the table above.

### V3-2 behaviour (implemented)

1. Exact SLP1 / normkey hit (same as 2.4 wordlist).  
2. Prefix + Levenshtein (length-scaled max dist 1–2) over the active wordlist.  
3. Data: seed `data/local_headwords.txt` or full MW via `build_local_wordlist.py` /
   `KEYSWAP_WORDLIST` — multi-MB packs stay opt-in paths, not default clone.  
4. Wired only behind `--plugin offline_fuzzy` / `KEYSWAP_PLUGINS` — **not** AHK
   default menus.

### Still out of default path

- No SQLite file committed (in-memory wordlist index is enough).  
- No import from `windows/KeySwap.ahk` or install scripts.  
- No change to Cologne online API as the primary online path.

## Operator checklist (every v3 PR)

- [ ] Default `install-windows.ps1` still starts only AHK core.  
- [ ] `python tools/KeySwap/validate_configs.py` green.  
- [ ] Grep: no new `plugins` import in AHK or install scripts.  
- [ ] Plugin `never_autoload: true` in manifest.  
- [ ] README / ROADMAP status row updated for touched V3-*.

### V3-7 behaviour (implemented — H1583)

1. Opt-in only: `--plugin network_autocomplete` / `KEYSWAP_PLUGINS=network_autocomplete`.  
2. **Implies** offline fuzzy pre-pass (V3-2).  
3. Network (Cologne Simple Search) runs **only** when offline is not confident
   (`not-found` / `no-wordlist`); exact / fuzzy-unique / fuzzy-multi stay local.  
4. Short network timeout (≤5 s); rate-limit errors use the same HUD labels as core.  
5. Never wired into default AHK / install.

## Status

| Deliverable | State |
|-------------|--------|
| This design memo | **shipped** (H1581) |
| First-pick decision (V3-2) | **recorded** |
| `plugins/` discovery + `offline_fuzzy` scaffold | **shipped** (H1581) |
| Fuzzy index (exact/prefix/edit) + `typing_check --plugin` | **shipped** |
| V3-7 `network_autocomplete` offline-first cascade | **shipped** (H1583) |
| V3-8 sibling app | **parked** (design-only pointer in ROADMAP) |

_Dr. Mārcis Gasūns_
