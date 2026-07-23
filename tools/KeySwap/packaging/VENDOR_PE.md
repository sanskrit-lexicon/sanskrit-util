# Vendor PE vs open shells (backlog #10)

_Created: 23-07-2026 · Last updated: 23-07-2026_

## Policy (KeySwap 2.1+)

| Artifact | Status |
|----------|--------|
| `vendor/keyswap.exe` | Optional legacy 1.x; **not** the default path |
| `windows/KeySwap.ahk` | **Default** Windows runtime |
| Apple / PWA | **Default** for those platforms |

Upstream (Yes Vedanta) documents **2021-09** fixes (“complex 2-bit characters”).
The vendored PE may predate that build (see [PROVENANCE.md](../PROVENANCE.md)).

## Recommended action

1. **Do not** re-vendor a new PE unless a human verifies SHA-256 against a
   trusted download and updates PROVENANCE.  
2. Prefer absorbing behaviour into AHK + `cycle_engine` (already done for
   cycle/smart/deadkey).  
3. If PE is removed later: keep `vendor/ReadMe.txt` quote + link to
   yesvedanta.com/keyswap for attribution.

## Verify current pin

```powershell
Get-FileHash tools\KeySwap\vendor\keyswap.exe -Algorithm SHA256
# expect: 276CB3AB886F2991F4063CF3F597AB71C1F5D56A836A6F56BE7EE745B6212B48
```

_Dr. Mārcis Gasūns_
