# KeySwap vs similar tools (web survey)

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Survey: 23-07-2026 · Model: Grok 4.5 · constraint: keep KeySwap light / fast to load_

## Peer map

### Type IAST / roman diacritics

| Tool | Model | Platforms | Weight |
|------|--------|-----------|--------|
| Keyswap (Yes Vedanta) | Letter + `=` cycle | Windows PE | Tiny PE |
| Lexilogos Sanskrit Latin | Same cycle web pad | Browser | Zero install |
| ABC Extended / Dunning (UBC) | Option/dead-key layout | Mac / Win MSKLC | Zero runtime |
| EasyUnicode (Unebe) | Option layout | Mac | Layout only |
| Heidelberg Input Solution | IAST layout (Keyman) | Multi via Keyman | Keyman stack |
| SIL Indic Roman | Roman diacritics (Keyman) | Multi via Keyman | Keyman stack |
| SanskritTypist (2025) | Long-press + `aa`→ā + Deva | iOS | App Store keyboard |
| Sanskrit Writer | Gesture / multi-output | Mac | App + dict hotkey — KeySwap 2.6 answers with Writer-scheme + script mode + Cologne gloss (see README) |
| ArshaDrishti | Dual Deva + IAST layout | Mac bundle | Layout install |

### Convert / paste (not OS typing)

| Tool | Strength | KeySwap stance |
|------|----------|----------------|
| Sanscript (learnsanskrit.org) | Scheme A→B; `##` escape | Link out; we already convert via sanskrit-util |
| Aksharamukha | 100+ scripts, OCR, plugin | Link out only — too heavy to embed |
| Yes Vedanta transliterate | Multi-scheme web | Overlap with scheme_bridge |

### Dictionary

| Tool | Notes |
|------|--------|
| Cologne Simple Search | Multi-input + fuzzy; KeySwap 2.2 preps dalnorm + open/API |
| Cologne webtc / MW | Citation deep links (optional add) |
| Sanskrit Heritage | Grammar/segmenter — do not embed |

## KeySwap 2.2 position

Lightweight **scholar typing companion** + scheme bridge + Cologne jump — not Keyman, not Aksharamukha, not a local dict DB.

| Capability | KeySwap 2.2 | Typical peer |
|------------|-------------|--------------|
| `=` cycle | Yes | Keyswap, Lexilogos |
| Smart digraphs | Yes | SanskritTypist |
| Long-press | iOS/PWA | SanskritTypist |
| Dead-key / layout path | AHK deadkey + docs | ABC Extended, EasyUnicode |
| HK/ITRANS/Velthuis → IAST | Yes | Sanscript |
| IAST ↔ Deva | sanskrit-util | Sanscript |
| Cologne search prep | dalnorm + open/API | Browser only |
| System-wide Win/Mac | AHK + event tap | Keyman, layouts |

## Lean next adds (Tier A — no heavy deps)

1. Copy SLP1 + normkey of clipboard (no browser) — companion to Cologne open.  
2. Tray “Ecosystem” submenu — static links (Sanscript, Aksharamukha, Dunning, EasyUnicode).  
3. Optional MW webtc deep-link template (URL string only).  
4. `pali-lite` config profile (data only).  
5. Document literal-`=` escape clearly.

## Skip (weight / load)

- Embed Aksharamukha or full script matrix  
- Local MW / hwnorm1c SQLite  
- Full Keyman-class IME  
- OCR / TTS / Heritage segmenter  
- Always-on network autocomplete  

## Sources (survey day)

- [yesvedanta.com/keyswap](https://www.yesvedanta.com/keyswap/)  
- [lexilogos.com/keyboard/sanskrit_latin.htm](https://www.lexilogos.com/keyboard/sanskrit_latin.htm)  
- [UBC Sanskrit tools](https://blogs.ubc.ca/ubcsanskrit/tools/)  
- [Yogic Studies / EasyUnicode](https://www.yogicstudies.com/blog/how-to-type-transliterated-sanskrit-with-diacritics-in-mac-osx)  
- [learnsanskrit.org Sanscript](https://www.learnsanskrit.org/tools/sanscript/)  
- [aksharamukha.com](https://www.aksharamukha.com/)  
- [Keyman Heidelberg Input Solution](https://keyman.com/keyboards/heidelberginputsolution)  
- [SanskritTypist](https://www.gingersunrise.com/p/sanskrit-type-devanagari-iast-iphone-ipad)  
- r/sanskrit typing threads (IAST setup, diacritics, Windows/Mac)

_Dr. Mārcis Gasūns_
