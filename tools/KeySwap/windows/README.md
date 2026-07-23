# KeySwap for Windows (open AutoHotkey v2)

_Created: 23-07-2026 · Last updated: 23-07-2026_

Open reimplementation of the classic Keyswap cycle behaviour. Prefer this over
[`../vendor/keyswap.exe`](../vendor/keyswap.exe) when you want readable source
and no opaque keyboard hook binary.

## Requirements

- [AutoHotkey v2](https://www.autohotkey.com/)
- This folder’s parent [`config.txt`](../config.txt) (default = classical IAST)

## Run

1. Install AutoHotkey v2.
2. Double-click [`KeySwap.ahk`](KeySwap.ahk).
3. Type a letter, press `=` to cycle (e.g. `n` `=` `=` → `ṇ` → `ṅ`).

Optional config path:

```text
autohotkey64.exe KeySwap.ahk "C:\...\tools\KeySwap\configs\vedic-draft.txt"
```

## Profiles

| File | Use |
|------|-----|
| [`../config.txt`](../config.txt) | Default (iast-classic) |
| [`../configs/iast-classic.txt`](../configs/iast-classic.txt) | Classical IAST |
| [`../configs/iso15919.txt`](../configs/iso15919.txt) | ISO-oriented extras |
| [`../configs/vedic-draft.txt`](../configs/vedic-draft.txt) | Accents / draft svara |
| [`../configs/personal-legacy.txt`](../configs/personal-legacy.txt) | Upstream personal map |

## Vendored binary (optional)

The original Andre / Yes Vedanta PE lives in [`../vendor/`](../vendor/). See
[`../PROVENANCE.md`](../PROVENANCE.md) and [`../THIRD_PARTY_NOTICE.md`](../THIRD_PARTY_NOTICE.md).

_Dr. Mārcis Gasūns_
