#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Offline fuzzy headword lookup (V3-2).

Opt-in only — **not** imported by default KeySwap AHK / install, and not loaded
by ``typing_check`` unless ``--plugin offline_fuzzy`` or
``KEYSWAP_PLUGINS=offline_fuzzy``.

Behaviour (over the active SLP1 wordlist — seed or ``KEYSWAP_WORDLIST``):

1. **Exact** match on query / optional normkey.
2. **Prefix** candidates (query is a prefix of a headword, or vice-versa for
   short queries).
3. **Edit distance** (Levenshtein) within a length window, first-char buckets.

Unique distance-1 (or single-prefix) hits are treated as soft ``found`` so the
HUD can show a near-match without pretending the index is a full morphology DB.

Run from repo root::

  python tools/KeySwap/plugins/offline_fuzzy/fuzzy_lookup.py rAm
  python tools/KeySwap/plugins/offline_fuzzy/fuzzy_lookup.py --max 5 rAma
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

PLUGIN_DIR = Path(__file__).resolve().parent
KEYSWAP_ROOT = PLUGIN_DIR.parent.parent
if str(KEYSWAP_ROOT) not in sys.path:
    sys.path.insert(0, str(KEYSWAP_ROOT))

from local_wordlist import get_wordlist, resolve_wordlist_path  # noqa: E402

MANIFEST_PATH = PLUGIN_DIR / "manifest.json"

# Soft caps keep full-MW (~200k) interactive without SQLite.
_DEFAULT_MAX_SUGGESTIONS = 5
_MAX_SCAN_CANDIDATES = 8000


@dataclass(frozen=True)
class FuzzyResult:
    """Result of an offline plugin lookup."""

    query: str
    found: bool
    match: str | None
    source: str
    status: str
    fuzzy_ready: bool = True
    suggestions: tuple[str, ...] = ()
    distance: int | None = None
    wordlist: str = ""

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["suggestions"] = list(self.suggestions)
        return d


def load_manifest() -> dict[str, Any]:
    """Load ``manifest.json`` (must keep ``never_autoload`` true)."""
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("never_autoload") is not True:
        raise RuntimeError(
            f"{MANIFEST_PATH}: never_autoload must be true for offline_fuzzy"
        )
    return data


def _max_edit_dist(n: int) -> int:
    if n <= 0:
        return 0
    if n <= 3:
        return 1
    if n <= 8:
        return 1
    return 2


def _levenshtein(a: str, b: str, *, max_dist: int) -> int:
    """Levenshtein distance with early abort when > max_dist."""
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > max_dist:
        return max_dist + 1
    if la == 0:
        return lb if lb <= max_dist else max_dist + 1
    if lb == 0:
        return la if la <= max_dist else max_dist + 1
    # Ensure a is shorter
    if la > lb:
        a, b = b, a
        la, lb = lb, la
    prev = list(range(la + 1))
    for j, cb in enumerate(b, 1):
        cur = [j] + [0] * la
        row_min = j
        for i, ca in enumerate(a, 1):
            cost = 0 if ca == cb else 1
            cur[i] = min(
                prev[i] + 1,  # deletion
                cur[i - 1] + 1,  # insertion
                prev[i - 1] + cost,  # substitution
            )
            if cur[i] < row_min:
                row_min = cur[i]
        if row_min > max_dist:
            return max_dist + 1
        prev = cur
    return prev[la]


@dataclass
class _WordIndex:
    """In-memory index over one wordlist path."""

    path: str
    words: frozenset[str]
    by_first: dict[str, tuple[str, ...]]
    sorted_words: tuple[str, ...]

    @classmethod
    def from_words(cls, path: str, words: frozenset[str]) -> "_WordIndex":
        buckets: dict[str, list[str]] = {}
        for w in words:
            if not w:
                continue
            buckets.setdefault(w[0], []).append(w)
        by_first = {k: tuple(sorted(v, key=lambda s: (len(s), s))) for k, v in buckets.items()}
        return cls(
            path=path,
            words=words,
            by_first=by_first,
            sorted_words=tuple(sorted(words)),
        )


@lru_cache(maxsize=8)
def _index_for(path_str: str) -> _WordIndex | None:
    words = get_wordlist(path_str)
    if words is None:
        return None
    return _WordIndex.from_words(path_str, words)


def clear_index_cache() -> None:
    """Drop indexes (tests / hot-reload)."""
    _index_for.cache_clear()


def _resolve_index(path: str | Path | None) -> _WordIndex | None:
    resolved = resolve_wordlist_path(path)
    if resolved is None:
        return None
    return _index_for(str(resolved.resolve()))


def _prefix_hits(index: _WordIndex, q: str, *, limit: int) -> list[str]:
    """Headwords that start with q (primary) or of which q is a near-prefix."""
    if not q:
        return []
    out: list[str] = []
    bucket = index.by_first.get(q[0], ())
    for w in bucket:
        if w.startswith(q) and w != q:
            out.append(w)
            if len(out) >= limit:
                break
    # Also: q longer than some short keys? rarely useful — skip.
    return out


def _edit_hits(
    index: _WordIndex,
    q: str,
    *,
    max_dist: int,
    limit: int,
    exclude: Iterable[str],
) -> list[tuple[int, str]]:
    """Ranked (distance, word) within max_dist."""
    if max_dist <= 0 or not q:
        return []
    excl = set(exclude)
    n = len(q)
    scored: list[tuple[int, str]] = []
    scanned = 0
    # Prefer same first char; if few, widen to all buckets of similar length.
    buckets: list[tuple[str, ...]] = []
    if q[0] in index.by_first:
        buckets.append(index.by_first[q[0]])
    # Neighbour first chars (SLP1 case-sensitive): include opposite case of first
    alt = q[0].swapcase()
    if alt != q[0] and alt in index.by_first:
        buckets.append(index.by_first[alt])

    for bucket in buckets:
        for w in bucket:
            if w in excl or w == q:
                continue
            if abs(len(w) - n) > max_dist:
                continue
            scanned += 1
            if scanned > _MAX_SCAN_CANDIDATES:
                break
            d = _levenshtein(q, w, max_dist=max_dist)
            if d <= max_dist:
                scored.append((d, w))
        if scanned > _MAX_SCAN_CANDIDATES:
            break

    scored.sort(key=lambda t: (t[0], len(t[1]), t[1]))
    # Dedup preserving order
    seen: set[str] = set()
    out: list[tuple[int, str]] = []
    for d, w in scored:
        if w in seen:
            continue
        seen.add(w)
        out.append((d, w))
        if len(out) >= limit:
            break
    return out


def lookup(
    slp1_or_key: str,
    *,
    path: str | Path | None = None,
    normkey: str = "",
    max_suggestions: int = _DEFAULT_MAX_SUGGESTIONS,
    max_dist: int | None = None,
) -> FuzzyResult:
    """Exact + fuzzy headword check against the local wordlist.

    Parameters
    ----------
    slp1_or_key:
        Headword key (SLP1 preferred; caller may pre-normalize).
    path:
        Optional wordlist override (same as core ``local_wordlist``).
    normkey:
        Optional dalnorm key also checked for exact match.
    max_suggestions:
        Cap on returned near-matches (default 5).
    max_dist:
        Override Levenshtein budget (default scales with query length).
    """
    q = (slp1_or_key or "").strip()
    nk = (normkey or "").strip()
    wl_label = ""
    resolved = resolve_wordlist_path(path)
    if resolved is not None:
        wl_label = resolved.name

    if not q and not nk:
        return FuzzyResult(
            query=q,
            found=False,
            match=None,
            source="offline_fuzzy",
            status="empty-query",
            fuzzy_ready=True,
            wordlist=wl_label,
        )

    index = _resolve_index(path)
    if index is None:
        return FuzzyResult(
            query=q or nk,
            found=False,
            match=None,
            source="offline_fuzzy",
            status="no-wordlist",
            fuzzy_ready=False,
            wordlist=wl_label,
        )

    # --- exact ---
    for cand in (q, nk):
        if cand and cand in index.words:
            return FuzzyResult(
                query=q or cand,
                found=True,
                match=cand,
                source="offline_fuzzy+exact",
                status="exact",
                fuzzy_ready=True,
                suggestions=(),
                distance=0,
                wordlist=wl_label,
            )

    probe = q or nk
    limit = max(1, max_suggestions)
    dist_cap = max_dist if max_dist is not None else _max_edit_dist(len(probe))

    prefixes = _prefix_hits(index, probe, limit=limit)
    edits = _edit_hits(
        index, probe, max_dist=dist_cap, limit=limit, exclude=prefixes
    )

    # Merge: unique prefix first, then by edit distance
    merged: list[tuple[int, str]] = []
    seen: set[str] = set()
    for w in prefixes:
        if w not in seen:
            seen.add(w)
            # prefix distance as 0-ish but tag via status later
            merged.append((0, w))
    for d, w in edits:
        if w not in seen:
            seen.add(w)
            merged.append((d, w))
    merged = merged[:limit]
    suggestions = tuple(w for _, w in merged)

    if not suggestions:
        return FuzzyResult(
            query=probe,
            found=False,
            match=None,
            source="offline_fuzzy",
            status="not-found",
            fuzzy_ready=True,
            suggestions=(),
            distance=None,
            wordlist=wl_label,
        )

    # Unique soft match: single prefix OR single edit at dist 1
    if len(suggestions) == 1:
        only = suggestions[0]
        d = 0 if only in prefixes else (edits[0][0] if edits else 1)
        soft_ok = only in prefixes or d <= 1
        if soft_ok:
            return FuzzyResult(
                query=probe,
                found=True,
                match=only,
                source="offline_fuzzy+fuzzy-unique",
                status="fuzzy-unique",
                fuzzy_ready=True,
                suggestions=suggestions,
                distance=d if only not in prefixes else 0,
                wordlist=wl_label,
            )

    best_d = merged[0][0]
    return FuzzyResult(
        query=probe,
        found=False,
        match=None,
        source="offline_fuzzy+fuzzy-multi",
        status="fuzzy-multi",
        fuzzy_ready=True,
        suggestions=suggestions,
        distance=best_d,
        wordlist=wl_label,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI: ``fuzzy_lookup.py [--max N] [--wordlist PATH] <key>``."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("key", help="SLP1 (or pre-normalized) headword probe")
    ap.add_argument("--max", type=int, default=_DEFAULT_MAX_SUGGESTIONS)
    ap.add_argument("--wordlist", default=None, help="override local wordlist path")
    ap.add_argument("--max-dist", type=int, default=None)
    ap.add_argument("--json", action="store_true", help="JSON only (default)")
    args = ap.parse_args(argv)

    load_manifest()
    result = lookup(
        args.key,
        path=args.wordlist,
        max_suggestions=args.max,
        max_dist=args.max_dist,
    )
    print(json.dumps(result.as_dict(), ensure_ascii=False))
    if result.found:
        return 0
    if result.suggestions:
        return 1
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
