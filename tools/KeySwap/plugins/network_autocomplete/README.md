# Plugin: `network_autocomplete` (V3-7)

_Created: 24-07-2026 · Last updated: 05-09-2026_

Optional **network autocomplete** over the Cologne Simple Search API, gated
**after** the offline fuzzy index (V3-2). See
[KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md).

## Why not core?

Always-on network autocomplete was an explicit **2.x skip**: latency, privacy,
and false confidence. V3 reopens it only as an **opt-in** plugin that still
prefers the local index first.

## Enable

```bash
# Implies offline_fuzzy pre-pass automatically
python tools/KeySwap/typing_check.py --plugin network_autocomplete --hud "rAm"

# Env
set KEYSWAP_PLUGINS=network_autocomplete
python tools/KeySwap/typing_check.py --hud "rAm"
```

Direct module smoke:

```bash
python tools/KeySwap/plugins/network_autocomplete/autocomplete.py rAm
# force live API (skip offline)
python tools/KeySwap/plugins/network_autocomplete/autocomplete.py --force-network rAm
```

## Cascade

| Offline status | Network? | Result source |
|----------------|----------|---------------|
| `exact` / `fuzzy-unique` | **No** | `offline_fuzzy` |
| `fuzzy-multi` | **No** (local near list kept) | `offline_fuzzy` |
| `not-found` / `no-wordlist` | **Yes** (opt-in only) | `network_autocomplete` |
| (force-network) | **Yes** | `network_autocomplete` |

## Do not

- Import this package from `windows/KeySwap.ahk` or `install-windows.ps1`.  
- Enable “always-on” without a user opt-in path.  
- Treat multi-hit API lists as morphology-correct forms.

_Dr. Mārcis Gasūns_
