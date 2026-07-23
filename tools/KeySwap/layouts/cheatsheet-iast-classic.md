# IAST classic — KeySwap cycle cheatsheet

_Created: 23-07-2026 · Last updated: 23-07-2026_

Profile: `configs/iast-classic.txt` · Trigger: `=` (cycle) · Smart: double letter

## Cycle (letter then =)

| Type | Press `=` → | → | → |
|------|-------------|---|---|
| a | ā | | |
| i | ī | | |
| u | ū | | |
| r | ṛ | ṝ | |
| l | ḷ | ḹ | |
| m | ṃ | ṁ | |
| h | ḥ | | |
| n | ṇ | ṅ | ñ |
| t | ṭ | | |
| d | ḍ | | |
| s | ṣ | ś | |

Uppercase mirrors: A→Ā, N→Ṇ→Ṅ→Ñ, etc.

## Smart double-letter (2.0, when enabled)

| Type | Becomes |
|------|---------|
| aa ii uu | ā ī ū |
| rr ll mm hh | ṛ ḷ ṃ ḥ |
| sh ss | ś ṣ |
| ng ny nn | ṅ ñ ṇ |
| tt dd | ṭ ḍ |

## Convert selection (2.0)

```bash
python tools/KeySwap/convert_bridge.py --to deva "rāmaḥ"
python tools/KeySwap/convert_bridge.py --to iast "रामः"
```

Windows AHK: hotkey converts clipboard via the same script (see windows README).

_Dr. Mārcis Gasūns_
