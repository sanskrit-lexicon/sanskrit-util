# MSKLC / system layout path (KeySwap 2.1)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Ship a **no-hook** IAST input path for Windows labs (UBC-style). This folder does
**not** replace the Microsoft Keyboard Layout Creator GUI; it provides:

1. A **dead-key chord map** aligned with KeySwap deadkey mode (`'` + letter).  
2. Pointers to the production-ready **ABC Extended** clone.  
3. A starter **`.klc` fragment** you can import/adapt in MSKLC.

## Prefer existing layouts (recommended for classrooms)

| Layout | Link |
|--------|------|
| ABC Extended for Windows | [adunning/Mac-Keyboard-Layouts-for-Windows](https://github.com/adunning/Mac-Keyboard-Layouts-for-Windows) |
| Mac built-in | ABC Extended / EasyUnicode |

Install those first. Use KeySwap AHK only when students need cycle/smart muscle memory.

## KeySwap dead-key map (matches AHK `deadkey` mode)

After typing **apostrophe** `'` then a letter:

| `'` + | Output |
|-------|--------|
| a i u r l | ā ī ū ṛ ḷ |
| m h n t d s | ṃ ḥ ṇ ṭ ḍ ś |
| A I U R L M H N T D S | Ā Ī Ū Ṛ Ḷ Ṃ Ḥ Ṇ Ṭ Ḍ Ś |

Cycle mode remains: letter then `=` using `configs/iast-classic.txt`.

## MSKLC steps (optional custom layout)

1. Install [Microsoft Keyboard Layout Creator 1.4](https://www.microsoft.com/en-us/download/details.aspx?id=102134) (or current).  
2. File → Load Existing Keyboard → US.  
3. Assign dead key on `VK_OEM_7` (apostrophe) → map combinations per table above.  
4. Project → Build DLL and Setup Package.  
5. Install the generated MSI on lab images.

A machine-readable chord table is in [`deadkey-chords.tsv`](deadkey-chords.tsv).

## When KeySwap PE/AHK still wins

- Users already trained on Keyswap `=` cycling.  
- Need smart digraphs (`aa`→ā) without learning Option chords.  
- Personal machines where Accessibility/AHK is acceptable.

_Dr. Mārcis Gasūns_
