#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KeySwap typing-tool port: Cologne headword check + local offline fallback.

Primary path: typed / clipboard → scheme→SLP1 → dalnorm → live Simple Search API.

Offline / no-network alternative: a plain SLP1 wordlist
(``data/local_headwords.txt`` or ``KEYSWAP_WORDLIST`` / ``--wordlist``).

Optional DCS-2026 frequencies (off by default):

  --dcs-freq          or  KEYSWAP_DCS_FREQ=1
  data/dcs_freq.txt   (csl-apidev simple-search/wf1 table)

When enabled, HUD shows ``dcs=N`` and multi-hit lists can be re-ranked.

Opt-in v3 plugins (never default Startup / never without flag):

  --plugin offline_fuzzy   or  KEYSWAP_PLUGINS=offline_fuzzy
  → exact + prefix/edit-distance over the local wordlist (V3-2)

Usage:
  python typing_check.py "kṛṣṇa"
  python typing_check.py --hud "rāma"
  python typing_check.py --local-only --hud "rāma"
  python typing_check.py --local-only --plugin offline_fuzzy --hud "rAm"
  python typing_check.py --dcs-freq --hud "rāma"
  python typing_check.py --dcs-freq --freqsrc wf1 --hud "rāma"

Exit codes: 0 = known (or keys-only offline prep), 1 = unknown / unrecoverable error, 2 = empty.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cologne_search import (  # noqa: E402
    fetch_results,
    fetch_results_detailed,
    format_api_error,
    prepare,
    webtc_url,
)
from dcs_freq import dcs_freq_enabled, freq_of  # noqa: E402
from local_wordlist import get_wordlist, lookup, wordlist_label  # noqa: E402
from plugins.discovery import plugin_enabled  # noqa: E402


@dataclass
class TypingCheck:
    """Result of a single-token headword check for the typing tool."""

    query: str
    known: bool | None  # None = not verified (keys-only / no local fallback)
    n_hits: int
    top: list[str]
    slp1: str
    normkey: str
    scheme: str
    dict: str
    error: str = ""
    source: str = ""  # "api" | "local" | "offline_fuzzy" | "keys" | ""
    dcs_n: int | None = None  # DCS-2026 token count when --dcs-freq
    freq_source: str = ""  # server freq_source or "local-dcs"
    gloss_url: str = ""  # Cologne webtc deep-link for full entry/gloss
    fuzzy_status: str = ""  # exact | fuzzy-unique | fuzzy-multi | …

    def hud_line(self, *, max_hits: int = 3) -> str:
        """One short line for tray ToolTip / status bar."""
        q = self.query[:40] + ("…" if len(self.query) > 40 else "")
        dcs = ""
        if self.dcs_n is not None and self.dcs_n >= 0:
            dcs = f"  ·  dcs={self.dcs_n}"
        gloss = "  ·  Ctrl+Alt+G" if self.known and self.gloss_url else ""
        if self.error and self.known is None:
            # Keep rate-limit message short and actionable (no slp1 clutter)
            if self.error.startswith("rate-limited"):
                return f"? {q}  ·  {self.error}"
            return f"? {q}  ·  {self.error}  ·  slp1={self.slp1}"
        if self.known is None:
            return f"· {q}  ·  slp1={self.slp1}  norm={self.normkey}{dcs}"
        if self.known:
            if self.source == "offline_fuzzy":
                tag = self.fuzzy_status or "exact"
                if tag == "fuzzy-unique" and self.top:
                    near = self.top[0]
                    return (
                        f"~ {q}  ·  fuzzy→{near}  ·  "
                        f"{wordlist_label()}{dcs}{gloss}"
                    )
                return (
                    f"✓ {q}  ·  fuzzy ({self.dict})  ·  "
                    f"{wordlist_label()}{dcs}{gloss}"
                )
            if self.source == "local":
                return (
                    f"✓ {q}  ·  local ({self.dict})  ·  "
                    f"{wordlist_label()}{dcs}{gloss}"
                )
            sample = ", ".join(self.top[:max_hits])
            extra = f" +{self.n_hits - max_hits}" if self.n_hits > max_hits else ""
            return (
                f"✓ {q}  ·  {self.dict} {self.n_hits} hit(s): "
                f"{sample}{extra}{dcs}{gloss}"
            )
        if self.source == "offline_fuzzy" and self.top:
            sample = ", ".join(self.top[:max_hits])
            return (
                f"~ {q}  ·  near: {sample}  ·  "
                f"slp1={self.slp1}{dcs}"
            )
        if self.source == "local":
            if self.error and self.error.startswith("rate-limited"):
                return f"? {q}  ·  {self.error}"
            return f"✗ {q}  ·  not in local ({self.dict})  ·  slp1={self.slp1}"
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


def _attach_dcs(result: TypingCheck, *, dcs: bool) -> TypingCheck:
    if not dcs:
        return result
    n = freq_of(result.slp1, result.normkey)
    if n is not None:
        result.dcs_n = n
        if not result.freq_source:
            result.freq_source = "local-dcs"
    return result


def _attach_gloss(result: TypingCheck) -> TypingCheck:
    """Add Cologne webtc deep-link when we have an SLP1 key."""
    if result.slp1 and result.known is not False:
        result.gloss_url = webtc_url(result.slp1, dict_code=result.dict or "mw")
    return result


def _local_result(
    query: str,
    q,
    dict_code: str,
    *,
    wordlist: str | Path | None,
    api_error: str = "",
    dcs: bool = False,
    use_fuzzy: bool = False,
) -> TypingCheck | None:
    """Return a TypingCheck from the local wordlist, or None if no file."""
    if use_fuzzy:
        return _fuzzy_local_result(
            query, q, dict_code, wordlist=wordlist, api_error=api_error, dcs=dcs
        )
    hit = lookup(q.slp1, q.normkey, path=wordlist)
    if hit is None:
        return None
    r = TypingCheck(
        query=query,
        known=hit,
        n_hits=1 if hit else 0,
        top=[q.slp1] if hit else [],
        slp1=q.slp1,
        normkey=q.normkey,
        scheme=q.scheme_resolved,
        dict=dict_code.lower(),
        error="" if hit else (api_error or ""),
        source="local",
    )
    return _attach_gloss(_attach_dcs(r, dcs=dcs))


def _fuzzy_local_result(
    query: str,
    q,
    dict_code: str,
    *,
    wordlist: str | Path | None,
    api_error: str = "",
    dcs: bool = False,
) -> TypingCheck | None:
    """Opt-in offline_fuzzy plugin path (lazy import)."""
    # Lazy: never import the plugin unless the caller opted in.
    from plugins.offline_fuzzy.fuzzy_lookup import lookup as fuzzy_lookup  # noqa: PLC0415

    fr = fuzzy_lookup(q.slp1, path=wordlist, normkey=q.normkey)
    if fr.status == "no-wordlist":
        return None
    if fr.status == "empty-query":
        return TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
            error="empty",
            source="offline_fuzzy",
            fuzzy_status=fr.status,
        )

    top: list[str] = []
    if fr.match:
        top.append(fr.match)
    for s in fr.suggestions:
        if s not in top:
            top.append(s)
    known = fr.found
    err = ""
    if not known:
        err = api_error or ""
    r = TypingCheck(
        query=query,
        known=known,
        n_hits=len(top) if top else (1 if known else 0),
        top=top[:10],
        slp1=q.slp1,
        normkey=q.normkey,
        scheme=q.scheme_resolved,
        dict=dict_code.lower(),
        error=err,
        source="offline_fuzzy",
        fuzzy_status=fr.status,
    )
    r = _attach_gloss(_attach_dcs(r, dcs=dcs))
    # Soft unique: gloss the resolved headword, not the mistyped probe.
    if known and fr.match and fr.status == "fuzzy-unique":
        r.gloss_url = webtc_url(fr.match, dict_code=dict_code.lower() or "mw")
    return r


def check_word(
    text: str,
    *,
    scheme: str = "auto",
    dict_code: str = "mw",
    timeout: float = 12.0,
    verify: bool = True,
    last_word_only: bool = True,
    local_only: bool = False,
    use_local: bool = True,
    wordlist: str | Path | None = None,
    dcs_freq: bool | None = None,
    freqsrc: str = "",
    plugins: Iterable[str] | None = None,
) -> TypingCheck:
    """Check one word against Cologne Simple Search and/or a local SLP1 wordlist.

    Parameters
    ----------
    dcs_freq
        Opt-in DCS-2026 frequency annotation (default: env KEYSWAP_DCS_FREQ).
    freqsrc
        Pass-through to Cologne API: ``wf1`` (DCS) or ``wf0`` (legacy). Empty =
        server default (wf1 after Fix I deploy).
    plugins
        Opt-in plugin ids (also ``KEYSWAP_PLUGINS``). ``offline_fuzzy`` enables
        V3-2 fuzzy local lookup. Empty = no plugins (default).
    """
    dcs = dcs_freq_enabled(dcs_freq)
    # When DCS mode is on and caller did not pick a server table, prefer wf1.
    if dcs and not freqsrc:
        freqsrc = "wf1"
    use_fuzzy = plugin_enabled("offline_fuzzy", plugins)

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

    q = prepare(
        query, scheme=scheme, dict_code=dict_code, output="iast", freqsrc=freqsrc
    )
    if not verify:
        r = TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
            source="keys",
        )
        return _attach_gloss(_attach_dcs(r, dcs=dcs))

    if local_only:
        local = _local_result(
            query, q, dict_code, wordlist=wordlist, dcs=dcs, use_fuzzy=use_fuzzy
        )
        if local is not None:
            return local
        return TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
            error="no local wordlist (see data/local_headwords.txt)",
            source="",
        )

    try:
        if dcs:
            hits_d, meta = fetch_results_detailed(q, timeout=timeout, dcs_freq=True)
            hit_strs = [h.dicthw for h in hits_d]
            dcs_n = None
            for h in hits_d:
                if h.key == q.slp1 or h.dicthw == q.slp1:
                    if h.dcs_n is not None and h.dcs_n >= 0:
                        dcs_n = h.dcs_n
                        break
            if dcs_n is None:
                dcs_n = freq_of(q.slp1, q.normkey)
            r = TypingCheck(
                query=query,
                known=len(hit_strs) > 0,
                n_hits=len(hit_strs),
                top=hit_strs[:10],
                slp1=q.slp1,
                normkey=q.normkey,
                scheme=q.scheme_resolved,
                dict=dict_code.lower(),
                source="api",
                dcs_n=dcs_n if dcs_n is not None else None,
                freq_source=str(meta.get("freq_source") or "local-dcs"),
            )
            return _attach_gloss(r)
        hits = fetch_results(q, timeout=timeout, dcs_freq=False)
    except Exception as e:  # noqa: BLE001 — surface any network/parse failure to HUD
        api_err = format_api_error(e)
        if use_local:
            local = _local_result(
                query,
                q,
                dict_code,
                wordlist=wordlist,
                api_error=api_err,
                dcs=dcs,
                use_fuzzy=use_fuzzy,
            )
            if local is not None:
                if local.known:
                    local.error = ""
                elif api_err.startswith("rate-limited"):
                    local.error = api_err
                else:
                    local.error = f"{api_err}; not in local"
                return local
        return TypingCheck(
            query=query,
            known=None,
            n_hits=0,
            top=[],
            slp1=q.slp1,
            normkey=q.normkey,
            scheme=q.scheme_resolved,
            dict=dict_code.lower(),
            error=api_err,
        )

    r = TypingCheck(
        query=query,
        known=len(hits) > 0,
        n_hits=len(hits),
        top=hits[:10],
        slp1=q.slp1,
        normkey=q.normkey,
        scheme=q.scheme_resolved,
        dict=dict_code.lower(),
        source="api",
    )
    return _attach_gloss(_attach_dcs(r, dcs=dcs))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("text", nargs="*", help="word or phrase (or stdin)")
    ap.add_argument("--from", dest="frm", default="auto")
    ap.add_argument("--dict", default="mw", help="Cologne dict code (mw, pw, …)")
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--no-verify", action="store_true", help="keys only, no network")
    ap.add_argument(
        "--local-only",
        action="store_true",
        help="skip Cologne API; use local SLP1 wordlist only",
    )
    ap.add_argument(
        "--no-local",
        action="store_true",
        help="do not fall back to local wordlist on API failure",
    )
    ap.add_argument(
        "--wordlist",
        default=None,
        help="path to local SLP1 list (default: data/local_headwords.txt or KEYSWAP_WORDLIST)",
    )
    ap.add_argument(
        "--dcs-freq",
        action="store_true",
        help="opt-in: annotate with DCS-2026 frequencies (data/dcs_freq.txt or KEYSWAP_DCS_FREQ=1)",
    )
    ap.add_argument(
        "--freqsrc",
        default="",
        help="Cologne API ranking table: wf1 (DCS-2026) or wf0 (legacy)",
    )
    ap.add_argument(
        "--plugin",
        action="append",
        default=[],
        metavar="ID",
        help="opt-in v3 plugin id (repeatable); also KEYSWAP_PLUGINS=id1,id2. "
        "offline_fuzzy = V3-2 local fuzzy index (never default)",
    )
    ap.add_argument("--full-text", action="store_true", help="do not reduce to last token")
    ap.add_argument("--hud", action="store_true", help="print one-line HUD status only")
    ap.add_argument("--json", action="store_true", help="print JSON result")
    ap.add_argument("--open-if-unknown", action="store_true", help="open Simple Search if unknown")
    ap.add_argument(
        "--open-gloss",
        action="store_true",
        help="open Cologne webtc full-entry (gloss) page for the key",
    )
    args = ap.parse_args(argv)

    text = " ".join(args.text) if args.text else sys.stdin.read()
    result = check_word(
        text,
        scheme=args.frm,
        dict_code=args.dict,
        timeout=args.timeout,
        verify=not args.no_verify,
        last_word_only=not args.full_text,
        local_only=args.local_only,
        use_local=not args.no_local,
        wordlist=args.wordlist,
        dcs_freq=True if args.dcs_freq else None,
        freqsrc=args.freqsrc,
        plugins=args.plugin,
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
        print(
            f"slp1={result.slp1}  normkey={result.normkey}  "
            f"scheme={result.scheme}  source={result.source or '-'}"
            + (f"  dcs={result.dcs_n}" if result.dcs_n is not None else "")
            + (f"  freq_source={result.freq_source}" if result.freq_source else "")
        )
        if get_wordlist(args.wordlist) is not None and result.source == "local":
            print(f"wordlist={wordlist_label(args.wordlist)}")

    if args.open_if_unknown and result.known is False:
        import webbrowser

        q = prepare(result.query, scheme=args.frm, dict_code=args.dict)
        webbrowser.open(q.ui_url)

    if args.open_gloss and result.gloss_url:
        import webbrowser

        webbrowser.open(result.gloss_url)

    if result.error == "empty":
        return 2
    if result.known is False:
        return 1
    if result.error and result.known is None:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
