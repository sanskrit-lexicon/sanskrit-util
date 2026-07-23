#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate all KeySwap config profiles (unique bases, NFC, non-empty forms).

Usage (from repo root or this directory):
  python tools/KeySwap/validate_configs.py
  python tools/KeySwap/validate_configs.py --strict
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cycle_engine import ConfigError, parse_chains, validate_config_text  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Config files (default: configs/*.txt and config.txt)",
    )
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors",
    )
    args = ap.parse_args(argv)

    paths = list(args.paths)
    if not paths:
        paths = sorted((ROOT / "configs").glob("*.txt"))
        default = ROOT / "config.txt"
        if default.is_file():
            paths.append(default)

    if not paths:
        print("No config files found", file=sys.stderr)
        return 2

    errors = 0
    warns = 0
    for path in paths:
        text = path.read_text(encoding="utf-8-sig")
        try:
            chains = parse_chains(text, path=str(path))
            warnings = validate_config_text(text, path=str(path))
        except ConfigError as e:
            print(f"ERROR  {path}: {e}")
            errors += 1
            continue
        n_forms = sum(len(c) for c in chains)
        print(f"OK     {path}: {len(chains)} chains, {n_forms} forms")
        for w in warnings:
            print(f"  WARN {w}")
            warns += 1
            if args.strict:
                errors += 1

    classic = ROOT / "configs" / "iast-classic.txt"
    default = ROOT / "config.txt"
    if classic.is_file() and default.is_file():

        def strip_comments(t: str) -> str:
            lines = []
            for line in t.splitlines():
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                if " #" in s:
                    s = s.split(" #", 1)[0].rstrip()
                lines.append(s)
            return "\n".join(lines) + "\n"

        a = strip_comments(classic.read_text(encoding="utf-8-sig"))
        b = strip_comments(default.read_text(encoding="utf-8-sig"))
        if a != b:
            print(
                "ERROR  config.txt chain body != configs/iast-classic.txt "
                "(keep them in sync)"
            )
            errors += 1
        else:
            print("OK     config.txt matches configs/iast-classic.txt")

    print(f"\n{errors} error(s), {warns} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
