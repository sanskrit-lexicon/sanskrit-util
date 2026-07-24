#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline fuzzy headword lookup (V3-2 scaffold).

This module is **not** imported by the default KeySwap AHK path or by
``typing_check`` / ``cologne_search`` at import time. Call it only when the
user opts into the plugin (env ``KEYSWAP_PLUGINS`` / future ``--plugin``).

Scaffold behaviour (H1581):
  - Exact match against the core seed wordlist via ``local_wordlist``
  - Fuzzy / full MW SQLite index: **not implemented** (returns a clear status)

Run from repo root::

  python -c "import sys; sys.path.insert(0, 'tools/KeySwap'); from plugins.offline_fuzzy.fuzzy_lookup import lookup; print(lookup('rama'))"
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PLUGIN_DIR = Path(__file__).resolve().parent
KEYSWAP_ROOT = PLUGIN_DIR.parent.parent
if str(KEYSWAP_ROOT) not in sys.path:
    sys.path.insert(0, str(KEYSWAP_ROOT))

# Core seed list only — does not pull a multi-MB pack.
from local_wordlist import get_wordlist  # noqa: E402

MANIFEST_PATH = PLUGIN_DIR / "manifest.json"


@dataclass(frozen=True)
class FuzzyResult:
    """Result of an offline plugin lookup."""

    query: str
    found: bool
    match: str | None
    source: str
    status: str
    fuzzy_ready: bool = False

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_manifest() -> dict[str, Any]:
    """Load ``manifest.json`` (must keep ``never_autoload`` true)."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("never_autoload") is not True:
        raise RuntimeError(
            f"{MANIFEST_PATH}: never_autoload must be true for offline_fuzzy"
        )
    return data


def lookup(slp1_or_key: str, *, path: str | Path | None = None) -> FuzzyResult:
    """Exact seed-list check; fuzzy index deferred.

    Parameters
    ----------
    slp1_or_key:
        Headword key (SLP1-style preferred; caller may pre-normalize).
    path:
        Optional wordlist override (same as core ``local_wordlist``).
    """
    q = (slp1_or_key or "").strip()
    if not q:
        return FuzzyResult(
            query=q,
            found=False,
            match=None,
            source="offline_fuzzy",
            status="empty-query",
            fuzzy_ready=False,
        )

    words = get_wordlist(path)
    if words is None:
        return FuzzyResult(
            query=q,
            found=False,
            match=None,
            source="offline_fuzzy",
            status="no-wordlist",
            fuzzy_ready=False,
        )

    if q in words:
        return FuzzyResult(
            query=q,
            found=True,
            match=q,
            source="offline_fuzzy+seed-exact",
            status="exact",
            fuzzy_ready=False,
        )

    # Future: prefix / edit-distance over a full index pack.
    return FuzzyResult(
        query=q,
        found=False,
        match=None,
        source="offline_fuzzy",
        status="not-in-seed; fuzzy-index-not-built",
        fuzzy_ready=False,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI smoke: ``python fuzzy_lookup.py <key>``."""
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        print("Usage: fuzzy_lookup.py <slp1-key>", file=sys.stderr)
        return 2
    load_manifest()  # fail loud if misconfigured
    result = lookup(args[0])
    print(json.dumps(result.as_dict(), ensure_ascii=False))
    return 0 if result.found else 1


if __name__ == "__main__":
    raise SystemExit(main())
