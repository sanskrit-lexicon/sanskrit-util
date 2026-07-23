# KeySwap **2.2** — IAST typing + Cologne Simple Search

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Version: [2.2.0](VERSION)_

**Add IAST diacritics by cycling a letter** (default trigger `=`), or type smart
digraphs (`aa`→ā, `sh`→ś). Works in Word, browser, chat — not only one app.

```text
n  =  =  =     →  ṇ → ṅ → ñ
r  =  =        →  ṛ → ṝ
s  =  =        →  ṣ → ś
kṛṣṇa · Rāmāyaṇam · saṃsāra · śiṣyāḥ
```

Also: HK/ITRANS/Velthuis paste → IAST, IAST↔Devanāgarī, Cologne Simple Search
prep. Not part of the PyPI/npm package API.

**Origin UX:** [Andre Vas / Yes Vedanta Keyswap](https://www.yesvedanta.com/keyswap/)
(Windows cycle + `config.txt`). This folder is the **open multi-platform 2.x**
toolkit. Feedback analysis: [UPSTREAM_KEYSWAP_ANALYSIS.md](UPSTREAM_KEYSWAP_ANALYSIS.md).

> **If `=` breaks Microsoft Word** (jumps to Draft view, splits the window, or
> turns `t` into ™): set the **system** keyboard to **English (US)** (Settings →
> Time & language → Typing — not Word’s language), **or change the trigger key**,
> **or use** [`windows/KeySwap.ahk`](windows/KeySwap.ahk) / PWA. This is the #1
> community failure mode on the upstream page.

---

## First 60 seconds (Windows)

1. Install [AutoHotkey v2](https://www.autohotkey.com/) (preferred) **or** use PWA.  
2. Double-click [`windows/KeySwap.ahk`](windows/KeySwap.ahk) — **no main window**; look for the **tray icon**.  
3. Open Notepad → type `n` → press `=` a few times → `ṇ` `ṅ` `ñ`.  
4. Optional: tray → change mode (cycle / smart / deadkey).

Legacy PE: [`vendor/keyswap.exe`](vendor/) — unsigned; SmartScreen “More info → Run anyway”. Prefer AHK.

---

## What’s in 2.2 (Cologne Simple Search)

| Feature | Detail |
|---------|--------|
| **`cologne_search.py`** | Multi-scheme → SLP1 → **dalnorm** (port of csl-apidev `Dalnorm::normalize`) |
| **Cologne URLs** | Builds [Simple Search](https://sanskrit-lexicon.uni-koeln.de/simple/) UI + getword_list API links |
| **`--open` / `--api`** | Browser jump or live headword list |
| **AHK Ctrl+Alt+C** | Clipboard → Cologne Simple Search |
| **PWA “Cologne”** | Opens Simple Search with scheme-aware `input` + `key` |
| **Mac menu** | Clipboard → Cologne Simple Search |

### 2.1 (still included)

scheme_bridge · convert `--from` · Keyman guard · allowlist · HUD · MSKLC docs · packaging checklists

### 2.0 (still included)

smart digraphs · long-press · PWA · profiles · AHK cycle/smart/deadkey

---

## What to run

| Platform | Recommended |
|----------|-------------|
| **Windows** | [`windows/KeySwap.ahk`](windows/KeySwap.ahk) |
| **iPhone** | [`apple/`](apple/) keyboard |
| **Mac** | [`apple/macos/`](apple/macos/) menu bar |
| **Browser** | [`pwa/`](pwa/) |
| **CLI convert** | `convert_bridge.py` / `scheme_bridge.py` |
| **Legacy PE** | [`vendor/`](vendor/) optional only |

---

## CLI

```bash
# Validate + unit tests
python tools/KeySwap/validate_configs.py
python tools/KeySwap/test_cycle_engine.py
python tools/KeySwap/test_smart_input.py
python tools/KeySwap/test_scheme_bridge.py

# Schemes → IAST
python tools/KeySwap/scheme_bridge.py --from hk "saMskRta"
python tools/KeySwap/scheme_bridge.py --from itrans "raama"
python tools/KeySwap/scheme_bridge.py --from velthuis "k.r.s.na"
python tools/KeySwap/scheme_bridge.py --from auto "saMskRta"

# To Devanāgarī / SLP1 (via sanskrit-util)
python tools/KeySwap/convert_bridge.py --from hk --to deva "rAma"
python tools/KeySwap/convert_bridge.py --from itrans --to iast "shiva"
python tools/KeySwap/convert_bridge.py --to slp1 "śiva"

# Cologne Simple Search (dalnorm keys + open/API)
python tools/KeySwap/cologne_search.py "rāma" --print-keys
python tools/KeySwap/cologne_search.py --from hk "ziva" --dict mw --open
python tools/KeySwap/cologne_search.py "śiva" --api --dict mw
python tools/KeySwap/test_cologne_search.py
```

---

## Windows AHK

| Key | Action |
|-----|--------|
| `=` (or your trigger) | Cycle last letter |
| F6 | Reload config + allowlist |
| F7 | Toggle teaching HUD |
| Ctrl+Alt+= | Clipboard → Devanāgarī |
| Ctrl+Alt+I / H | Clipboard auto-scheme → IAST |
| Ctrl+Alt+C | Clipboard → Cologne Simple Search |

Copy [`windows/allowlist.example.txt`](windows/allowlist.example.txt) → `allowlist.txt` to restrict apps.

**Non-US keyboards:** on Spanish layouts the physical key may be `+` not `=`; set another trigger (upstream users use `]`, `/`, `` ` ``, `|`). Layout often only affects the **trigger**, not the base letters (Hakon / Norway).

---

## Profiles

| Profile | Who |
|---------|-----|
| `iast-classic` (default) | Classical IAST; capitals included |
| `iso15919` | ē ō ḻ ṉ, vocalic r̥-style extras |
| `vedic-draft` / `vedic-svara` | Accents / svara experiments (Rudram, etc.) |
| `personal-legacy` | Upstream personal map (ç, æ, …) |

### Config recipes (from community + upstream help)

```text
# danda / double danda (Durgaprasad)
. > । > ॥

# oṃ / ॐ (Jai)
o > oṃ > ॐ

# svara: paste combining forms from Lexilogos, then e.g.
e > e̍ > e̱
```

After edit: **F6** (AHK) or quit tray app and relaunch (vendor PE). Chandrabindu and odd marks: type on [Lexilogos](https://www.lexilogos.com/keyboard/sanskrit_latin.htm) → paste into the chain.

---

## Troubleshooting (from 80 upstream comments)

| Symptom | Fix |
|---------|-----|
| Word Draft / Vertical Split / ™ when cycling | System keyboard **English (US)**; or change trigger; try Google Docs |
| Works day 1, fails day 2 in Office | Same layout fix; avoid competing keystroke tools |
| `an item with the same key has already been added` | PE: re-extract zip, SmartScreen → More info → Run anyway (#6342). AHK: check duplicate bases in config (`validate_configs.py`) |
| Keyman + KeySwap both on | Pause one of them |
| Capitals not cycling | Use `iast-classic` (has `A>Ā`…); uppercase and lowercase are **separate** chains |
| WordPerfect / stubborn apps | Last resort: run helper **and** app elevated — prefer AHK first |
| Font snaps to Cambria after cycle | PE quirk; try AHK; type into already-selected font |
| Mac / iPhone / Chromebook | Mac app · iOS keyboard · PWA (not the PE) |
| Need ISO r̥ / r̥̄ | `configs/iso15919.txt` or add to config |
| Need speed like Azhagi phonetic | Enable **smart** digraphs; or Keyman/Azhagi for pure phonetic Deva/IAST |

Full comment analysis: [UPSTREAM_KEYSWAP_ANALYSIS.md](UPSTREAM_KEYSWAP_ANALYSIS.md).

---

## Layout

```text
KeySwap/
  VERSION  (2.2.0)
  cologne_search.py     # Cologne Simple Search prep (dalnorm + URLs)
  scheme_bridge.py      # HK/ITRANS/Velthuis → IAST
  convert_bridge.py     # + --from schemes
  smart_input.py
  cycle_engine.py
  layouts/msklc/        # classroom / MSKLC
  packaging/            # App Store + PE policy
  windows/              # AHK + allowlist + Cologne hotkey
  pwa/                  # offline pad + Cologne button
  apple/                # iOS + Mac
  vendor/               # optional 1.x PE
```

---

## Security

Hooks can see keystrokes. Prefer [layouts/](layouts/) on shared labs. Do not ship
`vendor/*.exe` in PyPI/npm.

## Credits

Cycle UX: Yes Vedanta Keyswap + Lexilogos. Open 2.x toolkit: sanskrit-util (MIT).

_Dr. Mārcis Gasūns_
