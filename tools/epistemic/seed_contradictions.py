#!/usr/bin/env python3
"""seed_contradictions.py — auto-seed CONTRADICTIONS.md candidate rows (H356, medium automation).

Crosswalk-mismatch finder: given two TSV/CSV tables that are supposed to agree on a value for a
shared key, emit a ⚙️ candidate CONTRADICTIONS row for every key present in both sides whose
value differs. This is the cheap, high-yield seed the handoff calls out — run it over
`mw_roots`, `union_headwords` membership, DCS↔Whitney class crosswalks, etc.

Keys are compared with `form_key()` from sanskrit-util when available (length-preserving,
scheme-safe — never NFD+strip, see FINDINGS §36), falling back to a trimmed raw string so the
tool runs even outside an installed sanskrit-util.

Usage:
    python seed_contradictions.py --a <a.tsv> --b <b.tsv> \
        --key-col <name-or-index> --val-col <name-or-index> \
        [--a-label MW] [--b-label Whitney] --today DD-MM-YYYY [--repo <name>] [--limit 40]
"""
import argparse
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _provenance import linkify_repo_segment  # clickable repo tags in Source lines

try:  # length-preserving, scheme-safe key — the canonical helper
    from sanskrit_util import form_key as _form_key  # type: ignore
except Exception:  # pragma: no cover - fallback when the package isn't importable
    def _form_key(s):
        return (s or "").strip()


def _delim(path):
    return "\t" if path.lower().endswith((".tsv", ".tab")) else ","


def load(path, key_col, val_col):
    out = {}
    with open(path, encoding="utf-8", newline="") as f:
        rdr = csv.reader(f, delimiter=_delim(path))
        rows = list(rdr)
    if not rows:
        return out
    header = rows[0]

    def resolve(col):
        if col.isdigit():
            return int(col)
        return header.index(col)

    ki, vi = resolve(key_col), resolve(val_col)
    start = 0 if (key_col.isdigit() and val_col.isdigit()) else 1
    for r in rows[start:]:
        if len(r) <= max(ki, vi):
            continue
        k = _form_key(r[ki])
        if k:
            out[k] = r[vi].strip()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--key-col", required=True)
    ap.add_argument("--val-col", required=True)
    ap.add_argument("--a-label", default="A")
    ap.add_argument("--b-label", default="B")
    ap.add_argument("--today", required=True)
    ap.add_argument("--repo", default="<repo>")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()

    a = load(args.a, args.key_col, args.val_col)
    b = load(args.b, args.key_col, args.val_col)
    shared = sorted(set(a) & set(b))
    mism = [(k, a[k], b[k]) for k in shared if a[k] != b[k]]

    print(f"<!-- seed_contradictions.py: {len(shared)} shared keys, {len(mism)} mismatches "
          f"({args.a_label} vs {args.b_label}) — ⚙️ UNCONFIRMED candidates -->\n")
    for i, (k, av, bv) in enumerate(mism[: args.limit], 1):
        print(f"### §AUTO-{i}. `{k}`: {args.a_label} vs {args.b_label} disagree")
        print(f"🟠 ⚙️ **`{args.a_label}` says `{av}`, `{args.b_label}` says `{bv}` for `{k}`.**")
        print("Positions:")
        print("| Source | Value | Evidence loc |")
        print("|--------|-------|--------------|")
        print(f"| {args.a_label} | `{av}` | `{args.a}` |")
        print(f"| {args.b_label} | `{bv}` | `{args.b}` |")
        print("Status: 🔴 unresolved — <confirm it's a real disagreement, not a keying artifact>")
        print("Blocks: <the join / merge that can't proceed>")
        print(f"> **Source:** `{args.a}` vs `{args.b}` · {linkify_repo_segment(args.repo)} · {args.today} "
              f"· auto (seed_contradictions.py)\n")
    if len(mism) > args.limit:
        print(f"<!-- +{len(mism) - args.limit} more mismatches suppressed by --limit -->")


if __name__ == "__main__":
    main()
