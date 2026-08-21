# KeySwap 2.8 for Windows (AutoHotkey v2)

_Created: 23-07-2026 · Last updated: 21-08-2026_

## Run

1. Install [AutoHotkey v2](https://www.autohotkey.com/).  
2. Double-click [`KeySwap.ahk`](KeySwap.ahk).  
3. Default mode: **cycle** (letter then `=` only). Smart digraphs are opt-in.

```text
autohotkey64.exe KeySwap.ahk "..\configs\iast-classic.txt"
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
| **Trigger** (default `=`) | Cycle last form |
| Shift+**Trigger** | Literal trigger char (does not cycle) |

## 2.8 trigger presets (non-US)

When `=` is wrong for your layout (or Word steals it), pick another cycle key:

| Preset | Key | How |
|--------|-----|-----|
| `equals` | `=` | Default US |
| `bracket` | `]` | Common PE workaround |
| `slash` | `/` | Alternate |
| `backtick` | `` ` `` | Alternate |

**Ways to set:**

1. Tray → **Trigger: …** submenu (writes `trigger.ini`)  
2. Edit [`trigger.ini`](trigger.ini) (copy from [`trigger.example.ini`](trigger.example.ini)): `preset=bracket`  
3. Env `KEYSWAP_TRIGGER=bracket` (wins over file)

Canonical table: [`../trigger_presets.py`](../trigger_presets.py).

Also:

```text
python ..\scheme_bridge.py --from hk "saMskRta"
python ..\cologne_search.py "rāma" --open --dict mw
```

## Startup on non-US layouts

Writer-scheme `~` (e.g. `~n` → ñ) is registered as the braced key `{~}`.
If the active layout has no tilde (Russian JCUKEN), that one mark is
skipped silently — switch to EN and press **F6** to bind it. Do not
register `~` by string-concat (`"~*" "~"`): AutoHotkey parses that as
`~*~` and warns that `~^` is missing.

AHK v2.0 fat-arrows are a **single expression**. Tray items that need
several calls (reload) must use a named function (`ReloadConfig`), not
`(*) => { ... }`.

## Legacy PE

Optional: [`../vendor/`](../vendor/) — see [packaging/VENDOR_PE.md](../packaging/VENDOR_PE.md).

_Dr. Mārcis Gasūns_
