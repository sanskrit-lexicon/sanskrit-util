# App Store / notarized binary checklist (KeySwap backlog #11)

_Created: 23-07-2026 · Last updated: 05-09-2026_

KeySwap 2.x ships **source**. Publishing binaries is a separate release track
(Apple Developer Program + Windows signing). This checklist is the backlog item
so a future session can execute without re-deriving requirements.

## iOS / iPadOS (custom keyboard)

1. Create Xcode project per [apple/README.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/apple/README.md).  
2. Bundle ID: e.g. `org.sanskrit-lexicon.KeySwap` + `.keyboard`.  
3. App Group `group.keyswap` for profile defaults.  
4. Privacy strings: keyboard does **not** need Full Access for cycle/smart/long-press.  
5. If Full Access later: declare and justify network/clipboard use.  
6. Screenshots: Notepad-style demo of `n` → ṇ and long-press menu.  
7. TestFlight → App Review notes: “IAST scholarly keyboard; no account; offline.”  
8. Export compliance: no proprietary encryption beyond HTTPS if any.

## macOS menu-bar app

1. `LSUIElement` = YES (accessory).  
2. Hardened Runtime + **Accessibility** usage description in Info.plist.  
3. Notarize with `notarytool`; staple ticket.  
4. First-run UX: open System Settings → Privacy → Accessibility.  
5. Distribute via GitHub Releases `.dmg` or Mac App Store (Sandbox may block
   event taps — prefer Developer ID outside MAS if tap is required).

## Windows

1. Prefer distributing **AHK source** + “compile with Ahk2Exe” instructions.  
2. If PE: code-sign; never claim vendor PE is MIT ([THIRD_PARTY_NOTICE](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/THIRD_PARTY_NOTICE.md)).  
3. SmartScreen: publish with EV cert if possible.

## Out of scope for agents without credentials

Signing certs, App Store Connect API keys, and notarization Apple ID are
**human-held**. Agents prepare the project; a human ships the binary.

_Dr. Mārcis Gasūns_
