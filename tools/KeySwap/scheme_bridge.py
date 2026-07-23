#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap 2.1 — ASCII scheme bridge (Harvard-Kyoto, ITRANS, Velthuis → IAST).

Longest-token-first replacement (same discipline as to_slp1). Classical Sanskrit
focus; not a full multi-script Aksharamukha substitute.

Usage:
  python scheme_bridge.py --from hk "saMskRta"
  python scheme_bridge.py --from itrans "sa.nskRRitam"
  python scheme_bridge.py --from velthuis "sa.msk.rta"
  python scheme_bridge.py --from auto "saMskRta"   # heuristic
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from typing import Iterable

__all__ = [
    "hk_to_iast",
    "itrans_to_iast",
    "velthuis_to_iast",
    "scheme_to_iast",
    "detect_scheme",
    "SCHEMES",
]

SCHEMES = ("hk", "itrans", "velthuis", "iast", "auto")


def _nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def _apply_pairs(text: str, pairs: list[tuple[str, str]]) -> str:
    """Left-to-right longest-match over sorted pairs (longest key first)."""
    pairs = sorted(pairs, key=lambda kv: (-len(kv[0]), kv[0]))
    # Build trie-less scanner
    out: list[str] = []
    i = 0
    n = len(text)
    keys = [p[0] for p in pairs]
    amap = {a: b for a, b in pairs}
    max_len = max(len(k) for k in keys) if keys else 1
    while i < n:
        matched = False
        for L in range(min(max_len, n - i), 0, -1):
            chunk = text[i : i + L]
            if chunk in amap:
                out.append(amap[chunk])
                i += L
                matched = True
                break
        if not matched:
            out.append(text[i])
            i += 1
    return _nfc("".join(out))


# --- Harvard-Kyoto → IAST -------------------------------------------------
# https://en.wikipedia.org/wiki/Harvard-Kyoto
_HK_PAIRS: list[tuple[str, str]] = [
    # longest first will be enforced by _apply_pairs
    ("lRR", "ḹ"),
    ("lR", "ḷ"),
    ("RR", "ṝ"),
    ("R", "ṛ"),
    ("A", "ā"),
    ("I", "ī"),
    ("U", "ū"),
    ("ai", "ai"),
    ("au", "au"),
    ("Kh", "kh"),  # keep case variants for aspirates as plain
    ("Gh", "gh"),
    ("Ch", "ch"),
    ("Jh", "jh"),
    ("Th", "ṭh"),
    ("Dh", "ḍh"),
    ("th", "th"),
    ("dh", "dh"),
    ("kh", "kh"),
    ("gh", "gh"),
    ("ch", "ch"),
    ("jh", "jh"),
    ("ph", "ph"),
    ("bh", "bh"),
    ("T", "ṭ"),
    ("D", "ḍ"),
    ("N", "ṇ"),
    ("G", "ṅ"),
    ("J", "ñ"),
    ("z", "ś"),
    ("S", "ṣ"),
    ("M", "ṃ"),
    ("H", "ḥ"),
]


def hk_to_iast(text: str) -> str:
    return _apply_pairs(text, _HK_PAIRS)


# --- ITRANS → IAST --------------------------------------------------------
# Common ITRANS (Chopde-style) subset for Sanskrit romanization.
_ITRANS_PAIRS: list[tuple[str, str]] = [
    ("RRI", "ṝ"),
    ("RRi", "ṛ"),
    ("LLi", "ḷ"),
    ("LLI", "ḹ"),
    ("^i", "ṛ"),  # rare
    ("aa", "ā"),
    ("ii", "ī"),
    ("uu", "ū"),
    ("ai", "ai"),
    ("au", "au"),
    ("~N", "ṅ"),
    ("~n", "ñ"),
    (".N", "ṅ"),
    (".n", "ṇ"),
    (".m", "ṃ"),
    (".M", "ṃ"),
    (".h", "ḥ"),
    (".H", "ḥ"),
    (".t", "ṭ"),
    (".T", "ṭ"),
    (".d", "ḍ"),
    (".D", "ḍ"),
    (".r", "ṛ"),
    (".R", "ṝ"),
    (".l", "ḷ"),
    (".L", "ḹ"),
    (".s", "ṣ"),
    (".S", "ṣ"),
    ("Sh", "ṣ"),
    ("sh", "ś"),
    ("Ch", "ch"),
    ("ch", "ch"),
    ("Th", "ṭh"),
    ("th", "th"),
    ("Dh", "ḍh"),
    ("dh", "dh"),
    ("kh", "kh"),
    ("gh", "gh"),
    ("jh", "jh"),
    ("ph", "ph"),
    ("bh", "bh"),
    ("T", "ṭ"),
    ("D", "ḍ"),
    ("N", "ṇ"),
    ("M", "ṃ"),
    ("H", "ḥ"),
    ("R", "ṛ"),  # bare R often ṛ in informal ITRANS
]


def itrans_to_iast(text: str) -> str:
    return _apply_pairs(text, _ITRANS_PAIRS)


# --- Velthuis → IAST ------------------------------------------------------
_VELTHUIS_PAIRS: list[tuple[str, str]] = [
    ("aa", "ā"),
    ("ii", "ī"),
    ("uu", "ū"),
    (".rr", "ṝ"),
    (".r", "ṛ"),
    (".ll", "ḹ"),
    (".l", "ḷ"),
    ('"n', "ṅ"),
    ("~n", "ñ"),
    (".n", "ṇ"),
    (".t", "ṭ"),
    (".d", "ḍ"),
    (".s", "ṣ"),
    ('"s', "ś"),
    (".m", "ṃ"),
    (".h", "ḥ"),
    ("ai", "ai"),
    ("au", "au"),
    ("kh", "kh"),
    ("gh", "gh"),
    ("ch", "ch"),
    ("jh", "jh"),
    ("th", "th"),
    ("dh", "dh"),
    ("ph", "ph"),
    ("bh", "bh"),
]


def velthuis_to_iast(text: str) -> str:
    return _apply_pairs(text, _VELTHUIS_PAIRS)


def scheme_to_iast(text: str, scheme: str) -> str:
    s = (scheme or "auto").lower().strip()
    if s in ("iast", "latn", "roman"):
        return _nfc(text)
    if s in ("auto", "detect"):
        s = detect_scheme(text)
    if s in ("hk", "harvard-kyoto", "harvard_kyoto", "kyoto"):
        return hk_to_iast(text)
    if s in ("itrans", "itx"):
        return itrans_to_iast(text)
    if s in ("velthuis", "vel", "vh"):
        return velthuis_to_iast(text)
    if s in ("slp1", "slp"):
        # defer to sanskrit_util
        return _slp1_to_iast(text)
    raise ValueError(f"unknown scheme: {scheme!r}")


def _slp1_to_iast(text: str) -> str:
    root = __file__
    from pathlib import Path

    py = Path(root).resolve().parents[1] / "py"
    if str(py) not in sys.path:
        sys.path.insert(0, str(py))
    import sanskrit_util as su  # type: ignore

    return su.from_slp1(text)


def detect_scheme(text: str) -> str:
    """Heuristic scheme detector for short scholarly snippets."""
    t = text.strip()
    if not t:
        return "iast"
    # Devanāgarī block
    if any("\u0900" <= c <= "\u097f" for c in t):
        return "deva"
    # Already has IAST diacritics
    if re.search(r"[āīūṛṝḷḹṅñṭḍṇśṣṃṁḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂḤ]", t):
        return "iast"
    # Velthuis markers
    if re.search(r'\.[a-zA-Z]|"n|"s|~n', t):
        return "velthuis"
    # ITRANS markers
    if re.search(r"~N|~n|\.n|\.m|aa|ii|uu|RRi|sh|Sh", t):
        return "itrans"
    # HK: capitals used as phonemes (A I U R M H G J T D N S) mixed with lowercase
    if re.search(r"[AIURMGJTDNzSH]", t) and re.search(r"[a-z]", t):
        return "hk"
    # default: try HK (common for email) if any uppercase phoneme-like
    if re.search(r"[AIURMGH]", t):
        return "hk"
    return "iast"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--from",
        dest="frm",
        default="auto",
        help="hk | itrans | velthuis | slp1 | iast | auto",
    )
    ap.add_argument("text", nargs="*", help="input (or stdin)")
    args = ap.parse_args(argv)
    src = " ".join(args.text) if args.text else sys.stdin.read()
    detected = detect_scheme(src) if args.frm == "auto" else args.frm
    if detected == "deva":
        # route through convert_bridge logic
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from convert_bridge import convert

        out = convert(src, "iast")
    else:
        out = scheme_to_iast(src, detected if args.frm == "auto" else args.frm)
    if args.frm == "auto":
        print(f"# detected: {detected}", file=sys.stderr)
    sys.stdout.write(out)
    if src.endswith("\n") and not out.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
