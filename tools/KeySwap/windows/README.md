# KeySwap 2.1 for Windows (AutoHotkey v2)

_Created: 23-07-2026 · Last updated: 23-07-2026_

## Run

1. Install [AutoHotkey v2](https://www.autohotkey.com/).  
2. Double-click [`KeySwap.ahk`](KeySwap.ahk).  
3. Default mode: **smart** (digraphs + cycle).

```text
autohotkey64.exe KeySwap.ahk "..\configs\iast-classic.txt" smart
autohotkey64.exe KeySwap.ahk "..\configs\vedic-svara.txt" cycle
autohotkey64.exe KeySwap.ahk "..\config.txt" deadkey
```

## Modes

| Mode | Behaviour |
|------|-----------|
| `cycle` | Letter then `=` only |
| `smart` | Digraphs + `=` cycle |
| `deadkey` | `'` then letter → ā ī ū ṛ … |

## 2.1 guards & HUD

| Feature | How |
|---------|-----|
| **Keyman conflict** | Tray warning if Keyman processes are running |
| **Allowlist** | Copy `allowlist.example.txt` → `allowlist.txt` (one `exe` per line) |
| **Teaching HUD** | Brief ToolTip on cycle/smart (toggle **F7**) |
| **Hot-reload** | **F6** or config file change |

## Convert clipboard

Requires Python + repo `py/sanskrit_util`:

| Hotkey | Action |
|--------|--------|
| Ctrl+Alt+= | Clipboard → Devanāgarī |
| Ctrl+Alt+I / H | Clipboard auto-scheme → IAST |
| Ctrl+Alt+C | Clipboard → [Cologne Simple Search](https://sanskrit-lexicon.uni-koeln.de/simple/) |
| Ctrl+Alt+D | Toggle **script mode** IAST ⇄ Devanāgarī |
| Ctrl+Alt+V | Clipboard → current script mode |
| Ctrl+Alt+S | Clipboard **headword check** (Cologne API → local wordlist fallback, HUD) |
| Ctrl+Alt+G | Open Cologne **webtc gloss** (full MW entry) |
| Ctrl+Alt+K | Copy **SLP1 + normkey** of clipboard |
| Shift+= | Literal `=` (does not cycle) |

Also:

```text
python ..\scheme_bridge.py --from hk "saMskRta"
python ..\cologne_search.py "rāma" --open --dict mw
```

## Legacy PE

Optional: [`../vendor/`](../vendor/) — see [packaging/VENDOR_PE.md](../packaging/VENDOR_PE.md).

_Dr. Mārcis Gasūns_
