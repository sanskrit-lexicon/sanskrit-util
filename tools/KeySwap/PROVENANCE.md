# KeySwap provenance

_Created: 23-07-2026 · Last updated: 23-07-2026_

## Open components (this repo)

| Path | License | Notes |
|------|---------|--------|
| `cycle_engine.py`, `validate_configs.py`, `test_cycle_engine.py` | MIT (same as [sanskrit-util LICENSE](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/LICENSE)) | Shared cycle semantics |
| `configs/*.txt` | MIT | Scholarly profiles maintained here |
| `windows/KeySwap.ahk` | MIT | Open Windows reimplementation |
| `apple/**` | MIT | iPhone keyboard + Mac menu-bar cycler + Swift core |

## Vendored third-party Windows binary

| Field | Value |
|-------|--------|
| Path | [`vendor/keyswap.exe`](vendor/keyswap.exe) |
| Upstream | [https://www.yesvedanta.com/keyswap/](https://www.yesvedanta.com/keyswap/) |
| Author | Andre Vas (Yes Vedanta) |
| PE ProductVersion | 1.0.0.0 |
| PE LegalCopyright | Copyright c 2017 |
| File mtime (vendored) | 2019-05-21 |
| **SHA-256** | `276cb3ab886f2991f4063cf3f597ab71c1f5d56a836a6f56be7ee745b6212b48` |
| Size (bytes) | 132608 |

| Field | Value |
|-------|--------|
| Path | [`vendor/key.bin`](vendor/key.bin) |
| Meaning | `uint32` LE virtual-key code; default `0x000000BB` = `VK_OEM_PLUS` (`=`) |
| **SHA-256** | `cc2767afee4ba0da3615c64d506c93740a9cec3a0eb7078f672dffc025ccb47a` |

Upstream site documents **2021-09** fixes; this binary snapshot may predate them.
Prefer `windows/KeySwap.ahk` or the Apple apps for new installs.

Verify:

```powershell
Get-FileHash tools\KeySwap\vendor\keyswap.exe -Algorithm SHA256
```

_Dr. Mārcis Gasūns_
