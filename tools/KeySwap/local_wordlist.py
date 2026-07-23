#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local SLP1 headword set for offline typing_check (SpellCheck-file alternative).

Light alternative to the live Cologne Simple Search API — **not** a full
SanskritSpellCheck detector stack. A plain UTF-8 wordlist (one SLP1 key per
line, MW key1 style) is enough for ✓/✗ existence checks while offline.

Default path: ``data/local_headwords.txt`` next to this package.
Override with env ``KEYSWAP_WORDLIST`` or an explicit path argument.

Expand the seed list:

  python tools/KeySwap/build_local_wordlist.py --from-spellcheck
  python tools/KeySwap/build_local_wordlist.py --from-file path/to/MW-unique-key1.txt
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_WORDLIST = ROOT / "data" / "local_headwords.txt"
ENV_WORDLIST = "KEYSWAP_WORDLIST"


def resolve_wordlist_path(path: str | Path | None = None) -> Path | None:
    """Resolve the wordlist path; return None if nothing usable is configured."""
    if path is not None:
        p = Path(path).expanduser()
        return p if p.is_file() else None
    env = os.environ.get(ENV_WORDLIST, "").strip()
    if env:
        p = Path(env).expanduser()
        return p if p.is_file() else None
    if DEFAULT_WORDLIST.is_file():
        return DEFAULT_WORDLIST
    return None


def load_wordlist(path: str | Path) -> frozenset[str]:
    """Load SLP1 keys from a text file (BOM-safe; ``#`` comments skipped)."""
    p = Path(path)
    text = p.read_text(encoding="utf-8-sig")
    keys: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # Allow "key  note" / "key\tcount" rows from some exports
        key = s.split()[0].split("\t")[0].strip()
        if key:
            keys.add(key)
    return frozenset(keys)


@lru_cache(maxsize=8)
def _cached_load(path_str: str) -> frozenset[str]:
    return load_wordlist(path_str)


def get_wordlist(path: str | Path | None = None) -> frozenset[str] | None:
    """Return the loaded set, or None if no file is available."""
    resolved = resolve_wordlist_path(path)
    if resolved is None:
        return None
    return _cached_load(str(resolved.resolve()))


def clear_cache() -> None:
    """Drop loaded wordlists (tests / hot-reload)."""
    _cached_load.cache_clear()


def lookup(
    slp1: str,
    normkey: str = "",
    *,
    path: str | Path | None = None,
    wordset: frozenset[str] | None = None,
) -> bool | None:
    """True/False if a local set is available; None if no wordlist found.

    Matches exact SLP1 and dalnorm keys (and the raw query if it looks SLP1).
    """
    ws = wordset if wordset is not None else get_wordlist(path)
    if ws is None:
        return None
    candidates = []
    for c in (slp1, normkey):
        c = (c or "").strip()
        if c:
            candidates.append(c)
    return any(c in ws for c in candidates)


def wordlist_label(path: str | Path | None = None) -> str:
    """Short path label for HUD (basename only)."""
    resolved = resolve_wordlist_path(path)
    if resolved is None:
        return "local"
    return resolved.name
