# KeySwap — web survey: how else to improve

_Created: 23-07-2026 · Last updated: 05-09-2026_  
_Survey date: 23-07-2026 · Model: Grok 4.5 (`grok-4-1-thinking`) · feeds **KeySwap 2.x**_

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

## Ranked backlog (survey → 2.0 → 2.1)

| # | Item | Priority | Status |
|---|------|----------|--------|
| 1 | iOS **long-press** alternates | high | **shipped** 2.0 |
| 2 | **Smart vowels** digraphs | high | **shipped** 2.0 |
| 3 | **Convert selection** IAST↔Devanāgarī | high | **shipped** 2.0 (CLI + AHK + Mac 2.1) |
| 4 | **No-hook classroom path** | high | **shipped** 2.0 + MSKLC pack 2.1 |
| 5 | Layout/Keyman **guards** + allowlist | med-high | **shipped** 2.1 (AHK) |
| 6 | **Hot-reload** config | med | **shipped** 2.0 AHK |
| 7 | Offline **PWA** Lexilogos-style | med | **shipped** 2.0 + scheme UI 2.1 |
| 8 | **vedic-svara** profile | med | **shipped** 2.0 |
| 9 | **HK/ITRANS/Velthuis → IAST** bridge | med | **shipped** 2.1 (`scheme_bridge.py`) |
| 10 | Sync/drop stale PE policy | low | **shipped** 2.1 (`packaging/VENDOR_PE.md`) |
| 11 | App Store / notarized binaries | low | **checklist** 2.1 (`packaging/APP_STORE.md`) — needs human certs |
| 12 | Teaching **HUD** | med | **shipped** 2.1 (AHK ToolTip + PWA `#hud`) |
| 13 | Per-app **allowlist** | med | **shipped** 2.1 (`windows/allowlist.txt`) |

## Design decisions

1. **Version identity:** open multi-platform toolkit; vendor PE optional under `vendor/`.  
2. **Shared semantics** in Python + Swift KeySwapCore.  
3. **sanskrit-util** for Devanāgarī↔IAST↔SLP1; **scheme_bridge** for ASCII schemes → IAST only.  
4. **Profiles remain data**; modes are shells.  
5. **Classroom default** = `iast-classic` + system layouts / deadkey.

See [README.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/README.md), [VERSION](VERSION) (**2.1.0**).

_Dr. Mārcis Gasūns_
