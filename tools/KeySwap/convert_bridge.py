#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap 2.0 — convert selection via sanskrit-util (IAST ↔ Devanāgarī).

Usage:
  python convert_bridge.py --to deva "rāma"
  python convert_bridge.py --to iast "राम"
  python convert_bridge.py --to deva --clipboard   # Windows: read/write clipboard
  type file.txt | python convert_bridge.py --to iast

Does not reimplement a transcoder: imports sibling py/sanskrit_util when present.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]  # sanskrit-util/
PY_PKG = REPO / "py"


def _load_su():
    if str(PY_PKG) not in sys.path:
        sys.path.insert(0, str(PY_PKG))
    try:
        import sanskrit_util as su  # type: ignore
    except ImportError as e:
        raise SystemExit(
            "sanskrit_util not importable. Run from sanskrit-util checkout "
            f"with py/ on path (looked at {PY_PKG}): {e}"
        ) from e
    return su


def convert(text: str, to: str) -> str:
    su = _load_su()
    to = to.lower().strip()
    if to in ("deva", "devanagari", "devanāgarī", "dn"):
        return su.iast_to_devanagari(text)
    if to in ("iast", "roman", "latn"):
        # If already mostly Latin, leave; if Devanāgarī, convert
        if any("\u0900" <= c <= "\u097f" for c in text):
            return su.deva_to_iast(text)
        return text
    if to in ("slp1", "slp"):
        if any("\u0900" <= c <= "\u097f" for c in text):
            return su.deva_to_slp1(text)
        return su.to_slp1(text)
    raise SystemExit(f"unknown --to {to!r} (use deva|iast|slp1)")


def _clipboard_get() -> str:
    try:
        import ctypes

        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard(0)
        try:
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return ""
            data = kernel32.GlobalLock(handle)
            text = ctypes.wstring_at(data)
            kernel32.GlobalUnlock(handle)
            return text
        finally:
            user32.CloseClipboard()
    except Exception:
        return ""


def _clipboard_set(text: str) -> None:
    try:
        import ctypes

        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard(0)
        user32.EmptyClipboard()
        buf = ctypes.create_unicode_buffer(text)
        size = (len(text) + 1) * 2
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, size)
        locked = kernel32.GlobalLock(handle)
        ctypes.memmove(locked, buf, size)
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_UNICODETEXT, handle)
        user32.CloseClipboard()
    except Exception as e:
        raise SystemExit(f"clipboard set failed: {e}") from e


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--to", required=True, help="deva | iast | slp1")
    ap.add_argument("--clipboard", action="store_true", help="Windows clipboard in/out")
    ap.add_argument("text", nargs="*", help="Text args (or stdin if empty)")
    args = ap.parse_args(argv)

    if args.clipboard:
        src = _clipboard_get()
    elif args.text:
        src = " ".join(args.text)
    else:
        src = sys.stdin.read()

    out = convert(src, args.to)
    if args.clipboard:
        _clipboard_set(out)
        print(f"clipboard → {args.to}: {len(out)} chars", file=sys.stderr)
    else:
        sys.stdout.write(out)
        if not out.endswith("\n") and "\n" in src:
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
