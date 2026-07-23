#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap typing-tool port: light Cologne headword check for typed text.

Not a full SanskritSpellCheck detector stack and not a local dictionary.
Uses the same Simple Search API prep as ``cologne_search.py``:

  typed / clipboard → scheme→SLP1 → dalnorm → live getword_list → known?

Designed for tray/HUD (one-line status) and CLI smoke tests. Network only
when verifying; no multi-MB data, no Hunspell, no offline headword dump.

Usage:
  python typing_check.py "kṛṣṇa"
  python typing_check.py --hud "rāma"
  python typing_check.py --dict mw --from hk "rAma"
  echo krsna | python typing_check.py --from auto --hud

Exit codes: 0 = known (or offline keys-only), 1 = unknown / API error, 2 = empty.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cologne_search import fetch_results, prepare  # noqa: E402


@dataclass
class TypingCheck:
    """Result of a single-token headword check for the typing tool."""

    query: str
    known: bool | None  # None = not verified (offline / error)
    n_hits: int
    top: list[str]
    slp1: str
    normkey: str
    scheme: str
    dict: str
    error: str = ""

    def hud_line(self, *, max_hits: int = 3) -> str:
        """One short line for tray ToolTip / status bar."""
        q = self.query[:40] + ("…" if len(self.query) > 40 else "")
        if self.error:
            return f"? {q}  ·  {self.error}  ·  slp1={self.slp1}"
        if self.known is None:
            return f"· {q}  ·  slp1={self.slp1}  norm={self.normkey}"
        if self.known:
            sample = ", ".join(self.top[:max_hits])
            extra = f" +{self.n_hits - max_hits}" if self.n_hits > max_hits else ""
            return f"✓ {q}  ·  {self.dict} {self.n_hits} hit(s): {sample}{extra}"
        return f"✗ {q}  ·  not in {self.dict}  ·  slp1={self.slp1}"

    def as_dict(self) -> dict:
        return asdict(self)


_TOKEN_RE = re.compile(
    r"[\w\u0900-\u097F\u1E00-\u1EFF\u0100-\u017F]+(?:['ʼ\u0300-\u036F]*)?",
    re.UNICODE,
)


def last_token(text: str) -> str:
    """Last Sanskrit/Latin token from clipboard/selection (ignore trailing punctuation)."""
    text = (text or "").strip()
    if not text:
        return ""
    # Prefer last line, then last token
    line = text.splitlines()[-1].strip()
    parts = _TOKEN_RE.findall(line)
    return parts[-1] if parts else line.split()[-1] if line.split() else line


def check_word(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    timeout: float = 12.0,
    verify: bool = True,
    last_word_only: bool = True,
) -> TypingCheck:
    """Check one word against Cologne Simple Search (optional live API)."""
    raw = (text or "").strip()
    query = last_token(raw) if last_word_only else raw
    if not query:
        return TypingCheck(
            query="",
            known=None,
            n_hits=0,
            top=[],
            slp1="",
            normkey="",
            scheme=scheme,
            dict=dict_code,
            error="empty",
        )

    q = prepare(query, scheme=scheme, dict_code=dict_code, output="iast")
    if not verify:
        return TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
        )

    try:
        hits = fetch_results(q, timeout=timeout)
    except Exception as e:  # noqa: BLE001 — surface any network/parse failure to HUD
        return TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
            error=f"api: {type(e).__name__}",
        )

    return TypingCheck(
        query=query,
        known=len(hits) > 0,
        n_hits=len(hits),
        top=hits[:10],
        slp1=q.slp1,
        normkey=q.normkey,
        scheme=q.scheme_resolved,
        dict=dict_code.lower(),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="*", help="word or phrase (or stdin)")
    ap.add_argument("--from", dest="frm", default="auto")
    ap.add_argument("--dict", default="mw", help="Cologne dict code (mw, pw, …)")
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--no-verify", action="store_true", help="keys only, no network")
    ap.add_argument("--full-text", action="store_true", help="do not reduce to last token")
    ap.add_argument("--hud", action="store_true", help="print one-line HUD status only")
    ap.add_argument("--json", action="store_true", help="print JSON result")
    ap.add_argument("--open-if-unknown", action="store_true", help="open Simple Search if unknown")
    args = ap.parse_args(argv)

    text = " ".join(args.text) if args.text else sys.stdin.read()
    result = check_word(
        text,
        scheme=args.frm,
        dict_code=args.dict,
        timeout=args.timeout,
        verify=not args.no_verify,
        last_word_only=not args.full_text,
    )

    if args.hud:
        sys.stdout.write(result.hud_line() + "\n")
    elif args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(result.hud_line())
        if result.top:
            for i, h in enumerate(result.top, 1):
                print(f"  {i}. {h}")
        print(f"slp1={result.slp1}  normkey={result.normkey}  scheme={result.scheme}")

    if args.open_if_unknown and result.known is False:
        import webbrowser

        q = prepare(result.query, scheme=args.frm, dict_code=args.dict)
        webbrowser.open(q.ui_url)

    if result.error == "empty":
        return 2
    if result.known is False:
        return 1
    if result.error and result.known is None:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
