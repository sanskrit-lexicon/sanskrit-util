#!/usr/bin/env python3
"""_provenance.py — shared helpers for episteme-registry `> **Source:**` lines (H356).

Keeps provenance rendering identical across the seed scripts and the one-shot normalizer, and
enforces three MG conventions (08-07-2026):
  * every repo tag is a clickable link (verified owner map below) — "everything clickable";
  * the model tag is the bare version id in backticks (`claude-opus-4-8`), NOT the tier-prefixed
    "Opus 4.8 (`claude-opus-4-8`)" form — the version alone is enough in these compact lines;
  * the provenance date links to that day's commits in the registry's own repo, so a reader can
    see what landed when.

Import from a sibling script:  from _provenance import repo_link, date_link, strip_model_tier
"""
import re

# Verified 08-07-2026 via `gh repo view` — do not guess an owner; add here when a new repo appears.
REPO_URL = {
    "Uprava": "https://github.com/gasyoun/Uprava",
    "kosha": "https://github.com/gasyoun/kosha",
    "WhitneyRoots": "https://github.com/gasyoun/WhitneyRoots",
    "SanskritLexicography": "https://github.com/gasyoun/SanskritLexicography",
    "SanskritGrammar": "https://github.com/gasyoun/SanskritGrammar",
    "VisualDCS": "https://github.com/gasyoun/VisualDCS",
    "csl-atlas": "https://github.com/sanskrit-lexicon/csl-atlas",
    "csl-apidev": "https://github.com/sanskrit-lexicon/csl-apidev",
    "csl-guides": "https://github.com/sanskrit-lexicon/csl-guides",
    "csl-orig": "https://github.com/sanskrit-lexicon/csl-orig",
    "csl-observatory": "https://github.com/sanskrit-lexicon/csl-observatory",
    "csl-corrections": "https://github.com/sanskrit-lexicon/csl-corrections",
    "sanskrit-util": "https://github.com/sanskrit-lexicon/sanskrit-util",
    "SanskritSpellCheck": "https://github.com/drdhaval2785/SanskritSpellCheck",
    # RussianTranslation is a subdir of SanskritLexicography, not its own repo:
    "RussianTranslation": "https://github.com/gasyoun/SanskritLexicography/tree/master/RussianTranslation",
}

# match a repo name only as a whole token (so "SanskritLexicography" inside a URL is NOT touched
# — the caller must apply this ONLY to a plain repo segment, never to a field containing a link).
_NAME = re.compile("|".join(sorted((re.escape(k) for k in REPO_URL), key=len, reverse=True)))
_MODEL = re.compile(r"(?:Opus|Sonnet|Fable|Haiku)\s*[0-9.]+\s*\((`claude-[a-z0-9.-]+`)\)")
_DMY = re.compile(r"\b(\d{2})-(\d{2})-(20\d{2})\b")


def repo_link(name):
    """A single repo token -> markdown link (or the bare name if unknown)."""
    url = REPO_URL.get(name)
    return f"[{name}]({url})" if url else name


def linkify_repo_segment(seg):
    """Linkify every known repo name in a PLAIN segment (must contain no existing `](` link)."""
    if "](" in seg or "http" in seg:
        return seg
    return _NAME.sub(lambda m: repo_link(m.group(0)), seg)


def strip_model_tier(text):
    """'Opus 4.8 (`claude-opus-4-8`)' -> '`claude-opus-4-8`' (keep the bare version id)."""
    return _MODEL.sub(r"\1", text)


def commits_url(repo_url, branch, y, m, d):
    """That day's commits in the repo (since..until spans the single day)."""
    from datetime import date, timedelta
    nxt = date(int(y), int(m), int(d)) + timedelta(days=1)
    return (f"{repo_url}/commits/{branch}?since={y}-{m}-{d}"
            f"&until={nxt.year:04d}-{nxt.month:02d}-{nxt.day:02d}")


def date_link(dmy, repo_url, branch):
    """'08-07-2026' -> '[08-07-2026](…/commits/<branch>?since=2026-07-08&until=2026-07-09)'."""
    m = _DMY.fullmatch(dmy)
    if not m:
        return dmy
    d, mo, y = m.groups()
    return f"[{dmy}]({commits_url(repo_url, branch, y, mo, d)})"
