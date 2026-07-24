#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Network autocomplete suggestions (V3-7) — Cologne API after offline fuzzy.

Opt-in only — **not** imported by default KeySwap AHK / install, and not loaded
by ``typing_check`` unless ``--plugin network_autocomplete`` or
``KEYSWAP_PLUGINS=network_autocomplete``.

Policy (hard):

1. Prefer offline fuzzy (V3-2) when confident (exact / fuzzy-unique).
2. Hit the network only when offline is insufficient (not-found, multi,
   missing wordlist) **or** when ``force_network=True``.
3. Short timeout + rate-limit friendly HUD errors; never pretend offline
   succeeded when only the network failed.

Run from repo root::

  python tools/KeySwap/plugins/network_autocomplete/autocomplete.py rAm
  python tools/KeySwap/plugins/network_autocomplete/autocomplete.py --json kfzR
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent
KEYSWAP_ROOT = PLUGIN_DIR.parent.parent
if str(KEYSWAP_ROOT) not in sys.path:
    sys.path.insert(0, str(KEYSWAP_ROOT))

from cologne_search import (  # noqa: E402
    CologneQuery,
    fetch_results,
    format_api_error,
    prepare,
)

MANIFEST_PATH = PLUGIN_DIR / "manifest.json"

# Autocomplete must stay snappy; full typing_check default is 12s.
_DEFAULT_TIMEOUT = 5.0
_DEFAULT_MAX = 8

# Offline statuses that skip network (confident local answer).
_OFFLINE_CONFIDENT = frozenset({"exact", "fuzzy-unique"})


@dataclass(frozen=True)
class AutocompleteResult:
    """Result of offline-first + optional network autocomplete."""

    query: str
    found: bool
    match: str | None
    source: str
    status: str
    suggestions: tuple[str, ...] = ()
    offline_status: str = ""
    network_used: bool = False
    error: str = ""
    slp1: str = ""
    normkey: str = ""

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["suggestions"] = list(self.suggestions)
        return d


def load_manifest() -> dict[str, Any]:
    """Load ``manifest.json`` (must keep ``never_autoload`` true)."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("never_autoload") is not True:
        raise RuntimeError(
            f"{MANIFEST_PATH}: never_autoload must be true for network_autocomplete"
        )
    if data.get("id") != "network_autocomplete":
        raise RuntimeError(f"{MANIFEST_PATH}: id must be network_autocomplete")
    return data


def offline_is_confident(status: str) -> bool:
    """True when network should not run (local answer is good enough)."""
    return status in _OFFLINE_CONFIDENT


def suggest_from_network(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    timeout: float = _DEFAULT_TIMEOUT,
    max_suggestions: int = _DEFAULT_MAX,
    fetch=None,
) -> AutocompleteResult:
    """Query Cologne Simple Search for autocomplete candidates (network only).

    ``fetch`` is injectable for tests (signature like ``fetch_results``).
    """
    q: CologneQuery = prepare(text, scheme=scheme, dict_code=dict_code, output="iast")
    if not (text or "").strip():
        return AutocompleteResult(
            query="",
            found=False,
            match=None,
            source="network_autocomplete",
            status="empty-query",
            slp1=q.slp1,
            normkey=q.normkey,
        )

    do_fetch = fetch if fetch is not None else fetch_results
    try:
        hits = do_fetch(q, timeout=timeout)
    except Exception as e:  # noqa: BLE001 — surface to HUD
        return AutocompleteResult(
            query=text.strip(),
            found=False,
            match=None,
            source="network_autocomplete",
            status="network-error",
            network_used=True,
            error=format_api_error(e),
            slp1=q.slp1,
            normkey=q.normkey,
        )

    top = tuple(str(h) for h in (hits or [])[: max(1, max_suggestions)])
    if not top:
        return AutocompleteResult(
            query=text.strip(),
            found=False,
            match=None,
            source="network_autocomplete",
            status="not-found",
            suggestions=(),
            network_used=True,
            slp1=q.slp1,
            normkey=q.normkey,
        )

    # Single hit → treat as soft known for HUD (same as API path).
    found = True
    match = top[0] if len(top) == 1 else None
    status = "network-unique" if len(top) == 1 else "network-multi"
    return AutocompleteResult(
        query=text.strip(),
        found=found,
        match=match,
        source="network_autocomplete",
        status=status,
        suggestions=top,
        network_used=True,
        slp1=q.slp1,
        normkey=q.normkey,
    )


def suggest(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    timeout: float = _DEFAULT_TIMEOUT,
    max_suggestions: int = _DEFAULT_MAX,
    wordlist: str | Path | None = None,
    force_network: bool = False,
    fetch=None,
) -> AutocompleteResult:
    """Offline fuzzy first; network only when offline is not confident.

    Parameters
    ----------
    force_network:
        Skip the offline pre-pass (tests / diagnostics only).
    fetch:
        Injectable network fetch for unit tests.
    """
    probe = (text or "").strip()
    if not probe:
        return AutocompleteResult(
            query="",
            found=False,
            match=None,
            source="network_autocomplete",
            status="empty-query",
        )

    offline_status = ""
    if not force_network:
        # Lazy import: keep network plugin import free of fuzzy until needed.
        from plugins.offline_fuzzy.fuzzy_lookup import (  # noqa: PLC0415
            lookup as fuzzy_lookup,
        )

        q_prep = prepare(probe, scheme=scheme, dict_code=dict_code, output="iast")
        fr = fuzzy_lookup(
            q_prep.slp1,
            path=wordlist,
            normkey=q_prep.normkey,
            max_suggestions=max_suggestions,
        )
        offline_status = fr.status

        if fr.status == "empty-query":
            return AutocompleteResult(
                query=probe,
                found=False,
                match=None,
                source="offline_fuzzy",
                status="empty-query",
                offline_status=offline_status,
                slp1=q_prep.slp1,
                normkey=q_prep.normkey,
            )

        if offline_is_confident(fr.status):
            top: list[str] = []
            if fr.match:
                top.append(fr.match)
            for s in fr.suggestions:
                if s not in top:
                    top.append(s)
            return AutocompleteResult(
                query=probe,
                found=True,
                match=fr.match,
                source="offline_fuzzy",
                status=fr.status,
                suggestions=tuple(top[:max_suggestions]),
                offline_status=offline_status,
                network_used=False,
                slp1=q_prep.slp1,
                normkey=q_prep.normkey,
            )

        # fuzzy-multi: keep local near-matches; do not burn network for FP noise
        # unless force_network. Operator can re-query without offline.
        if fr.status == "fuzzy-multi" and fr.suggestions:
            return AutocompleteResult(
                query=probe,
                found=False,
                match=None,
                source="offline_fuzzy",
                status=fr.status,
                suggestions=tuple(fr.suggestions[:max_suggestions]),
                offline_status=offline_status,
                network_used=False,
                slp1=q_prep.slp1,
                normkey=q_prep.normkey,
            )

    net = suggest_from_network(
        probe,
        scheme=scheme,
        dict_code=dict_code,
        timeout=timeout,
        max_suggestions=max_suggestions,
        fetch=fetch,
    )
    # Preserve offline status for HUD/debug when we escalated.
    return AutocompleteResult(
        query=net.query,
        found=net.found,
        match=net.match,
        source=net.source,
        status=net.status,
        suggestions=net.suggestions,
        offline_status=offline_status or net.offline_status,
        network_used=net.network_used,
        error=net.error,
        slp1=net.slp1,
        normkey=net.normkey,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI: ``autocomplete.py [--force-network] [--max N] <query>``."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("query", help="typed probe (any scheme; default auto)")
    ap.add_argument("--from", dest="frm", default="auto")
    ap.add_argument("--dict", default="mw")
    ap.add_argument("--max", type=int, default=_DEFAULT_MAX)
    ap.add_argument("--timeout", type=float, default=_DEFAULT_TIMEOUT)
    ap.add_argument("--wordlist", default=None)
    ap.add_argument(
        "--force-network",
        action="store_true",
        help="skip offline pre-pass (diagnostics)",
    )
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args(argv)

    load_manifest()
    result = suggest(
        args.query,
        scheme=args.frm,
        dict_code=args.dict,
        timeout=args.timeout,
        max_suggestions=args.max,
        wordlist=args.wordlist,
        force_network=args.force_network,
    )
    print(json.dumps(result.as_dict(), ensure_ascii=False))
    if result.found:
        return 0
    if result.suggestions:
        return 1
    if result.error:
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
