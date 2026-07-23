# KeySwap **2.2** — IAST typing + Cologne Simple Search

_Created: 23-07-2026 · Last updated: 23-07-2026_  
_Version: [2.2.0](VERSION)_

Type Sanskrit **romanization** (IAST / ISO-style) with a shared config language
across **Windows, iPhone, Mac, and the browser**. Convert **HK / ITRANS /
Velthuis** paste, **IAST ↔ Devanāgarī**, and prepare **Cologne Simple Search**
queries (scheme → SLP1 → `dalnorm` key → open/API).

```text
n  =  =  =           →  ṇ → ṅ → ñ       (cycle)
aa ii sh             →  ā  ī  ś         (smart digraphs)
saMskRta --from hk   →  saṃskṛta        (scheme bridge 2.1)
long-press n         →  menu n ṇ ṅ ñ    (iOS / PWA)
```

Not part of the PyPI/npm package API. Web survey: [IMPROVEMENTS_FROM_WEB.md](IMPROVEMENTS_FROM_WEB.md).

---

## What’s in 2.2 (Cologne Simple Search)

| Feature | Detail |
|---------|--------|
| **`cologne_search.py`** | Multi-scheme → SLP1 → **dalnorm** (port of csl-apidev `Dalnorm::normalize`) |
| **Cologne URLs** | Builds [Simple Search](https://sanskrit-lexicon.uni-koeln.de/simple/) UI + getword_list API links |
| **`--open` / `--api`** | Browser jump or live headword list |
| **AHK Ctrl+Alt+C** | Clipboard → Cologne Simple Search |
| **PWA “Cologne”** | Opens Simple Search with scheme-aware `input` + `key` |
| **Mac menu** | Clipboard → Cologne Simple Search |

### 2.1 (still included)

scheme_bridge · convert `--from` · Keyman guard · allowlist · HUD · MSKLC docs · packaging checklists

### 2.0 (still included)

smart digraphs · long-press · PWA · profiles · AHK cycle/smart/deadkey

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

# Cologne Simple Search (dalnorm keys + open/API)
python tools/KeySwap/cologne_search.py "rāma" --print-keys
python tools/KeySwap/cologne_search.py --from hk "ziva" --dict mw --open
python tools/KeySwap/cologne_search.py "śiva" --api --dict mw
python tools/KeySwap/test_cologne_search.py
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
  VERSION  (2.2.0)
  cologne_search.py     # Cologne Simple Search prep (dalnorm + URLs)
  scheme_bridge.py      # HK/ITRANS/Velthuis → IAST
  convert_bridge.py     # + --from schemes
  smart_input.py
  cycle_engine.py
  layouts/msklc/        # classroom / MSKLC
  packaging/            # App Store + PE policy
  windows/              # AHK + allowlist + Cologne hotkey
  pwa/                  # offline pad + Cologne button
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
