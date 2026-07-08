#!/usr/bin/env python3
"""scan_assumptions.py — auto-seed ASSUMPTIONS.md candidate rows (H356, low automation).

Greps a code tree for tagged premises the pipelines rely on but never prove:
  * `# ASSUMES: <text>`     — an explicit relied-upon premise
  * `# INVARIANT: <text>`   — a condition the code assumes holds
  * a bare `assert <expr>`  in a *builder* file (dataset/crosswalk/promote scripts)

Each hit becomes a ⚙️ candidate ASSUMPTIONS row with `Relied on by` prefilled from the
enclosing file. Candidates are UNCONFIRMED — a human confirms (⚙️→✍️), fills the Test, or
deletes. Emits Markdown to stdout; pipe/paste into the side's ASSUMPTIONS.md and renumber.

Usage:
    python scan_assumptions.py --root <dir> [--root <dir> ...] --today DD-MM-YYYY \
        [--repo <name>] [--glob '*.py']
"""
import argparse
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _provenance import linkify_repo_segment  # clickable repo tags in Source lines

TAG = re.compile(r"#\s*(ASSUMES|INVARIANT)\s*:\s*(.+?)\s*$", re.I)
ASSERT = re.compile(r"^\s*assert\s+(.+?)\s*$")
BUILDER = re.compile(r"(build|promote|derive|crosswalk|merge|seed|gen_|import)", re.I)
DEFAULT_EXTS = (".py", ".mjs", ".js", ".sh")


def scan_file(path):
    hits = []
    is_builder = bool(BUILDER.search(os.path.basename(path)))
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                m = TAG.search(line)
                if m:
                    hits.append((m.group(1).upper(), m.group(2), lineno))
                elif is_builder:
                    a = ASSERT.match(line)
                    if a and "test" not in path.lower():
                        hits.append(("ASSERT", a.group(1)[:120], lineno))
    except OSError:
        pass
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="append", required=True)
    ap.add_argument("--today", required=True)
    ap.add_argument("--repo", default="<repo>")
    ap.add_argument("--glob", default=None, help="restrict to files matching this substring/ext")
    args = ap.parse_args()

    rows = []
    for root in args.root:
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in
                       (".git", "node_modules", "__pycache__", ".venv", "venv")]
            for fn in files:
                if not fn.endswith(DEFAULT_EXTS):
                    continue
                if args.glob and args.glob not in fn:
                    continue
                p = os.path.join(dirpath, fn)
                for kind, text, lineno in scan_file(p):
                    rows.append((os.path.relpath(p, root).replace("\\", "/"), lineno, kind, text))

    if not rows:
        print("<!-- scan_assumptions: no # ASSUMES: / # INVARIANT: / builder-assert tags found -->")
        return

    print(f"<!-- scan_assumptions.py candidates ({len(rows)}) — ⚙️ UNCONFIRMED, "
          f"human promotes/deletes -->\n")
    for i, (rel, lineno, kind, text) in enumerate(rows, 1):
        print(f"### §AUTO-{i}. {text[:70]}")
        print(f"🟡 ⚙️ **{text}**")
        print(f"Relied on by: `{rel}` (via `{kind}` at line {lineno}) — trace its consumers.")
        print("Verified?: ❌ never (auto-flagged premise)")
        print("Test to confirm: <fill in — the check that would validate or refute this>")
        print(f"> **Source:** `{rel}:{lineno}` · {linkify_repo_segment(args.repo)} · {args.today} · auto (scan_assumptions.py)\n")


if __name__ == "__main__":
    main()
