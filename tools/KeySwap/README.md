# KeySwap **2.6** — scholarly IAST anywhere + open Cologne dictionary layer

_Created: 23-07-2026 · Last updated: 24-07-2026_  
_Version: [2.6.0](VERSION)_

**Type IAST (and Devanagari) in any app** — cycle, smart digraphs, or
[Sanskrit Writer](https://sri.auroville.org/projects/sanskrit-writer/)-style
mark-then-letter (`-a` long a, `~n`, `'s`). Then check the word against
**Cologne** (headword check, optional DCS frequency, full **gloss** page).

```text
n  =  =  =     cycle diacritics
-a  ~n  's  h. Writer-scheme digraphs
Ctrl+Alt+D / V script mode IAST / Devanagari
Ctrl+Alt+S / G headword check / open MW gloss
```

Open multi-platform toolkit (not a closed desktop-only writer app).  
**One install:** [packaging/INSTALL.md](packaging/INSTALL.md).

**Origin UX:** [Yes Vedanta Keyswap](https://www.yesvedanta.com/keyswap/)  
(`=` cycle). Analysis: [UPSTREAM_KEYSWAP_ANALYSIS.md](UPSTREAM_KEYSWAP_ANALYSIS.md).

### KeySwap vs Sanskrit Writer

| | **KeySwap 2.6** | **Sanskrit Writer** (Auroville SRI) |
|--|-----------------|-------------------------------------|
| Job | Scholar **IAST anywhere** + **Cologne** | Compose Sanskrit with **morphology dict** |
| Input | `=` cycle · smart · **Writer-scheme** · deadkey | Gesture digraphs only |
| Output | IAST + Devanagari (script mode hotkey) | IAST · Devanagari · Brahmi |
| Dictionary | Cologne Simple Search + webtc **gloss** · optional DCS · local MW | Built-in conversational / form dictionary |
| Platforms | Windows AHK · Mac · iOS · PWA | Desktop app focus |
| Open source | Yes (this repo) | Product app |
| Weight | Light (hooks + data files) | Heavier app + forms DB |

> **Sanskrit Writer** helps you *compose* Sanskrit with forms.  
> **KeySwap** helps you *type scholarly IAST in any app*, with **Cologne** as the open dictionary layer.

> **If `=` breaks Microsoft Word**: system keyboard **English (US)**, change trigger, or use AHK/PWA. #1 upstream failure mode.

---

## First 60 seconds (Windows)

1. **One install:**  
   `powershell -ExecutionPolicy Bypass -File tools\KeySwap\packaging\install-windows.ps1`  
   (or double-click [windows/KeySwap.ahk](windows/KeySwap.ahk) after [AHK v2](https://www.autohotkey.com/)).  
2. Tray icon — type in Notepad: `n` then `=` · or Writer mode: `-` then `a`.  
3. Tray → **Profile: Writer-scheme** or **Mode: smart**.  
4. Ctrl+Alt+D toggles script mode; Ctrl+Alt+V converts clipboard.

Full install notes: [packaging/INSTALL.md](packaging/INSTALL.md).  
Legacy PE: [vendor/](vendor/) — prefer AHK.

---

## What's in 2.6 (vs Sanskrit Writer roadmap)

| # | Deliverable | Detail |
|---|-------------|--------|
| 1 | **Writer-scheme** | `configs/writer-scheme.txt` + smart digraphs |
| 2 | **Script mode** | Ctrl+Alt+D toggle · Ctrl+Alt+V convert clipboard |
| 3 | **Gloss deep-link** | Ctrl+Alt+G / `--open-gloss` → Cologne webtc |
| 4 | **One install** | `packaging/install-windows.ps1` · `install-macos.sh` · INSTALL.md |
| 5 | **Landing blurb** | This README comparison table |

### 2.5 (optional DCS-2026 frequencies)

| Feature | Detail |
|---------|--------|
| **`--dcs-freq` / `KEYSWAP_DCS_FREQ=1`** | Opt-in: annotate HUD with DCS lemma token counts (`dcs=N`) |
| **`data/dcs_freq.txt`** | Local copy of csl-apidev `simple-search/wf1` (DCS-2026 merge over wf0) |
| **`--freqsrc wf1\|wf0`** | Ask Cologne API which ranking table to use (after server Fix I) |
| **Default** | **Off** — no DCS unless you enable the flag/env |

```bash
python tools/KeySwap/typing_check.py --local-only --dcs-freq --hud "rāma"
# → ✓ rāma  ·  local (mw)  ·  local_headwords.txt  ·  dcs=6

set KEYSWAP_DCS_FREQ=1
python tools/KeySwap/typing_check.py --hud "kṛṣṇa"
```

### 2.4 (offline local wordlist)

| Feature | Detail |
|---------|--------|
| **`data/local_headwords.txt`** | Seed SLP1 list (~1k keys) for offline ✓/✗ |
| **API → local fallback** | If Cologne times out / 429 / no network, check the local file |
| **`--local-only`** | Force offline (no network) |
| **`--wordlist PATH` / `KEYSWAP_WORDLIST`** | Point at a larger list (e.g. full MW key1) |
| **`build_local_wordlist.py`** | Build full list from sibling SanskritSpellCheck `HeadwordLists/` |

Not a full SanskritSpellCheck detector stack — **existence check only** (word present / not).

### 2.3 (typing-tool headword check)

| Feature | Detail |
|---------|--------|
| **`typing_check.py`** | Last token → Cologne API → `✓` / `✗` HUD line |
| **AHK Ctrl+Alt+S** | Clipboard headword check (API first; local fallback since 2.4) |
| **Mac menu** | Clipboard headword check |

### 2.2 (Cologne Simple Search)

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

# Typing-tool headword check (live API, one-line HUD)
python tools/KeySwap/typing_check.py "kṛṣṇa" --hud
python tools/KeySwap/typing_check.py --hud --from hk "rAma"

# Offline / no Internet (local SLP1 wordlist)
python tools/KeySwap/typing_check.py --local-only --hud "rāma"
python tools/KeySwap/typing_check.py --local-only --hud --from hk "rAma"

# Expand seed → full MW (~194k keys) if SanskritSpellCheck is a sibling clone
python tools/KeySwap/build_local_wordlist.py --from-spellcheck
# or: python tools/KeySwap/build_local_wordlist.py --from-file path/to/MW-unique-key1-….txt

python tools/KeySwap/test_typing_check.py
python tools/KeySwap/test_local_wordlist.py
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
| Ctrl+Alt+S | Clipboard **headword check** (Cologne API → local wordlist fallback) |

Copy [`windows/allowlist.example.txt`](windows/allowlist.example.txt) → `allowlist.txt` to restrict apps.

**Non-US keyboards:** on Spanish layouts the physical key may be `+` not `=`; set another trigger (upstream users use `]`, `/`, `` ` ``, `|`). Layout often only affects the **trigger**, not the base letters (Hakon / Norway).

---

## Profiles

| Profile | Who |
|---------|-----|
| `iast-classic` (default) | Classical IAST; capitals included |
| `writer-scheme` | Same cycles + **Writer-style** digraphs |
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
| Headword check `? rate-limited` / API 429 | Cologne is throttling; local seed still ✓/✗ common words; use **Ctrl+Alt+C** in browser; expand list with `build_local_wordlist.py --from-spellcheck` |
| Headword check offline / no Internet | Works via `data/local_headwords.txt` (seed ~1k). Full MW: `build_local_wordlist.py --from-spellcheck` or set `KEYSWAP_WORDLIST` |

Full comment analysis: [UPSTREAM_KEYSWAP_ANALYSIS.md](UPSTREAM_KEYSWAP_ANALYSIS.md).

---

## Layout

```text
KeySwap/
  VERSION  (2.6.0)
  typing_check.py       # headword check: Cologne API + local fallback + optional DCS
  local_wordlist.py     # load/lookup SLP1 wordlist
  dcs_freq.py           # optional DCS-2026 frequency table
  build_local_wordlist.py
  data/local_headwords.txt  # offline list (seed or full MW)
  data/dcs_freq.txt         # DCS-2026 ranking counts (opt-in)
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
