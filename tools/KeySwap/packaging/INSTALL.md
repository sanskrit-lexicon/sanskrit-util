# KeySwap — one install path (Windows + Mac)

_Created: 24-07-2026 · Last updated: 21-08-2026_

**Goal:** double-click (or one script) and type — without hunting folders.

Notarized / code-signed binaries still need a human Apple/Windows cert
([APP_STORE.md](APP_STORE.md)). Until then this is the **supported developer install**.

---

## Two different “Keyswaps” (do not run both)

| | **Vendor PE (legacy 1.x)** | **KeySwap 2.x toolkit (this repo)** |
|--|---------------------------|--------------------------------------|
| What | Single `keyswap.exe` (Yes Vedanta–style portable app) | `AutoHotkey` + `windows/KeySwap.ahk` + Python helpers |
| Where you might see it | e.g. `Documents\KeySwap\keyswap.exe`, or [`vendor/`](../vendor/) | `sanskrit-util/tools/KeySwap/` |
| Features | `=` cycle (basic) | Cycle · smart/Writer · Cologne · gloss · script mode · offline list · optional DCS |
| Portable? | **Yes** — one folder / one exe | **Yes** — no MSI required; AHK zip + repo scripts + optional Startup **shortcut** |
| Default? | **No** | **Yes** (Windows) |

**Do not run PE and AHK at the same time.** Both hook keyboard input; dual `=` handlers fight (Word glitches, double-inserts). Quit `keyswap.exe` / remove its Startup entry before using AHK 2.x.

Policy detail: [VENDOR_PE.md](VENDOR_PE.md). Provenance of any vendored exe: [PROVENANCE.md](../PROVENANCE.md).

---

## Windows (recommended)

### Prerequisites

1. [AutoHotkey v2](https://www.autohotkey.com/)  
2. [Python 3.10+](https://www.python.org/) on `PATH` (for convert / Cologne / headword check)

### One command

From a PowerShell prompt in the **sanskrit-util** repo:

```powershell
powershell -ExecutionPolicy Bypass -File tools\KeySwap\packaging\install-windows.ps1
```

What it does:

- Ensures `windows\allowlist.txt` exists (from the example)  
- Locates AutoHotkey v2 under Program Files **or** a portable user install  
  (`%LocalAppData%\Programs\AutoHotkey\`)  
- Optionally adds a **Startup** shortcut so the **AHK script** loads at login  
  (not the PE)  
- Starts `windows\KeySwap.ahk` (tray icon — no main window)

If you already run a portable `keyswap.exe` from another folder, **exit it first**.

### Manual (same result)

1. Double-click [`windows/KeySwap.ahk`](../windows/KeySwap.ahk)  
2. Default is **cycle** only (`n` then `=`). Tray → **Mode: smart** only for a Sanskrit burst: smart rewrites English (`ll`→ḷ, `ss`→ṣ, `sh`→ś, `tt`→ṭ) and you cannot type ordinary words.  
3. Type in Notepad: `n` then `=` → ṇ. Writer-scheme is tray **Mode: writer** (`-` then `a` → ā).  

### First hotkeys

| Key | Action |
|-----|--------|
| `=` | Cycle diacritic |
| Ctrl+Alt+D | Toggle script mode IAST ⇄ Devanāgarī |
| Ctrl+Alt+V | Clipboard → current script mode |
| Ctrl+Alt+S | Headword check (Cologne → local) |
| Ctrl+Alt+G | Open MW **gloss** page (webtc) |
| Ctrl+Alt+C | Cologne Simple Search |

---

## macOS

### Prerequisites

1. Xcode Command Line Tools (`xcode-select --install`)  
2. Accessibility permission for KeySwap (System Settings → Privacy)  
3. Python 3 for convert / Cologne helpers

### One command

```bash
bash tools/KeySwap/packaging/install-macos.sh
```

What it does:

- Builds the menu-bar app with Swift Package Manager when possible  
- Or prints the run-from-source path  
- Opens Accessibility settings  

### Manual

```bash
cd tools/KeySwap/apple
swift build
# or open the package in Xcode and run KeySwapMacApp
```

Grant **Accessibility**, then use the tray menu: profiles, script mode, Cologne, gloss.

---

## Verify

```bash
python tools/KeySwap/validate_configs.py
python tools/KeySwap/test_smart_input.py
python tools/KeySwap/typing_check.py --local-only --hud "rāma"
```

---

## vs Sanskrit Writer (install expectation)

| | KeySwap | Sanskrit Writer |
|--|---------|-----------------|
| Install | AHK script or Mac tray app (this page) | Desktop app installer |
| Signed store build | Checklist only ([APP_STORE.md](APP_STORE.md)) | Product binary |
| After install | Tray icon; type system-wide | App-focused output modes |

_Dr. Mārcis Gasūns_
