# KeySwap **2.0** — IAST diacritic toolkit

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Version: [2.0.0](VERSION)_

Type Sanskrit **romanization** (IAST / ISO-style) with a shared config language
across **Windows, iPhone, Mac, and the browser**.

```text
n  =  =  =     →  ṇ → ṅ → ñ          (cycle)
aa ii sh       →  ā  ī  ś            (smart digraphs, 2.0)
long-press n   →  menu n ṇ ṅ ñ       (iOS / PWA, 2.0)
```

Not part of the [`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util)
library API (PyPI/npm). The library transcodes strings in code; KeySwap helps
humans *type*. Convert selection uses the library’s `iast_to_devanagari` /
`deva_to_iast`.

Web research that drove 2.0: [IMPROVEMENTS_FROM_WEB.md](IMPROVEMENTS_FROM_WEB.md).

---

## What’s new in 2.0

| Feature | Detail |
|---------|--------|
| **Smart digraphs** | `aa`→ā, `ii`→ī, `rr`→ṛ, `sh`→ś, `nn`→ṇ, … |
| **Long-press** | iOS keyboard + offline PWA show full cycle menus |
| **Convert bridge** | IAST ↔ Devanāgarī via sanskrit-util (`convert_bridge.py`) |
| **Hot-reload** | AHK watches `config.txt` (or F6) |
| **Modes (Windows)** | `cycle` · `smart` (default) · `deadkey` (`'` + letter) |
| **Vedic svara profile** | `configs/vedic-svara.txt` |
| **Classroom path** | [layouts/](layouts/) cheatsheet + system-layout guide |
| **Offline PWA** | [pwa/](pwa/) Lexilogos-style pad |
| **Open default** | Prefer AHK / Apple / PWA over the legacy PE |

---

## What to run

| Platform | Recommended | Path |
|----------|-------------|------|
| **Windows** | AHK 2.0 script | [windows/KeySwap.ahk](windows/KeySwap.ahk) |
| **iPhone / iPad** | Custom keyboard 2.0 | [apple/](apple/) |
| **Mac** | Menu-bar app 2.0 | [apple/macos/](apple/macos/) |
| **Any browser** | Offline PWA | [pwa/index.html](pwa/index.html) |
| **Windows (legacy)** | Vendor PE 1.x | [vendor/](vendor/) — optional |
| **Logic / CI** | Python | `cycle_engine.py`, `smart_input.py`, tests |

---

## Layout

```text
KeySwap/
  VERSION                    # 2.0.0
  README.md
  IMPROVEMENTS_FROM_WEB.md   # survey → backlog
  PROVENANCE.md              # vendor PE hashes
  THIRD_PARTY_NOTICE.md
  config.txt                 # default = iast-classic
  configs/                   # scholarly profiles
  cycle_engine.py            # cycle semantics
  smart_input.py             # digraphs + long-press menus
  convert_bridge.py          # IAST ↔ Deva via sanskrit-util
  validate_configs.py
  test_*.py
  layouts/                   # classroom / no-hook docs
  pwa/                       # offline web pad
  windows/KeySwap.ahk        # open Windows shell
  apple/                     # KeySwapCore + iOS + Mac
  vendor/                    # third-party 1.x PE
```

---

## Profiles

| File | Use |
|------|-----|
| `configs/iast-classic.txt` | Classical IAST (default) |
| `configs/iso15919.txt` | ē ō ḻ ṉ … |
| `configs/vedic-draft.txt` | Length + acute |
| `configs/vedic-svara.txt` | Accents / combining-mark experiments |
| `configs/personal-legacy.txt` | Upstream personal map |

```bash
python tools/KeySwap/validate_configs.py
python tools/KeySwap/test_cycle_engine.py
python tools/KeySwap/test_smart_input.py
```

---

## Quick starts

### Windows (AHK 2.0)

1. Install [AutoHotkey v2](https://www.autohotkey.com/).  
2. Run [`windows/KeySwap.ahk`](windows/KeySwap.ahk) (default mode **smart**).  
3. Type `n` then `=` to cycle; type `aa` for ā.  
4. Tray: switch mode · F6 reload · Ctrl+Alt+= clipboard→Devanāgarī · Ctrl+Alt+I →IAST.

```text
autohotkey64.exe tools\KeySwap\windows\KeySwap.ahk tools\KeySwap\configs\vedic-svara.txt smart
```

### iPhone

Xcode once: see [apple/README.md](apple/README.md). Then Settings → Keyboards → KeySwap.  
**Long-press** letters, toggle **smart✓**, press **= ⟳** to cycle.

### Mac

Build menu-bar app ([apple/macos](apple/macos)); grant **Accessibility**; letter + `=`; smart digraphs on by default.

### Browser PWA

```bash
# from repo (HTTP required for SW; or open index.html for local pad)
cd tools/KeySwap/pwa
python -m http.server 8765
# open http://127.0.0.1:8765/
```

### Convert selection (any OS with Python)

```bash
python tools/KeySwap/convert_bridge.py --to deva "rāmaḥ"
python tools/KeySwap/convert_bridge.py --to iast "रामः"
python tools/KeySwap/convert_bridge.py --to slp1 "śiva"
```

---

## Config format

```text
# comment
n > ṇ > ṅ > ñ
a > ā
```

Unique bases; NFC; reload after edit (AHK auto / F6).

---

## Security

Hooks (AHK, Mac tap, vendor PE) can see keystrokes in other apps. The iOS
keyboard and PWA only handle text entered there. Do not ship `vendor/*.exe` in
PyPI/npm packages. Prefer layouts ([layouts/README.md](layouts/README.md)) on
shared lab machines.

---

## Versioning

| Version | Meaning |
|---------|---------|
| **2.0.0** | Open multi-platform toolkit (this tree) |
| 1.x PE | Andre / Yes Vedanta binary in `vendor/` only |

Bump [VERSION](VERSION) when behaviour or profile schema changes.

---

## Credits

- Cycle UX lineage: [Keyswap (Andre Vas / Yes Vedanta)](https://www.yesvedanta.com/keyswap/), [Lexilogos](https://www.lexilogos.com/keyboard/sanskrit_latin.htm)  
- 2.0 open engines, profiles, AHK, Apple, PWA, convert bridge: sanskrit-util contributors (MIT)  
- Convert: [`sanskrit_util`](https://github.com/sanskrit-lexicon/sanskrit-util)  

_Dr. Mārcis Gasūns_
