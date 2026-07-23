# KeySwap 2.0 for Windows (AutoHotkey v2)

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
| `smart` | Digraphs `aa`→ā, `sh`→ś, … **and** `=` cycle |
| `deadkey` | `'` then letter → ā ī ū ṛ … (classroom-friendly) |

Tray menu switches mode live. **F6** or file change reloads config (duplicate bases show a message).

## Convert clipboard

Requires Python + repo `py/sanskrit_util`:

| Hotkey | Action |
|--------|--------|
| Ctrl+Alt+= | Clipboard → Devanāgarī |
| Ctrl+Alt+I | Clipboard → IAST |

## Legacy PE

Optional: [`../vendor/keyswap.exe`](../vendor/keyswap.exe) — see provenance docs. Prefer this AHK for 2.0.

_Dr. Mārcis Gasūns_
