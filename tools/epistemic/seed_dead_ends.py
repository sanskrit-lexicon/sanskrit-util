#!/usr/bin/env python3
"""seed_dead_ends.py — auto-seed DEAD_ENDS.md candidate rows (H356, medium automation).

Harvests two sources of abandoned approaches:
  1. QUESTIONS_LOG.md rows whose outcome is **refuted** (a hypothesis that did not survive).
  2. SERVER_OUTAGES.md rows flagged **permanent** / **dead** (a host that will not come back).

Each becomes a ⚙️ candidate DEAD_ENDS row. QUESTIONS_LOG refuted rows are per-*hypothesis*;
a human decides whether the refutation generalises to a whole *approach* worth a dead-end row
(the two are not identical — see the DEAD_ENDS preamble). Emits Markdown to stdout.

Usage:
    python seed_dead_ends.py [--questions-log <QUESTIONS_LOG.md>] \
        [--server-outages <SERVER_OUTAGES.md>] --today DD-MM-YYYY [--repo <name>]

The parsers are table-shape-tolerant: they look for a row (markdown table line or a bullet)
that carries a refuted/permanent marker and pull the id + nearest descriptive text. Output is
a starting point, not a finished registry.
"""
import argparse
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _provenance import linkify_repo_segment  # clickable repo tags in Source lines

REFUTED = re.compile(r"refut", re.I)
PERMANENT = re.compile(r"\b(permanent|permanently|dead|walled|hard[- ]?down|do not retry)\b", re.I)
QID = re.compile(r"\b([QTR]\d{4}-\d{2})\b")            # Q2607-08 / T2607-01 / R2606-01
HOST = re.compile(r"\b([a-z0-9.-]+\.[a-z]{2,}(?:/\S*)?)\b", re.I)


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def harvest_refuted(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not REFUTED.search(line):
                continue
            m = QID.search(line)
            qid = m.group(1) if m else "?"
            # grab the longest cell as the description
            desc = ""
            if "|" in line:
                cc = cells(line)
                desc = max(cc, key=len) if cc else ""
            else:
                desc = line.strip("-*# ").strip()
            out.append((qid, desc[:200]))
    return out


def harvest_permanent(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if not PERMANENT.search(line):
                continue
            h = HOST.search(line)
            host = h.group(1) if h else "?"
            desc = ""
            if "|" in line:
                cc = cells(line)
                desc = max(cc, key=len) if cc else ""
            else:
                desc = line.strip("-*# ").strip()
            out.append((host, desc[:200]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions-log")
    ap.add_argument("--server-outages")
    ap.add_argument("--today", required=True)
    ap.add_argument("--repo", default="Uprava")
    args = ap.parse_args()

    n = 0
    if args.questions_log:
        refuted = harvest_refuted(args.questions_log)
        print(f"<!-- seed_dead_ends.py: {len(refuted)} refuted QUESTIONS_LOG rows "
              f"— ⚙️ UNCONFIRMED, a human decides if it generalises to an approach -->\n")
        for qid, desc in refuted:
            n += 1
            print(f"### §AUTO-{n}. {qid} — refuted approach")
            print(f"🟠 ⚙️ **{desc or qid}**")
            print("Failed because: <the concrete failure mode from the refuted row>")
            print(f"Evidence: QUESTIONS_LOG {qid} (refuted).")
            print("Don't retry unless: <the condition that would make it worth revisiting>")
            print(f"> **Source:** QUESTIONS_LOG {qid} · {linkify_repo_segment(args.repo)} · {args.today} "
                  f"· auto (seed_dead_ends.py)\n")

    if args.server_outages:
        perm = harvest_permanent(args.server_outages)
        print(f"<!-- seed_dead_ends.py: {len(perm)} permanent/dead SERVER_OUTAGES rows -->\n")
        for host, desc in perm:
            n += 1
            print(f"### §AUTO-{n}. `{host}` — permanently dead")
            print(f"🔴 ⚙️ **{desc or host}**")
            print("Failed because: <permanent block / dead origin>")
            print("Evidence: SERVER_OUTAGES permanent-blocks row.")
            print("Don't retry unless: <a different IP / the host returns / a mirror exists>")
            print(f"> **Source:** SERVER_OUTAGES `{host}` · {linkify_repo_segment(args.repo)} · {args.today} "
                  f"· auto (seed_dead_ends.py)\n")

    if not n:
        print("<!-- seed_dead_ends: pass --questions-log and/or --server-outages -->")


if __name__ == "__main__":
    main()
