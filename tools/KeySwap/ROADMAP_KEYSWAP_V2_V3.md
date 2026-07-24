# KeySwap product roadmap — **v2 remainder** vs **v3 heavy**

_Created: 24-07-2026 · Last updated: 24-07-2026_  
_Source: [SIMILARS_COMPARISON.md](SIMILARS_COMPARISON.md) peer survey + shipped 2.0–2.6_  
_Model: Grok 4.5 (`grok-4.5`) · v3 design: [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md)_

**Constraint (until v3):** keep KeySwap a **light scholar typing companion** —
hooks + small data files + link-outs. No Keyman-class IME, no full script matrix,
no morphology DB, no always-on network autocomplete.

| Line | Scope | Version identity |
|------|--------|------------------|
| **Shipped** | 2.0–2.6 (cycle → Writer-scheme, Cologne, gloss, install, PE docs) | `tools/KeySwap` **2.6.x** |
| **v2 remainder** | Peer-survey residual: 10 light adds + highest-leverage pack | finish **2.x** (2.7+) |
| **v3** | Items **explicitly skipped** through 2.x (heavy / embed) | first **3.0** wave |

---

## Shipped baseline (do not re-plan)

See README changelog blocks 2.0–2.6. Headline: multi-platform typing + Cologne layer;
Writer-scheme; script mode; gloss; one-install; PE vs AHK documented.

---

## Version 2 remainder — light peer-survey backlog

### Highest-leverage pack (do first inside v2)

Closes almost everything the old Tier A list still owed:

| ID | Item | Status |
|----|------|--------|
| L1 | Copy **SLP1 + normkey** of clipboard (hotkey / tray; no browser) | **shipped 2.7** |
| L2 | Tray **Ecosystem** submenu — static peer links | **shipped 2.7** |
| L3 | **Literal `=` escape** (Shift+=) + README | **shipped 2.7** |
| L4 | **`pali-lite`** config profile (data only) | **shipped 2.7** |
| L5 | Refresh **SIMILARS** to “as of 2.6/2.7” + this roadmap pointer | **shipped 2.7** |

### The 10 “still worth adding” (v2 product backlog)

From the post-2.6 comparison read of SIMILARS (ranked):

| # | Item | Peer driver | Effort | Notes |
|---|------|-------------|--------|--------|
| 1 | Copy SLP1 + normkey | Cologne companion | S | = L1 |
| 2 | Ecosystem tray links | Sanscript, Aksharamukha, Dunning, … | S | = L2; includes #9 Brāhmī link-out |
| 3 | Literal-`=` escape | Upstream PE pain | S | = L3 |
| 4 | `pali-lite` profile | Pāli / Buddhist IAST subset | S | = L4 |
| 5 | Scancode / non-US **trigger presets** | Layout peers, PE comments | M | **shipped 2.8** `trigger_presets.py` + tray / `trigger.ini` / `KEYSWAP_TRIGGER` |
| 6 | **Classroom pack** one-pager | ABC Extended, EasyUnicode, MSKLC | S | **shipped 2.7** `docs/CLASSROOM_LAYOUT_VS_KEYSWAP.md` |
| 7 | **iOS long-press ↔ Writer digraphs** parity | SanskritTypist | M | Soft keyboard honesty |
| 8 | Optional **live Deva type-out** (not only clipboard) | SW / Typist dual output | M–H | Opt-in; keep off by default |
| 9 | **Aksharamukha / Brāhmī open** URL from clipboard | SW Brāhmī; link-out stance | S | Folded into L2 ecosystem |
| 10 | **SIMILARS refresh** (capability matrix, shipped/skipped) | Survey hygiene | S | = L5 |

**v2 exit criteria:** L1–L5 landed; #5–#8 either shipped or parked with a one-line reason in this file; no v3 embeds started.

---

## Version 3 — previously **explicit skips** (now planned heavy wave)

These were banned under the light constraint; **v3 reopens them** as opt-in / separate installers where possible.

Architecture (H1581): [docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md) ·
plugin tree: [plugins/](plugins/).

| # | Item | Why it was skipped in 2.x | v3 direction | Status (24-07-2026) |
|---|------|---------------------------|--------------|---------------------|
| V3-1 | **Embed Aksharamukha** (or full script matrix) | Weight / 100+ scripts | Optional module or sidecar; not core tray | planned (link-out until pack) |
| V3-2 | **Local MW / hwnorm1c SQLite** always-on DB | Multi-MB; server role | Optional offline fuzzy search pack | **shipped** (opt-in) — `plugins/offline_fuzzy/` exact+prefix+edit; `--plugin offline_fuzzy` / `KEYSWAP_PLUGINS`; full MW via `KEYSWAP_WORDLIST` / `build_local_wordlist.py` |
| V3-3 | **Full Keyman-class IME** | Competing stack; dual-hook hell | Documented dual install only, or thin Keyman bridge | planned (docs only) |
| V3-4 | **OCR** | Out of typing scope | Link-out or separate tool | planned (link-out) |
| V3-5 | **TTS** | Out of typing scope | Link-out (SRI TTS, etc.) | planned (link-out) |
| V3-6 | **Sanskrit Heritage segmenter** | Heavy grammar engine | Microservice / link-out | planned (link-out) |
| V3-7 | **Always-on network autocomplete** | Latency + privacy + false confidence | Optional after offline index (V3-2) | **shipped** (opt-in) — `plugins/network_autocomplete/`; offline fuzzy first, Cologne only when local not confident; never default Startup |
| V3-8 | **Full morphology / forms dictionary** (SW-class) | Product-sized DB | Separate “compose” companion, not KeySwap core | **parked** (sibling app; not tray plugin) |

**v3 principle:** core KeySwap stays the typing shell; heavy capabilities are **plugins or sibling apps**, never forced into the default Startup path.

**First cut (3.0.0 path):** V3-2 offline fuzzy **implemented** (opt-in plugin; seed or full wordlist). V3-8 remains a sibling design, not default KeySwap.

---

## Suggested release cuts

| Tag | Contents |
|-----|----------|
| **2.7.x** | Highest-leverage pack L1–L5 |
| **2.8.x** | #5 trigger presets (**shipped**) + #6 classroom pack (already 2.7) |
| **2.9.x** | #7 iOS Writer parity + #8 opt-in live Deva (or slip to 3.0 if too heavy) |
| **3.0.0** | First v3 capability: **V3-2** offline fuzzy (scaffold H1581 → full index follow-up); V3-8 stays sibling |

---

## Session starters

Leverage pack (2.7):

```
Read C:\Users\user\Documents\GitHub\sanskrit-util\tools\KeySwap\ROADMAP_KEYSWAP_V2_V3.md and implement the Version 2 highest-leverage pack L1–L5.
```

v3 design / first plugin wave (H1581):

```
Read C:\Users\user\Documents\GitHub\Uprava\handoffs\H1581-Sonnet_sanskrit-util_keyswap-v3-former-skips-heavy-wave_24.07.26.md and execute it.
```

On Sonnet 5 (`claude-sonnet-5`); design memo + first plugin scaffold (V3-2 or V3-8); never load into default Startup AHK.

_Dr. Mārcis Gasūns_
