#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Optional DCS-2026 lemma frequencies for KeySwap headword checks.

Source table: ``data/dcs_freq.txt`` — same ``slp1_key  count`` format as
csl-apidev ``simple-search/wf1/wf.txt`` (DCS lemmas.csv merge over legacy wf0).

Opt-in only (default off):

  KEYSWAP_DCS_FREQ=1
  typing_check.py --dcs-freq
  cologne_search.py --api --dcs-freq

Not a full corpus browser — token counts for ranking / HUD annotation.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_DCS_FREQ = ROOT / "data" / "dcs_freq.txt"
ENV_DCS_FREQ = "KEYSWAP_DCS_FREQ"
ENV_DCS_PATH = "KEYSWAP_DCS_FREQ_PATH"


def dcs_freq_enabled(flag: bool | None = None) -> bool:
    """Resolve whether DCS frequency mode is on.

    Explicit ``flag`` wins; else env ``KEYSWAP_DCS_FREQ`` in 1/true/yes/on.
    """
    if flag is not None:
        return bool(flag)
    v = os.environ.get(ENV_DCS_FREQ, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def resolve_dcs_freq_path(path: str | Path | None = None) -> Path | None:
    if path is not None:
        p = Path(path).expanduser()
        return p if p.is_file() else None
    env = os.environ.get(ENV_DCS_PATH, "").strip()
    if env:
        p = Path(env).expanduser()
        return p if p.is_file() else None
    if DEFAULT_DCS_FREQ.is_file():
        return DEFAULT_DCS_FREQ
    # Sibling csl-apidev (dev machines)
    sibling = ROOT.parents[2] / "csl-apidev" / "simple-search" / "wf1" / "wf.txt"
    if sibling.is_file():
        return sibling
    return None


def load_dcs_freq(path: str | Path) -> dict[str, int]:
    """Load ``slp1_key  count`` lines (BOM-safe; ``#`` comments skipped)."""
    text = Path(path).read_text(encoding="utf-8-sig")
    out: dict[str, int] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split()
        if len(parts) < 2:
            continue
        key, raw = parts[0], parts[-1]
        try:
            out[key] = int(raw)
        except ValueError:
            continue
    return out


@lru_cache(maxsize=4)
def _cached(path_str: str) -> frozenset[tuple[str, int]]:
    d = load_dcs_freq(path_str)
    return frozenset(d.items())


def get_dcs_freq(path: str | Path | None = None) -> dict[str, int] | None:
    resolved = resolve_dcs_freq_path(path)
    if resolved is None:
        return None
    return dict(_cached(str(resolved.resolve())))


def clear_cache() -> None:
    _cached.cache_clear()


def freq_of(
    slp1: str,
    normkey: str = "",
    *,
    path: str | Path | None = None,
    table: dict[str, int] | None = None,
) -> int | None:
    """Return DCS-style token count for a key, or None if table/key missing."""
    tab = table if table is not None else get_dcs_freq(path)
    if tab is None:
        return None
    for c in (slp1, normkey):
        c = (c or "").strip()
        if c and c in tab:
            return tab[c]
    return None


def rank_hits(
    hits: list[str],
    *,
    path: str | Path | None = None,
    table: dict[str, int] | None = None,
) -> list[tuple[str, int]]:
    """Re-order headword strings by DCS frequency (desc); unknown → -1."""
    tab = table if table is not None else get_dcs_freq(path)
    if tab is None:
        return [(h, -1) for h in hits]
    scored: list[tuple[str, int]] = []
    for h in hits:
        # hits may be IAST; caller should pass SLP1 when possible.
        # Try raw form first (API often returns IAST for output=iast).
        n = tab.get(h)
        if n is None:
            n = -1
        scored.append((h, n))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


def rank_slp1_hits(
    hits_slp1: list[str],
    *,
    path: str | Path | None = None,
    table: dict[str, int] | None = None,
) -> list[tuple[str, int]]:
    """Rank a list of SLP1 keys by DCS frequency (desc)."""
    tab = table if table is not None else get_dcs_freq(path)
    if tab is None:
        return [(h, -1) for h in hits_slp1]
    scored = [(h, tab.get(h, -1)) for h in hits_slp1]
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored
