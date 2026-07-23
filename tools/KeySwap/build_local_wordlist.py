#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build or expand tools/KeySwap/data/local_headwords.txt for offline checks.

Sources (first match wins unless --merge):

  --from-spellcheck   sibling SanskritSpellCheck/HeadwordLists/MW-unique-key1-*.txt
  --from-file PATH    any one-key-per-line SLP1 list (BOM OK)
  --from-vectors      sanskrit-util/vectors/slp1_roundtrip_sample.txt (seed)
  --from-stdin        read keys from stdin

Examples:

  python tools/KeySwap/build_local_wordlist.py --from-spellcheck
  python tools/KeySwap/build_local_wordlist.py --from-file HeadwordLists/MW-unique-key1-193978.txt
  python tools/KeySwap/build_local_wordlist.py --from-vectors --out tools/KeySwap/data/local_headwords.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]  # sanskrit-util
DEFAULT_OUT = ROOT / "data" / "local_headwords.txt"


def _find_spellcheck_mw() -> Path | None:
    # …/GitHub/sanskrit-util/tools/KeySwap → …/GitHub/SanskritSpellCheck
    candidates = [
        REPO.parent / "SanskritSpellCheck" / "HeadwordLists",
        REPO.parent / "sanskrit-lexicon" / "SanskritSpellCheck" / "HeadwordLists",
        Path.home() / "Documents" / "GitHub" / "SanskritSpellCheck" / "HeadwordLists",
    ]
    for d in candidates:
        if not d.is_dir():
            continue
        # Prefer key1 (unique lemmas) over key2
        matches = sorted(d.glob("MW-unique-key1-*.txt"))
        if matches:
            return matches[0]
        matches = sorted(d.glob("MW-unique-key2-*.txt"))
        if matches:
            return matches[0]
    return None


def _read_keys(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8-sig")
    keys: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        key = s.split()[0].split("\t")[0].strip()
        if key:
            keys.add(key)
    return keys


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-spellcheck", action="store_true")
    src.add_argument("--from-file", type=Path)
    src.add_argument("--from-vectors", action="store_true")
    src.add_argument("--from-stdin", action="store_true")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument(
        "--merge",
        action="store_true",
        help="union with existing --out instead of replacing",
    )
    args = ap.parse_args(argv)

    keys: set[str] = set()
    source_label = ""
    if args.from_spellcheck:
        p = _find_spellcheck_mw()
        if p is None:
            print(
                "No SanskritSpellCheck HeadwordLists/MW-unique-key*.txt found "
                "(expected sibling of sanskrit-util).",
                file=sys.stderr,
            )
            return 2
        keys = _read_keys(p)
        source_label = str(p)
    elif args.from_file:
        if not args.from_file.is_file():
            print(f"not a file: {args.from_file}", file=sys.stderr)
            return 2
        keys = _read_keys(args.from_file)
        source_label = str(args.from_file)
    elif args.from_vectors:
        p = REPO / "vectors" / "slp1_roundtrip_sample.txt"
        if not p.is_file():
            print(f"missing {p}", file=sys.stderr)
            return 2
        keys = _read_keys(p)
        source_label = str(p)
    else:
        for line in sys.stdin:
            s = line.strip()
            if s and not s.startswith("#"):
                keys.add(s.split()[0].split("\t")[0])
        source_label = "stdin"

    if args.merge and args.out.is_file():
        keys |= _read_keys(args.out)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# KeySwap local headword list (SLP1, one key per line)\n"
        f"# Built from: {source_label}\n"
        f"# Keys: {len(keys)}\n"
        f"# Used by typing_check when offline / API fails.\n"
    )
    body = "\n".join(sorted(keys, key=lambda x: (x.lower(), x))) + "\n"
    args.out.write_text(header + body, encoding="utf-8")
    print(f"wrote {args.out}  keys={len(keys)}  from={source_label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
