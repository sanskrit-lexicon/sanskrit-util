# Upstream Keyswap page analysis (Yes Vedanta)

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Source: [https://www.yesvedanta.com/keyswap/](https://www.yesvedanta.com/keyswap/) · 80 comments scraped 23-07-2026 · Grok 4.5_

How the original product page + community feedback should improve **our** KeySwap
README and product (tools/KeySwap 2.x), without re-vendoring the PE as default.

---

## What the page does well (copy patterns)

| Pattern | Why it works | Apply to our README |
|---------|--------------|---------------------|
| One-sentence promise | “add diacritics by pressing `=` after any key” | Keep first line that simple |
| Live cycle example | `n > ṇ > ṅ > ñ` | Already have; put **above** feature lists |
| Real words | *Rāmāyaṇam, saṃsāra, śiṣyāḥ* | Keep; add *kṛṣṇa* (commenter pain word) |
| Origin story | University homework, handwriting too slow | One short “Why cycle?” line for scholars |
| Explicit config steps | Notepad → edit → **full exit** → relaunch | We have hot-reload; still document “if broken, F6 / restart” |
| Known conflicts | Keyman named | Keep; expand with Word/`=` shortcut conflict |
| Troubleshooting | SmartScreen, keyboard layout | Elevate to top-level **Troubleshooting** |
| Mac fallback | Lexilogos link | We have Mac/iOS/PWA — still link Lexilogos as no-install |

Changelog honesty (2017 → 2021 “2-bit characters”) teaches us to **date** our VERSION and note PE may be older than 2021.

---

## Comment themes (n=80, qualitative)

### Love / job-to-be-done (majority of non-bug posts)

- “Life changing”, “indispensable”, “must have for transliteration”.
- **Cross-app typing** beats Word-only macros (Fede, Frank).
- **Simplicity**: no chord memorization; cycle until right glyph (Viji — also Carnatic notation).
- **Config file** is the product: MIA languages, IPA, music, fonts projects (Kate, Hakon).
- Portable / no installer calms Word-addin trauma (ramachandran).
- Donation willingness (YR, Vidyashankar) — goodwill, not a monetize mandate.

### Recurring pain (product requirements)

| Issue | Evidence | Our status / action |
|-------|----------|---------------------|
| **`=` steals Word shortcuts** (Draft layout, Vertical Split, TM superscript) | Aravindaksan, Narayan (years), Arvind, Rūmā | **Critical.** Document: non-US layout + Word; change trigger; prefer AHK smart over PE. Default trigger **not** `=` when possible, or warn hard. |
| **Keyboard layout** must be English (US) for PE; India/Spain/Norway differ | Bhuvana (fix), Fede (`+` instead of `=`), Hakon (change trigger), Andre Australia exception | README: “layout vs trigger key” (Hakon is right: often only trigger is layout-bound). AHK should bind by scancode where possible. |
| **Run as Administrator** | Official steps + many replies | PE page pushes admin. **We should not** default-admin; document elevation only as last resort (security). |
| **SmartScreen / “same key already added”** | José Luis, Rāma Mukunda #6342 | PE unsigned. Prefer AHK source; for PE: “More info → Run anyway”, re-extract folder. |
| **Capitals missing in old zip** | Fede | We ship uppercase chains in `iast-classic`. |
| **ISO 15919** (r̥, r̥̄) | simuno | We have `iso15919` profile — advertise. |
| **Svara / Vedic** | Marina, Vidyashankar, Terence, Stephane | Ship **ready `vedic-svara`** + “how to paste from Lexilogos/Rudram PDF”. Multi-underline combining marks are hard — document limits. |
| **Danda / punctuation** | Durgaprasad | Document `. > । > ॥` (or `\|`) recipe. |
| **Chandrabindu** | Bangali Purush | Document Lexilogos → config paste. |
| **Font jumps to Cambria** | Stephane | Rare PE inject quirk; document “type into selected font; if stuck, try AHK”. |
| **Mac / mobile / ChromeOS** | Amrit, Eddie, Rita (iPad→Lexilogos), AP Taylor | **Our 2.x differentiator** — put platforms table first. |
| **Beginner launch confusion** | Rita | “Double-click AHK / exe → tray icon only, no window”. |
| **Download flaky** | Danny, Kate | Prefer git clone + release assets; pin hashes (we have PROVENANCE). |
| **Phonetic speed** (Azhagi) | ramu left for Azhagi | Keep **smart digraphs**; optional note “for pure phonetic speed see Keyman/Azhagi”. |
| **Source / GitHub** | Abhinav | Point at this repo + open AHK, not only S3 zip. |
| **Aum / ॐ** | Jai | Tiny FAQ: `o > oṃ > ॐ` in config or insert ॐ. |
| **Sound pedagogy** | Nitin | Link IAST Wikipedia; optional HUD “ṇ = retroflex n”. |

### Official page troubleshooting (must mirror)

1. Keyman conflict.  
2. Duplicate-key error → re-extract + SmartScreen “Run anyway” (#6342).  
3. Unpredictable cycle → English (US) system keyboard (not Word language only).  
4. Admin for stubborn apps (WordPerfect, Word).  

---

## README improvements (concrete outline)

1. **Hero** — one sentence + cycle demo + three sample words including *kṛṣṇa*.  
2. **Platforms first** — Windows AHK (recommended) · Mac · iPhone · PWA · legacy PE last.  
3. **“If it breaks Word” box** — layout US English · change trigger · not Word language · try Google Docs · AHK over PE.  
4. **First 60 seconds** — double-click → tray only → Notepad test `n` + trigger.  
5. **Profiles table** — classic / ISO / vedic-svara / personal-legacy with “who wants this”.  
6. **Config recipes** — danda, ॐ, chandrabindu, svara paste from Lexilogos.  
7. **Troubleshooting** — table from comments above.  
8. **Credits** — Andre Vas / Yes Vedanta origin + our open 2.x.  
9. **Do not lead with admin** — reverse of upstream; security-first.

---

## Product improvements (mapped to feedback)

| Priority | Change | Comment driver |
|----------|--------|----------------|
| P0 | Document Word+`=` disaster; default docs to **Alt+`=` or configurable** trigger | Aravindaksan, Rūmā, Narayan |
| P0 | First-run “tray icon only” + Notepad smoke test | Rita |
| P1 | Ship **vedic-svara** as advertised profile + sample Rudram line | Marina, Vidyashankar |
| P1 | Config recipes (danda, ॐ, ISO r̥) in README / cheatsheet | Durgaprasad, Jai, simuno |
| P1 | SmartScreen / unsigned PE section; prefer AHK | #6342 |
| P2 | Teaching HUD: optional Devanāgarī of current form | Nitin |
| P2 | Multi-config switch without editing (profiles) | Hakon |
| P2 | Mac/iOS/ChromeOS/PWA called out as solved | Amrit, Eddie, Taylor |
| P3 | Phonetic-speed note vs Azhagi/Keyman | ramu |
| — | Skip font embedding; skip Merriam-Webster debate | Aditya, Raja |

Already shipped that answers comments: capitals, ISO profile, vedic-svara, Mac/iOS/PWA, hot-reload, multi-profile configs, open source in-repo, Cologne open.

---

## What not to copy from the page

- **Run as administrator as step 1** — high risk; keep as last resort.  
- **Opaque PE as primary download** — community SmartScreen pain.  
- **Mac = Lexilogos only** — we can do better (and did).  
- Vague “fixed bugs” changelog without repro — keep our versioned VERSION + tests.

---

## Attribution

Original product and community: **Andre Vas / Yes Vedanta**.  
Comment corpus: 80 public WordPress comments on the page above (not reproduced in full here).

_Dr. Mārcis Gasūns_
