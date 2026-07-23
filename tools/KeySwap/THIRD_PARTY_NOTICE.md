# Third-party notice — vendored Keyswap binary

_Created: 23-07-2026 · Last updated: 23-07-2026_

The file [`vendor/keyswap.exe`](vendor/keyswap.exe) (and companion
[`vendor/key.bin`](vendor/key.bin), [`vendor/ReadMe.txt`](vendor/ReadMe.txt),
[`vendor/rtfm.txt`](vendor/rtfm.txt)) is **not** original to the sanskrit-util
project.

- **Product:** Keyswap — IAST diacritics Windows software  
- **Author / site:** Andre Vas / [Yes Vedanta](https://www.yesvedanta.com/keyswap/)  
- **Copyright (from PE metadata):** Copyright c 2017  

It is redistributed here for convenience as an optional Windows typing helper.
**It is not covered by the sanskrit-util MIT license** unless the upstream
author grants matching terms. All rights in the binary remain with the
upstream author.

The open reimplementations in this folder (`cycle_engine.py`,
`windows/KeySwap.ahk`, `apple/**`, and the `configs/` profiles) are original
to this repository and are MIT-licensed with the rest of sanskrit-util.

Do not ship `vendor/keyswap.exe` inside the PyPI/npm packages.

_Dr. Mārcis Gasūns_
