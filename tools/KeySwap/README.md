# KeySwap — IAST diacritic cycler (Windows, iPhone, Mac)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Type Sanskrit **romanization (IAST / ISO-style)** by cycling Latin letters with a
**trigger** (default `=`):

```text
n  =  =  =   →  ṇ  →  ṅ  →  ñ
a  =         →  ā
s  =  =      →  ṣ  →  ś
```

Works as an **OS input helper**, not as part of the
[`sanskrit-util`](https://github.com/sanskrit-lexicon/sanskrit-util) transcoder
API. Use the library (`to_slp1`, `norm`, …) in code; use KeySwap to *type*.

---

## What to run (by platform)

| Platform | Recommended | Path |
|----------|-------------|------|
| **Windows** | Open AutoHotkey v2 script | [`windows/KeySwap.ahk`](windows/KeySwap.ahk) + [`windows/README.md`](windows/README.md) |
| **Windows** | Legacy PE (third-party) | [`vendor/keyswap.exe`](vendor/keyswap.exe) — see [PROVENANCE](PROVENANCE.md) |
| **iPhone / iPad** | Custom keyboard (Swift) | [`apple/`](apple/) — see [apple/README.md](apple/README.md) |
| **Mac** | Menu-bar `=` cycler (Swift) | [`apple/macos/`](apple/macos/) — Accessibility permission |
| **All (logic)** | Python reference engine | [`cycle_engine.py`](cycle_engine.py) |

---

## Use cases

1. **Everyday IAST** in mail, Word, browser, chat — keep QWERTY, spin diacritics on demand.  
2. **Dictionary / catalogue entry** — type IAST, then normalize with `to_slp1` / `norm` in tools.  
3. **Teaching** ṇ vs ṅ vs ñ, ṣ vs ś — cycle live in any editor.  
4. **ISO / Vedic drafts** — switch profile (`iso15919`, `vedic-draft`) without remapping the whole keyboard.  
5. **Cross-device scholars** — same config language on Windows AHK, iOS keyboard, and Mac tap.  
6. **Portable Windows lab machine** — AHK script or vendor PE; no MSKLC install required.

---

## Layout

```text
KeySwap/
  README.md                 # this file
  PROVENANCE.md             # SHA-256 pins for vendor PE
  THIRD_PARTY_NOTICE.md     # Andre / Yes Vedanta binary is not MIT
  config.txt                # default profile (= iast-classic)
  configs/
    iast-classic.txt        # classical IAST (recommended default)
    iso15919.txt            # ē ō ḻ ṉ …
    vedic-draft.txt         # length + acute / macron+acute
    personal-legacy.txt     # upstream personal map
  cycle_engine.py           # reference semantics + longest-suffix cycle
  validate_configs.py       # CI-friendly config gate
  test_cycle_engine.py      # unit tests
  windows/KeySwap.ahk       # open Windows reimplementation
  apple/                    # KeySwapCore + iOS keyboard + Mac app
  vendor/                   # third-party keyswap.exe (optional)
```

---

## Config format

```text
# comments allowed
n > ṇ > ṅ > ñ
a > ā
l > ḷ > ḹ
```

- One chain per line; `>`-separated; UTF-8 (BOM optional).  
- First token is the **base** you type; must be **unique** in the file.  
- Uppercase and lowercase are **separate** chains.  
- Forms are NFC-normalized by the engines.  
- After editing: quit/reload the platform app; run `validate_configs.py`.

### Validate

```bash
python tools/KeySwap/validate_configs.py
python tools/KeySwap/test_cycle_engine.py
```

---

## Quick starts

### Windows (AHK — preferred open path)

1. Install [AutoHotkey v2](https://www.autohotkey.com/).  
2. Double-click [`windows/KeySwap.ahk`](windows/KeySwap.ahk).  
3. Type `n`, press `=`, repeat.

```text
autohotkey64.exe tools\KeySwap\windows\KeySwap.ahk tools\KeySwap\configs\vedic-draft.txt
```

### Windows (legacy binary)

1. Run [`vendor/keyswap.exe`](vendor/keyswap.exe) (tray icon).  
2. Prefer copying a profile over `config.txt` next to the exe, or keep using
   the open AHK loader on `configs/*.txt`.  
3. Hashes and copyright: [PROVENANCE.md](PROVENANCE.md), [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md).

### iPhone

1. On a Mac, open Xcode and follow [apple/README.md](apple/README.md) (host app + keyboard extension + local KeySwapCore package).  
2. Install host app → **Settings → General → Keyboard → Keyboards → Add → KeySwap**.  
3. In any app, switch to KeySwap, type a letter, tap **= cycle**.

### Mac

1. Build/run the menu-bar app from [apple/macos/KeySwapMacApp.swift](apple/macos/KeySwapMacApp.swift) (see apple README).  
2. Grant **Accessibility**, relaunch.  
3. In any app: letter then `=`.

---

## Architecture

| Layer | Role |
|-------|------|
| Config profiles | Data only — scholarly maps |
| `cycle_engine.py` / `KeySwapCore` | Parse chains, longest-suffix / next-form |
| Platform shell | AHK hotkey · iOS keyboard · Mac CGEvent tap · vendor PE |

**Security:** system-wide hooks (Windows PE/AHK, Mac tap) can see keystrokes in
other apps. The iOS keyboard only handles text entered through that keyboard.
Do not ship `vendor/keyswap.exe` inside PyPI/npm artifacts.

---

## Improvements landed (priority map)

| Priority | Item | Status |
|----------|------|--------|
| P0 | SHA-256 pin + third-party notice | [PROVENANCE.md](PROVENANCE.md), [THIRD_PARTY_NOTICE.md](THIRD_PARTY_NOTICE.md) |
| P0 | Vendor PE isolated under `vendor/` | done |
| P1 | Named scholarly profiles + `ḹ` fix | `configs/*` |
| P1 | Validator + default/`iast-classic` sync check | `validate_configs.py` |
| P2 | Open Windows reimplementation | `windows/KeySwap.ahk` |
| P2 | Shared engine + tests | Python + Swift KeySwapCore |
| — | **iPhone custom keyboard** | `apple/ios-keyboard` + host |
| — | **Mac system-wide cycler** | `apple/macos` |
| P3 | Hot-reload / HUD / per-app allowlist | backlog |
| P4 | Root README pointer | see package README “Related tools” |

### Still open (backlog)

- Hot-reload config without process restart (all shells).  
- On-screen cycle HUD (teaching mode).  
- Per-app allowlist for hooks.  
- Notarized / TestFlight binaries (out of band).  
- Full Access optional sync of profile across iOS keyboards via App Group UI.

---

## Relationship to sanskrit-util

| Concern | Tool |
|---------|------|
| Type IAST on device | **KeySwap** (this tree) |
| IAST ⇄ SLP1 ⇄ Devanāgarī in code | `py/sanskrit_util`, `js/` |
| Golden vectors | `vectors/vectors.json` |

Never call KeySwap from library tests or CI packages. Config validation tests
here are optional tooling checks only.

---

## Upstream credit

Classic Windows idea and original PE: **Andre Vas / Yes Vedanta** —
[https://www.yesvedanta.com/keyswap/](https://www.yesvedanta.com/keyswap/).  
Open engines, profiles, AHK, and Apple ports: sanskrit-util contributors (MIT).

_Dr. Mārcis Gasūns_
