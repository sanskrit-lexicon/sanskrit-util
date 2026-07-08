#!/usr/bin/env python3
"""normalize_provenance.py — rewrite every `> **Source:**` line in the episteme registries of a
directory to the three MG conventions (see `_provenance.py`): clickable repo tags, bare model
version id, and a commits-by-date link on the provenance date. Idempotent — safe to re-run.

Usage:
    python normalize_provenance.py --dir <registries-dir> --repo-url <repo-root-url> --branch <b>

Only the six entry-shaped registries are touched (STALENESS is a generated table with no Source
lines). Every other line is passed through untouched.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _provenance import (REPO_URL, date_link, linkify_repo_segment,  # noqa: E402
                         strip_model_tier)

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

FILES = ["ASSUMPTIONS", "CONTRADICTIONS", "GAPS", "DEAD_ENDS", "RECIPES", "GLOSSARY"]
SOURCE = re.compile(r"^> \*\*Source:\*\* ")
_DMY_FULL = re.compile(r"^\d{2}-\d{2}-20\d{2}$")
_LEAD_REPO = re.compile(r"^(" + "|".join(sorted((re.escape(k) for k in REPO_URL),
                                                key=len, reverse=True)) + r")(\b)")


def fix_line(line, repo_url, branch):
    if not SOURCE.match(line):
        return line
    fields = line.split(" · ")
    out = []
    for i, f in enumerate(fields):
        if i == 0:
            # linkify a LEADING bare repo token right after "> **Source:** "
            head = "> **Source:** "
            rest = f[len(head):] if f.startswith(head) else f
            if "](" not in rest.split(" ")[0]:  # first word isn't already a link
                rest = _LEAD_REPO.sub(lambda m: f"[{m.group(1)}]({REPO_URL[m.group(1)]}){m.group(2)}", rest, count=1)
            out.append(head + rest if f.startswith(head) else rest)
            continue
        f = strip_model_tier(f)
        if _DMY_FULL.match(f.strip()):
            out.append(date_link(f.strip(), repo_url, branch))
        else:
            out.append(linkify_repo_segment(f))
    return " · ".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--repo-url", required=True, help="repo root, e.g. https://github.com/gasyoun/Uprava")
    ap.add_argument("--branch", required=True, help="default branch, e.g. master or main")
    args = ap.parse_args()

    root = Path(args.dir)
    for name in FILES:
        p = root / f"{name}.md"
        if not p.exists():
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        new = [fix_line(ln, args.repo_url, args.branch) for ln in lines]
        changed = sum(1 for a, b in zip(lines, new) if a != b)
        if changed:
            p.write_text("\n".join(new), encoding="utf-8")
        print(f"{name}.md: {changed} Source lines normalized")


if __name__ == "__main__":
    main()
