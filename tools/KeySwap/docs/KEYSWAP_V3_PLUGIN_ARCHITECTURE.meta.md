# Metadoc — KEYSWAP_V3_PLUGIN_ARCHITECTURE.md

_Created: 24-07-2026 · Last updated: 24-07-2026_

## Purpose

Companion record for the KeySwap v3 plugin/sibling architecture memo — the hard
boundary that keeps the typing shell light while former 2.x “explicit skips”
return only as opt-in packs.

## Audience

Agents extending KeySwap; humans deciding whether a feature is core vs plugin
vs sibling app.

## Provenance

| Field | Value |
|-------|--------|
| Subject | [KEYSWAP_V3_PLUGIN_ARCHITECTURE.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/docs/KEYSWAP_V3_PLUGIN_ARCHITECTURE.md) |
| Handoffs | [H1581](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1581-Sonnet_sanskrit-util_keyswap-v3-former-skips-heavy-wave_24.07.26.md) (design + V3-2), [H1583](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1583-Sonnet_sanskrit-util_keyswap-v3-7-network-autocomplete_24.07.26.md) (V3-7) |
| Model (this metadoc) | Grok 4.5 (`grok-4.5`) |

## Ranked improvement backlog

1. Document future tray `plugins.ini` under `%APPDATA%` when that lands.  
2. Add a third plugin only after ROADMAP V3-1/3–6 pick a concrete pack.  
3. Sibling V3-8 compose-companion design memo (parked).

## Limitations

- Discovery is CLI/env only (no tray toggle yet).  
- No SQLite pack vendored; full MW via `KEYSWAP_WORDLIST` opt-in path.  
- Network path depends on Cologne uptime/rate limits.

## Related docs

- [ROADMAP_KEYSWAP_V2_V3.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/ROADMAP_KEYSWAP_V2_V3.md)  
- [plugins/README.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/plugins/README.md)  
- [SIMILARS_COMPARISON.md](https://github.com/sanskrit-lexicon/sanskrit-util/blob/main/tools/KeySwap/SIMILARS_COMPARISON.md)

## Revision history

| Date | Change |
|------|--------|
| 24-07-2026 | Metadoc created during `/artifact-propagate` for V3-7 ship (H1583 / v0.8.9) |

_Dr. Mārcis Gasūns_
