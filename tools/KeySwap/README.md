# KeySwap **2.1** — IAST diacritic toolkit

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Version: [2.1.0](VERSION)_

Type Sanskrit **romanization** (IAST / ISO-style) with a shared config language
across **Windows, iPhone, Mac, and the browser**. Convert **HK / ITRANS /
Velthuis** paste and **IAST ↔ Devanāgarī** via this repo’s library.

```text
n  =  =  =           →  ṇ → ṅ → ñ       (cycle)
aa ii sh             →  ā  ī  ś         (smart digraphs)
saMskRta --from hk   →  saṃskṛta        (scheme bridge 2.1)
long-press n         →  menu n ṇ ṅ ñ    (iOS / PWA)
```

Not part of the PyPI/npm package API. Web survey: [IMPROVEMENTS_FROM_WEB.md](IMPROVEMENTS_FROM_WEB.md).

---

## What’s in 2.1 (backlog completion)

| Feature | Detail |
|---------|--------|
| **scheme_bridge** | Harvard-Kyoto, ITRANS, Velthuis → IAST (longest-token) |
| **convert `--from`** | `auto\|hk\|itrans\|velthuis\|iast\|deva\|slp1` → `iast\|deva\|slp1` |
| **Keyman guard** | AHK warns if Keyman processes are running |
| **Allowlist** | Optional `windows/allowlist.txt` — only listed apps |
| **Teaching HUD** | AHK ToolTip (F7) + PWA status line |
| **MSKLC path** | [layouts/msklc/](layouts/msklc/) chords + classroom docs |
| **Packaging docs** | [packaging/APP_STORE.md](packaging/APP_STORE.md), [VENDOR_PE.md](packaging/VENDOR_PE.md) |
| **Mac clipboard convert** | Menu: clipboard → IAST / Devanāgarī via Python |

All **2.0** features remain (smart, long-press, PWA, profiles, AHK modes).

---

## What to run

| Platform | Recommended |
|----------|-------------|
| **Windows** | [`windows/KeySwap.ahk`](windows/KeySwap.ahk) |
| **iPhone** | [`apple/`](apple/) keyboard |
| **Mac** | [`apple/macos/`](apple/macos/) menu bar |
| **Browser** | [`pwa/`](pwa/) |
| **CLI convert** | `convert_bridge.py` / `scheme_bridge.py` |
| **Legacy PE** | [`vendor/`](vendor/) optional only |

---

## CLI

```bash
# Validate + unit tests
python tools/KeySwap/validate_configs.py
python tools/KeySwap/test_cycle_engine.py
python tools/KeySwap/test_smart_input.py
python tools/KeySwap/test_scheme_bridge.py

# Schemes → IAST
python tools/KeySwap/scheme_bridge.py --from hk "saMskRta"
python tools/KeySwap/scheme_bridge.py --from itrans "raama"
python tools/KeySwap/scheme_bridge.py --from velthuis "k.r.s.na"
python tools/KeySwap/scheme_bridge.py --from auto "saMskRta"

# To Devanāgarī / SLP1 (via sanskrit-util)
python tools/KeySwap/convert_bridge.py --from hk --to deva "rAma"
python tools/KeySwap/convert_bridge.py --from itrans --to iast "shiva"
python tools/KeySwap/convert_bridge.py --to slp1 "śiva"
```

---

## Windows AHK (2.1)

| Key | Action |
|-----|--------|
| `=` | Cycle |
| F6 | Reload config + allowlist |
| F7 | Toggle teaching HUD |
| Ctrl+Alt+= | Clipboard → Devanāgarī |
| Ctrl+Alt+I / H | Clipboard auto-scheme → IAST |

Copy [`windows/allowlist.example.txt`](windows/allowlist.example.txt) → `allowlist.txt` to restrict apps.

---

## Profiles

`iast-classic` (default) · `iso15919` · `vedic-draft` · `vedic-svara` · `personal-legacy`

---

## Layout

```text
KeySwap/
  VERSION  (2.1.0)
  scheme_bridge.py      # HK/ITRANS/Velthuis → IAST
  convert_bridge.py     # + --from schemes
  smart_input.py
  cycle_engine.py
  layouts/msklc/        # classroom / MSKLC
  packaging/            # App Store + PE policy
  windows/              # AHK + allowlist
  pwa/                  # offline pad + scheme → IAST
  apple/                # iOS + Mac
  vendor/               # optional 1.x PE
```

---

## Security

Hooks can see keystrokes. Prefer [layouts/](layouts/) on shared labs. Do not ship
`vendor/*.exe` in PyPI/npm.

## Credits

Cycle UX: Yes Vedanta Keyswap + Lexilogos. Open 2.x toolkit: sanskrit-util (MIT).

_Dr. Mārcis Gasūns_
