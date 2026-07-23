# KeySwap 2.0 for iPhone and Mac

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Version: 2.0.0_

| Target | Features |
|--------|----------|
| **iPhone / iPad** | Custom keyboard: **= cycle**, **smart digraphs**, **long-press** menus, profile picker in host app |
| **Mac** | Menu-bar system-wide `=` + smart digraphs (Accessibility) |
| **KeySwapCore** | Swift package — cycle + smart (parity with Python) |

```bash
cd tools/KeySwap/apple
swift test   # when Xcode/Swift toolchain available
```

## Xcode wiring (one-time)

Same as 1.x shell, plus:

1. Link **KeySwapCore** to host **and** keyboard targets.  
2. Copy `Resources/configs/*.txt` (including `vedic-svara.txt`) into the keyboard bundle.  
3. Optional App Group `group.keyswap` for profile sync (`profile` key).  
4. iOS: long-press any letter key; toggle **smart✓** on the bottom row.

Full steps: parent [README.md](../README.md) + this file’s 1.x instructions remain valid for target creation:

1. New iOS App → replace with `ios-host/KeySwapHostApp.swift`.  
2. Add Custom Keyboard Extension → `ios-keyboard/*`.  
3. Add local package (this `apple/` folder).  
4. macOS App → `macos/KeySwapMacApp.swift`, `LSUIElement` = YES.

## 2.0 behaviour

- **Cycle:** longest known suffix advances (same as Python `CycleEngine`).  
- **Smart:** after insert, expand `aa`/`sh`/… via `SmartTables`.  
- **Long-press:** `engine.longPressMenu(for:)`.

_Dr. Mārcis Gasūns_
