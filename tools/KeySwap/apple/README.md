# KeySwap for iPhone and Mac

_Created: 23-07-2026 · Last updated: 23-07-2026_

Open Apple ports of the KeySwap IAST diacritic cycler. Shared logic lives in
**KeySwapCore** (Swift Package); platform UIs are separate.

| Target | What you get | Privilege model |
|--------|----------------|-----------------|
| **iPhone / iPad** | Custom system keyboard (type letter → tap **= cycle**) | Standard keyboard extension — **no Full Access** required for v1 |
| **Mac** | Menu-bar app; press `=` after a letter **in any app** | **Accessibility** permission (event tap), same idea as the Windows hook |

## Layout

```text
apple/
  Package.swift                 # KeySwapCore SPM
  Sources/KeySwapCore/          # CycleEngine (parity with ../cycle_engine.py)
  Tests/KeySwapCoreTests/
  Resources/configs/            # Bundled profiles (copy of ../configs)
  ios-host/KeySwapHostApp.swift # Host app (required to install a keyboard)
  ios-keyboard/                 # UIInputViewController + Info.plist
  macos/KeySwapMacApp.swift     # Menu-bar system-wide cycler
  README.md                     # this file
```

## Build KeySwapCore (any Mac with Xcode / Swift)

```bash
cd tools/KeySwap/apple
swift test
```

## Xcode app setup (one-time)

Apple does not let a bare folder run as an App Store keyboard; you wire targets once:

### iPhone / iPad keyboard

1. Open Xcode → **File → New → Project → App** (iOS), Product Name `KeySwap`, Interface SwiftUI, Language Swift.  
   Bundle ID example: `org.sanskrit-lexicon.KeySwap`.
2. Replace the generated app entry with sources from [`ios-host/KeySwapHostApp.swift`](ios-host/KeySwapHostApp.swift).
3. **File → New → Target → Custom Keyboard Extension**, name `KeySwapKeyboard`.
4. Replace the extension’s `KeyboardViewController.swift` with
   [`ios-keyboard/KeyboardViewController.swift`](ios-keyboard/KeyboardViewController.swift)
   and merge keys from [`ios-keyboard/Info.plist`](ios-keyboard/Info.plist).
5. **File → Add Package Dependencies… → Add Local…** → select this `apple/` folder
   (the package root with `Package.swift`). Link **KeySwapCore** to the keyboard target
   (and host if desired).
6. Add `Resources/configs/*.txt` to the **keyboard** target (Copy Bundle Resources).
7. Run the **host app** on a device/simulator, then:
   **Settings → General → Keyboard → Keyboards → Add New Keyboard… → KeySwap**.
8. In any app, switch keyboards with 🌐, type `n`, tap **= cycle**.

App Group (optional, for profile sync): capability `group.keyswap`, key `profile`
= `iast-classic` | `iso15919` | `vedic-draft` | `personal-legacy`.

### Mac menu-bar app

1. Xcode → **File → New → Project → App** (macOS), SwiftUI.
2. Replace app sources with [`macos/KeySwapMacApp.swift`](macos/KeySwapMacApp.swift);
   set `LSUIElement` = YES in Info (see [`macos/Info.plist`](macos/Info.plist)).
3. Add local package **KeySwapCore**; copy `Resources/configs` into the app bundle.
4. Run once → macOS prompts for **Accessibility** → enable KeySwap → relaunch.
5. Type in TextEdit: `n` then `=` → `ṇ` → `ṅ` → …

## Behaviour (shared)

Same as Windows / Python:

1. Config chains: `base > form1 > form2 > …` (see [`../configs/`](../configs/)).
2. Trigger advances the **longest known suffix** (or, on Mac/Windows, the last
   tracked letter form).
3. Profiles: classical IAST (default), ISO 15919, Vedic draft, personal legacy.

## Limitations (honest)

| Platform | Limit |
|----------|--------|
| iOS keyboard | Only active while KeySwap is the current keyboard (Apple policy). Cannot rewrite text typed with another keyboard. |
| iOS simulator | Keyboard extensions work; always re-test on a device before relying on it. |
| Mac event tap | Needs Accessibility; some secure fields block synthetic events. |
| App Store | Keyboard + Accessibility apps need privacy strings and review; this tree is **source**, not a notarized binary. |

## Parity tests

| Layer | Command |
|-------|---------|
| Python | `python tools/KeySwap/test_cycle_engine.py` |
| Configs | `python tools/KeySwap/validate_configs.py` |
| Swift | `cd tools/KeySwap/apple && swift test` |

_Dr. Mārcis Gasūns_
