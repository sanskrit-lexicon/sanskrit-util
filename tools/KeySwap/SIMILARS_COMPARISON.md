# KeySwap vs similar tools (web survey)

_Created: 23-07-2026 · Last updated: 05-09-2026_  
_Survey: 23-07-2026 · Refresh: 24-07-2026 (post V3-2/V3-7 + product tiers) · 25-07-2026 (post 2.9 residual, H1638; post V3 tray/link-out residual, H1639) · Model: Grok 4.5 (`grok-4.5`); H1638 update: Fable 5 (`claude-fable-5`); H1639 update: Sonnet 5 (`claude-sonnet-5`)_

**Roadmap:** [ROADMAP_KEYSWAP_V2_V3.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md) — **v2 free/portable** · **v3 heavy open** · **v4 paid full** (Mac/iOS advanced).  
**Architecture (v3 plugins):** [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Verdict (one line)

KeySwap does **not** contain every feature of every free/paid peer. It is strongest as a
**free, mostly portable “type scholarly IAST anywhere + Cologne” companion** (Windows
flagship; Mac/iOS thinner). Sanskrit Writer still wins on **forms/morphology**; Aksharamukha
on **script matrix/OCR**; Keyman on **system IME**. Closing those gaps is staged: v2 → v3 → v4.

---

## Product tiers (KeySwap)

| Tier | Price | Weight | Goal | Default install |
|------|-------|--------|------|-----------------|
| **v2.x** | **Free** | **Mostly portable** (AHK/scripts + small data; optional PE) | Match / beat light typing peers without becoming SW/Keyman | Light shell only |
| **v3.x** | **Free** | **Heavier** opt-in plugins / sidecars | Open-source path to offline index, network assist, link-outs; **not** “maximum product” | Still light; plugins off |
| **v4.x** | **Paid** | Full product (signed Mac/iOS, forms DB, advanced Apple UX) | **Most** peer features, including advanced Mac + iOS | Paid SKUs unlock heavy packs |

**Hard rules**

- v2 never ships multi-MB always-on DB, OCR/TTS engines, or Keyman dual-hook by default.  
- v3 may ship heavy **opt-in** packs; free users can use them; product still not “maximum.”  
- v4 is where **paid** monetization, notarized builds, App Store / advanced Mac-iOS, and
  SW-class compose features live — without forcing free users into that weight.

---

## Peer map

### Type IAST / roman diacritics

| Tool | Model | Platforms | Price / weight | vs KeySwap today (2.8 + V3 plugins) |
|------|--------|-----------|----------------|--------------------------------------|
| Keyswap (Yes Vedanta) | Letter + `=` cycle | Windows PE | Free, tiny | Origin UX; PE optional under `vendor/` |
| Lexilogos Sanskrit Latin | Same cycle web pad | Browser | Free, zero install | PWA covers pad; we add OS-wide |
| ABC Extended / Dunning (UBC) | Option/dead-key layout | Mac / Win MSKLC | Free, layout only | Classroom path; no hook |
| EasyUnicode (Unebe) | Option layout | Mac | Free, layout only | Ecosystem link-out |
| Heidelberg Input Solution | IAST via Keyman | Multi | Free+Keyman stack | Link-out; never dual-hook default |
| SIL Indic Roman | Roman diacritics (Keyman) | Multi | Free+Keyman | Same |
| SanskritTypist (2025) | Long-press + `aa`→ā + Deva | iOS | App Store keyboard | We have smart digraphs + iOS long-press scaffold; Writer-digraph parity **shipped v2.9**; App-Store-quality polish → **v4 Apple** |
| Sanskrit Writer (SRI) | Gesture / multi-output + **forms dict** | Desktop (Mac-focused) | Product app | Writer-scheme + script mode + Cologne gloss; **no forms DB** until **v4** (v3 parks sibling design) |
| ArshaDrishti | Dual Deva + IAST layout | Mac | Layout bundle | Classroom / ecosystem link |

### Convert / paste (not OS typing)

| Tool | Strength | KeySwap stance |
|------|----------|----------------|
| Sanscript (learnsanskrit.org) | Scheme A→B; `##` escape | Link-out + `scheme_bridge` / `convert_bridge` (v2) |
| Aksharamukha | 100+ scripts, OCR, plugin | Link-out through v2; optional embed/sidecar **v3**; full product polish **v4** |
| Yes Vedanta transliterate | Multi-scheme web | Overlap with scheme_bridge |

### Dictionary / grammar

| Tool | Notes | KeySwap tier |
|------|--------|--------------|
| Cologne Simple Search / webtc | dalnorm + API + gloss | **v2** core (online + seed offline) |
| Offline fuzzy / full MW list | Seed + opt-in full wordlist | **v2** seed · **v3** `offline_fuzzy` plugin |
| Network autocomplete | Offline-first then Cologne | **v3** `network_autocomplete` (opt-in) |
| SW forms / morphology DB | Product-sized | **v4** paid (v3 design-only / sibling) |
| Sanskrit Heritage segmenter | Grammar engine | **v3** link-out (tray "Ecosystem" ▸ Sanskrit Heritage segmenter, shipped H1639) · **v4** integrated if paid product needs it |

---

## Capability matrix (as of 2.8 + V3-2/V3-7)

Legend: **Y** = shipped default or easy path · **P** = opt-in plugin · **L** = link-out · **—** = missing · tier column = first tier that **owns** the gap.

| Capability | KeySwap now | Win | Mac | iOS | Typical peer | Gap owner |
|------------|-------------|-----|-----|-----|--------------|-----------|
| `=` cycle | **Y** | Y | Y | Y | Keyswap, Lexilogos | — |
| Smart digraphs | **Y** | Y | Y | Y | SanskritTypist | — |
| Writer-scheme digraphs | **Y** | Y | partial | **Y** 2.9 | Sanskrit Writer | — |
| Long-press menus | **Y** | — | — | Y/PWA | SanskritTypist | polish **v4** |
| Dead-key / layout path | docs + AHK | Y | docs | — | ABC Extended, EasyUnicode | classroom **v2** |
| Non-US cycle trigger | **Y** 2.8 | Y | env | PWA | PE comments | — |
| HK/ITRANS/Velthuis → IAST | **Y** | Y | Y* | Y* | Sanscript | — |
| IAST ↔ Deva (clipboard / mode) | **Y** | Y | Y* | partial | SW, Typist | — |
| Live Deva type-out (not only clipboard) | **P** 2.9 (Win) | **P** 2.9 | — | — | SW / Typist | Mac/iOS parked — see ROADMAP 2.9 notes |
| Cologne search / gloss | **Y** | Y | Y* | Y* | Browser Cologne | Mac UX polish **v4** |
| Offline headword seed | **Y** 2.4 | Y | Y* | — | SW local (different) | — |
| Offline fuzzy / full MW index | **P** V3-2 | Y | Y* | — | SW local dict | full pack **v3** |
| Network autocomplete (not always-on) | **P** V3-7 | Y | Y* | — | web tools | tray UX **v3/v4** |
| Optional DCS frequency | **Y** 2.5 | Y | Y* | — | — | — |
| SLP1 + normkey copy | **Y** 2.7 | Y | Y* | — | — | — |
| Ecosystem link tray | **Y** 2.7 | Y | thin | — | — | Mac tray **v4** |
| Literal trigger escape | **Y** 2.7/2.8 | Y | env | PWA | layouts | — |
| `pali-lite` profile | **Y** 2.7 | Y | Y | Y | — | — |
| Portable free install | **Y** | AHK+scripts | scripts | — | PE Keyswap | keep **v2** |
| Full morphology / forms DB | — | — | — | — | Sanskrit Writer | **v4 paid** |
| Full script matrix | **L** shipped | L | L | L | Aksharamukha | tray link done H1639; embed **v3** later · product **v4** |
| OCR | **L** shipped | L | L | L | Aksharamukha (same converter page — has an OCR upload feature, not a separate tool) | tray link done H1639 (shares the Aksharamukha entry) · **v4** if paid |
| TTS | **L** shipped | L | L | L | [Sanskrit Text-to-Speech (SRI Auroville)](https://sri.auroville.org/projects/sanskrit-text-to-speech/) | tray link done H1639 (was a vague "SRI TTS etc." placeholder; now a real URL) |
| Heritage segmenter | **L** shipped | L | L | L | [Sanskrit Heritage](https://sanskrit.inria.fr/) | tray link done H1639 · **v4** if integrated |
| Keyman-class system IME | **L** | dual-docs | dual-docs | — | Keyman (already linked, tray "Ecosystem" ▸ Keyman Heidelberg Input Solution) | never dual-default; bridge **v3** |
| Signed / notarized Mac app | — | — | dev-only | — | SW, Typist | **v4 paid** |
| App Store iOS keyboard polish | scaffold | — | — | scaffold | SanskritTypist | **v4 paid** |

\* Mac/iOS: core cycle/smart exist; Cologne/Python helpers and tray depth lag Windows.

---

## Free portable peers — does v2 “win”?

| Peer class | KeySwap v2 goal | Status |
|------------|-----------------|--------|
| Yes Vedanta PE / Lexilogos cycle | Match cycle UX + OS-wide + more schemes | **Met** (and exceeded on schemes/Cologne) |
| OS layouts (ABC / EasyUnicode / MSKLC) | Document when layout > hook | **Met** (classroom doc); not replace layouts |
| Keyman keyboards | Coexist; do not dual-hook | **Met** (docs + ecosystem link) |
| Browser converters | Keep portable convert path | **Met** (`scheme_bridge` / PWA) |

**v2 residual — closed 25-07-2026 (H1638):**

1. **#7** iOS long-press ↔ Writer digraphs parity — **shipped**  
2. **#8** Opt-in live Deva type-out (off by default) — **shipped on Windows** (selection-in-place, `Ctrl+Alt+Shift+D`); Mac/iOS parked with reason  
3. Portable packaging hygiene (one zip / one script; PE vs AHK still clear) — **audited, already clean**  
4. Keep default Startup free of plugins — **held** (nothing in this pass touches default Startup)  

---

## Heavier free peers — what v3 may take

| Peer capability | v3 free stance | Not in v3 |
|-----------------|----------------|-----------|
| Offline MW / fuzzy index | **P** `offline_fuzzy` (shipped; full wordlist opt-in) | Always-on multi-MB in default Startup |
| Network autocomplete | **P** offline-first (shipped) | Always-on default |
| Aksharamukha / OCR / TTS / Heritage | Link-out or optional sidecar | Full in-app product chrome |
| Keyman | Dual-install docs / thin bridge | Dual-hook default |
| SW morphology | Design sibling only | Paid **v4** product |

v3 = **heavier open toolkit**, still **not maximum**.

---

## Paid peers — what v4 must reach

| Peer | Features to match or beat under paid SKU | Notes |
|------|------------------------------------------|--------|
| **Sanskrit Writer** | Forms/morphology-aware compose surface; multi-script output polish | Core differentiator of paid tier |
| **SanskritTypist** | Advanced iOS keyboard: long-press, digraph parity, Deva/IAST, App Store quality | v4 Apple workstream |
| **Mac desktop apps** | Notarized menu-bar + Accessibility, full tray parity with Win, signed updates | v4 Mac workstream |
| **Aksharamukha-class** | In-product script/OCR path where license allows | Prefer optional module + attribution |
| **Cologne depth** | Gloss, offline index, autocomplete — already free; paid adds UX + sync | Do not paywall Cologne API itself |

**v4 non-goals:** forcing free users off v2; dual Keyman+KeySwap hooks; closed-source core of the free shell (prefer free core + paid packs/apps).

---

## Platform honesty (Win vs Mac vs iOS)

| Platform | Today | v2 free portable | v3 free heavy | v4 paid |
|----------|--------|------------------|---------------|---------|
| **Windows** | Flagship AHK tray + Python helpers | Portable install audited; #7–#8 shipped 2.9 | Plugins wired behind opt-in tray | Optional paid pack installer |
| **Mac** | Menu-bar cycle/smart; Accessibility | Improve install script; env triggers | Same Python plugins if PATH set | **Notarized app**, full tray parity, advanced UX |
| **iOS** | Keyboard scaffold + long-press | Writer digraph parity **shipped 2.9** | Limited (sandbox) | **App Store** keyboard + host; advanced features |

---

## Version mapping (quick)

| Capability gap | Owner version |
|----------------|---------------|
| Residual light UX (#7, #8), portable free story | **v2.9** (shipped) |
| Offline fuzzy pack, network autocomplete, link-out sidecars | **v3** (partly shipped) |
| Morphology/forms, advanced Mac/iOS, paid SKU, signed builds | **v4** |

Full backlog tables: [ROADMAP_KEYSWAP_V2_V3.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md).

---

## Skip in **default free** install (still true)

- Always-on multi-MB MW/SQLite  
- Full Keyman dual-hook  
- OCR / TTS / Heritage engines in-process  
- Always-on network autocomplete  
- Full morphology dictionary  
- App Store–grade Mac/iOS product chrome  

---

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
- [Sanskrit Text-to-Speech (SRI Auroville)](https://sri.auroville.org/projects/sanskrit-text-to-speech/) — H1639, replaces the earlier "SRI TTS etc." placeholder  
- [Sanskrit Heritage Site (INRIA)](https://sanskrit.inria.fr/) — H1639  
- r/sanskrit typing threads (IAST setup, diacritics, Windows/Mac)

_Dr. Mārcis Gasūns_
