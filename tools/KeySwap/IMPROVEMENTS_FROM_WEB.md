# KeySwap — web survey: how else to improve

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Survey date: 23-07-2026 · Model: Grok 4.5 (`grok-4-1-thinking`) · feeds **KeySwap 2.0**_

Sources: upstream [Keyswap (Yes Vedanta)](https://www.yesvedanta.com/keyswap/),
[Lexilogos Sanskrit Latin](https://www.lexilogos.com/keyboard/sanskrit_latin.htm),
[UBC Sanskrit tools](https://blogs.ubc.ca/ubcsanskrit/tools/),
[Yogic Studies / EasyUnicode](https://www.yogicstudies.com/blog/how-to-type-transliterated-sanskrit-with-diacritics-in-mac-osx),
[SanskritTypist (2025)](https://www.gingersunrise.com/p/sanskrit-type-devanagari-iast-iphone-ipad),
[Sanskrit Writer](https://sri.auroville.org/projects/sanskrit-writer/),
[Dunning ABC Extended for Windows](https://github.com/adunning/Mac-Keyboard-Layouts-for-Windows),
[Keyman Vedic ITRANS](https://keyman.com/keyboards/itrans_devanagari_sanskrit_vedic),
Harvard-Kyoto / convert workflows (learnsanskrit.org, Aksharamukha, Cologne).

---

## Competing input models

| Model | Examples | Strength | Gap vs 1.x cycle-only |
|--------|-----------|----------|------------------------|
| Cycle after letter | Keyswap, Lexilogos (`a=`, `n===`) | Keeps QWERTY; low training | Already our core |
| Dead-key / Option layout | Mac ABC Extended; Dunning Windows; EasyUnicode | No hook; university-endorsed | Must learn chords |
| Phonetic / double letter | SanskritTypist `aa`→ā/आ; Keyman ITRANS | Fast bulk entry | Different muscle memory |
| Long-press soft keys | SanskritTypist 2025 relaunch | iOS-native, zero extra key | Missing in 1.x iOS shell |
| Dual script modes | Sanskrit Writer, SanskritTypist | IAST and Devanāgarī in one app | 1.x IAST-only |
| ASCII scheme + convert | HK / Velthuis / ITRANS → IAST | Email/code friendly | Extra step; we own SLP1/IAST/Deva in-repo |

## Upstream Keyswap pain (product requirements)

From the vendor site troubleshooting:

1. Conflicts with **Keyman** in the background.  
2. Often needs **Run as administrator** for stubborn apps.  
3. **Non-US English** layouts break cycling (e.g. English–Australia).  
4. Duplicate `config.txt` bases → *“item with the same key has already been added”*.  
5. Config changes need **full process restart**.  
6. Mac users were pointed only to **online** Lexilogos.

## Ranked backlog (survey → 2.0)

| # | Item | Priority | 2.0 status |
|---|------|----------|------------|
| 1 | iOS **long-press** alternates | high | **shipped** |
| 2 | **Smart vowels** `aa`/`ii`/`uu`/`rr`/`ll`/`mm`/`hh` → diacritics | high | **shipped** |
| 3 | **Convert selection** IAST↔Devanāgarī via sanskrit-util | high | **shipped** (CLI + AHK/Mac hooks) |
| 4 | **No-hook classroom path** (layout cheatsheet + dead-key mode) | high | **shipped** (docs + AHK dead-key) |
| 5 | Layout/Keyman **guards** + clearer errors | med-high | **shipped** (AHK) |
| 6 | **Hot-reload** config | med | **shipped** (AHK file watch; validate CLI) |
| 7 | Offline **PWA** Lexilogos-style | med | **shipped** |
| 8 | Real **vedic-svara** profile | med | **shipped** (profile + docs; sample-tested lightly) |
| 9 | HK/ITRANS paste bridge | med | **partial** (HK-ish ASCII fold via double-letter + convert; full ITRANS deferred) |
| 10 | Sync/drop stale PE vs 2021 upstream | low | **docs** (prefer open 2.0 shells) |
| 11 | App Store / notarized binaries | low | backlog |

## Design decisions for 2.0

1. **Version identity:** `KeySwap 2.0` = open multi-platform toolkit; vendor PE stays 1.x optional under `vendor/`.  
2. **Shared semantics** live in Python (`cycle_engine.py`, `smart_input.py`, `convert_bridge.py`) and Swift `KeySwapCore`.  
3. **sanskrit-util** is the only converter for Devanāgarī↔IAST (no second transcoder).  
4. **Profiles remain data**; modes (cycle / smart / dead-key / long-press) are shells.  
5. **Classroom default** = `iast-classic` + no personal-legacy extras.

Implementation details and operator docs: [README.md](README.md), [VERSION](VERSION), [pwa/](pwa/), [layouts/](layouts/).

_Dr. Mārcis Gasūns_
