# KeySwap product roadmap — **v2 free portable** · **v3 heavy open** · **v4 paid full**

_Created: 24-07-2026 · Last updated: 25-07-2026_  
_Source: [SIMILARS_COMPARISON.md](SIMILARS_COMPARISON.md) peer survey + shipped 2.0–2.9 + V3-2/V3-7_  
_Model: Grok 4.5 (`grok-4.5`) · v3 design: [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md) · 2.9 residual (H1638): Fable 5 (`claude-fable-5`) · v3 free-heavy residual (H1639): Sonnet 5 (`claude-sonnet-5`)_

## Product principles

| Tier | Price | Weight | Promise |
|------|-------|--------|---------|
| **v2.x** | **Free** | **Mostly portable** | Best light scholar typing companion; Win flagship; no heavy default |
| **v3.x** | **Free** | **Heavier opt-in** | Plugins/sidecars (offline fuzzy, network AC, link-outs); **not maximum** |
| **v4.x** | **Paid** | Full product | **Most** peer features: forms/morphology, advanced **Mac + iOS**, signed builds |

**Never:** dual-hook Keyman+KeySwap by default · always-on multi-MB DB on free Startup · paywall the open Cologne API itself.

---

## Line map

| Line | Scope | Version identity |
|------|--------|------------------|
| **Shipped** | 2.0–2.9 + V3-2 offline_fuzzy + V3-7 network_autocomplete + tray opt-in/full-MW docs/link-out polish | `tools/KeySwap` **2.9.x** · package **0.8.10** |
| **v2 remainder** | none — #7/#8/P shipped in 2.9 (H1638) | closed |
| **v3 free-heavy residual** | none — tray opt-in, full-MW pack docs, V3-1/4/5/6 link-out polish shipped (H1639) | closed |
| **v3** | Free heavy plugins / sidecars (former explicit skips) | **3.x** open |
| **v4** | Paid product + advanced Apple + morphology | **4.x** paid SKUs |

---

## Shipped baseline (do not re-plan)

See README + CHANGELOG 2.0–2.8 / v0.8.9. Headline: multi-platform typing + Cologne;
Writer-scheme; script mode; gloss; one-install; PE vs AHK; trigger presets; V3 plugins
(opt-in only).

---

## Version 2 — free, mostly portable

### Highest-leverage pack (done)

| ID | Item | Status |
|----|------|--------|
| L1 | Copy **SLP1 + normkey** | **shipped 2.7** |
| L2 | Tray **Ecosystem** submenu | **shipped 2.7** |
| L3 | **Literal trigger escape** | **shipped 2.7/2.8** |
| L4 | **`pali-lite`** profile | **shipped 2.7** |
| L5 | SIMILARS / roadmap hygiene | **shipped 2.7**; **refreshed 24-07-2026** (tiers) |

### Residual free backlog → **2.9** — shipped 25-07-2026 (H1638)

| # | Item | Peer driver | Effort | Status |
|---|------|-------------|--------|-------|
| 7 | **iOS long-press ↔ Writer digraphs** parity | SanskritTypist | M | **shipped** — `KeyboardViewController` now resolves `SmartTables.forProfile(name)` instead of a hardcoded classic table |
| 8 | Optional **live Deva type-out** (not only clipboard) | SW / Typist | M–H | **shipped, scoped down** — `Ctrl+Alt+Shift+D` converts the current **selection** to Devanāgarī in place (Windows). Continuous per-keystroke auto-flip was considered and **parked**: `convert_bridge.py` calls a real transliteration algorithm (`sanskrit_util.iast_to_devanagari`) via a PowerShell+Python subprocess per invocation — firing that on every keystroke (rather than on an explicit user action) would add per-character latency and was also impossible to validate in an environment with no AHK interpreter. A future session may revisit continuous mode once it can be tested live. |
| P | Portable free packaging pass | PE / classroom users | M | **audited, no changes needed** — `packaging/INSTALL.md` + `VENDOR_PE.md` already give one clear path per platform and explicitly warn against dual PE+AHK; no drift found |

**v2 exit criteria — met:** #7 + #8 shipped (or parked with reason, disclosed above); free install still portable and plugin-free by default; SIMILARS matrix current (see below).

---

## Version 3 — free, heavier (not maximum)

Architecture: [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md) · [plugins/](plugins/).

| # | Item | Status (25-07-2026) | Next |
|---|------|---------------------|------|
| V3-1 | Aksharamukha / script matrix | **link-out shipped** (tray "Ecosystem" ▸ Aksharamukha, H1639) | optional free sidecar (not default) |
| V3-2 | Offline fuzzy / MW index | **shipped** opt-in + **tray opt-in shipped** (H1639) + **full-MW pack docs shipped** (H1639) | none — residual closed |
| V3-3 | Keyman-class IME | dual-install docs (already tray-linked) | thin bridge doc only |
| V3-4 | OCR | **link-out shipped** — shares the Aksharamukha tray entry (same tool's upload feature, H1639) | stay link-out in free v3 |
| V3-5 | TTS | **link-out shipped** (tray "Ecosystem" ▸ Sanskrit Text-to-Speech, H1639 — replaces the former vague "SRI TTS etc." mention) | stay link-out |
| V3-6 | Heritage segmenter | **link-out shipped** (tray "Ecosystem" ▸ Sanskrit Heritage segmenter, H1639) | optional microservice later |
| V3-7 | Network autocomplete | **shipped** opt-in offline-first + **tray opt-in shipped** (H1639) | none — residual closed |
| V3-8 | Morphology / forms DB | **parked** (sibling design) | **owned by v4 paid**, child C3 ([H1640](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1640-Fable_sanskrit-util_keyswap-v4-paid-sku-and-apple_25.07.26.md)), not free maximum |

**v3 free-heavy residual — closed 25-07-2026 (H1639):** tray opt-in for
offline_fuzzy/network_autocomplete (Windows menu + Mac status-bar menu,
`$env:KEYSWAP_PLUGINS`, still off by default); full-MW pack docs pointing at
`SanskritLexicography/HeadwordLists/` (not vendored); V3-1/3-4/3-5/3-6
link-out polish (accurate, tested URLs replacing stale/vague mentions).

**v3 principle:** free users may opt into heavy packs; default Startup stays v2-light.  
**v3 is not the product ceiling** — that is v4.

---

## Version 4 — paid, most features (incl. advanced Mac + iOS)

### Promise

Paid SKUs must get **most** features that free/paid peers have, especially:

1. **Advanced Mac** — notarized menu-bar app, full tray parity with Windows, Accessibility polish, signed updates.  
2. **Advanced iOS** — App Store keyboard + host: long-press, Writer digraph parity, Deva/IAST, settings sync.  
3. **Compose / forms** — SW-class morphology or forms dictionary (license-clear data).  
4. **Integrated heavy packs** — offline index + autocomplete UX polished; optional script/OCR modules with attribution.  
5. **Install / update** — paid installer; free core remains available without paid chrome.

### v4 workstreams (for handoff fan-out)

| Stream | Deliverables | Depends on |
|--------|--------------|------------|
| **V4-A** Business / SKU | Pricing SKUs, license, free-vs-paid boundary `@DECIDE` | Human |
| **V4-B** Mac advanced | Notarization path, tray parity, install UX | V4-A |
| **V4-C** iOS advanced | App Store pipeline, keyboard feature parity | V4-A |
| **V4-D** Forms / morphology | Data rights + compose surface (sibling or paid module) | V4-A + rights |
| **V4-E** Polish free→paid bridge | Plugin discovery UI, offline pack download, no silent network | v3 plugins |

**v4 non-goals:** paywalling the free v2 shell; dual Keyman hooks; closing the free GitHub toolkit.

---

## Suggested release cuts

| Tag | Contents |
|-----|----------|
| **2.7.x–2.8.x** | Leverage + triggers (**shipped**) |
| **2.9.x** | #7 iOS Writer parity + #8 live Deva + portable free pass (**shipped**) |
| **3.0.x** | V3 plugin UX (tray opt-in) + remaining free sidecars as opt-in (**shipped**, H1639) |
| **3.x later** | dual-install Keyman docs only |
| **4.0.0** | First paid SKU + Mac **or** iOS advanced slice (pick after V4-A) |
| **4.x** | Forms/morphology + second Apple platform + pack polish |

---

## Session starters

v2 residual (2.9): 🔴 EXECUTED: [H1638-Sonnet_sanskrit-util_keyswap-v2-9-free-portable-residual_25.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1638-Sonnet_sanskrit-util_keyswap-v2-9-free-portable-residual_25.07.26.md)

v3 free-heavy residual: 🔴 EXECUTED: [H1639-Sonnet_sanskrit-util_keyswap-v3-free-heavy-residual_25.07.26.md](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1639-Sonnet_sanskrit-util_keyswap-v3-free-heavy-residual_25.07.26.md)

Full improvement programme (this plan’s umbrella):

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H###-…_keyswap-v2-v3-v4-full-improvement_….md and execute it.
```

_Dr. Mārcis Gasūns_
