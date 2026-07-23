#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap × Cologne Simple Search — query preparation + URL/API helpers.

Ports the *input half* of csl-apidev/simple-search:

1. Accept multi-scheme input (IAST, HK, ITRANS, Velthuis, SLP1, Devanāgarī, auto)
2. Transcode to SLP1 (sanskrit-util + scheme_bridge — same role as transcoder.php)
3. ``dalnorm_normalize`` — faithful port of ``Dalnorm::normalize`` in
   csl-apidev/simple-search/v1.1a/dalnorm.php (hwnorm1c key space)
4. Build Cologne Simple Search UI / API URLs (optional live JSON fetch)

Does **not** vendor hwnorm1c.sqlite or reimplement transition-table expansion
offline (that needs the full PHP engine + DB). For variants, call the live API.

Usage:
  python cologne_search.py "rāma"
  python cologne_search.py --from hk "rAma" --dict mw
  python cologne_search.py --from auto "saMskRta" --open
  python cologne_search.py --api "śiva" --dict mw
  python cologne_search.py --print-keys "kṛṣṇa"

Refs:
  https://sanskrit-lexicon.uni-koeln.de/simple/
  csl-apidev/simple-search/v1.1a/simple_search.php
  csl-apidev/simple-search/v1.1a/dalnorm.php
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Cologne endpoints (stable as of 2026-07 eval harness)
COLOGNE_SIMPLE_UI = "https://www.sanskrit-lexicon.uni-koeln.de/simple/"
COLOGNE_API = (
    "https://www.sanskrit-lexicon.uni-koeln.de/scans/csl-apidev/"
    "simple-search/v1.1/getword_list_1.0.php"
)

# Input schemes accepted by Cologne simple-search (precise modes)
COLOGNE_INPUTS = ("default", "slp1", "deva", "iast", "hk", "itrans")


def _find_repo() -> Path:
    for p in [ROOT, *ROOT.parents]:
        if (p / "py" / "sanskrit_util").is_dir():
            return p
    return ROOT.parents[1]


def _load_su():
    py = _find_repo() / "py"
    if str(py) not in sys.path:
        sys.path.insert(0, str(py))
    import sanskrit_util as su  # type: ignore

    return su


def dalnorm_normalize(slp1: str) -> str:
    """Port of PHP ``Dalnorm::normalize`` (v1.1a/dalnorm.php).

    Operates on **SLP1** headword keys (phonemic case preserved).
    """
    a = slp1 or ""
    # 1. Homorganic nasal rather than anusvāra
    nasal_map = {
        "k": "N",
        "K": "N",
        "g": "N",
        "G": "N",
        "N": "N",
        "c": "Y",
        "C": "Y",
        "j": "Y",
        "J": "Y",
        "Y": "Y",
        "w": "R",
        "W": "R",
        "q": "R",
        "Q": "R",
        "R": "R",
        "t": "n",
        "T": "n",
        "d": "n",
        "D": "n",
        "n": "n",
        "p": "m",
        "P": "m",
        "b": "m",
        "B": "m",
        "m": "m",
    }

    def _anusvara(m: re.Match[str]) -> str:
        c = m.group(2)
        return nasal_map.get(c, "M") + c

    a = re.sub(r"(M)([kKgGNcCjJYwWqQRtTdDnpPbBm])", _anusvara, a)
    # 2. rxx → rx (double after r)
    a = re.sub(r"([r])(.)\2", r"\1\2", a)
    # 2-asp. rxX → rX when X is aspirate of x
    asp = {
        "k": "K",
        "g": "G",
        "c": "C",
        "j": "J",
        "w": "W",
        "q": "Q",
        "t": "T",
        "d": "D",
        "p": "P",
        "b": "B",
    }

    def _rxX(m: re.Match[str]) -> str:
        x, X = m.group(1), m.group(2)
        if asp.get(x) == X:
            return "r" + X
        return "r" + x + X

    a = re.sub(r"r(.)(.)", _rxX, a)
    # 4. ending aH/uH/iH → a/u/i (Apte-style)
    a = re.sub(r"aH$", "a", a)
    a = re.sub(r"uH$", "u", a)
    a = re.sub(r"iH$", "i", a)
    # 5. ttr → tr
    a = re.sub(r"ttr", "tr", a)
    # 6. ending ant → at
    a = re.sub(r"ant$", "at", a)
    # 7. vowel + C → vowel + cC; consonant + cC → consonant + C
    a = re.sub(r"([aAiIuUfFxXeEoO])C", r"\1cC", a)
    a = re.sub(
        r"([kKgGNcCjJYwWqQRtTdDnpPbBmyrlvhzSsHM])cC",
        r"\1C",
        a,
    )
    return a


def to_slp1(text: str, scheme: str = "auto") -> tuple[str, str]:
    """Return (slp1, resolved_scheme). ``scheme`` like Cologne input modes + auto/velthuis."""
    from scheme_bridge import detect_scheme, scheme_to_iast

    su = _load_su()
    s = (scheme or "auto").lower().strip()
    if s in ("auto", "detect", "default", "simple"):
        det = detect_scheme(text)
        if det == "deva":
            return su.deva_to_slp1(text), "deva"
        if det == "iast":
            return su.to_slp1(text), "iast"
        if det == "hk":
            return su.to_slp1(scheme_to_iast(text, "hk")), "hk"
        if det == "itrans":
            return su.to_slp1(scheme_to_iast(text, "itrans")), "itrans"
        if det == "velthuis":
            return su.to_slp1(scheme_to_iast(text, "velthuis")), "velthuis"
        # bare ascii → treat as HK-ish default for Cologne "default" mode
        if re.search(r"[AIURMGJTDNzSH]", text):
            return su.to_slp1(scheme_to_iast(text, "hk")), "hk"
        return su.to_slp1(text), "iast"

    if s in ("slp1", "slp"):
        return text, "slp1"
    if s in ("deva", "devanagari", "devanāgarī", "dn"):
        return su.deva_to_slp1(text), "deva"
    if s in ("iast", "roman", "latn"):
        return su.to_slp1(text), "iast"
    if s in ("hk", "harvard-kyoto", "harvard_kyoto"):
        return su.to_slp1(scheme_to_iast(text, "hk")), "hk"
    if s in ("itrans", "itx"):
        return su.to_slp1(scheme_to_iast(text, "itrans")), "itrans"
    if s in ("velthuis", "vel", "vh"):
        return su.to_slp1(scheme_to_iast(text, "velthuis")), "velthuis"
    # Cologne "default" fuzzy input: pass as loose latin → IAST via HK heuristics
    if s == "default":
        iast = scheme_to_iast(text, detect_scheme(text))
        return su.to_slp1(iast), "default"
    raise ValueError(f"unknown scheme: {scheme!r}")


def cologne_input_param(resolved: str) -> str:
    """Map internal scheme name to Cologne ``input`` query param."""
    if resolved in ("deva", "iast", "hk", "itrans", "slp1", "default"):
        return resolved
    if resolved == "velthuis":
        # Cologne UI has no Velthuis; send IAST after our convert
        return "iast"
    return "iast"


@dataclass
class CologneQuery:
    """Prepared simple-search query."""

    original: str
    scheme_resolved: str
    cologne_input: str
    slp1: str
    normkey: str
    dict: str
    output: str
    ui_url: str
    api_url: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def prepare(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    output: str = "iast",
) -> CologneQuery:
    """Prepare SLP1 + dalnorm key and Cologne URLs for ``text``."""
    text = (text or "").strip()
    slp1, resolved = to_slp1(text, scheme)
    # strip accents for key (Cologne often strips; slp1_norm does similar)
    su = _load_su()
    slp1_clean = su.slp1_norm(slp1) if hasattr(su, "slp1_norm") else slp1
    # slp1_norm may collapse space; good for headword keys
    normkey = dalnorm_normalize(slp1_clean)
    cin = cologne_input_param(resolved)
    # For UI: pass original text with the scheme Cologne understands.
    # If we converted Velthuis ourselves, pass IAST form so Cologne gets precise input.
    if resolved == "velthuis":
        key_for_cologne = su.from_slp1(slp1_clean)
        cin = "iast"
    elif cin == "slp1":
        key_for_cologne = slp1_clean
    elif cin == "deva":
        key_for_cologne = text  # already Devanāgarī
    else:
        key_for_cologne = text

    qs = urllib.parse.urlencode(
        {
            "dict": dict_code.lower(),
            "input": cin,
            "output": output,
            "key": key_for_cologne,
        }
    )
    # Simple Search UI is mostly interactive; deep-link via API is reliable.
    # Also offer a citation-style UI base.
    api_url = f"{COLOGNE_API}?{qs}"
    ui_url = f"{COLOGNE_SIMPLE_UI}?{qs}"
    return CologneQuery(
        original=text,
        scheme_resolved=resolved,
        cologne_input=cin,
        slp1=slp1_clean,
        normkey=normkey,
        dict=dict_code.lower(),
        output=output,
        ui_url=ui_url,
        api_url=api_url,
    )


def fetch_results(q: CologneQuery, *, timeout: float = 30.0) -> list[str]:
    """Live API: return ordered ``dicthw`` list (IAST/output as requested)."""
    req = urllib.request.Request(q.api_url, headers={"User-Agent": "KeySwap-cologne_search/2.2"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    return [x.get("dicthw", "") for x in data.get("result", []) if x.get("dicthw")]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="*", help="query (or stdin)")
    ap.add_argument("--from", dest="frm", default="auto", help="auto|iast|hk|itrans|velthuis|slp1|deva")
    ap.add_argument("--dict", default="mw", help="dictionary code (mw, pw, ap90, …)")
    ap.add_argument("--output", default="iast", help="Cologne output scheme")
    ap.add_argument("--open", action="store_true", help="open UI URL in default browser")
    ap.add_argument("--api", action="store_true", help="fetch live JSON and print headwords")
    ap.add_argument("--print-keys", action="store_true", help="print slp1 + normkey only")
    ap.add_argument("--json", action="store_true", help="print CologneQuery as JSON")
    args = ap.parse_args(argv)

    text = " ".join(args.text) if args.text else sys.stdin.read()
    if not text.strip():
        print("empty query", file=sys.stderr)
        return 2

    q = prepare(text, scheme=args.frm, dict_code=args.dict, output=args.output)

    if args.print_keys:
        print(f"slp1\t{q.slp1}")
        print(f"normkey\t{q.normkey}")
        print(f"scheme\t{q.scheme_resolved} → cologne input={q.cologne_input}")
        return 0

    if args.json:
        print(json.dumps(q.as_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"original:  {q.original}")
        print(f"scheme:    {q.scheme_resolved} (cologne input={q.cologne_input})")
        print(f"slp1:      {q.slp1}")
        print(f"normkey:   {q.normkey}")
        print(f"ui:        {q.ui_url}")
        print(f"api:       {q.api_url}")

    if args.api:
        try:
            hits = fetch_results(q)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"API error: {e}", file=sys.stderr)
            return 1
        print(f"results ({len(hits)}):")
        for i, h in enumerate(hits[:40], 1):
            print(f"  {i:2d}. {h}")
        if len(hits) > 40:
            print(f"  … +{len(hits) - 40} more")

    if args.open:
        import webbrowser

        webbrowser.open(q.ui_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
