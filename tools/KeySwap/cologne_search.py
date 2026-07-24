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
    freqsrc: str = ""  # "" | "wf1" | "wf0" — Cologne ranking table preference

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CologneHit:
    """One Simple Search result row (display form + optional ranking fields)."""

    dicthw: str
    key: str = ""  # SLP1 key when the API provides it
    wf: int | None = None  # ranking frequency from API (server-side table)
    dcs_n: int | None = None  # local DCS-2026 table when --dcs-freq is on


def prepare(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    output: str = "iast",
    freqsrc: str = "",
) -> CologneQuery:
    """Prepare SLP1 + dalnorm key and Cologne URLs for ``text``.

    ``freqsrc``: when non-empty, appends ``?freqsrc=`` for the getword_list API
    (``wf1`` = DCS-2026 default after Fix I, ``wf0`` = legacy 2017 table).
    """
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

    params: dict[str, str] = {
        "dict": dict_code.lower(),
        "input": cin,
        "output": output,
        "key": key_for_cologne,
    }
    freq = (freqsrc or "").strip().lower()
    if freq in ("wf0", "wf1", "dcs", "legacy"):
        params["freqsrc"] = "wf0" if freq in ("wf0", "legacy") else "wf1"
        freq = params["freqsrc"]
    else:
        freq = ""
    qs = urllib.parse.urlencode(params)
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
        freqsrc=freq,
    )


def format_api_error(exc: BaseException) -> str:
    """Map network/API failures to short HUD-friendly labels.

    HTTP 429 (Cologne rate limit) is the common live failure mode — point users
    at the browser Simple Search path (AHK Ctrl+Alt+C) instead of raw HTTPError.
    """
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code == 429:
            return "rate-limited — try browser (Ctrl+Alt+C)"
        if exc.code >= 500:
            return f"api server {exc.code}"
        return f"api HTTP {exc.code}"
    if isinstance(exc, urllib.error.URLError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, TimeoutError) or (
            reason is not None and "timed out" in str(reason).lower()
        ):
            return "api timeout"
        return "api network error"
    if isinstance(exc, TimeoutError):
        return "api timeout"
    if isinstance(exc, json.JSONDecodeError):
        return "api bad JSON"
    return f"api: {type(exc).__name__}"


def fetch_results_detailed(
    q: CologneQuery,
    *,
    timeout: float = 30.0,
    dcs_freq: bool = False,
) -> tuple[list[CologneHit], dict[str, Any]]:
    """Live API: structured hits + response meta.

    When ``dcs_freq`` is True, annotate each hit with local DCS-2026 counts
    (``data/dcs_freq.txt``) and re-order by that table when the API does not
    already expose server ``wf`` values (or when client re-rank is preferred).

    Raises urllib/json errors; callers may use :func:`format_api_error`.
    """
    req = urllib.request.Request(
        q.api_url, headers={"User-Agent": "KeySwap-cologne_search/2.5"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.load(r)
    rows = data.get("result") or []
    hits: list[CologneHit] = []
    for x in rows:
        if not isinstance(x, dict):
            continue
        dw = x.get("dicthw") or x.get("dicthwoutput") or ""
        if not dw:
            continue
        wf_raw = x.get("wf")
        wf: int | None
        try:
            wf = int(wf_raw) if wf_raw is not None else None
        except (TypeError, ValueError):
            wf = None
        hits.append(
            CologneHit(
                dicthw=str(dw),
                key=str(x.get("key") or ""),
                wf=wf,
            )
        )

    meta: dict[str, Any] = {
        "freq_source": data.get("freq_source") or q.freqsrc or "",
        "n": len(hits),
    }

    if dcs_freq:
        from dcs_freq import get_dcs_freq  # local import keeps base path light

        tab = get_dcs_freq()
        if tab:
            for h in hits:
                key = h.key or ""
                n = tab.get(key) if key else None
                if n is None:
                    # API output is often IAST; fall back not possible without reverse
                    # map — use server wf only if key empty
                    n = tab.get(h.dicthw)
                h.dcs_n = n if n is not None else -1
            # Prefer local DCS order when enabled (works pre- and post-server Fix I)
            hits.sort(
                key=lambda h: (
                    -(h.dcs_n if h.dcs_n is not None and h.dcs_n >= 0 else -1),
                    h.dicthw,
                )
            )
            meta["dcs_freq"] = True
            meta["dcs_keys"] = len(tab)
        else:
            meta["dcs_freq"] = False
            meta["dcs_error"] = "no dcs_freq table (data/dcs_freq.txt)"

    return hits, meta


def fetch_results(
    q: CologneQuery,
    *,
    timeout: float = 30.0,
    dcs_freq: bool = False,
) -> list[str]:
    """Live API: return ordered ``dicthw`` list (IAST/output as requested).

    Raises urllib/json errors; callers may use :func:`format_api_error` for HUD text.
    """
    hits, _meta = fetch_results_detailed(q, timeout=timeout, dcs_freq=dcs_freq)
    return [h.dicthw for h in hits]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="*", help="query (or stdin)")
    ap.add_argument("--from", dest="frm", default="auto", help="auto|iast|hk|itrans|velthuis|slp1|deva")
    ap.add_argument("--dict", default="mw", help="dictionary code (mw, pw, ap90, …)")
    ap.add_argument("--output", default="iast", help="Cologne output scheme")
    ap.add_argument(
        "--freqsrc",
        default="",
        help="Cologne ranking table: wf1 (DCS-2026) or wf0 (legacy); empty = server default",
    )
    ap.add_argument(
        "--dcs-freq",
        action="store_true",
        help="annotate/re-rank with local data/dcs_freq.txt (DCS-2026)",
    )
    ap.add_argument("--open", action="store_true", help="open UI URL in default browser")
    ap.add_argument("--api", action="store_true", help="fetch live JSON and print headwords")
    ap.add_argument("--print-keys", action="store_true", help="print slp1 + normkey only")
    ap.add_argument("--json", action="store_true", help="print CologneQuery as JSON")
    args = ap.parse_args(argv)

    text = " ".join(args.text) if args.text else sys.stdin.read()
    if not text.strip():
        print("empty query", file=sys.stderr)
        return 2

    q = prepare(
        text,
        scheme=args.frm,
        dict_code=args.dict,
        output=args.output,
        freqsrc=args.freqsrc,
    )

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
        if q.freqsrc:
            print(f"freqsrc:   {q.freqsrc}")
        print(f"ui:        {q.ui_url}")
        print(f"api:       {q.api_url}")

    if args.api:
        try:
            hits, meta = fetch_results_detailed(
                q, dcs_freq=args.dcs_freq
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"API error: {e}", file=sys.stderr)
            return 1
        print(f"results ({len(hits)}) freq_source={meta.get('freq_source') or '-'}:")
        for i, h in enumerate(hits[:40], 1):
            extra = ""
            if h.dcs_n is not None and h.dcs_n >= 0:
                extra = f"  dcs={h.dcs_n}"
            elif h.wf is not None:
                extra = f"  wf={h.wf}"
            print(f"  {i:2d}. {h.dicthw}{extra}")
        if len(hits) > 40:
            print(f"  … +{len(hits) - 40} more")

    if args.open:
        import webbrowser

        webbrowser.open(q.ui_url)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
