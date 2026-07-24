# KeySwap vs similar tools (web survey)

_Created: 23-07-2026 · Last updated: 24-07-2026_  
_Survey: 23-07-2026 · Refresh: 24-07-2026 · Model: Grok 4.5 · constraint: light / fast to load through **2.x**_

**Roadmap:** [ROADMAP_KEYSWAP_V2_V3.md](ROADMAP_KEYSWAP_V2_V3.md) — **v2 remainder** (10 light adds + leverage pack) vs **v3** (former explicit skips).

## Peer map

### Type IAST / roman diacritics

| Tool | Model | Platforms | Weight | vs KeySwap 2.6+ |
|------|--------|-----------|--------|-----------------|
| Keyswap (Yes Vedanta) | Letter + `=` cycle | Windows PE | Tiny PE | Origin UX; PE optional under `vendor/` |
| Lexilogos Sanskrit Latin | Same cycle web pad | Browser | Zero install | PWA covers pad; we add OS-wide |
| ABC Extended / Dunning (UBC) | Option/dead-key layout | Mac / Win MSKLC | Zero runtime | Classroom path (docs); no hook |
| EasyUnicode (Unebe) | Option layout | Mac | Layout only | Ecosystem link-out |
| Heidelberg Input Solution | IAST layout (Keyman) | Multi via Keyman | Keyman stack | Ecosystem link; do not dual-hook |
| SIL Indic Roman | Roman diacritics (Keyman) | Multi via Keyman | Keyman stack | Same |
| SanskritTypist (2025) | Long-press + `aa`→ā + Deva | iOS | App Store keyboard | Smart digraphs + iOS long-press; Deva script mode |
| Sanskrit Writer | Gesture / multi-output | Mac | App + dict | Writer-scheme + script mode + Cologne gloss (not forms DB) |
| ArshaDrishti | Dual Deva + IAST layout | Mac bundle | Layout install | Classroom / ecosystem link |

### Convert / paste (not OS typing)

| Tool | Strength | KeySwap stance |
|------|----------|----------------|
| Sanscript (learnsanskrit.org) | Scheme A→B; `##` escape | Link out + `scheme_bridge` / `convert_bridge` |
| Aksharamukha | 100+ scripts, OCR, plugin | Link out only through **2.x**; embed = **v3** |
| Yes Vedanta transliterate | Multi-scheme web | Overlap with scheme_bridge |

### Dictionary

| Tool | Notes |
|------|--------|
| Cologne Simple Search | dalnorm + open/API (2.2); headword check (2.3); offline list (2.4); DCS opt-in (2.5) |
| Cologne webtc / MW | Gloss deep-link (2.6 Ctrl+Alt+G) |
| Sanskrit Heritage | Grammar/segmenter — **v3** link-out / service, not 2.x embed |

## Capability matrix (as of 2.7 leverage pack)

| Capability | KeySwap | Typical peer |
|------------|---------|--------------|
| `=` cycle | Yes | Keyswap, Lexilogos |
| Smart digraphs | Yes | SanskritTypist |
| Writer-scheme digraphs | Yes (2.6) | Sanskrit Writer |
| Long-press | iOS/PWA | SanskritTypist |
| Dead-key / layout path | AHK deadkey + MSKLC docs | ABC Extended, EasyUnicode |
| HK/ITRANS/Velthuis → IAST | Yes | Sanscript |
| IAST ↔ Deva | convert + script mode | Sanscript, SW, Typist |
| Cologne search / gloss | Yes | Browser only |
| Offline headword set | Yes (2.4) | SW local dict (different) |
| Optional DCS freq | Yes (2.5) | — |
| SLP1 + normkey copy | Yes (2.7) | — |
| Ecosystem link tray | Yes (2.7) | — |
| Literal `=` escape | Shift+= (2.7) | Layouts use other keys |
| `pali-lite` profile | Yes (2.7) | — |
| Full morphology forms DB | **v3** | Sanskrit Writer |
| Full script matrix / OCR | **v3** | Aksharamukha |
| Keyman-class IME | **v3** / never dual-default | Keyman |

## Version 2 remainder (open)

See [ROADMAP_KEYSWAP_V2_V3.md](ROADMAP_KEYSWAP_V2_V3.md) § Version 2:

- Highest-leverage pack L1–L5 → **2.7**
- Still open after leverage: non-US trigger presets (#5), classroom pack (#6), iOS Writer parity (#7), opt-in live Deva type-out (#8)

## Version 3 (former explicit skips)

Aksharamukha embed · local hwnorm1c/MW SQLite · Keyman IME · OCR · TTS · Heritage segmenter · always-on autocomplete · SW-class morphology DB — all **planned under v3**, not 2.x default path.

## Skip in 2.x (still true for default install)

- Embed Aksharamukha or full script matrix  
- Local MW / hwnorm1c SQLite as always-on DB  
- Full Keyman-class IME  
- OCR / TTS / Heritage segmenter  
- Always-on network autocomplete  
- Full morphology dictionary  

## Sources (survey day)

- [yesvedanta.com/keyswap](https://www.yesvedanta.com/keyswap/)  
- [lexilogos.com/keyboard/sanskrit_latin.htm](https://www.lexilogos.com/keyboard/sanskrit_latin.htm)  
- [UBC Sanskrit tools](https://blogs.ubc.ca/ubcsanskrit/tools/)  
- [Yogic Studies / EasyUnicode](https://www.yogicstudies.com/blog/how-to-type-transliterated-sanskrit-with-diacritics-in-mac-osx)  
- [learnsanskrit.org Sanscript](https://www.learnsanskrit.org/tools/sanscript/)  
- [aksharamukha.com](https://www.aksharamukha.com/)  
- [Keyman Heidelberg Input Solution](https://keyman.com/keyboards/heidelberginputsolution)  
- [SanskritTypist](https://www.gingersunrise.com/p/sanskrit-type-devanagari-iast-iphone-ipad)  
- [Sanskrit Writer](https://sri.auroville.org/projects/sanskrit-writer/)  
- r/sanskrit typing threads (IAST setup, diacritics, Windows/Mac)

_Dr. Mārcis Gasūns_
