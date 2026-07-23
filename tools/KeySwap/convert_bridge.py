#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap 2.1 — convert selection via sanskrit-util + ASCII schemes.

Usage:
  python convert_bridge.py --to deva "rāma"
  python convert_bridge.py --to iast "राम"
  python convert_bridge.py --from hk --to iast "saMskRta"
  python convert_bridge.py --from itrans --to deva "raama"
  python convert_bridge.py --from auto --to iast "saMskRta"
  python convert_bridge.py --to deva --clipboard

Pipeline: optional scheme_bridge (HK/ITRANS/Velthuis) → IAST → sanskrit_util target.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _find_repo() -> Path:
    for p in [ROOT, *ROOT.parents]:
        if (p / "py" / "sanskrit_util").is_dir() or (p / "py" / "sanskrit_util" / "__init__.py").is_file():
            return p
        if (p / "py" / "sanskrit_util.py").is_file():
            return p
    # tools/KeySwap → parents: KeySwap, tools, repo
    return ROOT.parents[1] if len(ROOT.parents) > 1 else ROOT


REPO = _find_repo()
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


def _to_iast(text: str, frm: str) -> str:
    """Normalize any supported input to IAST (or leave Devanāgarī for su path)."""
    frm = (frm or "auto").lower().strip()
    if frm in ("deva", "devanagari", "devanāgarī", "dn"):
        su = _load_su()
        return su.deva_to_iast(text)
    if frm in ("iast", "roman", "latn") or (
        frm == "auto"
        and any("\u0900" <= c <= "\u097f" for c in text) is False
        and any(ord(c) > 127 for c in text)
    ):
        if any("\u0900" <= c <= "\u097f" for c in text):
            return _load_su().deva_to_iast(text)
        if frm in ("iast", "roman", "latn"):
            return text
    if frm in ("slp1", "slp"):
        return _load_su().from_slp1(text)

    # ASCII schemes + auto
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from scheme_bridge import detect_scheme, scheme_to_iast

    if frm in ("auto", "detect"):
        det = detect_scheme(text)
        if det == "deva":
            return _load_su().deva_to_iast(text)
        if det == "iast":
            return text
        return scheme_to_iast(text, det)
    return scheme_to_iast(text, frm)


def convert(text: str, to: str, frm: str = "auto") -> str:
    to = to.lower().strip()
    su = _load_su()

    # Fast path: Devanāgarī source to iast/slp1 without scheme_bridge
    if any("\u0900" <= c <= "\u097f" for c in text) and frm in (
        "auto",
        "detect",
        "deva",
        "devanagari",
    ):
        if to in ("iast", "roman", "latn"):
            return su.deva_to_iast(text)
        if to in ("slp1", "slp"):
            return su.deva_to_slp1(text)
        if to in ("deva", "devanagari", "devanāgarī", "dn"):
            return text

    iast = _to_iast(text, frm)

    if to in ("iast", "roman", "latn"):
        return iast
    if to in ("deva", "devanagari", "devanāgarī", "dn"):
        return su.iast_to_devanagari(iast)
    if to in ("slp1", "slp"):
        return su.to_slp1(iast)
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
    ap.add_argument(
        "--from",
        dest="frm",
        default="auto",
        help="auto | iast | deva | hk | itrans | velthuis | slp1",
    )
    ap.add_argument("--clipboard", action="store_true", help="Windows clipboard in/out")
    ap.add_argument("text", nargs="*", help="Text args (or stdin if empty)")
    args = ap.parse_args(argv)

    if args.clipboard:
        src = _clipboard_get()
    elif args.text:
        src = " ".join(args.text)
    else:
        src = sys.stdin.read()

    out = convert(src, args.to, frm=args.frm)
    if args.clipboard:
        _clipboard_set(out)
        print(f"clipboard {args.frm}→{args.to}: {len(out)} chars", file=sys.stderr)
    else:
        sys.stdout.write(out)
        if not out.endswith("\n") and "\n" in src:
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
