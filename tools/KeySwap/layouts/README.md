# Classroom / no-hook layouts (KeySwap 2.0)

_Created: 23-07-2026 · Last updated: 05-09-2026_

Universities (e.g. [UBC Sanskrit tools](https://blogs.ubc.ca/ubcsanskrit/tools/))
prefer **system keyboard layouts** over global hooks: no admin PE, works with
Keyman side-by-side, same training on Mac and Windows labs.

## Recommended path (IAST without KeySwap running)

| OS | Layout | Notes |
|----|--------|--------|
| macOS | **ABC Extended** (built-in) | Option + key for diacritics; [Penn State guide](https://sites.psu.edu/symbolcodes/mac/codemacext/) |
| macOS | **EasyUnicode** (Unebe) | Popular for Sanskrit/Pāli; community download |
| Windows | [Dunning ABC Extended for Windows](https://github.com/adunning/Mac-Keyboard-Layouts-for-Windows) | Clone of Mac ABC Extended via MSKLC |
| Windows | KeySwap AHK **dead-key mode** | See `../windows/KeySwap.ahk` — `Mode: deadkey` |

## ABC Extended cheatsheet (common IAST)

Approximate Option (Mac) / AltGr-style chords — verify on your layout viewer:

| Goal | Typical chord (ABC Extended) |
|------|------------------------------|
| ā | Option-a, then a |
| ī | Option-a, then i |
| ū | Option-a, then u |
| ṛ | Option-x, then r (varies by layout) |
| ṅ | Option-n, then g / dedicated |
| ñ | Option-n, then n |
| ṇ | underdot + n |
| ṭ ḍ | underdot + t/d |
| ś | Option-s or acute + s |
| ṣ | underdot + s |
| ṃ ḥ | underdot / candrabindu variants |

Print [cheatsheet-iast-classic.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/layouts/cheatsheet-iast-classic.md) for the **cycle**
order used when KeySwap *is* running (letter then `=`).

## When to use what

| Situation | Use |
|-----------|-----|
| Shared lab, no install rights for hooks | System layout only |
| Personal Windows, want Keyswap muscle memory | AHK cycle mode (default) |
| Personal Windows + Keyman for Devanāgarī | Layout or pause KeySwap; avoid dual hooks |
| iPhone | KeySwap keyboard long-press (2.0) or SanskritTypist |

_Dr. Mārcis Gasūns_
