# KeySwap v4 paid SKU brief — pricing options · advanced Mac/iOS checklists · forms data rights

_Created: 26-07-2026 · Last updated: 26-07-2026_

**What this is:** the decision brief that makes **V4-A ruleable** and **V4-B/C/D scopeable** —
[H1640](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1640-Fable_sanskrit-util_keyswap-v4-paid-sku-and-apple_25.07.26.md),
child C3 of the
[H1619 programme](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1619-Fable_sanskrit-util_keyswap-v2-v3-v4-full-improvement_24.07.26.md).
It presents **options for a human ruling, not decisions**: no price is chosen here, no data
right is ruled here. Authored by Fable 5 (`claude-fable-5`).

**Sources:**
[ROADMAP_KEYSWAP_V2_V3.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md)
§ "Version 4 — paid" (workstreams V4-A…V4-E) ·
[SIMILARS_COMPARISON.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/SIMILARS_COMPARISON.md)
§ "Paid peers — what v4 must reach" + § "Platform honesty".

**Invariants (carried from the programme, binding on every option below):**

- The free v2 shell and the free v3 opt-in plugins stay free and useful — v4 never
  retracts anything already shipped free (including the full-MW offline pack docs, free
  since [v0.8.10](https://github.com/sanskrit-lexicon/sanskrit-util/releases/tag/v0.8.10)).
- The open Cologne API is never paywalled — paid adds UX, packaging, and sync on top.
- No dual Keyman+KeySwap hooks, free or paid.
- No silent network anywhere; offline-first defaults carry into paid builds.

---

## 1 · V4-A — pricing / SKU options (`@DECIDE`, human rules)

Known fixed costs any option must clear: Apple Developer Program **US$99/year**
(prerequisite for notarization and the App Store, i.e. for V4-B *and* V4-C), plus App
Store commission on iOS sales (15 % under the Small Business Program below US$1M/year,
30 % standard). Peer anchors: Sanskrit Writer and SanskritTypist both sell as
one-time-purchase apps; no Sanskrit-input peer sells a subscription.

### Option S1 — one-time paid app per platform

"KeySwap Pro for Mac" and "KeySwap Pro for iOS" as separate one-time purchases.

| Aspect | Shape |
|---|---|
| Unlocks | Notarized Mac menu-bar app (full tray parity, signed updates) · App Store iOS keyboard + host · forms compose on the purchased platform |
| Free/paid boundary | Free = everything shipped today (all Windows features, script-level Mac/iOS, v3 plugins). Paid = signed Apple **builds** + forms compose + paid installer |
| Pros | Simplest to sell and support; matches the "free core + paid packs/apps" principle; matches both paid peers' model; no accounts/licensing infra |
| Cons | No recurring revenue against the recurring US$99/year + App Store maintenance; upgrade pricing needs a later ruling; two SKUs to maintain |

### Option S2 — single subscription (all platforms)

One annual subscription unlocking every paid surface on every platform, plus
settings sync.

| Aspect | Shape |
|---|---|
| Unlocks | Everything in S1 on both platforms · cross-device settings sync · pack updates |
| Free/paid boundary | Same as S1; sync exists only under subscription |
| Pros | Funds the recurring Apple costs structurally; sync is naturally subscription-shaped; one SKU |
| Cons | Heaviest infra (accounts, entitlement checks, renewal flows); subscription fatigue in a small academic market; highest risk of *reading* as a paywall even while the free core stays intact |

### Option S3 — à-la-carte one-time packs

Separate one-time purchases: "Apple advanced pack" (Mac + iOS binaries together),
"Forms/morphology pack" (compose surface + data, per V4-D), future script/OCR module.

| Aspect | Shape |
|---|---|
| Unlocks | Each pack unlocks exactly its own surface; packs compose |
| Free/paid boundary | Same baseline as S1; finer-grained on top |
| Pros | Buyers pay only for what they use; closest fit to the plugin architecture v3 already ships; the forms pack can ship later than the Apple pack without blocking it |
| Cons | SKU sprawl (support matrix, bundle-pricing questions); per-pack revenue may be too thin to justify per-pack App Store listings |

A hybrid (S1 for the Apple apps + S3 for the forms pack) is a legitimate fourth answer;
it is listed as a combination, not recommended over the pure shapes.

**`@DECIDE` (V4-A):** pick S1 / S2 / S3 / S1+S3 hybrid, and set the price band. The
ruling also picks which platform ships first in 4.0.0 (ROADMAP release table: "Mac
**or** iOS advanced slice — pick after V4-A").

---

## 2 · V4-B — advanced Mac checklist (ordered, for a future execution handoff)

Today's Mac state: menu-bar cycle/smart exist; tray opt-in submenu shipped in
[H1639](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1639-Sonnet_sanskrit-util_keyswap-v3-free-heavy-residual_25.07.26.md)
(`apple/macos/KeySwapMacApp.swift` status-bar menu + `UserDefaults` persistence);
Cologne/Python helpers and tray depth lag Windows; dev-signed only.

1. **Apple Developer Program enrollment** — US$99/year; organisation vs individual
   account is part of the V4-A ruling's fine print. Gates everything below.
2. **Signing + notarization pipeline** — hardened runtime, `codesign` + `notarytool`
   in CI, stapled tickets; produces the first distributable build.
3. **Full tray parity with Windows** — scheme cycle/smart toggles, the Plugins
   opt-in submenu (exists), the complete Ecosystem link set (Windows tray is the
   reference), HUD/status indicators.
4. **Accessibility onboarding** — `AXIsProcessTrusted` first-run flow with a
   System Settings deep link and a clear "why" screen (today: manual grant, no UX).
5. **Cologne/Python helper parity** — bundle a Python runtime or port the helper
   calls to Swift; the execution handoff decides which after measuring bundle size.
6. **Signed updates** — Sparkle with EdDSA keys, or notarized-DMG re-download;
   explicit "check for updates" only, no silent network (invariant).
7. **Paid install/licensing** — DMG + license key, or Mac App Store distribution;
   follows the V4-A ruling.

## 3 · V4-C — advanced iOS checklist (ordered)

Today's iOS state: keyboard scaffold with long-press and (since v2.9,
[H1638](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1638-Sonnet_sanskrit-util_keyswap-v2-9-free-portable-residual_25.07.26.md))
Writer-profile smart-digraph parity; host app scaffold `apple/ios-host/KeySwapHostApp.swift`
is minimal; nothing App-Store-shaped yet.

1. **App IDs, entitlements, targets** — keyboard extension + host app as real
   targets with an App Group between them.
2. **Keyboard feature parity** — carry the shipped long-press + Writer digraph
   parity; add Deva/IAST output toggle and cycle triggers to match the desktop
   feature set where a soft keyboard sensibly can.
3. **Settings via App Group** — host app configures, extension reads; iCloud
   settings **sync** is the paid-tier candidate (and S2's flagship feature).
4. **Full Access policy** — keyboard must be fully functional *without* Full
   Access (Apple requires this for keyboard extensions); network autocomplete
   stays opt-in behind Full Access with an honest privacy label. Offline-first
   default is an invariant, not a setting.
5. **App Store compliance pass** — keyboard-extension guidelines, privacy
   nutrition labels, review notes explaining the Cologne link-outs.
6. **TestFlight beta → App Store listing** — screenshots, localized description
   (EN + Sanskrit-studies framing), pricing per the V4-A ruling.
7. **Forms compose surface on iOS** — only after the V4-D ruling; likely the
   host app's job, not the extension's (memory budget).

---

## 4 · V4-D — forms/morphology data rights (`@DECIDE`, human rules)

The requirement: Sanskrit Writer's differentiator is a forms/morphology-aware compose
surface; v4 needs a full-paradigm generator or a precomputed forms DB whose data rights
allow **bundling in a paid product**. Sanskrit Writer's own forms data is not
rights-clear for KeySwap and is not a candidate.

**Primary candidate — `vidyut-prakriya` ([ambuda-org/vidyut](https://github.com/ambuda-org/vidyut)): rights-clear on the evidence checked.**

- **Code:** MIT (repo license, checked 26-07-2026).
- **Bundled data:** the Dhātupāṭha it derives from comes from ashtadhyayi.com, and the
  vidyut-prakriya docs state the ashtadhyayi.com author "graciously agreed to share this
  file with us under an MIT license" (checked 26-07-2026 against the repo, not from
  memory). MIT permits commercial redistribution with attribution — a paid KeySwap
  module fits, with an attribution screen naming vidyut and ashtadhyayi.com.
- **Org prior art:** the org already drives `vidyut.prakriya` locally — kosha's
  [H1368 derivation harness](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H1368-Sonnet_kosha_w2a-vidyut-prakriya-derivation-harness_20.07.26.md)
  and SamudraManthanam's
  [H906 vidyut-diff work](https://github.com/gasyoun/Uprava/blob/main/handoffs/H906-Opus_SamudraManthanam_nkrya-sa-morphology-dcs-vidyut_14.07.26.md) —
  so integration expertise exists in-house.
- **Two integration shapes** for the execution handoff: (a) **precompute** forms tables
  offline (kosha-harness style) and ship them as a pack — keeps the paid app light, no
  Rust runtime shipped, recommended default; (b) embed the crate for on-device
  derivation — heavier, only worth it if paradigm coverage must be unbounded.

**Fallback candidates, if the primary is not approved:**

- **Sanskrit Heritage Platform morphology** (Gérard Huet, INRIA) — mature full-paradigm
  data, but distributed under LGPL-LR-style terms; bundling inside a *paid closed* pack
  carries copyleft-for-data obligations that would need a legal read first. Fallback,
  not co-equal.
- **In-house precomputation** — generate the forms DB ourselves with the existing kosha
  harness; the generated tables are our build artifact (still derived from the MIT
  Dhātupāṭha, so the same attribution applies). This is really shape (a) of the primary
  candidate stated as a fallback posture.

Supplementary (not a forms source): DCS attestation frequencies could rank forms inside
the compose surface; DCS data rights are **to be confirmed at point of use** — outside
this `@DECIDE`.

**`@DECIDE` (V4-D):** approve `vidyut-prakriya` (MIT code + MIT Dhātupāṭha, attribution
shown in-product) as the v4 forms data source, or reject and direct the fallback path.
A human rules on data-rights use — this brief only establishes that at least one
rights-clear candidate exists.

---

## 5 · V4-E — free→paid bridge (note only, no build)

The bridge already has its natural surface: the tray "Plugins (opt-in; off by default)"
submenu shipped in H1639. V4-E extends it with a pack-discovery entry ("Get more
packs…") where paid packs appear alongside the free plugin toggles, and with an
explicit-click offline-pack download flow reusing the same out-of-tree install
convention the free full-MW pack docs already use. Invariants hold unchanged: nothing
enters default Startup, no silent network, free toggles never degrade when paid packs
are absent. No build in this handoff; V4-E rides on v3 plugins and needs no ruling of
its own.

---

## 6 · Sequencing — what consumes this brief

1. The **V4-A ruling** unblocks V4-B and V4-C; its platform pick defines the 4.0.0
   slice (ROADMAP release table).
2. The **V4-D ruling** unblocks the forms workstream (4.x, second Apple platform
   window).
3. After both rulings, fan out per-stream execution handoffs against the checklists in
   §2/§3 — this brief is their scope document; nothing in it is implemented yet.

Both `@DECIDE` rows live in
[GTD_NEXT_ACTIONS.md](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md)
(added the same pass as this brief).

_Dr. Mārcis Gasūns_
